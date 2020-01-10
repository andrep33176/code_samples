import pandas.io.html as ph
import datetime
import csv
import urllib2
import pandas as pd
import numpy as np
import math
from BeautifulSoup import BeautifulSoup
import re
import time
import math
from pandas.io.data import Options

t1=time.time()

token='QJwenTEyTkfCEGjRy6XS'

#figure days to expiry
expiry=datetime.date(2016,1,16)
today=datetime.date.today()
time_left=expiry-today
#fetch Leap Data from cboe
url = 'http://www.cboe.com/publish/ScheduledTask/MktData/cboesymboldir2.csv'
response = urllib2.urlopen(url)
#Parse csv into pandas readable format
cr = csv.reader(response)
rows=[]
for row in cr:
    rows.append(row)
rel_rows=rows[2:]

yahoo_cap_url='http://finance.yahoo.com/d/quotes.csv?s='

#Create Dataframe
names=["Name","Symbol","DPM Name","Cycle","Traded at C2","Leaps 2015","Leaps 2016","Leaps 2017","Product Type","10","11","12","13"]
options=pd.DataFrame(rel_rows)
options.columns=names
#Cull Possible Leaps
rel_variables=options[['Name','Symbol','DPM Name','Leaps 2016','Leaps 2017','Product Type','10','11','12','13']]
rel_options=rel_variables[(rel_variables['Product Type']=='L')|(rel_variables['10']=='L')|(rel_variables['11']=='L')|(rel_variables['12']=='L')\
|(rel_variables['Leaps 2016']=='Y')|(rel_variables['Leaps 2017']=='Y')|(rel_variables['13']=='L')]
ticker_symbols=(rel_options['Symbol'])
print len(ticker_symbols)


companies=pd.DataFrame({'Ticker':ticker_symbols})

#yahoo api only permits 200 tickers at a time, splitting symbols accordingly
n_splits=math.ceil(len(ticker_symbols)/200.0)                
symbol_lists=np.array_split(ticker_symbols,n_splits)   

pb_list=[]
for e in symbol_lists:
   symbol_concat='+'.join(e)
   response = urllib2.urlopen(yahoo_cap_url+symbol_concat+"&f=p6")
   html = response.read()
   sub_list=html.strip().split('\n')
   pb_list.append(sub_list)

pb=sum(pb_list,[])
pb=[e.strip() for e in pb]



pb_float=[]
for e in pb:
    if e=='N/A':
        pb_float.append(e)
    else:
        e=float(e)
        pb_float.append(e)
eps_list=[]
for e in symbol_lists:
   symbol_concat='+'.join(e)
   response = urllib2.urlopen(yahoo_cap_url+symbol_concat+"&f=e")
   html = response.read()
   sub_list=html.strip().split('\n')
   eps_list.append(sub_list)

eps=sum(eps_list,[])
eps=[e.strip() for e in eps]
eps_float=[]
for e in eps:
    if e=='N/A':
        pass
    else:
        e=float(e)
    eps_float.append(e)
    
pe_list=[]
for e in symbol_lists:
   symbol_concat='+'.join(e)
   response = urllib2.urlopen(yahoo_cap_url+symbol_concat+"&f=r")
   html = response.read()
   sub_list=html.strip().split('\n')
   pe_list.append(sub_list)

pe=sum(pe_list,[])
pe=[e.strip() for e in pe]

pe_float=[]
for e in pe:
    if e=='N/A':
        pe_float.append(e)
    else:
        e=float(e)
        pe_float.append(e)
        
companies['P/B']=pb_float
companies['EPS']=eps_float
companies['P/E']=pe_float
companies=companies[(companies['P/B']<1)|(companies['P/E']<9.1)]
#companies=companies[(companies['EPS']>0)]
print companies.shape
companies.to_csv("candidates.csv",index=False)

        





