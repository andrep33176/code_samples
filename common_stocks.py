import pandas as pd
import numpy as np
import math
from BeautifulSoup import BeautifulSoup
import re
import urllib2
from StringIO import StringIO
import time

inflation_rate=0.1
t1=time.time()

url="http://www.nasdaq.com/screening/companies-by-industry.aspx?\
industry=ALL&region=North+America&country=United+States&render=download"



def fetch_file(url):

    file_fetcher = urllib2.build_opener()
    file_fetcher.addheaders = [('User-agent', 'Mozilla/5.0')]
    file_data = file_fetcher.open(url).read()
    file_data=file_data[:-1]
    file_data=StringIO(file_data)
    file_data=pd.read_csv(file_data,sep=",")
    return file_data

frame=fetch_file(url)

nasurl="ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"

nasdaq=pd.read_csv(nasurl,sep ="|")
nasdaq=nasdaq[nasdaq["Security Name"].str.contains("Common Stock|Units",na=True)]
nassyms=list(nasdaq['Symbol'])

otherurl="ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt"
other=pd.read_csv(otherurl,sep ="|")
other=other[other["Security Name"].str.contains("Common Stock|Units",na=True)]
othersyms=list(other['ACT Symbol'])
syms=nassyms+othersyms


stocks=frame[frame['Symbol'].isin(syms)]

stocks=stocks[~stocks['Industry'].str.contains('Insurance|Insurer|Banks|Savings Institutions|Investment')]





tickers=list(stocks['Symbol'])
companies=list(stocks['Name'])
industries=list(stocks['Industry'])



stocks_dict={'Ticker':tickers,'Company':companies,'Industry':industries}
stocks=pd.DataFrame(stocks_dict)

#yahoo api only permits 200 tickers at a time, splitting symbols accordingly
n_splits=math.ceil(len(tickers)/200.0)                
symbol_lists=np.array_split(tickers,n_splits)


yahoo_cap_url='http://finance.yahoo.com/d/quotes.csv?s='


cap_list=[]
for e in symbol_lists:
   symbol_concat='+'.join(e)
   response = urllib2.urlopen(yahoo_cap_url+symbol_concat+"&f=j1")
   html = response.read()
   sub_list=html.strip().split('\n')
   cap_list.append(sub_list)
 
   
market_cap=sum(cap_list,[])
market_cap=[e.strip() for e in market_cap]

price_list=[]
for e in symbol_lists:
   symbol_concat='+'.join(e)
   response = urllib2.urlopen(yahoo_cap_url+symbol_concat+"&f=l1")
   html = response.read()
   sub_list=html.strip().split('\n')
   price_list.append(sub_list)
 
   
price=sum(price_list,[])
price=[e.strip() for e in price]
price=[float(e) if e!='N/A' else 0 for e in price]

high_list=[]
for e in symbol_lists:
   symbol_concat='+'.join(e)
   response = urllib2.urlopen(yahoo_cap_url+symbol_concat+"&f=k")
   html = response.read()
   sub_list=html.strip().split('\n')
   high_list.append(sub_list)
 
   
high=sum(high_list,[])
high=[e.strip() for e in high]

yield_list=[]
for e in symbol_lists:
   symbol_concat='+'.join(e)
   response = urllib2.urlopen(yahoo_cap_url+symbol_concat+"&f=y")
   html = response.read()
   sub_list=html.strip().split('\n')
   yield_list.append(sub_list)
 
   
yield_list=sum(yield_list,[])
yield_list=[e.strip() for e in yield_list]

pe_list=[]
for e in symbol_lists:
   symbol_concat='+'.join(e)
   response = urllib2.urlopen(yahoo_cap_url+symbol_concat+"&f=r")
   html = response.read()
   sub_list=html.strip().split('\n')
   pe_list.append(sub_list)

pe=sum(pe_list,[])
pe=[e.strip() for e in pe]

peg_list=[]
for e in symbol_lists:
   symbol_concat='+'.join(e)
   response = urllib2.urlopen(yahoo_cap_url+symbol_concat+"&f=r5")
   html = response.read()
   sub_list=html.strip().split('\n')
   peg_list.append(sub_list)

peg=sum(peg_list,[])
peg=[e.strip() for e in peg]
peg_float=[]
for e in peg:
    if e=='N/A':
        pass
    else:
        e=float(e)
    peg_float.append(e)

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


pb_list=[]
for e in symbol_lists:
   symbol_concat='+'.join(e)
   response = urllib2.urlopen(yahoo_cap_url+symbol_concat+"&f=p6")
   html = response.read()
   sub_list=html.strip().split('\n')
   pb_list.append(sub_list)

pb=sum(pb_list,[])
pb=[e.strip() for e in pb]


ps_list=[]
for e in symbol_lists:
   symbol_concat='+'.join(e)
   response = urllib2.urlopen(yahoo_cap_url+symbol_concat+"&f=p5")
   html = response.read()
   sub_list=html.strip().split('\n')
   ps_list.append(sub_list)

ps=sum(ps_list,[])
ps=[e.strip() for e in ps]



def conv_to_float(x):
    if x=='N/A':
        value='N/A'
    else:
         a=x.split('.')
         all_match=[]
         for e in a:
            matches=re.findall(r'[0-9]*?.[0-9]*',e)
            all_match.append(matches)
            elem_list=sum(all_match,[])
            if len(elem_list)==3:
                num=float(elem_list[0]+'.'+elem_list[1])
            else:
                num=float(elem_list[0])
            if elem_list[-1]=='B':
                value=num*1e9
            elif elem_list[-1]=='M':
                value=num*1e6
            else:
                value=num*1e3
   
    return value


pe_float=[]
for e in pe:
    if e=='N/A':
        pe_float.append(e)
    else:
        e=float(e)
        pe_float.append(e)
        
pb_float=[]
for e in pb:
    if e=='N/A':
        pb_float.append(e)
    else:
        e=float(e)
        pb_float.append(e)
        
ps_float=[]
for e in ps:
    if e=='N/A':
        ps_float.append(e)
    else:
        e=float(e)
        ps_float.append(e)

market_cap_float=[conv_to_float(e) for e in market_cap]


stocks['Market_Cap']=market_cap
stocks['Market_Cap_Num']=market_cap_float
stocks['P/B']=pb_float
stocks['P/E']=pe_float
stocks['P/S']=ps_float
stocks['EPS']=eps_float
stocks['Price']=price
stocks['PEG']=peg_float
stocks['High']=high
stocks['Dividend_Yield']=yield_list

stocks=stocks.sort(columns=['P/B','P/E','P/S','EPS'],ascending=[1,1,1,0])
stocks=stocks[(stocks['P/E']<15)|(stocks['P/E']=='N/A')]
stocks=stocks[(stocks['P/B']<1.5)]
stocks=stocks[['Company','Ticker','Industry','Market_Cap','Market_Cap_Num','P/B','P/E','P/S','EPS','Dividend_Yield','PEG','Price','High']]

symbols=stocks['Ticker']


def key_stat(SYM):
    url = "http://finance.yahoo.com/q/ks?s=" + SYM + "+Key+Statistics"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    res = [[x.text for x in y.parent.contents] for  y in soup.findAll('td', attrs={"class" : "yfnc_tablehead1"})]
    res=sum(res,[])
    res=[str(e) for e in res]
    res=dict(zip(res[::2],res[1::2]))
    return res


cfs=[]
lcfs=[]
deb2es=[]
cash=[]
nullsyms=[]
for e in symbols:
	try:
    		data=key_stat(e)
    		cf=data['Operating Cash Flow (ttm):']
    		lcf=data['Levered Free Cash Flow (ttm):']
    		deb2e=data['Total Debt/Equity (mrq):']
    		cps=data['Total Cash Per Share (mrq):']
    		deb2e=deb2e.replace(",", "")
    		cps=cps.replace(",","")
    		cfs.append(cf)
    		lcfs.append(lcf)
    		deb2es.append(deb2e)
    		cash.append(cps)
	except:
		nullsyms.append(e)

for e in nullsyms:
	stocks=stocks[stocks['Ticker']!=e]

print nullsyms

cash=[e if e!='N/A' else 0 for e in cash]
cash_float=[float(e) for e in cash]  
cfs_float=[conv_to_float(e) for e in cfs]
lcfs_float=[conv_to_float(e) for e in lcfs]
lcfs_float=[e if e!='N/A' else 1 for e in lcfs_float]
deb2es_float=[]
for e in deb2es:
    if e=='N/A':
        deb2es_float.append(e)
    else:
        e=float(e)
        deb2es_float.append(e)
        
stocks['CPS']=cash_float
stocks['Cash_Flow']=cfs
stocks['Cash_Flow_Num']=cfs_float
stocks['Levered_Cash_Flow']=lcfs
stocks['Levered_Cash_Flow Num']=lcfs_float
stocks['Debt_to_Equity']=deb2es_float

stocks=stocks[(stocks['Levered_Cash_Flow Num']>0)&(stocks['Cash_Flow_Num']>0)]


def dcf(cash_flow):
    if cash_flow =='N/A':
        return 'N/A'
    else:
        cash=np.ones((10))*cash_flow
        vec= np.ones((10))-(np.arange(1,11)*inflation_rate)
        return sum(vec*cash)


dcfs=[dcf(e) for e in stocks['Cash_Flow_Num']]
stocks['DCF']=dcfs
stocks['DCF']=stocks['DCF'].replace('N/A',0)
stocks['DCF_Val']=stocks['DCF']/stocks['Market_Cap_Num']
stocks['P/S']=stocks['P/S'].replace('N/A',1)
stocks['P/E']=stocks['P/E'].replace('N/A',0.001)
stocks['Profit_Margin']=(stocks['P/S']/stocks['P/E'])*100
stocks['ROE']=(stocks['P/B']/stocks['P/E'])*100
stocks['Debt_to_Equity']=stocks['Debt_to_Equity'].replace('N/A',0)
stocks['Debt_to_Earnings']=stocks['Debt_to_Equity']/stocks['ROE']
#stocks['GV']=stocks['P/E']*stocks['P/B']
#stocks['GN']=(stocks['EPS']*(stocks['Price']/stocks['P/B'])*22.5)**0.5
#stocks=stocks[(stocks['Debt_to_Equity']<55)|(stocks['Debt_to_Earnings']<5.1)]
stocks=stocks.sort(columns=['ROE','Profit_Margin','DCF_Val','Debt_to_Earnings'],ascending=[0,0,0,1])

stocks=stocks[['Company','Ticker','Industry','Market_Cap','DCF','DCF_Val','ROE','Debt_to_Earnings',\
		'P/B','P/E','P/S','EPS','Debt_to_Equity','Dividend_Yield',\
		'Profit_Margin','PEG','Cash_Flow','Levered_Cash_Flow','CPS','Price','High']]
stocks=stocks[(stocks['DCF_Val']>1)]




print stocks.shape

stocks.to_csv('common_stocks.csv',index=False)
t2=time.time()
print t2-t1

