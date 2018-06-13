import shapefile
from json import dumps

# Read ShapeFile
shpReader = shapefile.Reader("../learning/centroids.geojson/centroids")
shpFields = shpReader.fields[1:]
fieldNames = [field[0] for field in shpFields]
buffer = []

# Iterate over Records to feed the Buffer
for record in shpReader.shapeRecords():
    attr = dict(zip(fieldNames, record.record))
    geom = record.shape.__geo_interface__
    buffer.append(dict(type="Feature", geometry=geom, properties=attr))

# write GeoJson File
geojson = open("centroidsVagos.geojson", "w")
geojson.write(dumps({"type": "FeatureCollection", "features": buffer}))
geojson.close()

