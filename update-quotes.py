#!/usr/bin/env python

from stockwatch import *

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



