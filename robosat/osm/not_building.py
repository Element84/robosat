# This should live in robosat/osm/not_building.py
# This is the inverse of the BuildingHandler. Instead of gathering all "building"
# polygons, this gathers all polygons that are not tagged "building"

import sys

import osmium
import geojson
import shapely.geometry

from robosat.osm.building import BuildingHandler
from robosat.osm.core import is_polygon


class NotBuildingHandler(osmium.SimpleHandler):
    """Extracts all non-building polygon features (visible in satellite imagery) from the map.
    """

    # building=* to discard because these features are not vislible in satellite imagery
    building_filter = set(
        ["construction", "houseboat", "static_caravan", "stadium", "conservatory", "digester", "greenhouse", "ruins"]
    )

    # location=* to discard because these features are not vislible in satellite imagery
    location_filter = set(["underground", "underwater"])

    def __init__(self):
        super().__init__()
        self.features = []

    def way(self, w):
        if not is_polygon(w):
            return

        # This is the reverse of BuildingHandler's logic
        if "building" in w.tags:
            return


        if "location" in w.tags and w.tags["location"] in self.location_filter:
            return

        geometry = geojson.Polygon([[(n.lon, n.lat) for n in w.nodes]])
        shape = shapely.geometry.shape(geometry)

        if shape.is_valid:
            feature = geojson.Feature(geometry=geometry)
            self.features.append(feature)
        else:
            print("Warning: invalid feature: https://www.openstreetmap.org/way/{}".format(w.id), file=sys.stderr)

    def save(self, out):
        collection = geojson.FeatureCollection(self.features)

        with open(out, "w") as fp:
            geojson.dump(collection, fp)
