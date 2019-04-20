from google2pandas import *

query = {\
    'ids'           : '71568478',
    'metrics'       : 'pageviews',
    'dimensions'    : ['date', 'pagePath', 'browser'],
    'filters'       : ['pagePath=~iPhone', 'and', 'browser=~Firefox'],
    'start_date'    : '8daysAgo',
    'max_results'   : 10}

conn = GoogleAnalyticsQuery(token_file_name='my_analytics.dat',secrets='my_client_secrets_v3.json')
df, metadata = conn.execute_query(**query)
