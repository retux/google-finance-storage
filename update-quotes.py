#!/usr/bin/env python

from stockwatch import *

def main():

	"""
	Symbols list contain a list of pairs which describes stock symbols as used by Google API.
	Each element should be 'EXCHANGE:SYMBOL' examples:
        As from 2017 0901 API seems to have been updated, symbols do not require stock exchange
        name as prefix, as follows:
	
		 [ 'GOOG', 'CSCO', 'IBM', 'YPFD' ]
	"""

	Symbols = [ 'GOOG', 'CSCO', 'BABA', 'APPL', 'IBM', 'YPFD' , 'GLOB' ]
	#Symbols = [ 'GOOG' ]

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



