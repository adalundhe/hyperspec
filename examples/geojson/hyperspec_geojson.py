from __future__ import annotations

import hyperspec

Position = tuple[float, float]


# Define the 7 standard Geometry types.
# All types set `tag=True`, meaning that they'll make use of a `type` field to
# disambiguate between types when decoding.
class Point(hyperspec.Struct, tag=True):
    coordinates: Position


class MultiPoint(hyperspec.Struct, tag=True):
    coordinates: list[Position]


class LineString(hyperspec.Struct, tag=True):
    coordinates: list[Position]


class MultiLineString(hyperspec.Struct, tag=True):
    coordinates: list[list[Position]]


class Polygon(hyperspec.Struct, tag=True):
    coordinates: list[list[Position]]


class MultiPolygon(hyperspec.Struct, tag=True):
    coordinates: list[list[list[Position]]]


class GeometryCollection(hyperspec.Struct, tag=True):
    geometries: list[Geometry]


Geometry = (
    Point
    | MultiPoint
    | LineString
    | MultiLineString
    | Polygon
    | MultiPolygon
    | GeometryCollection
)


# Define the two Feature types
class Feature(hyperspec.Struct, tag=True):
    geometry: Geometry | None = None
    properties: dict | None = None
    id: str | int | None = None


class FeatureCollection(hyperspec.Struct, tag=True):
    features: list[Feature]


# A union of all 9 GeoJSON types
GeoJSON = Geometry | Feature | FeatureCollection


# Create a decoder and an encoder to use for decoding & encoding GeoJSON types
loads = hyperspec.json.Decoder(GeoJSON).decode
dumps = hyperspec.json.Encoder().encode
