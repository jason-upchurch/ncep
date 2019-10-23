'''
Created on Apr 9, 2018

ncep_util.py is a low-level interface to retrieve and process weather data 
from NOAA's daily historical and forecast heating and cooling degree days 
at the level of the 344 state climate divisions or the Lower 48 states. See
raw data at: ftp://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/

@author: Jason Upchurch
         
         email: jmu7av@virginia.edu
'''

import urllib.request
from datetime import datetime, timedelta
import pandas as pd
from ftplib import FTP

DEGREE_DAY_HISTORY_FTP = r'ftp://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data//'
DEGREE_DAY_FORECAST_FTP = r'ftp://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_forecasts_7day/'
HISTORY = r'htdocs/degree_days/weighted/daily_data'
FORECAST = r'htdocs/degree_days/weighted/daily_forecasts_7day'
CDD_FNAME_STATE = 'StatesCONUS.Cooling.txt'
HDD_FNAME_STATE = 'StatesCONUS.Heating.txt'
CDD_FNAME_STCD = 'ClimateDivisions.Cooling.txt'
HDD_FNAME_STCD = 'ClimateDivisions.Heating.txt'
NOAA_FTP_SERVER = 'ftp.cpc.ncep.noaa.gov'
AGG_DICT = {'stcd':[CDD_FNAME_STCD,HDD_FNAME_STCD],
            'state':[CDD_FNAME_STATE,HDD_FNAME_STATE]}

def degree_day_history(fname,year):
    df = pd.read_table(DEGREE_DAY_HISTORY_FTP+'/'+str(year)+'/'+fname,
                       header=3,sep='|',index_col=0,na_values = '-9999').T   
    df.index = pd.to_datetime(df.index,format='%Y%m%d')
    return df

def forecast_date_isnan(fname,date):
    day = '{:02d}'.format(date.day)
    month = '{:02d}'.format(date.month)
    year = str(date.year)
    df = pd.read_table(DEGREE_DAY_FORECAST_FTP+year+'/'+month+'/'+\
                       day+'/'+fname, header=3,sep='|',index_col=0,na_values = '-9999').T   
    df = df.drop('Total')
    df.index = pd.to_datetime(df.index,format='%Y%m%d') 
    df.dropna(inplace=True)
    if date in df.index.values:
        return False
    return True
        
def degree_day_forecast(fname,date):
    day = '{:02d}'.format(date.day)
    month = '{:02d}'.format(date.month)
    year = str(date.year)
     
    df = pd.read_table(DEGREE_DAY_FORECAST_FTP+year+'/'+month+'/'+\
                       day+'/'+fname, header=3,sep='|',index_col=0,na_values = '-9999').T   
    df = df.drop('Total')
    df.index = pd.to_datetime(df.index,format='%Y%m%d')  
    df.dropna(inplace=True)
    return df      

'''
returns a dataframe of normal hdd or cdd based on the specified interval
(it will contain either 365 or 366 days depending on whether or not
the interval contains a leap year)
'''
def _normal(fname,year_begin,year_end,email):
    if year_begin > last_date_in_forecast(email).year:
        return pd.DataFrame()
    if year_end < first_date_in_history(email).year:
        return pd.DataFrame()
    fyh = first_date_in_history(email).year
    if year_begin < fyh:
        year_begin = fyh
        print('Warning for '+fname+': normal year start provided occurs before first year in NOAA FTP. Using '+\
              str(year_begin)+ ' as begin normal year.')
    lyh = last_date_in_forecast(email).year
    if year_end > lyh:
        year_end = lyh
        print('Warning for '+fname+': normal year end provided occurs after last year in NOAA FTP. Using '+\
              str(year_end)+ ' as end normal year.')        
    df = degree_day_history(fname,year_begin)
    for i in range(year_begin+1,year_end+1):
        df = df.append(degree_day_history(fname,i),sort=True)
    df.index = pd.to_datetime(df.index,format='%Y%m%d')
    ldh = last_date_in_history(email)
    ld_requested = datetime(year_end,12,31).date()
    if ldh < ld_requested:
        df = df.append(retrieve_range(fname, ldh+timedelta(days=1), ld_requested,email),sort=True)
    df.index = pd.to_datetime(df.index,format='%Y%m%d')
    df = df.groupby([df.index.month,df.index.day],as_index=True).mean()
    return df

def depart_from_normal(fname,date_start,date_end,begin_normal_year,end_normal_year,email):  
    dd_n = _normal(fname,begin_normal_year,end_normal_year,email)
    dd_a = retrieve_range(fname, date_start, date_end,email)
    if dd_n.empty or dd_a.empty:
        print('Warning for '+fname+': dates provided return an empty DataFrame.')
        return pd.DataFrame()
    dfn = pd.DataFrame(index=dd_a.index,columns=dd_a.columns)
    for date in dfn.index:
        try:
            dfn.loc[date] = dd_a.loc[date].values-dd_n.loc[date.month,date.day].values
        except KeyError:
            dfn.loc[date] = 0
    return dfn 

def depart_from_normal_temps(date_start,date_end,begin_normal_year,end_normal_year,email,how='stcd'):
    dfn_cdd = depart_from_normal(AGG_DICT[how][0], date_start, date_end, begin_normal_year, end_normal_year,email)
    dfn_hdd = depart_from_normal(AGG_DICT[how][1], date_start, date_end, begin_normal_year, end_normal_year,email)
    return dfn_cdd-dfn_hdd

def average_dd(fname,date_start,date_end,email):
    df = retrieve_range(fname,date_start,date_end,email)
    df = pd.DataFrame(df.mean()).T
    df.index = [str(date_start)+' to '+str(date_end)]
    return df

def _retrieve_forecast_range(fname,date_start,date_end,email):
    ldf = last_date_in_forecast(email)
    if date_start > date_end:
        return pd.DataFrame()
    if date_start < first_date_in_forecast(email):
        date_start = first_date_in_forecast(email)
    if date_end > ldf:
        date_end = ldf
        print('Warning for '+fname+': end date provided occurs after last date in NOAA FTP. Using '+\
              str(date_end)+ ' as date end.')
    ldir = _last_directory_with_forecast_date(fname,date_end,email)
    rng = pd.date_range(start = date_start,end=date_end)
    df = pd.DataFrame(index = pd.to_datetime(rng,format='%Y%m%d'))
    for date in df.index:
        try:
            if ldir < date_end and ldir < date.date():
                df_tmp = degree_day_forecast(fname, ldir)
            else:
                df_tmp = degree_day_forecast(fname, date.date())
            df = df.append(df_tmp,sort=True)
        except urllib2.URLError:
            continue
    df.index = pd.to_datetime(df.index,format='%Y%m%d')
    df = df[~df.index.duplicated(keep='last')]
    return df.loc[date_start:date_end]
      
def _retrieve_history_range(fname,date_start,date_end,email):
    if date_start > date_end:
        print('Warning for '+fname+': start date provided occurs after end date provided')
        return pd.DataFrame()
    if date_start < first_date_in_history(email):
        date_start = first_date_in_history(email)
        print('Warning for '+fname+': start date provided occurs before first day in NOAA FTP. Using '+\
              str(date_start)+' as the new start date.')
    if date_end > last_date_in_history(email):
        date_end = last_date_in_history(email)
    rng = pd.date_range(start = date_start,end=date_end)
    df = pd.DataFrame(index = pd.to_datetime(rng,format='%Y%m%d'))
    df.index = df.index.date
    df_tmp = degree_day_history(fname,date_start.year)
    for year in range(date_start.year+1,date_end.year+1):
        df_tmp = df_tmp.append(degree_day_history(fname,year),sort=True)
    df_tmp.index=df_tmp.index.date
    return df_tmp.loc[df.index[0]:df.index[-1]]        
 
def date_in_history(fname,date): 
    try:
        df = degree_day_history(fname, date.year)
        if date in df.index:
            return True
    except urllib2.URLError:
        return False
    return False
    
def date_in_forecast(fname,date):
    try:
        degree_day_forecast(fname, date)
        return True
    except urllib2.URLError:
        return False

def _noaa_ftp_login(email):
    ftp = FTP(NOAA_FTP_SERVER)
    ftp.login(user='anonymous',passwd=email)
    return ftp    

def _last_directory_in_ftp(ftp,directory):    
    ftp.cwd(directory)
    nlist = [x for x in ftp.nlst() if x.isdigit()]
    if nlist:
        nlist = [int(max(nlist))]
        nlist+=_last_directory_in_ftp(ftp,max([x for x in ftp.nlst() if x.isdigit()]))
    return nlist

def _last_directory_with_forecast_date(fname,date,email):
    fdate = first_date_in_forecast(email)
    ldate = last_date_in_forecast(email)
    if date < fdate or date > ldate:
        return None
    else:
        rng = pd.date_range(start = fdate,end=ldate).sort_values(ascending=False)
        for d in rng:
            try:
                df = degree_day_forecast(fname, d)
                if date in df.index:
                    return d.date()
            except:
                continue
    return None
                
def _first_directory_in_ftp(ftp,directory):    
    ftp.cwd(directory)
    nlist = [x for x in ftp.nlst() if x.isdigit()]
    if nlist:
        nlist = [int(min(nlist))]
        nlist+=_first_directory_in_ftp(ftp,min([x for x in ftp.nlst() if x.isdigit()]))
    return nlist

def _first_date_in_ftp(ftp,directory):
    nlist = _first_directory_in_ftp(ftp,directory)
    if len(nlist)==3:
        df = degree_day_forecast(CDD_FNAME_STATE, datetime(nlist[0],nlist[1],nlist[2]).date())
    elif len(nlist)==1:
        df = degree_day_history(CDD_FNAME_STATE, nlist[0])
    return df.index[0].date()

def _last_date_in_ftp(ftp,directory):
    nlist = _last_directory_in_ftp(ftp,directory)
    if len(nlist)==3:
        df = degree_day_forecast(CDD_FNAME_STATE, datetime(nlist[0],nlist[1],nlist[2]).date())
    elif len(nlist)==1:
        df = degree_day_history(CDD_FNAME_STATE, nlist[0])
    return df.index[-1].date()

def first_date_in_history(email):
    ftp = _noaa_ftp_login(email)
    fd = _first_date_in_ftp(ftp,HISTORY)
    ftp.quit()
    return fd

def first_date_in_forecast(email):
    ftp = _noaa_ftp_login(email)
    fd = _first_date_in_ftp(ftp, FORECAST)
    ftp.quit()
    return fd

def last_date_in_history(email):
    ftp = _noaa_ftp_login(email)
    ld = _last_date_in_ftp(ftp, HISTORY)
    ftp.quit()
    return ld
    
def last_date_in_forecast(email):
    ftp = _noaa_ftp_login(email)
    ld = _last_date_in_ftp(ftp,FORECAST)
    ftp.quit()
    return ld      

def compare_average_temps(date_start, date_end, date_start_compare, date_end_compare,email,how='stcd'):
    df_start = average_temps(date_start, date_end, email,how)
    df_compare = average_temps(date_start_compare, date_end_compare,email, how)
    if df_start.empty or df_compare.empty:
        print('Warning: dates provided returns an empty DataFrame.')
        return pd.DataFrame()
    df = df_start.loc[str(date_start)+' to '+str(date_end)]-df_compare.loc[str(date_start_compare)+' to '+str(date_end_compare)]
    df = pd.DataFrame(df).T
    df.index = [str(date_start)+' to '+str(date_end)+' compared to '+str(date_start_compare)+' to '+str(date_end_compare)]
    return df

def average_temps(date_start,date_end,email,how='stcd'):
    df_cdd = average_dd(AGG_DICT[how][0],date_start,date_end,email)
    df_hdd = average_dd(AGG_DICT[how][1],date_start,date_end,email)
    df = 65+df_cdd-df_hdd
    df = pd.DataFrame(df)
    df.index = [str(date_start)+' to '+str(date_end)]
    return df

def retrieve_range(fname,date_start,date_end,email):
    if date_start > date_end:
        print('Warning for '+fname+': start date provided occurs after end date provided.')
        return pd.DataFrame()
    ldh = last_date_in_history(email)
    fdh = first_date_in_history(email)
    ldf = last_date_in_forecast(email)
    if date_end < fdh:
        print('Warning for '+ fname+':  end date provided occurs prior to first day in NOAA FTP.')
        return pd.DataFrame()
    if date_start > ldf:
        print('Warning for '+fname+': start date provided occurs after last day in NOAA FTP.')
        return pd.DataFrame()
    if date_end <= ldh:
        return _retrieve_history_range(fname,date_start,date_end,email)
    elif date_start > ldh:
        return _retrieve_forecast_range(fname,date_start,date_end,email)
    else:
        dfh = _retrieve_history_range(fname,date_start,ldh,email)
        dfh.index = pd.to_datetime(dfh.index)
        dff = _retrieve_forecast_range(fname,ldh+timedelta(days=1),date_end,email)
        dfh.index = pd.to_datetime(dfh.index)
    df = dfh.append(dff,sort=True)
    df.index = pd.to_datetime(df.index.date)
    return df
