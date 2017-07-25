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
  def __init__(self, endpoint):
    self._endpoint = ''
  def collect(self):
    # Fetch the quotes
    #response = json.loads(requests.get(self._endpoint).content.decode('UTF-8'))

    Symbols = [ 'NASDAQ:GOOG', 'NASDAQ:CSCO', 'NASDAQ:BABA', 'NASDAQ:APPL', 'NYSE:IBM', 'NYSE:GLOB' ]
    #Symbols = [ 'NASDAQ:GOOG' ]

    strSymbols = cat_to_string(Symbols)
    JSp = GoogleFinanceAPI()
   
    if JSp.get(strSymbols):
        JSp.Quotes2Stdout()	# // Show a little data, just for testing
        JSp.JsonQot2Obj()
        #print("[debug] Quotes list length: {0}".format(JSp.getQuotesListLength())) 	
        for quote in JSp.QuotesList:
            print("[debug] symbol: {0}, last: {1}".format(quote.Symbol, quote.Last))
    
            # Convert quotes to metric
            metric = Metric('{0}_last_price'.format(quote.Symbol), 'Last price for {0} stock'.format(quote.Symbol), 'summary')
            metric.add_sample('{0}_last_price'.format(quote.Symbol), value=float(quote.Last), labels={})
            yield metric	

def main():

    """
    Symbols list contain a list of pairs which describes stock symbols as used by Google API.
    Each element should be 'EXCHANGE:SYMBOL' examples:
 
         [ 'NASDAQ:GOOG', 'NASDAQ:CSCO', 'NYSE:IBM', 'BCBA:YPFD' ]
    """
    start_http_server(int(sys.argv[1]))
    REGISTRY.register(QuoteCollector('blah'))
    while True: time.sleep(1)
		

if __name__ == "__main__":
    main()

	