import os
import time
import pymssql
import pandas as pd
import datetime
import socket
import requests
import json
import urllib


print('started')

print('WORKERS_COUNT', os.environ.get('WORKERS_COUNT', ''))


def ms_sql_con():

	return pymssql.connect(
			server = os.environ.get('MSSQL_SERVER', ''),
			user = os.environ.get('MSSQL_LOGIN', ''),
			password = os.environ.get('MSSQL_PASSWORD', ''),
			database = 'voice_ai',
			autocommit=True
		)


def read_sql(query):
	return pd.read_sql(query, con=ms_sql_con(), parse_dates=None)


def summarize(text, phrases_count):
	print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'summarizing', len(text), '/', phrases_count)
	if phrases_count<2 or len(text)<255:
		print('short return', phrases_count, len(text))
		return text
	request = {
		'in_text':text,
		'in_max_length':600,
		'out_no_repeat_ngram_size':3,
		'out_num_beams':5,
		'out_top_k':0
	}
	request_str = json.dumps(request)
	r = requests.post(os.environ.get('SUMMARUS_SERVER_DEFAULT', ''), json=request_str)
	print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'summarized size: ', len(r.text))
	return r.text


def commit(df):
	insert = ''
	delete = ''
	for idx, row in df.iterrows():    
		
		insert += "insert into summarization"
		insert += "(linkedid, record_date, sum_date, side, text, phrases_count, text_length, source_id) "
		insert += " values("
		insert += "'"+str(row.linkedid)+"',"
		insert += "'"+str(row.record_date)+"',"
		insert += "'"+str(row.sum_date)+"',"
		insert += ('1' if str(row.side) == 'True' else '0')+","
		insert += "'"+str(row.text)+"',"
		insert += "'"+str(row.phrases_count)+"',"
		insert += "'"+str(row.text_length)+"',"
		insert += str(row.source_id)
		insert += ");"

		delete += "delete from summarization_queue where"
		delete += " linkedid='"+str(row.linkedid)+"' and"
		delete += " side="+('1' if str(row.side) == 'True' else '0')+";"

	conn = ms_sql_con()  
	cursor = conn.cursor()
	try:
		cursor.execute(insert+delete)
	except Exception as e:
		print(e)
		print(insert)
		print(delete)


def get_jaccard_sim(str1, str2): 
	a = set(str1.split()) 
	b = set(str2.split())
	c = a.intersection(b)
	denominator = (len(a) + len(b) - len(c))
	if denominator > 0:
		return float(len(c) / denominator)
	else:
		return 0


def summarize_by_row(row):
	return summarize(row.text, row.phrases_count)


def jaccard_sim_by_row(row, wrong_words):
	for wrong in wrong_words:
		if wrong in row.text_short:
			print('jaccard_sim_by_row ratet as 0:', wrong)
			return 0
	return get_jaccard_sim(row.text, row.text_short)


def replace_wrong_by_row(row, wrong_words):
	for wrong in wrong_words:
		if wrong in row.text_short:
			print('replace_wrong_by_row replaced:', wrong)
			return row.text[:MAX_TEXT_SIZE]
	return row.text_short


def fix_wrong_symbols(row):
	result = row.text_short
	if "'" in result:
		result = result.replace("'","")
	if '"' in result:
		result = result.replace('"','')
	return result


def send_to_telegram(message):
		token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
		chat_id = os.environ.get('TELEGRAM_CHAT', '')
		session = requests.Session()
		get_request = 'https://api.telegram.org/bot' + token	
		get_request += '/sendMessage?chat_id=' + chat_id
		get_request += '&text=' + urllib.parse.quote_plus(message)
		session.get(get_request)


send_to_telegram('started summarization worker '+str(socket.gethostname()))

while True:

	query = "SELECT top 100"
	query += " linkedid, record_date, side, phrases_count, text_length, text, version, source_id, "
	query += " '' as text_short, 0 as jaccard_sim"
	query += " from summarization_queue"
	# query += " where source_id = "+str(sys.argv[2])
	query += " order by record_date desc, linkedid, side, version;"
	df = read_sql(query)

	crop_marker = pd.DataFrame()
	crop_marker['linkedid'] = df.linkedid
	crop_marker['record_date'] = df.record_date
	crop_marker.sort_values('record_date', ascending = False, inplace = True)

	df = df[df.linkedid.isin( pd.Series(crop_marker[:300].linkedid.unique()) )]

	if len(df) == 0:
		print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'nothing to do. sleeping..')
		time.sleep(1)
		continue

	print('batch size:', len(df), 'from:', df.record_date.min(), 'to:', df.record_date.max())

	# summarize
	df.text_short = df.apply(summarize_by_row, axis=1)

	print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'preparing')
	# evaluate error
	wrong_words = ['погиб', 'смерть', 'путин'] # high frequency and not relevant newspaper words
	df.jaccard_sim = df.apply(jaccard_sim_by_row, axis=1, wrong_words = wrong_words)
	jsims = pd.DataFrame(df.groupby(by=['linkedid','side']).max().jaccard_sim)
	jsims.reset_index(inplace = True)

	# drop wroworst results
	df = pd.merge(df, jsims, how = 'inner', on = ['linkedid','side', 'jaccard_sim'])

	# group the same results
	jfirst = pd.DataFrame(df.groupby(by=['linkedid','side']).min().version)
	jfirst.reset_index(inplace = True)
	df = pd.merge(df, jfirst, how = 'inner', on = ['linkedid','side', 'version'])

	# replace wrong words and symbols
	df.text_short = df.apply(replace_wrong_by_row, axis=1, wrong_words = wrong_words)
	df.text_short = df.apply(fix_wrong_symbols, axis=1)

	print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'saving')

	# save
	current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	df['sum_date'] = [current_date for i in range(len(df))]
	df.drop(['jaccard_sim', 'text', 'version'], axis = 1, inplace = True)
	df.rename(columns={'text_short': 'text'}, inplace=True)
	commit(df)

	print(
		datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
		'job complete:', len(df),
		'from:', min(df.record_date),
		'to:', max(df.record_date)
		)
