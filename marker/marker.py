import asyncio
from aiohttp import web
import pandas as pd
import os
import pymssql
# import json
from io import StringIO
import logging


# init logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def ms_sql_con():
    con = pymssql.connect(
        server=os.environ.get('MSSQL_SERVER', ''),
        user=os.environ.get('MSSQL_LOGIN', ''),
        password=os.environ.get('MSSQL_PASSWORD', ''),
        database='voice_ai',
        #autocommit=True			
    )
    # logging.info('Connected to MSSQL')
    return con

async def call_test(request):

    logging.info('call_test')
    return web.Response(
        text='ok',
        content_type="text/html")

async def call_mark(request):

    #request_str = json.loads(str(await request.text()))
    request_str = str(await request.text())
    df = pd.read_csv(
        StringIO(request_str),
        sep=';',
        dtype={'linkedid': 'str', 'record_date': 'str', 'side': 'str', 'city': 'str'}
        )
    answer = 'ok'
    
    for _id, row in df.iterrows():
        query = "update summarization set "+str(row.city)+" = 1 where "
        query += " record_date = '"+str(row.record_date)+"' and"
        query += " linkedid = '"+str(row.linkedid)+"' and"
        query += " side = '"+str(row.side)+"';"
        conn = ms_sql_con()  
        cursor = conn.cursor()
        cursor.execute(query)

    logging.info('query: '+query)
    logging.info('marked'+str(len(df)))

    return web.Response(
        text=answer,
        content_type="text/html")

logging.info('Start')
app = web.Application(client_max_size=1024**3)
app.router.add_route('GET', '/test', call_test)
app.router.add_post('/mark', call_mark)
logging.info('Start server')
web.run_app(
    app,
    port=os.environ.get('PORT', ''),
)
