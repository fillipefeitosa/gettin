from requests_html import HTMLSession
import csv
import pandas as pd
session = HTMLSession()

links = ["https://bookinxisto.com/pt/lodge-catalog/lodge?id=", "https://bookinxisto.com/pt/experience-catalog/experience?id="]

for link in links:
    for i in range(2000):
        data = []
        r = session.get(link+str(i))
        print(r.status_code)
        if(r.status_code == 200):
            titulo  = r.html.find('.product-title', first=True)
            print(titulo.text)
            data.append(i)
            data.append(link+str(i))
            data.append(titulo.text)
            with open("output-re-checking.csv", "a") as fp:
                wr = csv.writer(fp, dialect='excel')
                wr.writerow(data)


# try:
#     # print(r.text)
#     # prints the int of the status code. Find more at httpstatusrappers.com :)
# except requests_html.ConnectionError:
#     print("failed to connect")
