"""Objetive: send GET requests to a site and store its data on a DataFrame."""

# List of Imports
from requests_html import HTMLSession
import pandas as pd

# List of Globals
session = HTMLSession()
links = ["https://bookinxisto.com/pt/lodge-catalog/lodge?id=","https://bookinxisto.com/pt/experience-catalog/experience?id="]
crawlerIterations = 10
data = []

# Logic
for link in links:
    for i in range(crawlerIterations):
        request = session.get(link+str(i))
        print(request.status_code)
        if(request.status_code == 200):
            titulo = request.html.find('.product-title', first=True).text
            # data['id'] = int(i)
            data.append([int(i), titulo, link+str(i)])

print(data)
result = pd.DataFrame(data=data, columns=['titulo', 'url'])
print(result)
result.to_json("xisto_dataframe.json")
