# Import Libraries
from gurobi import *
import math
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import geopy.distance
from collections import defaultdict
from shapely.geometry import Point, LineString


def generate_lines(selectedPolygon, pd_SchoolAndBgri, schoolsPre):
    print("entered lines")
    prePolygonLines = pd.merge(selectedPolygon, pd_SchoolAndBgri, how='left', left_on=[selectedPolygon.BGRI11], right_on=[pd_SchoolAndBgri.BGRI])
    # Some BGRI are missing, or the demand is zero
    prePolygonLines = prePolygonLines[prePolygonLines['school'].notna()]
    prePolygonLines.school = prePolygonLines.school.astype(int)
    prePolygonLines.geometry = prePolygonLines.centroid

    # Get List of lines
    listOfLines = []

    for e in prePolygonLines.iterrows():
        pointSchool = [schoolsPre[schoolsPre.index==e[1].school].geometry.x.values[0], schoolsPre[schoolsPre.index==e[1].school].geometry.y.values[0]]
        line = LineString([[e[1].geometry.x, e[1].geometry.y],pointSchool])
        listOfLines.append(line)
    prePolygonLines['line'] = listOfLines

    # Lines
    teste = prePolygonLines
    teste.geometry = teste.line

    return teste

def generate_fig_projection(selectedPolygon,pd_SchoolAndBgri,schoolsPre,schoolSelection):
    print("entered fig projection")
    # PLOT
    teste = generate_lines(selectedPolygon, pd_SchoolAndBgri, schoolsPre)
    fig, ax = plt.subplots(figsize=(15,15))
    teste.plot(ax=ax, alpha=0.15, color='black')

    selectedPolygon.plot(ax=ax, facecolor='#E6E6FA', edgecolor='#B0C4DE')
    ax.set_axis_off()

    counter = 0
    for idx, row in schoolsPre.iterrows():
        if (counter%2 == 0):
            offset = {'x':-12, 'y':0}
        else:
            offset = {'x':+24, 'y':0}
        
        offset = {'x':45, 'y':-15} if idx==17 else offset
        ax.annotate(int(row['students']), xy=(row['geometry'].x,row['geometry'].y),
                xytext=(offset['x'], offset['y']), textcoords='offset points',
                size=8, ha='right', va="center",zorder=200,
                bbox=dict(boxstyle="round", alpha=0.8),
                arrowprops=dict(arrowstyle="-", alpha=1));
        ax.annotate(int(row[schoolSelection]), xy=(row['geometry'].x,row['geometry'].y),
                xytext=(offset['x'], offset['y']-13), textcoords='offset points',
                size=8, ha='right', va="center",zorder=200,
                bbox=dict(boxstyle="round", alpha=0.8, color='#FFFF66')
                );
        counter += 1
    schoolsPre.plot(ax=ax, markersize=40, color='red', marker='o', label='centroid')

    return fig

def generate_land_use():
    # _-------------_ Uso do Solo: Categorias _-----------_


    #recebe RGB em dicionários de float e devolve o hexadecimal correspondente
    def rgb_to_hex (diccionario_cores): 
        dict_novo = {}
        for nome in diccionario_cores:
            dict_novo [nome] = '#%02x%02x%02x'%tuple(int(i * 255) for i in diccionario_cores[nome])
        return(dict_novo)
    #define RGB para cada tipo de ocupação de solo 
    colors_cos = {'Territórios artificializados': (0.8, 0, 0),
                'Agricultura': (0.9, 0.7, 0.03), 
                'Pastagens': (0.96, 0.93, 0.03),
                'Sistemas agro-florestais': (0.85, 0.6, 0),
                'Florestas': (0, 0.5, 0), 
                'Matos': (0, 0.7, 0),
                'Espaços descobertos ou com vegetação esparsa': (0.9, 0.9, 0.5),
                'Zonas húmidas': (0.9, 0.9, 0.5), 
                'Corpos de água': (0.3, 0.6, 1)}
    colors_cos_hexa = rgb_to_hex(colors_cos)


    # _-------------_ Estradas: Categorias _-----------_

    motorway = ['motorway', 'motorway_link']
    primary = ['primary', 'trunk', 'secondary']
    n_mapear = ['cycleway', 'steps', 'track','track_grade1','track_grade2',
                'track_grade3','track_grade4','track_grade5','pedestrian',
                'footway', 'unclassified','path']

    dict_temp = {}
    for nome in gdf_open_street2019_municipio.fclass.unique(): 
        if nome in motorway:
            dict_temp [nome] = list((0.4,6))
        elif nome in primary: 
            dict_temp [nome] = list((0.3,4))
        elif nome in n_mapear:
            dict_temp [nome] = list((0.2,1))
        else: 
            dict_temp [nome] = list((0.3,2))


def generate_fig_landuse():
    generate_land_use()
    # _-------------_ Criação do Gráfico _-----------_
    fig, ax = plt.subplots(figsize=(20, 20))

    #Plota os limites das freguesias 
    # gdf_freguesias_CAOP2018.plot(ax=ax,
    #                         facecolor='None', edgecolor='black', linewidth=0.4, zorder=20)


    #Plota ocupação e uso de solo por categoria, em função do esquema de cores definido em colors_cos_hexa
    for categoria, data in gpd_COS_municipio.groupby('Megaclasse'):
        # Define the color for each group using the dictionary
        color = colors_cos_hexa[categoria]
        # Plot each group using the color defined above
        data.plot(color=color, ax=ax, alpha=0.12, zorder=10)

    #Plota a rede de estradas, em função da linewidths e alphas definido em dict_temp 
    for ctype, data in gdf_open_street2019_municipio.groupby('fclass'):
        alpha = dict_temp[ctype][0]
        linewidth = dict_temp[ctype][0]
        data.plot(color = 'black', ax=ax, alpha=alpha, 
                linewidth=linewidth, zorder=15)
        
    teste.plot(ax=ax, alpha=0.06, color='black')


    ax.set_axis_off()

    markersize = 150
    # If the School has critic mass
    schoolsPre.plot(ax=ax, markersize=markersize, color='green', marker='o', label='Equipamento com mais de 21 alunos', alpha=0.8,zorder=50)
    # IF the school is a closing Candidate
    schoolsPre[schoolsPre['students']<=22].plot(ax=ax, markersize=markersize, color='#FFA500', marker='s', label='Equipamento com menos de 21 alunos', alpha=0.8, zorder=60)
    plt.legend(prop={'size':15}, bbox_to_anchor = (1.2,0.28))


    for idx, row in schoolsPre.iterrows():
        offset = {'x':-20, 'y':0}

    return fig
        



# Load Data
# Load Distance Matrix - GEOMETRY is Coming as STRING
distanceMatrix_raw = pd.read_csv('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/distance_matrix/distance-matrix-schools-1107.csv', dtype={'destination':str})
distanceMatrix_raw = distanceMatrix_raw.drop(columns=['geometry'])
distanceMatrix_raw['real_distance'] = distanceMatrix_raw['real_distance'].fillna(10000)

# Load Projection Data
population_projection_raw = pd.read_csv('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/df_alunos_subseccao_2040_Loures_final.csv', dtype={'Unnamed: 0':str})
population_projection_raw.rename(columns={'Unnamed: 0':'BGRI'}, inplace=True)
population_projection_raw.index = population_projection_raw['BGRI']
population_projection_raw = population_projection_raw.drop(columns=['BGRI'])
# Aggregate 2 and 3 cicles
population_projection_raw['proj_sum_2_3'] = population_projection_raw.loc[:,"2_CEB_Proj_2040"]+population_projection_raw.loc[:,"3_CEB_Proj_2040"]

# Used for Loures, beacuse of CAOP 2018 redesing
gdf_freguesias_CAOP2018_raw = gpd.read_file('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/loures_subseccoes_BGRI_CAOP_2018/gdf_BGRI_2011_Loures_Final.shp')
gdf_freguesias_CAOP2018_raw = gdf_freguesias_CAOP2018_raw[gdf_freguesias_CAOP2018_raw['DTMN11']=='1107']

selectedPolygon = gdf_freguesias_CAOP2018_raw[gdf_freguesias_CAOP2018_raw['DTMN11']=='1107']

# Used for Loures, to generate better plotting based on macro regions
loures_macro_regions = gpd.read_file('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/macro_regioes_shp/Areas_Territoriais2.shp')

# Load and Overlay Plotting Data
gpd_COS_municipio_raw = gpd.read_file('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/gdf_COS/gdf_COS_2015_Loures.shp')
gdf_open_street2019_municipio_raw = gpd.read_file('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/gdf_open_street2019/gdf_open_street2019_Loures.shp')

# For Loures -> We need to correct the number of BGRI (demand) for CAOP 2018

# Load School (Ofer) Data
# schools = gpd.read_file('./data_gettin/escolasourem/gdf_escolas_Ourem2019_capacidades.shp')
schools_raw = gpd.read_file('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/escolas_loures/gdf_escolas_2019_elegiveis_Loures.shp')
# schools_raw.Capacidade = schools_raw.Capacidade.astype(float)
schools_raw['Capacida_2_3'] = schools_raw.Capacida_2+schools_raw.Capacida_3
schools_raw['Alunos_2CE_3CE'] = schools_raw.Alunos_2CE+schools_raw.Alunos_3CE

# Conserve the correspondent Disctance Matrix Index
schools_raw['reserved_index'] = schools_raw.index


# Define some globals
globals_dict = {"pre":['Capacidade','Pre_escolar_Proj_2040','Alunos_EPE'],'1_ciclo':['Capacida_1','1_CEB_Proj_2040','Alunos_1CE'],'2_ciclo':['Capacida_2','2_CEB_Proj_2040','Alunos_2CE'],'3_ciclo':['Capacida_3','3_CEB_Proj_2040','Alunos_3CE'],'4_ciclo':['Capacida_4','Secundario_Proj_2040','Alunos_Sec']}
list_tipology = ['Oriental','Norte_Urbano','Norte_Rural']

for ciclo in globals_dict.keys():
    for tipology in list_tipology:
        print("running model for {} - {}".format(ciclo,tipology))
        schoolSelection = globals_dict[ciclo][0]
        projectionSelection = globals_dict[ciclo][1]
        studentsActualEnrolledSelection = globals_dict[ciclo][2]

        # Load data for plotting

        gdf_freguesias_CAOP2018 = gpd.overlay(loures_macro_regions[loures_macro_regions['Tipologia']==tipology], gdf_freguesias_CAOP2018_raw, how='intersection')
        gpd_COS_municipio = gpd.overlay(loures_macro_regions[loures_macro_regions['Tipologia']==tipology], gpd_COS_municipio_raw, how='intersection')
        gdf_open_street2019_municipio = gpd.overlay(loures_macro_regions[loures_macro_regions['Tipologia']==tipology], gdf_open_street2019_municipio_raw, how='intersection')


        # Limit the map to the Macro Region
        selectedPolygon = gpd.overlay(loures_macro_regions[loures_macro_regions['Tipologia']==tipology], gdf_freguesias_CAOP2018_raw, how='intersection')

        # Perform the overlay
        schools = gpd.overlay(schools_raw, selectedPolygon, how='intersection') # REMEMBER TO RESTART THE SCHOOLS
        # Reindex to avoid pure caos
        schools.index = schools.reserved_index


        # Limit the projection to the analized BGRI's
        population_projection = population_projection_raw[population_projection_raw.index.isin(selectedPolygon.BGRI11)]

        # First Limitation on distanceMatrix
        distanceMatrix = distanceMatrix_raw[(distanceMatrix_raw.destination.isin(population_projection.index))] # projection is based on 2018

        # Limit distance matrix to the selected Polygon
        distanceMatrix = distanceMatrix[(distanceMatrix.destination.isin(selectedPolygon.BGRI11))]

        # Limit Schools By selection
        schoolsPre = schools[schools[schoolSelection]>0]
        # Used in Demand and Capacity
        selectedSchoolCapacity = schoolsPre.loc[ : , schoolSelection ]
        selectecProjection = population_projection.loc[:,projectionSelection]


        # Start Logic 
        # -------------- Decision Variables -------------- #

        # School demand per BGRI
        demand = dict(zip(population_projection.index, selectecProjection))


        # Plant capacity in thousands of units
        capacity = dict(zip(schoolsPre.index, selectedSchoolCapacity))

        # Model
        m = Model("capacitaded_location_schools")

        # School open decision variables: open[p] == 1 if plant p is open.
        open = m.addVars(list(capacity.keys()), vtype=GRB.BINARY, name="open")
        
        # Transport DestinationsAndCosts Structure to make model ULTRA FAST!!!

        transportCosts = []
        notExistingBGRI = []

        distanceMatrix_TD = list(zip(distanceMatrix.origin,distanceMatrix.destination))
        distanceMatrix_structure = dict(zip(distanceMatrix_TD,distanceMatrix.real_distance.values))

        for bgri in demand:
            tempList = []
            for e in capacity:
                try:
                    tempList.append(distanceMatrix_structure[(e,bgri)] * demand[bgri])
        #             tempList.append(distanceMatrix_structure[(e,bgri)])
        #             tempList.append(distanceMatrix[distanceMatrix['origin']==e][distanceMatrix['to']==bgri].real_distance.values[0])
                except:
                    notExistingBGRI.append(bgri)
            transportCosts.append(tempList)
        try:
            # Create Transport Decision Variables
            transport = m.addVars(list(demand.keys()), list(capacity.keys()), obj=transportCosts, name="trans")

            m.update()

            # The objective is to minimize the total fixed and variable costs
            m.modelSense = GRB.MINIMIZE

            # Capacity constraints
            m.addConstrs(
                (transport.sum('*',p) <= capacity[p] for p in list(capacity.keys())),
                "Capacity")


            # Demand constraints
            m.addConstrs(
                (transport.sum(w) == demand[w] for w in list(demand.keys())),
                "Demand")

            # Save model
            m.write('facility_Pre.lp')

            # Use barrier to solve root relaxation
            m.Params.method = 2

            # Solve
            m.optimize()

        except: 
            print("Nenhuma ou só uma escola")

        try:
            # Print solution
            # print('\nTOTAL COSTS: %g' % m.objVal)
            # print('SOLUTION:')
            listOfCapacities = []
            listOfSchoolAndBgri = []
            enrolledStudentsCount = []
            for p in capacity:
                
                if open[p].x < 0.99:
                    # print('School %s open' % p)
                    tempList = []
                    for w in demand:
                        if transport[w,p].x > 0:
                            # print('  Transport %g units from BGRI %s' % \
                            #     (transport[w,p].x, w))
                            # Create a list of School and BGRI and the distance to school
                            listOfSchoolAndBgri.append([w,p,distanceMatrix_structure[p,w], distanceMatrix_structure[p,w]*transport[w,p].x])
                            tempList.append(transport[w,p].x)
                    
                    # print('SUM of School %d : %f' % (p, sum(tempList)))
                    
                    # To create a DF with school and number of students
                    enrolledStudentsCount.append([p,sum(tempList)])
                    # To verify if the correct number of students are enrolled
                    listOfCapacities.append(sum(tempList))
                        
                else:
                    print('School is %s closed!' % p)
            pd_SchoolAndBgri = pd.DataFrame(listOfSchoolAndBgri, columns=['BGRI','school','Unitary_real_distance','pondered_real_distance'])
            pd_SchoolAndStudents = pd.DataFrame(enrolledStudentsCount, columns=['school', 'students'])
        

            # Create the metrics from the pd with alocated demands and real_distance
            schoolsPre['dist_media'] = pd_SchoolAndBgri[['school','Unitary_real_distance']].groupby('school').mean()
            schoolsPre['dist_min'] = pd_SchoolAndBgri[['school','Unitary_real_distance']].groupby('school').min()
            schoolsPre['dist_max'] = pd_SchoolAndBgri[['school','Unitary_real_distance']].groupby('school').max()
            schoolsPre['dist_STDeviation'] = pd_SchoolAndBgri[['school','Unitary_real_distance']].groupby('school').std()


            # Add to the selected schools how many students are alocated
            schoolsPre = pd.merge(schoolsPre, pd_SchoolAndStudents[['students']], how='left', left_on=[schoolsPre.index], right_on=[pd_SchoolAndStudents.school])

            # clean after merge
            schoolsPre = schoolsPre.rename(columns={'key_0':'school'})
            schoolsPre.index = schoolsPre.school

            # save things
            print("----- saving Excel file -------")
            schoolsPre.to_excel('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/results/'+tipology+'-'+projectionSelection + '.xls')
            print("------generating figure------")
            fig = generate_fig_projection(selectedPolygon,pd_SchoolAndBgri,schoolsPre, schoolSelection)
            print("------saving figure in file------")
            fig.savefig("/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/results/macro_regioes/"+tipology+"-"+studentsActualEnrolledSelection+"-proj2040_box.png")
        except:
            print("Model Infeaseble")