"""
    Script to get data from carta social/PT, and parse it to dataframes.
    Output: Two Dataframes. First one with the data from source.
            Second one is related to all data within the source.
"""
# List of Imports
from requests_html import HTMLSession
import pandas as pd
import unicodedata
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# List of Globals
session = HTMLSession()
link = "http://www.cartasocial.pt/resultados_pesquisadetalhe.php?equip="
crawlerIterations = 40001

cartaSocialIndex = ['Id','lat','long','Morada', 'CP', 'Email', 'Entidade Proprietária', 'Natureza Jurídica', 'algo', 'algo2']
dataSocialResponsesIndex = ['CartaSocialId', 'Resposta Social', 'Capacidade', 'Utentes', 'Horário','Última Actualização', 'Certificações', 'Imagem', 'Algo', 'Algo2']
data = []
dataSocialResponses = []
geolocator = Nominatim(user_agent="cartasocial")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

i=1000
while i < crawlerIterations:
    request = session.get(link+str(i))
    if(request.status_code == 200 and request.html.find('.info2', first=True) != None):
        info = request.html.find('.info2')
        infoArray = []
        infoArray.append(int(i))


        new_str = unicodedata.normalize("NFKD", info[1].text)
        moradaSplit = (info[0].text).split(',', 1)
        cityPostalCode = new_str.split('   ', 1)
        # Routine to return Lat and Long for the social response address
        # site = {'street': moradaSplit[0], 'city':cityPostalCode[1], 'postalcode':cityPostalCode[0]}
        if info[0].text != "NULL":
            try:
                location = geocode(query=moradaSplit[0]+ ' ' + cityPostalCode[1], country_codes='PT')
                address = location.address
                latitude = location.latitude
                longitude = location.longitude
            except:
                address = 'Not found'
                latitude = 'N/A'
                longitude = 'N/A'
        else:
            address = 'N/A'
            latitude = 'N/A'
            longitude = 'N/A'

        print(str(i) + ' - ' + address + ' ' + str(latitude) + ', ' + str(longitude))
        infoArray.append(latitude)
        infoArray.append(longitude)

        for item in range(len(info)):
            infoArray.append(info[item].text)
        data.append(infoArray)


        #IF Social Responses exists
        if(request.html.find('.TabPesqlin1', first=True) != None):
            # Names used in the original website. Good to organize.
            tabPesqlin1 = request.html.find('.TabPesqlin1')
            tabPesqlin2 = request.html.find('.TabPesqlin2')
            # The site groups the table in the same sequence. Therefore I need to split lin2 in equal parts
            tabPesqlin2 = np.array_split(np.asarray(tabPesqlin2), len(tabPesqlin1))
            for indexName in range(len(tabPesqlin1)):
                socialResponsesArray = []
                socialResponsesArray.append(i)
                socialResponsesArray.append(tabPesqlin1[indexName].text)

                for element in tabPesqlin2[indexName]:
                    socialResponsesArray.append(element.text)
                # Add data to first Array
                dataSocialResponses.append(socialResponsesArray)
    i += 1
print(data)
result = pd.DataFrame(data=data, columns=cartaSocialIndex)
result = result.set_index('Id')
cartaSocialResult = pd.DataFrame(data=dataSocialResponses, columns=dataSocialResponsesIndex)
print(result.head())
print(cartaSocialResult.head())
result.to_json('cartasSociais_latLong.json')
result.to_csv('cartasSociais_latLong.csv')
cartaSocialResult.to_json('respostasSociais.json')
cartaSocialResult.to_csv('respostasSociais.csv')
