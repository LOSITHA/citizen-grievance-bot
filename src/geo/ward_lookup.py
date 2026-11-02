"""Map a (lat, lon) point to a GCC ward number."""
import geopandas as gpd
from shapely.geometry import Point

class WardLookup:
    def __init__(self, path="data/gazetteer/wards.geojson", snap_m=150):
        w = gpd.read_file(path).set_crs(epsg=4326, allow_override=True)
        self.wards = w
        self.proj = w.to_crs(epsg=32644)  # UTM 44N, metres (Chennai)
        self.sindex = self.proj.sindex
        self.snap_m = snap_m

    def ward_of(self, lat, lon, return_how=False):
        pt = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(epsg=32644).iloc[0]
        hits = self.sindex.query(pt, predicate="intersects")
        if len(hits):
            res = (int(self.proj.iloc[hits[0]]["ward_no"]), "inside")
        else:
            i = self.sindex.nearest(pt)[1][0]
            d = self.proj.geometry.iloc[i].distance(pt)
            res = (int(self.proj.iloc[i]["ward_no"]), f"snapped_{d:.0f}m") if d <= self.snap_m else (None, "outside_gcc")
        return res if return_how else res[0]

if __name__ == "__main__":
    wl = WardLookup()
    tests = {"Marina Beach": (13.0500, 80.2824), "T Nagar": (13.0418, 80.2341),
             "Guindy": (13.0067, 80.2206), "Tambaram": (12.9249, 80.1000)}
    for name, (la, lo) in tests.items():
        print(name, "->", wl.ward_of(la, lo, return_how=True))
