API Docs
========

Structs
-------

.. currentmodule:: hyperspec

.. autoclass:: Struct

.. autoclass:: StructMeta(name, bases, namespace, /, *, **struct_config)

.. autofunction:: field

.. autofunction:: defstruct

.. autofunction:: hyperspec.structs.replace

.. autofunction:: hyperspec.structs.asdict

.. autofunction:: hyperspec.structs.astuple

.. autofunction:: hyperspec.structs.force_setattr

.. autofunction:: hyperspec.structs.fields

.. autoclass:: hyperspec.structs.FieldInfo

.. autoclass:: hyperspec.structs.StructConfig

.. autodata:: NODEFAULT
   :no-value:

Meta
----

.. autoclass:: Meta
    :members:


Raw
---

.. currentmodule:: hyperspec

.. autoclass:: Raw
    :members:

Unset
-----

.. autodata:: UNSET
   :no-value:

.. autoclass:: UnsetType


JSON
----

.. currentmodule:: hyperspec.json

.. autoclass:: Encoder
    :members: encode, encode_lines, encode_into

.. autoclass:: Decoder
    :members: decode, decode_lines

.. autofunction:: encode

.. autofunction:: decode

.. autofunction:: format


MessagePack
-----------

.. currentmodule:: hyperspec.msgpack

.. autoclass:: Encoder
    :members: encode, encode_into

.. autoclass:: Decoder
    :members: decode

.. autoclass:: Ext
    :members:

.. autofunction:: encode

.. autofunction:: decode


YAML
----

.. currentmodule:: hyperspec.yaml

.. autofunction:: encode

.. autofunction:: decode


TOML
----

.. currentmodule:: hyperspec.toml

.. autofunction:: encode

.. autofunction:: decode


JSON Schema
-----------

.. currentmodule:: hyperspec.json

.. autofunction:: schema

.. autofunction:: schema_components


.. _inspect-api:


Converters
----------

.. currentmodule:: hyperspec

.. autofunction:: convert

.. autofunction:: to_builtins


Inspect
-------

.. currentmodule:: hyperspec.inspect

.. autofunction:: is_struct
.. autofunction:: is_struct_type
.. autofunction:: type_info
.. autofunction:: multi_type_info
.. autoclass:: Type
.. autoclass:: Metadata
.. autoclass:: AnyType
.. autoclass:: NoneType
.. autoclass:: BoolType
.. autoclass:: IntType
.. autoclass:: FloatType
.. autoclass:: StrType
.. autoclass:: BytesType
.. autoclass:: ByteArrayType
.. autoclass:: MemoryViewType
.. autoclass:: DateTimeType
.. autoclass:: TimeType
.. autoclass:: DateType
.. autoclass:: TimeDeltaType
.. autoclass:: UUIDType
.. autoclass:: DecimalType
.. autoclass:: ExtType
.. autoclass:: RawType
.. autoclass:: EnumType
.. autoclass:: LiteralType
.. autoclass:: CustomType
.. autoclass:: UnionType
    :members:
.. autoclass:: CollectionType
.. autoclass:: ListType
.. autoclass:: SetType
.. autoclass:: FrozenSetType
.. autoclass:: VarTupleType
.. autoclass:: TupleType
.. autoclass:: DictType
.. autoclass:: Field
.. autoclass:: TypedDictType
.. autoclass:: NamedTupleType
.. autoclass:: DataclassType
.. autoclass:: StructType


Exceptions
----------

.. currentmodule:: hyperspec

.. autoexception:: MsgspecError
    :show-inheritance:

.. autoexception:: EncodeError
    :show-inheritance:

.. autoexception:: DecodeError
    :show-inheritance:

.. autoexception:: ValidationError
    :show-inheritance:
