from bs4 import BeautifulSoup 
import numpy as np 
import pandas as pd 
import requests
import time
from datetime import date,timedelta

cutoff=date.today()-timedelta(180)

t1=time.time()

def conv_percent(x):
     x=x.replace('New','1')
     x=x.replace('>','')
     return float(x.replace('%',''))

def conv_value(x):
     x=x.replace(',','')
     return float(x.replace('$',''))
                
frame=pd.DataFrame()

url='http://openinsider.com/'

extensions=['screener?fd=365&fdr=&td=0&tdr=&s=&o=&t=p&minprice=&maxprice=&v=0&isofficer=1&isceo=1&iscfo=1&sicMin=&sicMax=&sortcol=0&maxresults=1000','screener?fd=0&fdr=&td=0&tdr=&s=&o=&t=p&minprice=&maxprice=&v=0&isofficer=1&isceo=1&iscfo=1&sicMin=&sicMax=&sortcol=2&maxresults=1000','screener?fd=0&fdr=&td=0&tdr=&s=&o=&t=p&minprice=&maxprice=&v=0&isofficer=1&isceo=1&iscfo=1&sicMin=&sicMax=&sortcol=8&maxresults=1000','screener?fd=365&fdr=&td=0&tdr=&s=&o=&t=p&minprice=&maxprice=&v=0&isofficer=1&isceo=1&iscfo=1&sicMin=&sicMax=&sortcol=0&maxresults=1000','screener?fd=365&fdr=&td=0&tdr=&s=&o=&t=p&minprice=&maxprice=&v=0&isofficer=1&isceo=1&iscfo=1&sicMin=&sicMax=&sortcol=8&maxresults=1000','screener?fd=90&fdr=&td=0&tdr=&s=&o=&t=p&minprice=&maxprice=&v=0&isofficer=1&isceo=1&iscfo=1&sicMin=&sicMax=&sortcol=0&maxresults=1000','screener?fd=90&fdr=&td=0&tdr=&s=&o=&t=p&minprice=&maxprice=&v=0&isofficer=1&isceo=1&iscfo=1&sicMin=&sicMax=&sortcol=2&maxresults=1000','screener?fd=90&fdr=&td=0&tdr=&s=&o=&t=p&minprice=&maxprice=&v=0&isofficer=1&isceo=1&iscfo=1&sicMin=&sicMax=&sortcol=2&maxresults=1000','screener?fd=30&fdr=&td=0&tdr=&s=&o=&t=p&minprice=&maxprice=&v=0&isofficer=1&isceo=1&iscfo=1&sicMin=&sicMax=&sortcol=0&maxresults=1000']
print len(extensions)

for e in extensions:
    status=False
    while not status:
        try:
            site=requests.get(url+e)
            status=True
        except:
            pass
    soup=BeautifulSoup(site.content,"lxml")    
    headers=[x.text for x in soup.find_all('h3')]
    results=[[str(x.text) for x in e.find_all('td')] for e in soup.find_all('tbody')]
    original_results=sum(results,[])
    results=np.asarray(original_results)
    results=results.reshape((len(original_results)/len(headers)),len(headers))
    results=pd.DataFrame(results)
    results.columns=headers
    frame=frame.append(results)
    print frame.shape
    

frame=frame.drop_duplicates()
tt=frame.columns[7]
frame=frame.drop(['X',tt,'Filing Date','1d ret','1w ret','1m ret','6m ret'],axis=1)
frame['Value Traded']= frame['Value Traded'].apply(conv_value)
frame['Own chg']=frame['Own chg'].apply(conv_percent)
frame['Trade Date']=pd.to_datetime(frame['Trade Date'])
frame=frame[(frame['Trade Date']>=cutoff)&(frame['Own chg']>0)]


frame['Counts'] = frame.groupby(['Ticker'])['Insider Title'].transform('nunique')
frame['Sum']=frame.groupby(['Ticker'])['Own chg'].transform('sum')
frame=frame[(frame['Counts']>2)]
frame=frame.sort_values(['Sum','Ticker','Trade Date','Counts','Value Traded'],ascending=[0,1,1,0,0])
frame.to_csv('insider.csv',encoding='utf-8')
print frame.shape
t2=time.time()

print t2-t1
print "Done"
