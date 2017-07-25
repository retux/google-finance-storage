#!/usr/bin/env python

"""
stock-watch: gets stock quotes from Google Financial API and stores in a db.
-----------

	Within main function there is a Symbols list containing a list of pairs which describes stock 
	symbols as used by Google API. Stocks can be configured as you like.
	Each element should be 'EXCHANGE:SYMBOL' examples

	[ 'NASDAQ:GOOG', 'NASDAQ:CSCO', 'NYSE:IBM', 'BCBA:YPFD' ]

"""

import urllib2
import json
import time
import sqlite3
import re
from pprint import pprint


class Quote:
	def __init__ (self, googleID = None, symbol = None, last = None, diference = None, vpercentual = None, previous = None, lasttime = None, exchange = None, \
			timestp = None, datejson = None):
		self.GoogleID = googleID
		self.Symbol = symbol
		self.Last = last
		self.Diference = diference
		self.vPercentual  = vpercentual
		self.Previous = previous
		self.LastTime = lasttime
		self.Exchange = exchange
		self.Timestamp = timestp
		self.Date = datejson

class GoogleFinanceAPI:
	def __init__(self):
		self.prefix = "http://finance.google.com/finance/info?client=ig&q="
		self.JSONObject = None
		self.QuotesList = []
		self.SqlLiteFile = './google_quotes.sqlite3'
		

	def get(self,ExchangeSymbols):
		url = self.prefix+"%s"%(ExchangeSymbols)
		u = urllib2.urlopen(url)
		content = u.read()
		# [3:] Es un parche horrible. Tomar los caracteres subsiguientes al //
		# supongo que debe haber algun otro metodo mas pulenta.
		self.JSONObject = json.loads(content[3:] )
		return True

	def getJsonFromFile(self):
		# // This method is for testing, it loads json info from local file jsontest.json
		with open('jsontest.json') as data_file:    
			#pprint(self.JSONObject)
			self.JSONObject = json.load(data_file)
			return True

	def Quotes2Stdout(self):
		# // Method just for a little json debugging
		if self.JSONObject == None:
			return
		for quote in self.JSONObject:
			print "id=%s, symbol=%s, last=%s, dif=%s, vporc=%s, prev=%s, horaLast=%s, exch=%s" % ( quote['id'], quote['t'], quote['l'], \
				quote['c'], quote['cp'], quote['pcls_fix'], quote['ltt'], quote['e'], quote['lt_dts'] )

	def JsonQot2Obj (self):
		if self.JSONObject == None:
			return
		for jquote in self.JSONObject:
			proviDate2 = None
			proviDate = jquote['lt_dts'].split("T")
			if len(proviDate) == 2:
				proviDate2 = re.sub("T", "", proviDate[0])
			mylitQuote = Quote(jquote['id'], jquote['t'], jquote['l'], jquote['c'], jquote['cp'],\
					 jquote['pcls_fix'], jquote['ltt'], jquote['e'], int(time.time()), proviDate2 )
			self.QuotesList.append(mylitQuote)
			mylitQuote = None		# // delete object.
		# print "Debug QuotesList.length=" + str(len(self.QuotesList))	


	def DumpSnap2Sqlite (self):
		# stores quotes snapshot in the snapshot table
		try:
			db = sqlite3.connect(self.SqlLiteFile)
			cursor = db.cursor()
			cursor.execute('''CREATE TABLE IF NOT EXISTS
				snapshot ( googID	INT PRIMARY KEY,
				symbol TEXT,
				last REAL,
				diference REAL,
				percentual REAL,
				previous REAL,
				time_last TEXT,
				exchange TEXT,
				timestamp INT );''')
			try:
				# explore list of quotes
				for myQuote in self.QuotesList:
					cursor.execute('''UPDATE snapshot SET symbol=?, last=?, diference=?, percentual=?, previous=?, time_last=?, \
							exchange=?, timestamp=? WHERE googID=?''', (myQuote.Symbol, myQuote.Last, myQuote.Diference, myQuote.vPercentual, \
							myQuote.Previous, myQuote.LastTime, myQuote.Exchange, int(myQuote.Timestamp), myQuote.GoogleID ))
					db.commit()
					if cursor.rowcount < 1:
						cursor.execute('''INSERT INTO snapshot (googID, symbol, last, diference, percentual, previous, time_last, exchange, timestamp) \
						VALUES(?,?,?,?,?,?,?,?,?)''', (myQuote.GoogleID, myQuote.Symbol, myQuote.Last, myQuote.Diference, myQuote.vPercentual, \
						myQuote.Previous, myQuote.LastTime, myQuote.Exchange, myQuote.Timestamp ))
						db.commit()
			except Exception as Error:
				print "SQLite Error: " + str(Error)
		finally:
			db.close()


	def UpdateDaySqlite (self):
		# // updates Dayly db for technical analysis and other uses.
		# // history dayly dataset, stored in Day_MMYYYY tables.
		# // each day there must be an entry in table for each symbol.
		Myyyy = time.strftime('%m%Y')
		TableName = 'Day_' + Myyyy
		Today = time.strftime('%Y-%m-%d')
		table_name_validator = re.compile(r'^[0-9a-zA-Z_\$]+$')
		if not table_name_validator.match(TableName):
			print 'Error: someone is trying some sql injection?'
			return

		try:
			db = sqlite3.connect(self.SqlLiteFile)
			db.row_factory = sqlite3.Row
			cursor = db.cursor()
			cursor.execute('''CREATE TABLE IF NOT EXISTS
				''' + TableName + '''(date TEXT,
				symbol TEXT,
				opening REAL,
				high REAL,
				low REAL,
				close REAL,
				exchange TEXT, PRIMARY KEY(date, symbol, exchange) );''') 
			db.commit()
			try:
				# explore list of quotes
				for myQuote in self.QuotesList:
					cursor.execute('''SELECT * FROM ''' + TableName + ''' WHERE date=? AND symbol=? AND exchange=? ''',\
									 ( myQuote.Date, myQuote.Symbol, myQuote.Exchange))
					row = cursor.fetchone()

					if (row == None) and (Today == myQuote.Date):
						# // entry doesn't exist so, do the INSERT 
						print 'Debug: Do the INSERT for ' + myQuote.Symbol
						cursor.execute('''INSERT INTO ''' + TableName + ''' (date, symbol, opening, high, low, close, exchange) \
						VALUES(?,?,?,?,?,?,?)''', (myQuote.Date, myQuote.Symbol, myQuote.Last, myQuote.Last, myQuote.Last, myQuote.Last, \
						myQuote.Exchange ))
						db.commit()
					else:
						# // entry exists, do the update
						if float(myQuote.Last) > float(row['high']) and (Today==myQuote.Date):
							cursor.execute('''UPDATE ''' + TableName + '''
							SET high=?, close=?
							WHERE date=? AND symbol=? AND exchange=? ''', \
							(myQuote.Last, myQuote.Last, myQuote.Date, myQuote.Symbol, myQuote.Exchange) )
							db.commit()
							print 'Debug ' + myQuote.Symbol + ' updated high.'
						else:
							if float(myQuote.Last) < float(row['low']) and (Today==myQuote.Date):
								cursor.execute('''UPDATE ''' + TableName + '''
								SET low=?, close=?
								WHERE date=? AND symbol=? AND exchange=? ''', \
								(myQuote.Last, myQuote.Last, myQuote.Date, myQuote.Symbol, myQuote.Exchange) )
								db.commit()
								print 'Debug ' + myQuote.Symbol + ' updated low.'
							else:
								if float(myQuote.Last) != float(row['close']) and (Today==myQuote.Date):
									cursor.execute('''UPDATE ''' + TableName + '''
									SET close=?
									WHERE date=? AND symbol=? AND exchange=? ''', \
									(myQuote.Last, myQuote.Date, myQuote.Symbol, myQuote.Exchange) )
									db.commit()
									print 'Debug ' + myQuote.Symbol + ' updated last only.'
								else:
									print 'Debug ' + myQuote.Symbol + ' no changes.'

			except Exception as Error:
				print "SQLite Error: " + str(Error)
		finally:
			db.close()




def main():

	"""
	Symbols list contain a list of pairs which describes stock symbols as used by Google API.
	Each element should be 'EXCHANGE:SYMBOL' examples:
	
		 [ 'NASDAQ:GOOG', 'NASDAQ:CSCO', 'NYSE:IBM', 'BCBA:YPFD' ]
	"""

	Symbols = [ 'NASDAQ:GOOG', 'NASDAQ:CSCO', 'NASDAQ:BABA', 'NASDAQ:APPL', 'NYSE:IBM', 'BCBA:YPFD' , 'NYSE:GLOB' ]
	#Symbols = [ 'NASDAQ:GOOG' ]

	strSymbols = ' ' 
	o = 0
	for i in Symbols:
		if o == 0:
			strSymbols = i
		else:
			strSymbols = strSymbols + ',' + i
		o += 1

	JSp = GoogleFinanceAPI()

	#if JSp.getJsonFromFile():	# // gets data from test file, just for debbugging.
	if JSp.get(strSymbols):
		#JSp.Quotes2Stdout()	# // Show a little data, just for testing
		JSp.JsonQot2Obj()
		JSp.DumpSnap2Sqlite()
		JSp.UpdateDaySqlite()


if __name__ == "__main__":
	main()



