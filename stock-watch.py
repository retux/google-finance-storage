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

class Quote:
	def __init__ (self, googleID = None, symbol = None, last = None, diference = None, vpercentual = None, previous = None, lasttime = None, exchange = None, timestp = None):
		self.GoogleID = googleID
		self.Symbol = symbol
		self.Last = last
		self.Diference = diference
		self.vPercentual  = vpercentual
		self.Previous = previous
		self.LastTime = lasttime
		self.Exchange = exchange
		self.Timestamp = timestp

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

	def Quotes2Stdout(self):
		# // Metodo solo para algun debug del json
		if self.JSONObject == None:
			return
		for quote in self.JSONObject:
			print "id=%s, symbol=%s, last=%s, dif=%s, vporc=%s, prev=%s, horaLast=%s, exch=%s" % ( quote['id'], quote['t'], quote['l'], \
				quote['c'], quote['cp'], quote['pcls_fix'], quote['ltt'], quote['e'] )

	def JsonQot2Obj (self):
		if self.JSONObject == None:
			return
		for jquote in self.JSONObject:
			mylitQuote = Quote(jquote['id'], jquote['t'], jquote['l'], jquote['c'], jquote['cp'],\
					 jquote['pcls_fix'], jquote['ltt'], jquote['e'], int(time.time()) )
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
			except sqlite3.IntegrityError:
				# // Do the update
				print('Record already exists')

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

	Symbols = [ 'NASDAQ:GOOG', 'NASDAQ:CSCO', 'NASDAQ:BABA', 'NASDAQ:APPL', 'NYSE:IBM', 'BCBA:YPFD' ]
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
	if JSp.get(strSymbols):
		#JSp.Quotes2Stdout()	# Show a little data, just for testing
		JSp.JsonQot2Obj()
		JSp.DumpSnap2Sqlite()


if __name__ == "__main__":
	main()



