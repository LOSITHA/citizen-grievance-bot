import sys
from src.geo.ward_lookup import WardLookup

lat, lon = float(sys.argv[1]), float(sys.argv[2])
print(WardLookup().ward_of(lat, lon, return_how=True))
