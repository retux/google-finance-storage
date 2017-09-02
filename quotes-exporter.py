#!/usr/bin/env python
'''
   quotes-exporter: exposes quotes as prometheus exporter api
   Usage: quotes-exporter.py <port> 
'''
import sys
from prometheus_client import start_http_server, Metric, REGISTRY

from stockwatch import *

def cat_to_string (Symbols):
    strSymbols = ' '
    o = 0
    for i in Symbols:
        if o == 0:
            strSymbols = i
        else:
            strSymbols = strSymbols + ',' + i
        o += 1
    return strSymbols    


class QuoteCollector(object):
  def __init__(self):
    self._endpoint = ''
  def collect(self):
    Symbols = [ 'GOOG', 'CSCO', 'BABA', 'APPL', 'IBM', 'GLOB' ]
    #Symbols = [ 'GOOG' ]

    strSymbols = cat_to_string(Symbols)
    JSp = GoogleFinanceAPI()
   
    if JSp.get(strSymbols):
        #JSp.Quotes2Stdout()	# // Show a little data, just for testing
        JSp.JsonQot2Obj()
        metric = Metric('stock_quotes', 'stock quotes last price', 'gauge')
        for quote in JSp.QuotesList:
            # Convert quotes to metric
            metric.add_sample('stock_quotes', value=float(quote.Last), labels={'symbol': quote.Symbol})
        yield metric	

def main():

    """
    Symbols list contain a list of pairs which describes stock symbols as used by Google API.
    Each element should be 'EXCHANGE:SYMBOL' examples:
 
         [ 'NASDAQ:GOOG', 'NASDAQ:CSCO', 'NYSE:IBM', 'BCBA:YPFD' ]
    """
    start_http_server(int(sys.argv[1]))
    REGISTRY.register(QuoteCollector())
    while True: time.sleep(1)
		

if __name__ == "__main__":
    main()

	
