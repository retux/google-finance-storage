This scripts stores stock information from Google Finance public API and store it within a database.

How this script works?

It gets stock quotes from Google Public API. The stock list is defined at main function, within Symbols array. 
This array contains a list of 'EXCHANGE:SYMBOL'. For instance:


 Symbols list contain a list of pairs which describes stock symbols as used by Google API.
        Each element should be 'EXCHANGE:SYMBOL' examples:

        Symbols = [ 'NASDAQ:GOOG', 'NASDAQ:CSCO', 'NASDAQ:BABA', 'NASDAQ:APPL', 'NYSE:IBM', 'BCBA:YPFD' ]


The script creates and store data in a sqlite3 database, called google_quotes.sqlite3.
That db contains tables for snapshot quotes (the most recent snapshot) in a table call "snapshot", and tables
for historical data, dynamically created with the following pattern: Day_DDYYYY.

sqlite> .tables
Day_122014  snapshot


