'''
Created on Apr 9, 2018

ncep_main.py is a high-level interface to map weather data based on NOAA's
daily historical and forecast heating and cooling degree days at the level
of the 344 state climate divisions or the Lower 48 states.

@author: Jason Upchurch
         
         email: jmu7av@virginia.edu
         
'''
from datetime import datetime
import ncep_util
import ncep_mapping



'''
user configuration:

path: enter a path to save your maps and data (not required, but if the 
      "savepath" argument is passed, path must be a valid directory or
      the boolean False))
email: enter your email address (optional)
'''


'''
map average temps:

fname is the filename you wish to save as (this will apply to the csv and
the png that are saved. Do not provide an extension--both files will get 
the same name with csv and png extensions.
'''
# fname1 = 'average_temps'
# savepath = path+fname1
# date_start = datetime(2019,1,29).date() #provide a valid start date YYYY, (M)M, (D)D
# date_end = datetime(2019,2,2).date()  #provide a valid start date YYYY, (M)M, (D)D
# plt_average_temps = ncep_mapping.map_average_temps(date_start, date_end,email,
#                                       split_on = 55,how='state',legend=True,savepath=False)
# plt_average_temps.show()



'''
map compare average temps
'''
fname2 = 'compare_average_temps'
savepath = False
date_start = datetime(2019,7,4).date()
date_end = datetime(2019,7,4).date()
date_start_compare = datetime(2018,7,4).date()
date_end_compare = datetime(2018,7,4).date()
plt_compare = ncep_mapping.map_compare_average_temps(date_start, date_end, date_start_compare, date_end_compare,
                '', how='stcd',legend = True)
plt_compare.show()



'''
map departure from normal temps
'''
# path = ''
# fname3 = 'Jan_30_departures'
# savepath = path + fname3
# date_start = datetime(2019,2,1).date()
# date_end = datetime(2019,2,26).date()
# begin_normal_year, end_normal_year = 1981, 2010
# plt_depart_from_normal = ncep_mapping.map_depart_from_normal_temps(
#                             date_start, date_end, begin_normal_year, end_normal_year,
#                             email,how='state', legend = True, savepath=False)
# plt_depart_from_normal.show()
 
 
 
'''
advanced: get range of heating degree days for state (illustrates interaction with
          ncep_util module
'''
# fname4 = 'default'
# date_start = datetime(2016,1,1).date()
# date_end = datetime(2016,12,31).date()
# HDD_FNAME_STATE = 'StatesCONUS.Heating.txt'
# hdd = ncep_util.retrieve_range(HDD_FNAME_STATE, date_start, date_end, email)
# hdd.to_csv(path+fname4)
