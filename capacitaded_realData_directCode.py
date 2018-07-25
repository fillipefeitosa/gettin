# Import Libraries
from gurobi import *
import math
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import geopy.distance
from collections import defaultdict
# TEST Used for testing with a small sample
# import random

# ------------------------- Problem data ------------------------- #

# Dict for SubSections With Demand
rawData = pd.read_excel('./subseccao_vagos/Pop_escolar_Vagos.xlsx')
listOfSubsections_2010 = {}
for e in range(len(rawData)-1):
    listOfSubsections_2010[int(rawData.SUBSECCAO[e])] = rawData.P_esc_1CEB_2010[e]+ rawData.P_esc_2CEB_2010[e]+rawData.P_esc_3CEB_2010[e]+rawData.P_esc_secund_2010[e]+rawData.Pre_escolar_2010[e]


# TEST Used _sample for testing with a small sample to CREATE A SAMPLE OF POTENTIAL SCHOOL POINTS
# listOfSubsections_2010 = {}

# for i in range(15):
#     sampleSchool, sampleDemand = random.choice(list(listOfSubsections_2010_total.items()))
#     if sampleSchool not in schoolsCapacityCost:
#         listOfSubsections_2010[sampleSchool] = sampleDemand


# Dict of Lists for Schools with Capacity And Cost by Size
tupleOfCapacity = (80, 120, 200)

# TEST used for testing with small sample
# tupleOfCapacity = (10, 20, 50)

schoolsCapacityCost = defaultdict(list)

# # TEST Using _SAMPLE to get a sample of Points to create schools
for bgri in list(listOfSubsections_2010.keys()):
    for capacity in tupleOfCapacity:
        cost = capacity*6200
        tempList = (capacity, cost)
        schoolsCapacityCost[bgri].append(tempList)


# Retrieve Coordinates and Vinculate to Identifier (BGRI)
vagos = gpd.read_file('./data_gettin/vagos.geojson');
centroids = vagos.centroid

iteratorHandler = centroids.size
centroidVector = []
for centroid in centroids:
    obj = [centroid.xy[0][0], centroid.xy[1][0]]
    centroidVector.append(obj)

coordinates_X = {}
coordinates_Y = {}
for e in range (len(vagos)):
    coordinates_X[int(vagos.BGRI11[e])] = centroids[e].xy[0][0]
    coordinates_Y[int(vagos.BGRI11[e])] = centroids[e].xy[1][0]

coordinates_X[list(listOfSubsections_2010.keys())[0]]



# -------- Distance Matrix Logic ------- #
transportationCosts = {}

for bgri_1 in list(listOfSubsections_2010.keys()):
    coords_1 = (coordinates_X[bgri_1], coordinates_Y[bgri_1])
    for bgri_2 in list(listOfSubsections_2010.keys()):
        coords_2 = (coordinates_X[bgri_2], coordinates_Y[bgri_2])
        # 0.29 cents per KM * 180 days
        cost = geopy.distance.vincenty(coords_1, coords_2).km*0.29*180
        transportationCosts[bgri_1, bgri_2] = cost

transportationCosts





# -------- Decision Variables ---------- #

# numSchools = len(escola)
# numSubSections = len(subSecao)

# Creting Guroby Model
m = Model()

# Decision Variables
x = {}
y = {}
# d = {} # Distance Matrix
# @alpha: 0.29 de custo por Km  por (365 dias * 5 anos)
# alpha = 529.25

# creating binary variable for every school
for j in list(schoolsCapacityCost.keys()):
    for schoolSize in tupleOfCapacity:
        x[(j,schoolSize)] = m.addVar(vtype=GRB.BINARY, name="escola(%d,%d)" % (j, schoolSize))

# creating continuous variable for subsections to check suply fractions
for subsection in list(listOfSubsections_2010.keys()):
    for school in list(schoolsCapacityCost.keys()):
        for capacity in schoolsCapacityCost[school]:
        # y of Subsection Suply
            y[(subsection,school,capacity[0])] = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Fração da Sub[%d], escola[%d][%d]" % (subsection,school, capacity[0]))

m.update()



# Constraint for Every Student on School
# for i in range(numSubSections):
#     m.addConstr(quicksum(y[(i,j)] for j in range(numSchools)) == 1)

# Constraint to repect demands on Every Subsection - OK
for i in list(listOfSubsections_2010.keys()):
    m.addConstr(quicksum(y[(i,j,k)] for j in list(schoolsCapacityCost.keys()) for k in tupleOfCapacity) == listOfSubsections_2010[i])

# Constraint to restrain school capacity - OK
for school in list(schoolsCapacityCost.keys()):
    for schoolSize in range(len(schoolsCapacityCost[school])):
        numericalSizeOfSchool = schoolsCapacityCost[school][schoolSize][0]
        m.addConstr(quicksum(y[(i,school, numericalSizeOfSchool)] for i in list(listOfSubsections_2010.keys())) <= numericalSizeOfSchool * x[school, numericalSizeOfSchool], "SchoolK(%s,%s)"%(school, numericalSizeOfSchool))

# Add restriction to fraction Size - OK
for (i,j,k) in y:
    m.addConstr(y[i,j,k] <= listOfSubsections_2010[i]*x[j, k], "FractionConst(%s,%s,%s)"%(i,j,k))

# Setting objective

m.setObjective(
    quicksum(schoolsCapacityCost[school][schoolSize][1]*x[school, schoolsCapacityCost[school][schoolSize][0]] for school in list(schoolsCapacityCost.keys()) for schoolSize in range(len(schoolsCapacityCost[school]))) +
    quicksum(transportationCosts[i,j]*y[i,j,k] for i in list(listOfSubsections_2010.keys()) for j in list(schoolsCapacityCost.keys()) for k in tupleOfCapacity), GRB.MINIMIZE )


m.optimize()

m.getConstrs()

print('Obj: %g' % m.objVal)

for v in m.getVars():
    if(v.x != 0):
       print('%s   %g' % (v.varName, v.x))

m = None

disposeDefaultEnv()
