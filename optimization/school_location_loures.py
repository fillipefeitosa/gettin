# Import Libraries
from gurobi import *
import math
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
import geopandas as gpd
import geopy.distance
from collections import defaultdict
from shapely.geometry import Point, LineString



def generate_lines(selectedPolygon, pd_SchoolAndBgri, schoolsPre):
    print("---> Entered lines creation")
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

def generate_fig_projection(selectedPolygon,schoolsPre,schoolSelection, teste):
    print("entered fig projection")
    # PLOT
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
        ax.annotate(int(idx), xy=(row['geometry'].x,row['geometry'].y),
                xytext=(offset['x'], offset['y']), textcoords='offset points',
                size=8, ha='right', va="center",zorder=200,
                bbox=dict(boxstyle="round", alpha=0.8, color="#84AF9F"),
                arrowprops=dict(arrowstyle="-", alpha=1));
        # ax.annotate(int(row[schoolSelection]), xy=(row['geometry'].x,row['geometry'].y),
        #         xytext=(offset['x'], offset['y']-13), textcoords='offset points',
        #         size=8, ha='right', va="center",zorder=200,
        #         bbox=dict(boxstyle="round", alpha=0.8, color='#FFFF66')
        #         );
        counter += 1
    schoolsPre.plot(ax=ax, markersize=40, color='red', marker='o', label='centroid')

    return fig

#recebe RGB em dicionários de float e devolve o hexadecimal correspondente
def rgb_to_hex (diccionario_cores): 
    dict_novo = {}
    for nome in diccionario_cores:
        dict_novo [nome] = '#%02x%02x%02x'%tuple(int(i * 255) for i in diccionario_cores[nome])
    return(dict_novo)

def add_street_to_map(gdf_open_street2019_municipio):
    # _-------------_ Estradas: Categorias _-----------_

    motorway = ['motorway', 'motorway_link']
    primary = ['primary', 'trunk', 'secondary']
    n_mapear = ['cycleway', 'steps', 'track','track_grade1','track_grade2',
                'track_grade3','track_grade4','track_grade5','pedestrian',
                'footway', 'unclassified','path']

    street_categories = {}
    for nome in gdf_open_street2019_municipio.fclass.unique(): 
        if nome in motorway:
            street_categories [nome] = list((0.4,6))
        elif nome in primary: 
            street_categories [nome] = list((0.3,4))
        elif nome in n_mapear:
            street_categories [nome] = list((0.2,1))
        else: 
            street_categories [nome] = list((0.3,2))
    
    return street_categories
         
def generate_fig_landuse(schoolsPre, gdf_open_street2019_municipio,gpd_COS_municipio, lines, selection,selectedPolygon):
    
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
    dict_temp = add_street_to_map(gdf_open_street2019_municipio)

    # _-------------_ Criação do Gráfico _-----------_
    fig, ax = plt.subplots(figsize=(20, 20))
    ax.set_axis_off()

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
        
    lines.plot(ax=ax, alpha=0.06, color='black')

    # Get the outer boundary for the selected Polygon
    if (selection['tipology']=='Loures'):
        loures_macro_regions.plot(ax=ax,facecolor='None',edgecolor='gray',linewidth=5, alpha=0.8, zorder=30)
    else:
        polygon = selectedPolygon.geometry.unary_union
        selectedPolygon = gpd.GeoDataFrame(geometry=[polygon])
        selectedPolygon.plot(ax=ax,facecolor='None',edgecolor='gray',linewidth=5, alpha=0.8, zorder=30)

    ax.set_axis_off()

    markersize = 180

    if ('added_classes' in schoolsPre.columns):
        schoolsPre[schoolsPre['added_classes']==0].plot(ax=ax, markersize=markersize, color='green', marker='o', alpha=1,zorder=50, label='Escolas sem redução de alunos')
        schoolsPre[schoolsPre['added_classes']==1].plot(ax=ax, markersize=markersize, marker='$1$', label='Escola ajustada com 1(uma) turma adicional', color='#3c1361', alpha=1, zorder=80)
        schoolsPre[schoolsPre['added_classes']==2].plot(ax=ax, markersize=markersize, marker='$2$', label='Escola ajustada com 2(duas) turmas adicional', color='#52307c', alpha=1, zorder=80)
        schoolsPre[schoolsPre['added_classes']==3].plot(ax=ax, markersize=markersize, marker='$3$', label='Escola ajustada com 3(três) turmas adicional', color='#663a82', alpha=1, zorder=80)

    else: 
        schoolsPre.plot(ax=ax, markersize=markersize, color='#00b300', marker='o', alpha=1,zorder=50, label='Escolas sem redução de alunos')

    schoolsPre[schoolsPre.students<schoolsPre.loc[:,studentsActualEnrolledSelection]].plot(ax=ax, markersize=markersize, color='#8D021F', marker='s', label='Escola com redução de alunos', alpha=1, zorder=60)



    # plt.legend(prop={'size':15}, bbox_to_anchor = (1.2,0.28))

    counter = 0
    for idx, row in schoolsPre.iterrows():

        offset = {'x':+35, 'y':0}
        
        
        # Offset Correction
        offset = {'x':35, 'y':45} if idx==0 else offset
        offset = {'x':35, 'y':35} if idx==1 else offset
        offset = {'x':-35, 'y':35} if idx==2 else offset
        offset = {'x':-25, 'y':-25} if idx==3 else offset
        offset = {'x':25, 'y':35} if idx==5 else offset
        offset = {'x':25, 'y':35} if idx==6 else offset
        offset = {'x':-25, 'y':-35} if idx==7 else offset
        offset = {'x':-35, 'y':35} if idx==9 else offset
        offset = {'x':35, 'y':-15} if idx==13 else offset
        offset = {'x':65, 'y':35} if idx==13 else offset
        offset = {'x':65, 'y':-35} if idx==16 else offset
        offset = {'x':30, 'y':30} if idx==30 else offset
        offset = {'x':-45, 'y':45} if idx==32 else offset
        offset = {'x':40, 'y':50}  if idx==42 else offset
        offset = {'x':25, 'y':50}  if idx==43 else offset
        offset = {'x':-25, 'y':-25} if idx==44 else offset
        offset = {'x':35, 'y':-25} if idx==45 else offset
        offset = {'x':-25, 'y':-25} if idx==46 else offset
        offset = {'x':0, 'y':-30} if idx==47 else offset
        offset = {'x':-45, 'y':-15} if idx==48 else offset
        offset = {'x':-45, 'y':-15} if idx==49 else offset
        offset = {'x':+35, 'y':35} if idx==51 else offset
        offset = {'x':55, 'y':-30} if idx==54 else offset
        offset = {'x':-25, 'y':-25} if idx==56 else offset
        offset = {'x':35, 'y':35} if idx==57 else offset
        offset = {'x':70, 'y':60} if idx==58 else offset
        offset = {'x':+35, 'y':+35} if idx==70 else offset
        offset = {'x':+35, 'y':-35} if idx==71 else offset
        offset = {'x':+35, 'y':-30} if idx==78 else offset
        offset = {'x':+35, 'y':+35} if idx==83 else offset
        offset = {'x':+35, 'y':+35} if idx==85 else offset
        offset = {'x':60, 'y':45} if idx==87 else offset
        offset = {'x':45, 'y':0} if idx==88 else offset
        offset = {'x':+35, 'y':-35} if idx==90 else offset
        offset = {'x':+35, 'y':+35} if idx==91 else offset


        offset = {'x':95, 'y':20} if idx==94 else offset
        offset = {'x':25, 'y':35} if idx==97 else offset
        offset = {'x':25, 'y':-45} if idx==103 else offset
        offset = {'x':35, 'y':35} if idx==105 else offset
        offset = {'x':35, 'y':-20} if idx==107 else offset
        offset = {'x':35, 'y':20} if idx==108 else offset
        offset = {'x':45, 'y':0} if idx==111 else offset
        offset = {'x':35, 'y':20} if idx==114 else offset
        offset = {'x':-35, 'y':-35} if idx==120 else offset
        offset = {'x':+35, 'y':+35} if idx==131 else offset
        offset = {'x':-50, 'y':30} if idx==134 else offset
        offset = {'x':-25, 'y':25} if idx==136 else offset
        offset = {'x':25, 'y':-30} if idx==138 else offset
        offset = {'x':-25, 'y':-25} if idx==141 else offset
        offset = {'x':-35, 'y':-35} if idx==143 else offset
        offset = {'x':-35, 'y':35} if idx==147 else offset
        offset = {'x':-25, 'y':-25} if idx==150 else offset
        offset = {'x':35, 'y':35} if idx==151 else offset
        offset = {'x':25, 'y':35} if idx==152 else offset
        offset = {'x':-45, 'y':-25} if idx==161 else offset
        offset = {'x':-35, 'y':-35} if idx==163 else offset
        offset = {'x':-45, 'y':-25} if idx==164 else offset
        offset = {'x':30, 'y':35} if idx==167 else offset
        offset = {'x':-35, 'y':30} if idx==168 else offset
        offset = {'x':35, 'y':-50} if idx==169 else offset
        offset = {'x':35, 'y':20} if idx==148 else offset
        
        # school code
        # ax.annotate(str(int(idx)).zfill(3), xy=(row['geometry'].x,row['geometry'].y),
        #         xytext=(offset['x']+19, offset['y']+10), textcoords='offset points',
        #         size=8, ha='right', va="center",zorder=200,
        #         bbox=dict(boxstyle="round", alpha=0.8,color='#F1AF9F')
        #         )
        # Enroled students 2021
        ax.annotate(str(int(row[selection['studentsActualEnrolledSelection']])).zfill(3), xy=(row['geometry'].x,row['geometry'].y),
                    xytext=(offset['x']+27, offset['y']-8), textcoords='offset points',
                    size=10, ha='right', va="center",zorder=200,
                    bbox=dict(boxstyle="round", alpha=0.8, color="gray"))
        # students projected
        ax.annotate(str(int(row['students'])).zfill(3), xy=(row['geometry'].x,row['geometry'].y),
                    xytext=(offset['x'], offset['y']), textcoords='offset points',
                    size=10, ha='right', va="center",zorder=200,
                    bbox=dict(boxstyle="round", alpha=0.8)
                    )
        # School Capacity
        ax.annotate(str(int(row[selection['schoolSelection']])).zfill(3), xy=(row['geometry'].x,row['geometry'].y),
                    xytext=(offset['x'], offset['y']-18), textcoords='offset points',
                    size=10, ha='right', va="center",zorder=100,
                    bbox=dict(boxstyle="round", alpha=0.8, color="#FFFF66"),
                    arrowprops=dict(arrowstyle="-", alpha=1, zorder=200))
        counter += 1

    return fig


# Define function to create fregs using CAOP 2018 RAW
# Define one function to calculate demand Density by area by BGRI
# Define onde function to calculate demand Density by total of demand by BGRI
def calculate_demand_density_area_bgri(df_projection, demandSelection, gdf_shapes):
    # total_vacancy = df_projection[:,demandSelection].sum()
    df_projection = pd.merge(left=df_projection, right=gdf_shapes[['BGRI11','area','geometry']],how='left', left_on=[df_projection.index], right_on=[gdf_shapes[['BGRI11','area']].BGRI11])
    df_projection['densidade_total_area'] = df_projection.loc[:, demandSelection]/df_projection['area']
    df_projection = df_projection.drop(columns=['BGRI11'])
    return df_projection

def calculate_demand_density_totalDemand_bgri(df_projection, demandSelection):
    total_vacancy = df_projection.loc[:,demandSelection].sum()
    df_projection['densidade_total_vagas'] = (df_projection.loc[:,demandSelection]/total_vacancy)*1000
    return df_projection

def sample_density_heatmaps(df_projection, demandSelection, gdf_shapes):
    print('---> Generating Heatmaps for {}'.format(demandSelection))
    df_projection = calculate_demand_density_area_bgri(df_projection, demandSelection, gdf_shapes)
    # Get the ratio of the total demand in the Municipality
    df_projection = calculate_demand_density_totalDemand_bgri(df_projection, demandSelection)
    gdf_projection = gpd.GeoDataFrame(df_projection)
    gdf_projection = gdf_projection[['Code_Freg','geometry','densidade_total_vagas']]



    fig, ax = plt.subplots(1,1,figsize=(20,20))
    ax.set_axis_off()

    loures_2019_fregs.plot(ax=ax, edgecolor='#B0C4DE', facecolor='None', linewidth=2, alpha=0.8, zorder=40)
    
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right",size="5%",pad=0.1)
    loures_macro_regions.plot(ax=ax, edgecolor='gray', facecolor='None',linewidth=5, alpha=0.8,zorder=50)
    gdf_projection.dissolve(by='Code_Freg',aggfunc='mean').plot(ax=ax,column='densidade_total_vagas', legend=True, cax=cax, cmap='Reds',zorder=20)
    fig.savefig('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/results/heatmap_densidade/heatmap_densidade_vagas_'+demandSelection+'.png')

    return df_projection

def generate_fregs_density_shape(df_projection,gdf_shapes,demandSelection,tipology):
    # Get the density for the selected Projection and tipology... Forced by demand on DF_Projection
    gdf_projection = gpd.GeoDataFrame(df_projection)
    gdf_freg = gdf_projection.dissolve(by='Code_Freg')
    gdf_freg['densidade_freg_vagas'] = gdf_projection[['Code_Freg','densidade_total_vagas']].groupby('Code_Freg').mean()
    
    # No need for map here
    # fig, ax = plt.subplots(1,1,figsize=(20,20))
    # ax.set_axis_off()
    # gdf_shapes.plot(ax=ax,facecolor='white', edgecolor='#B0C4DE',zorder=10)
    # divider = make_axes_locatable(ax)
    # cax = divider.append_axes("right",size="5%",pad=0.1)
    # gdf_freg[gdf_freg['densidade_total_vagas']>0].plot(ax=ax,column='densidade_total_vagas', legend=True, cax=cax, cmap='Reds',zorder=20)
    # fig.savefig('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/results/heatmap_densidade/heatmap_'+tipology+'_'+demandSelection+'.png')

    # index to str, compatible with schoolsPre Cod_Freg Column
    gdf_freg.index = gdf_freg.index.astype(str)
    return gdf_freg

# Load Data
# Load Distance Matrix - GEOMETRY is Coming as STRING
distanceMatrix_raw = pd.read_csv('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/distance_matrix/distance-matrix-schools-1107.csv', dtype={'destination':str})
distanceMatrix_raw = distanceMatrix_raw.drop(columns=['geometry'])
distanceMatrix_raw['real_distance'] = distanceMatrix_raw['real_distance'].fillna(10000)

# Load Projection Data
population_projection_raw = pd.read_csv('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/df_alunos_subseccao_2030_Loures_novo.csv', dtype={'Unnamed: 0':str})
population_projection_raw.rename(columns={'Unnamed: 0':'BGRI'}, inplace=True)
population_projection_raw.index = population_projection_raw['BGRI']
population_projection_raw = population_projection_raw.drop(columns=['BGRI'])
# Aggregate 2 and 3 cicles
population_projection_raw['proj_sum_2_3'] = population_projection_raw.loc[:,"2_CEB_Proj_2030"]+population_projection_raw.loc[:,"3_CEB_Proj_2030"]

# Used for Loures, beacuse of CAOP 2018 redesing
# gdf_freguesias_CAOP2018_raw = gpd.read_file('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/loures_subseccoes_BGRI_CAOP_2018/gpd_BGRI_2011_CAOP2018_Final.shp')
gdf_freguesias_CAOP2018_raw = gpd.read_file('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/loures_subseccoes_BGRI_CAOP_2018/gdf_BGRI_2011_CAOP2018_MACRO_Loures.shp')
gdf_freguesias_CAOP2018_raw = gdf_freguesias_CAOP2018_raw[gdf_freguesias_CAOP2018_raw['DTMN11']=='1107']

# Used for Loures, to generate better plotting based on macro regions
# Needed to adjust after CAOP alteration
loures_macro_regions = gdf_freguesias_CAOP2018_raw.dissolve(by='Tipo')
loures_macro_regions['Tipologia'] = loures_macro_regions.index
loures_macro_regions.index = [0,1,2]

# Load new Freg boundaries
loures_2019_fregs = gpd.read_file('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/CAOP_2019_Freguesias/Cont_AAD_CAOP2019_Loures.shp')

# Load and Overlay Plotting Data
gpd_COS_municipio_raw = gpd.read_file('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/gdf_COS/gdf_COS_2015_Loures.shp')
gdf_open_street2019_municipio_raw = gpd.read_file('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/gdf_open_street2019/gdf_open_street2019_Loures.shp')

# For Loures -> We need to correct the number of BGRI (demand) for CAOP 2018

# Load School (Ofer) Data
# schools = gpd.read_file('./data_gettin/escolasourem/gdf_escolas_Ourem2019_capacidades.shp')
schools_raw = gpd.read_file('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/escolas_loures/gdf_escolas_2019_elegiveis_Loures.shp')
# schools_raw.Capacidade = schools_raw.Capacidade.astype(float)
# Change Offer according to tech team, missing or wrong
schools_raw.at[21,'Capacida_3'] = 0
schools_raw.at[21,'Capacida_4'] = 0
schools_raw.at[38,'Capacida_1'] = 24
schools_raw.at[98,'Capacidade'] = 25
schools_raw.at[98,'Alunos_EPE'] = 0
schools_raw.at[42,'Capacidade'] = 25
schools_raw.at[42,'Alunos_EPE'] = 0
schools_raw.at[68,'Alunos_3CE'] = 284
# Add the sencond and third schemma
schools_raw['Capacida_2_3'] = schools_raw.Capacida_2+schools_raw.Capacida_3
schools_raw['Alunos_2CE_3CE'] = schools_raw.Alunos_2CE+schools_raw.Alunos_3CE

# Conserve the correspondent Disctance Matrix Index
schools_raw['reserved_index'] = schools_raw.index


# Define some globals
globals_dict = {"pre":['Capacidade','Pre_escolar_Proj_2030','Alunos_EPE',25],'1_ciclo':['Capacida_1','1_CEB_Proj_2030','Alunos_1CE',24],'2_ciclo':['Capacida_2','2_CEB_Proj_2030','Alunos_2CE',28],'3_ciclo':['Capacida_3','3_CEB_Proj_2030','Alunos_3CE',28],'4_ciclo':['Capacida_4','Secundario_Proj_2030','Alunos_Sec',28]}
list_tipology = ['Oriental','Norte_Urbano','Norte_Rural', 'Loures']
# globals_dict = {'3_ciclo':['Capacida_3','3_CEB_Proj_2030','Alunos_3CE',28]}
# list_tipology = ['Loures']
# population_projection_raw = sample_density_heatmaps(population_projection_raw, globals_dict['pre'][1], gdf_freguesias_CAOP2018_raw)
# population_projection_raw.index = population_projection_raw.key_0
# population_projection_raw.drop(columns=['key_0'], inplace=True)

infeasible = []
unique_added_class = []
for ciclo in globals_dict.keys():
    # Create heatmaps for each study cicle
    projectionSelection = globals_dict[ciclo][1]

    population_projection_with_density = sample_density_heatmaps(population_projection_raw, globals_dict[ciclo][1], gdf_freguesias_CAOP2018_raw)
    population_projection_with_density.index = population_projection_with_density.key_0
    population_projection_with_density.drop(columns=['key_0'], inplace=True)

    for tipology in list_tipology:
        print("---------------------------------------")
        print("---> Running model for {} - {}".format(ciclo,tipology))
        schoolSelection = globals_dict[ciclo][0]
        studentsActualEnrolledSelection = globals_dict[ciclo][2]



        if (tipology != 'Loures'):

            # Limit data for plotting

            gdf_freguesias_CAOP2018 = gpd.overlay(loures_macro_regions[loures_macro_regions['Tipologia']==tipology], gdf_freguesias_CAOP2018_raw, how='intersection')
            gpd_COS_municipio = gpd.overlay(loures_macro_regions[loures_macro_regions['Tipologia']==tipology], gpd_COS_municipio_raw, how='intersection')
            gdf_open_street2019_municipio = gpd.overlay(loures_macro_regions[loures_macro_regions['Tipologia']==tipology], gdf_open_street2019_municipio_raw, how='intersection')

            # Limit the map to the Macro Region
            selectedPolygon = gdf_freguesias_CAOP2018_raw[gdf_freguesias_CAOP2018_raw['Tipo']==tipology]
            # selectedPolygon = gpd.overlay(loures_macro_regions[loures_macro_regions['Tipologia']==tipology], gdf_freguesias_CAOP2018_raw, how='intersection')
        else:
            # If All is selected, use raw and the Original SelectedPolygon
            gdf_freguesias_CAOP2018 = gdf_freguesias_CAOP2018_raw
            gpd_COS_municipio = gpd_COS_municipio_raw
            gdf_open_street2019_municipio = gdf_open_street2019_municipio_raw
            # Get the entire Polygon
            selectedPolygon = gdf_freguesias_CAOP2018_raw[gdf_freguesias_CAOP2018_raw['DTMN11']=='1107']


        # Perform the overlay
        schools = gpd.overlay(schools_raw, selectedPolygon, how='intersection') # REMEMBER TO RESTART THE SCHOOLS
        # Reindex to avoid pure caos
        schools.index = schools.reserved_index
        

        # Limit the projection to the analized BGRI's
        population_projection = population_projection_with_density[population_projection_with_density.index.isin(selectedPolygon.BGRI11)]

        # First Limitation on distanceMatrix
        distanceMatrix = distanceMatrix_raw[(distanceMatrix_raw.destination.isin(population_projection.index))] # projection is based on 2018

        # Limit distance matrix to the selected Polygon
        distanceMatrix = distanceMatrix[(distanceMatrix.destination.isin(selectedPolygon.BGRI11))]

        # Limit Schools By Positive Offer
        schoolsPre = schools[schools[schoolSelection]>0]
        print('---> Number of Schools in model: {}'.format(len(schoolsPre.index)))

        # Verify if demand is bigger than offer
        total_offer = schoolsPre.loc[:,schoolSelection].sum()
        total_demand = population_projection.loc[:,projectionSelection].sum()
        if (total_demand > total_offer and len(schoolsPre.index)>1):
            shortage = total_demand - total_offer
            print("---> Lacking school vacancy: {} vacancies needed".format(shortage))
            print("---> Creating new vacancies based on demand density.")
            gdf_freg = generate_fregs_density_shape(population_projection,selectedPolygon,globals_dict[ciclo][1],tipology)
            # Get offer from gdf_freg
            schoolsPre['densidade_freg_vagas'] = schoolsPre.apply(lambda x: gdf_freg.loc[x['Cod_Freg']==gdf_freg.index].densidade_freg_vagas.values[0], axis=1)
            # Put schools in descending order of vacancy density
            schoolsPre = schoolsPre.sort_values(by='densidade_freg_vagas', ascending=False)
            schoolsPre[schoolSelection+'_original'] = schoolsPre[schoolSelection]
            # This is to mark what schools had offer altered
            schoolsPre['added_classes'] = 0

            class_size = globals_dict[ciclo][3]
            school_counter = 0
            while total_demand > total_offer:
                # some scenarios are so bad that Counter restart is needed
                if (school_counter>=len(schoolsPre.index)):
                    school_counter = 0
                schoolsPre.at[schoolsPre.iloc[school_counter].reserved_index, schoolSelection] += class_size
                schoolsPre.at[schoolsPre.iloc[school_counter].reserved_index, 'added_classes'] += 1
                school_counter += 1
                total_offer = schoolsPre.loc[:,schoolSelection].sum()
        
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
        # Stop console logging for better output reading
        m.Params.LogToConsole = 0

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


            lines = generate_lines(selectedPolygon, pd_SchoolAndBgri, schoolsPre)

            # save things
            print("---> saving Excel file")
            schoolsPre.to_excel('/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/results/'+tipology+'-'+projectionSelection + '.xls')
            
            # print("------generating projection figure------")
            # fig = generate_fig_projection(selectedPolygon,schoolsPre,schoolSelection, lines)
            # fig.savefig("/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/results/macro_regioes/"+tipology+"-"+studentsActualEnrolledSelection+"-school_cod.png")

            # print("------generating projXcapacidade landuse figure------")
            # plot_type = {'box_color':'#FFFF66','selection': schoolSelection, 'box_field':'projXcapacidade'}
            # fig = generate_fig_landuse(schoolsPre, gdf_open_street2019_municipio,gpd_COS_municipio, lines, plot_type)
            # fig.savefig("/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/results/macro_regioes/"+tipology+"-"+studentsActualEnrolledSelection+"-proj2030.png")

            print("---> generating projXatual landuse figure")
            # plot_type = { 'selection': studentsActualEnrolledSelection, 'box_field':'projXatual'}
            selection = {'schoolSelection':schoolSelection, 'studentsActualEnrolledSelection': studentsActualEnrolledSelection, 'tipology':tipology}
            fig = generate_fig_landuse(schoolsPre, gdf_open_street2019_municipio,gpd_COS_municipio, lines, selection,selectedPolygon)
            fig.savefig("/home/fillipe/Projects/gettin/optimization/data_gettin/carta_educativa_loures/results/macro_regioes/"+tipology+"-"+studentsActualEnrolledSelection+".png")

            if ('added_classes' in schoolsPre.columns):
                unique_added_class.append(schoolsPre.added_classes.unique())
        except:
            print("Model Infeaseble")
            infeasible.append("{} - {}".format(ciclo, tipology))

print('---> lista das excessões: {}'.format(infeasible))
print('---> casos únicos de turmas adicionadas: {}'.format(unique_added_class))