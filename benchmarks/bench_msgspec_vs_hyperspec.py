"""
Benchmark msgspec (upstream) vs hyperspec (this fork).

Measures two things for each library:
1) Struct instantiation time (constructing 10k objects from already-typed values)
2) Validation/conversion time (converting 10k nested dict payloads into Structs)

Usage:
  python benchmarks/bench_msgspec_vs_hyperspec.py --runs 10 --n 10000

Notes:
- Requires BOTH `msgspec` and `hyperspec` importable in the environment.
- Designed to be "reasonably sophisticated": nested structs, lists, dicts, UUID,
  datetime, and a handful of validation constraints via Meta.
"""

import argparse
import gc
import statistics as stats
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Annotated, Any


def _pct(delta: float, base: float) -> float:
    if base == 0:
        return float("nan")
    return 100.0 * (delta / base)


def _classify_regression(pct_slower: float) -> str:
    # pct_slower > 0 means hyperspec slower than msgspec
    if pct_slower <= 0.0:
        return "hyperspec faster"
    if pct_slower <= 1.0:
        return "within 1%"
    if pct_slower <= 5.0:
        return "within 5%"
    if pct_slower <= 10.0:
        return "within 10%"
    return "more than 10%"


def _bench_one(lib: Any, *, n: int) -> dict[str, float]:
    """
    Returns timings in seconds:
      - instantiate_s
      - validate_s
    """
    Struct = lib.Struct
    Meta = lib.Meta
    convert = lib.convert

    class Address(Struct):
        line1: Annotated[str, Meta(min_length=5, max_length=64)]
        city: Annotated[str, Meta(min_length=2, max_length=40)]
        postal_code: Annotated[str, Meta(min_length=4, max_length=12)]
        country: Annotated[str, Meta(min_length=2, max_length=2)]

    class Event(Struct):
        ts: datetime
        kind: Annotated[str, Meta(min_length=3, max_length=24)]
        payload: dict[str, int]

    class Profile(Struct):
        display_name: Annotated[str, Meta(min_length=1, max_length=32)]
        bio: Annotated[str, Meta(max_length=160)]
        address: Address

    class User(Struct):
        user_id: uuid.UUID
        created_at: datetime
        active: bool
        score: Annotated[int, Meta(ge=0, le=1_000_000)]
        tags: list[str]
        profile: Profile
        events: list[Event]

    # Pre-create already-typed values for instantiation
    uid0 = uuid.uuid4()
    now = datetime.now(tz=timezone.utc)
    addr = Address(
        line1="123 Benchmark Ave",
        city="Testville",
        postal_code="12345",
        country="US",
    )
    prof = Profile(display_name="alice", bio="bio", address=addr)
    evs = [
        Event(ts=now, kind="login", payload={"ok": 1, "lat_ms": 12}),
        Event(ts=now, kind="click", payload={"x": 3, "y": 9}),
    ]

    # Pre-create raw payloads for validation/conversion
    raw_one = {
        "user_id": str(uid0),
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "active": True,
        "score": 123,
        "tags": ["a", "b", "c", "d"],
        "profile": {
            "display_name": "alice",
            "bio": "bio",
            "address": {
                "line1": "123 Benchmark Ave",
                "city": "Testville",
                "postal_code": "12345",
                "country": "US",
            },
        },
        "events": [
            {
                "ts": now.isoformat().replace("+00:00", "Z"),
                "kind": "login",
                "payload": {"ok": 1, "lat_ms": 12},
            },
            {
                "ts": now.isoformat().replace("+00:00", "Z"),
                "kind": "click",
                "payload": {"x": 3, "y": 9},
            },
        ],
    }
    raw = [raw_one] * n

    # --- Measure instantiation ---
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        t0 = time.perf_counter()
        out = [
            User(
                user_id=uid0,
                created_at=now,
                active=True,
                score=i,
                tags=["a", "b", "c", "d"],
                profile=prof,
                events=evs,
            )
            for i in range(n)
        ]
        # Use the objects so they aren't optimized away
        if len(out) != n:
            raise RuntimeError("unexpected length")
        t1 = time.perf_counter()
        instantiate_s = t1 - t0
    finally:
        if gc_was_enabled:
            gc.enable()

    # --- Measure validation/conversion ---
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        t0 = time.perf_counter()
        out2 = convert(raw, type=list[User])
        if len(out2) != n:
            raise RuntimeError("unexpected length")
        t1 = time.perf_counter()
        validate_s = t1 - t0
    finally:
        if gc_was_enabled:
            gc.enable()

    return {"instantiate_s": instantiate_s, "validate_s": validate_s}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10_000, help="number of objects")
    ap.add_argument(
        "--runs",
        type=int,
        default=10,
        help="number of benchmark runs (max 10 recommended)",
    )
    ap.add_argument("--warmup", type=int, default=1, help="warmup runs (not counted)")
    args = ap.parse_args(argv)

    try:
        import msgspec as msgspec_lib  # upstream
    except Exception as e:  # noqa: BLE001
        print(
            "ERROR: couldn't import `msgspec` (upstream). Install it first, e.g. `pip install msgspec`.",
            file=sys.stderr,
        )
        print(f"  import error: {e!r}", file=sys.stderr)
        return 2

    import hyperspec as hyperspec_lib  # this fork

    runs = max(1, min(args.runs, 10))
    warmup = max(0, args.warmup)
    n = args.n

    print(f"Python: {sys.version.splitlines()[0]}")
    print(f"n={n} runs={runs} warmup={warmup}")
    print(f"msgspec version: {getattr(msgspec_lib, '__version__', 'unknown')}")
    print(f"hyperspec version: {getattr(hyperspec_lib, '__version__', 'unknown')}")
    print()

    # warmup
    for _ in range(warmup):
        _bench_one(msgspec_lib, n=max(100, n // 100))
        _bench_one(hyperspec_lib, n=max(100, n // 100))

    msg_inst, msg_val = [], []
    hyp_inst, hyp_val = [], []

    for i in range(runs):
        m = _bench_one(msgspec_lib, n=n)
        h = _bench_one(hyperspec_lib, n=n)
        msg_inst.append(m["instantiate_s"])
        msg_val.append(m["validate_s"])
        hyp_inst.append(h["instantiate_s"])
        hyp_val.append(h["validate_s"])

        inst_pct = _pct(h["instantiate_s"] - m["instantiate_s"], m["instantiate_s"])
        val_pct = _pct(h["validate_s"] - m["validate_s"], m["validate_s"])
        print(
            f"run {i + 1:02d}/{runs}: "
            f"inst msg={m['instantiate_s']:.6f}s hyp={h['instantiate_s']:.6f}s ({inst_pct:+.2f}%) | "
            f"val msg={m['validate_s']:.6f}s hyp={h['validate_s']:.6f}s ({val_pct:+.2f}%)"
        )

    def summarize(
        name: str, msg: list[float], hyp: list[float]
    ) -> tuple[float, float, float]:
        m_med = stats.median(msg)
        h_med = stats.median(hyp)
        pct = _pct(h_med - m_med, m_med)
        print(
            f"{name}: median msg={m_med:.6f}s hyp={h_med:.6f}s ({pct:+.2f}%) => {_classify_regression(pct)}"
        )
        return m_med, h_med, pct

    print()
    inst_med_msg, inst_med_hyp, inst_pct = summarize("instantiate", msg_inst, hyp_inst)
    val_med_msg, val_med_hyp, val_pct = summarize("validate", msg_val, hyp_val)

    # Worst-case *slowdown* (ignore cases where hyperspec is faster)
    worst_pct = max(0.0, inst_pct, val_pct)
    print()
    print(
        f"worst-case median regression: {worst_pct:+.2f}% ({_classify_regression(worst_pct)})"
    )

    # Enforce: hyperspec must not be more than 1% slower on median for either.
    if inst_pct > 1.0 or val_pct > 1.0:
        print("\nFAIL: hyperspec regression > 1% (unacceptable).", file=sys.stderr)
        return 1
    print("\nPASS: hyperspec within 1% for both instantiation and validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
