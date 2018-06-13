import shapefile as sh
from pprint import pprint

# Read ShapeFile Folder to create a Reader Obj
# sf = sh.Reader("escolas_detim/equipamentos_escolares_novo")
sf = sh.Reader("escolas_wg8/Escolas_novo")

print("Equipamentos Escolares -> Fields \n")
pprint(sf.fields)

print("\n \n \n Quantidade de Escolas -> Records \n")
print(len(sf.records()))

# Tests using SHapeRecords
shapeRecords = sf.shapeRecords()
record1 = shapeRecords[0]
print("Record 1: ", record1.record)
print("Record 1 Points: ", record1.shape.points)
      
# Show Shapes and Records
for shapeRecord in sf.shapeRecords():
    print("Escola: ", shapeRecord.record[7]) 
    print("x: ", shapeRecord.shape.points[0][0])
    print("y: ", shapeRecord.shape.points[0][1])
    print("--------------")

# Tests with Records and Geo_Interface
print("----------- Geo_Interface Test ----------")
s = sf.shape(0)
print(s.__geo_interface__["coordinates"])

s2 = sf.shape(1)
print(s2.__geo_interface__["coordinates"])

