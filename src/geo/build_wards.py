"""Clean raw Chennai ward GeoJSON -> data/gazetteer/wards.geojson (ward_no + polygon only)."""
import json
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import force_2d

RAW = "data/gazetteer/wards_raw.geojson"
OUT = "data/gazetteer/wards.geojson"

def polygons_only(geom):
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        return geom
    parts = [g for g in geom.geoms if isinstance(g, (Polygon, MultiPolygon))]
    return unary_union(parts)

def main():
    raw = json.load(open(RAW, encoding="utf-8"))
    feats = []
    for f in raw["features"]:
        ward_no = int(f["properties"]["name2"].strip())
        geom = force_2d(polygons_only(shape(f["geometry"])))
        if not geom.is_valid:
            geom = geom.buffer(0)
        feats.append({"type": "Feature",
                      "properties": {"ward_no": ward_no},
                      "geometry": mapping(geom)})
    feats.sort(key=lambda x: x["properties"]["ward_no"])
    json.dump({"type": "FeatureCollection", "features": feats},
              open(OUT, "w", encoding="utf-8"))
    print(f"wrote {len(feats)} wards -> {OUT}")

if __name__ == "__main__":
    main()
