'''
Created on Apr 3, 2018

@author: Jason Upchurch
         email: jmu7av@virginia.edu
'''

import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import ncep_util
from mpmath import eps

STCD_SHAPEFILE_PATH = r'../shapefiles/'
STCD_SHAPEFILE_FNAME = 'GIS.OFFICIAL_CLIM_DIVISIONS.shp'
STATE_SHAPEFILE_PATH = r'../shapefiles/'
STATE_SHAPEFILE_FNAME = 'cb_2017_us_state_500k.shp'
ATTRIBUTE_DICT = {'stcd':['CLIMDIV',STCD_SHAPEFILE_PATH+STCD_SHAPEFILE_FNAME],
                  'state':['STUSPS',STATE_SHAPEFILE_PATH+STATE_SHAPEFILE_FNAME]}
FIG_SIZE = (5,3)
'''
colormap
'''
den = 255.0
color_palette = dict([(-25,(0/den,74/den, 106/den)),
                      (-20,(0/den,112/den,159/den)),
                      (-15,(0/den,150/den,215/den)),
                      (-10,(77/den,202/den,255/den)),
                      (-5,(136/den,219/den,255/den)),
                      (-eps,(196/den,237/den,255/den)),
                      (0,(242/den,242/den,242/den)),
                      (eps,(244/den,226/den,208/den)),
                      (5,(235/den,199/den,163/den)),
                      (10,(224/den,171/den,118/den)),
                      (15,(189/den,115/den,42/den)),
                      (20,(141/den,86/den,31/den)),
                      (25,(94/den,57/den,21/den))])

def map_depart_from_normal_temps(date_start, date_end, begin_normal_year, 
                                 end_normal_year,email, how='stcd', legend=False,savepath=False):
    fig = plt.figure(figsize=FIG_SIZE)
    ax = plt.axes(projection=ccrs.LambertConformal())
    ax.set_extent([-124.5,-64,21.3,49], ccrs.Geodetic())
    plt.margins(0,0)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    plt.tight_layout()
    reader_state = Reader(STATE_SHAPEFILE_PATH+STATE_SHAPEFILE_FNAME)
    reader_how = Reader(ATTRIBUTE_DICT[how][1])
    dfn_temps = ncep_util.depart_from_normal_temps(date_start, date_end, begin_normal_year, 
                                                   end_normal_year,email,how=how)
    dfn = pd.DataFrame(dfn_temps.mean(skipna=True).round()).T.astype(int)
    for record in reader_how.records():
        if record.attributes[ATTRIBUTE_DICT[how][0]] in dfn.columns:
            val = dfn[record.attributes[ATTRIBUTE_DICT[how][0]]].values.astype(int)[0]
            if val < 0:
                color_palette_modified = [x for x in color_palette.keys() if x > val]
                facecolor = color_palette[min(color_palette_modified)]
            if val > 0:
                color_palette_modified = [x for x in color_palette.keys() if x < val]
                facecolor = color_palette[max(color_palette_modified)]
            if val < eps and val > -eps:
                facecolor = color_palette[0]
            ax.add_geometries(record.geometry,ccrs.PlateCarree(),facecolor=facecolor,
                              edgecolor=facecolor,linewidth=0.4)
    for record in reader_state.records():
        ax.add_geometries(record.geometry,ccrs.PlateCarree(),facecolor='none',
                          edgecolor='white',linewidth=0.5)
    ax.outline_patch.set_edgecolor('white')    
    if legend:
        inc = 0.2
        y = list(set([float(x) for x in color_palette.keys()]))
        y.sort()
        for color in y:
            rect = mpatches.Rectangle(xy=(0.85,inc), width=0.025, height=0.05,
                                            facecolor=color_palette[color],
                                            transform = ax.transAxes)
            ax.add_patch(rect)
            if color < 0:   
                if int(color)==int(min(y)):
                    plt.annotate(str(int(color))+' or below',xy=(0,0),xytext=(0.875,inc+0.005),
                                 textcoords='axes fraction',fontname='Arial',fontsize=9,
                             color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)                 
                elif int(color)==0:
                    plt.annotate(' '+str(int(color))+' to '+str(int(color-5)),xy=(0,0),
                                 xytext=(0.875,inc+0.005),textcoords='axes fraction',fontname='Arial',fontsize=9,
                             color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)    
                else:                    
                    plt.annotate(str(int(color))+' to '+str(int(color-5)),xy=(0,0),
                                 xytext=(0.875,inc+0.005),textcoords='axes fraction',fontname='Arial',fontsize=9,
                             color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)
            elif color > 0:
                if int(color)==int(max(y)):
                    plt.annotate(' '+str(int(color))+' or above',xy=(0,0),xytext=(0.875,inc+0.005),
                                 textcoords='axes fraction',fontname='Arial',fontsize=9,
                             color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)                      
    
                else:
                    plt.annotate(' '+str(int(color))+' to '+str(int(color+5)),xy=(0,0),
                                 xytext=(0.875,inc+0.005),textcoords='axes fraction',fontname='Arial',fontsize=9,
                        color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)     
            else:
                plt.annotate(' '+str(int(color)),xy=(0,0),xytext=(0.875,inc+0.005),textcoords='axes fraction',
                             fontname='Arial',fontsize=9,
                         color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)                          
            inc+=0.05
        plt.annotate('degrees\nFahrenheit',xy=(0,0), xytext = (0.85,inc+0.075),textcoords='axes fraction',
                     fontname='Arial',fontsize=9,
                    color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)
        plt.annotate('above/below',xy=(0,0),xytext = (0.85,inc+.02),textcoords='axes fraction',fontname='Arial',
                     fontsize=9,
                    color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)         
    if savepath:
        dfn.to_csv(savepath+'.csv')
        fig.savefig(savepath+".png",bbox_inches='tight',transparent=True)
    return plt  

def map_compare_average_temps(date_start, date_end, date_start_compare, date_end_compare,email,how='stcd',
                              legend=False,savepath=False):
    fig = plt.figure(figsize=FIG_SIZE)
    ax = plt.axes(projection=ccrs.LambertConformal())
    ax.set_extent([-124.5,-64,21.3,49], ccrs.Geodetic())
    plt.margins(0,0)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    plt.tight_layout()
    reader_state = Reader(STATE_SHAPEFILE_PATH+STATE_SHAPEFILE_FNAME)
    reader_how = Reader(ATTRIBUTE_DICT[how][1])
    df = ncep_util.compare_average_temps(date_start, date_end, date_start_compare, date_end_compare, email,how)
    for record in reader_how.records():
        if record.attributes[ATTRIBUTE_DICT[how][0]] in df.columns:
            val = df[record.attributes[ATTRIBUTE_DICT[how][0]]].values.astype(int)[0]
            if val < 0:
                color_palette_modified = [x for x in color_palette.keys() if x > val]
                facecolor = color_palette[min(color_palette_modified)]
            if val > 0:
                color_palette_modified = [x for x in color_palette.keys() if x < val]
                facecolor = color_palette[max(color_palette_modified)]
            if val < eps and val > -eps:
                facecolor = color_palette[0]
            ax.add_geometries(record.geometry,ccrs.PlateCarree(),facecolor=facecolor,edgecolor=facecolor,
                              linewidth=0.4)
    for record in reader_state.records():
        ax.add_geometries(record.geometry,ccrs.PlateCarree(),facecolor='none',edgecolor='white',linewidth=0.5)
    ax.outline_patch.set_edgecolor('white')    
    if legend:
        inc = 0.2
        y = list(set([float(x) for x in color_palette.keys()]))
        y.sort()
        for color in y:
            rect = mpatches.Rectangle(xy=(0.85,inc), width=0.025, height=0.05,
                                            facecolor=color_palette[color],
                                            transform = ax.transAxes)
            ax.add_patch(rect)
            if color < 0:   
                if int(color)==int(min(y)):
                    plt.annotate(str(int(color))+' or below',xy=(0,0),xytext=(0.875,inc+0.005),
                                 textcoords='axes fraction',fontname='Arial',fontsize=9,
                             color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)                 
                elif int(color)==0:
                    plt.annotate(' '+str(int(color))+' to '+str(int(color-5)),xy=(0,0),
                                 xytext=(0.875,inc+0.005),textcoords='axes fraction',fontname='Arial',fontsize=9,
                             color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)    
                else:                    
                    plt.annotate(str(int(color))+' to '+str(int(color-5)),xy=(0,0),xytext=(0.875,inc+0.005),
                                 textcoords='axes fraction',fontname='Arial',fontsize=9,
                             color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)
            elif color > 0:
                if int(color)==int(max(y)):
                    plt.annotate(' '+str(int(color))+' or above',xy=(0,0),xytext=(0.875,inc+0.005),
                                 textcoords='axes fraction',fontname='Arial',fontsize=9,
                             color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)                      
    
                else:
                    plt.annotate(' '+str(int(color))+' to '+str(int(color+5)),xy=(0,0),xytext=(0.875,inc+0.005),
                                 textcoords='axes fraction',fontname='Arial',fontsize=9,
                        color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)     
            else:
                plt.annotate(' '+str(int(color)),xy=(0,0),xytext=(0.875,inc+0.005),textcoords='axes fraction',
                             fontname='Arial',fontsize=9,
                         color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)                          
            inc+=0.05
        plt.annotate('degrees\nFahrenheit',xy=(0,0), xytext = (0.85,inc+0.075),textcoords='axes fraction',
                     fontname='Arial',fontsize=9,
                    color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)
        plt.annotate('above/below',xy=(0,0),xytext = (0.85,inc+0.02),textcoords='axes fraction',
                     fontname='Arial',fontsize=9,
                    color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)         
    if savepath:
        df.to_csv(savepath+'.csv')
        plt.savefig(savepath+".png",bbox_inches='tight',transparent=True)
    return plt  

def map_average_temps(date_start,date_end,email,split_on = 65,how='stcd',legend=False,savepath=False):
    fig = plt.figure(figsize=FIG_SIZE)
    ax = plt.axes(projection=ccrs.LambertConformal())
    ax.set_extent([-124.5,-64,21.3,49], ccrs.PlateCarree())
    plt.margins(0,0)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    plt.tight_layout()
    reader_state = Reader(STATE_SHAPEFILE_PATH+STATE_SHAPEFILE_FNAME)
    reader_how = Reader(ATTRIBUTE_DICT[how][1])
    df_temps = ncep_util.average_temps(date_start, date_end,email,how=how)
    for record in reader_how.records():
        if record.attributes[ATTRIBUTE_DICT[how][0]] in df_temps.columns:
            val = df_temps[record.attributes[ATTRIBUTE_DICT[how][0]]].values.astype(int)[0]
            if val < split_on:
                color_palette_modified = [x for x in color_palette.keys() if x+split_on > val]
                facecolor = color_palette[min(color_palette_modified)]
            elif val > split_on:
                color_palette_modified = [x for x in color_palette.keys() if x+split_on < val]
                facecolor = color_palette[max(color_palette_modified)]
            else:
                facecolor = color_palette[0]
            ax.add_geometries(record.geometry,ccrs.PlateCarree(),facecolor=facecolor,edgecolor=facecolor,
                              linewidth=0.4)
    for record in reader_state.records():
        ax.add_geometries(record.geometry,ccrs.PlateCarree(),facecolor='none',edgecolor='white',linewidth=0.5)
    ax.outline_patch.set_edgecolor('white')  
    if legend:
        inc = 0.2
        y = list(set([float(x) for x in color_palette.keys()]))
        y.sort()
        for color in y:
            rect = mpatches.Rectangle(xy=(0.85,inc), width=0.025, height=0.05,
                                            facecolor=color_palette[color],
                                            transform = ax.transAxes)
            ax.add_patch(rect)
            if color < 0:   
                if int(color)==int(min(y)):
                    plt.annotate(' '+str(int(split_on+color))+' or below',xy=(0,0),xytext=(0.875,inc+0.005),
                                 textcoords='axes fraction',fontname='Arial',fontsize=9,
                             color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)                 
                elif int(color)==0:
                    plt.annotate(' '+str(int(split_on-color-5))+' to '+str(int(split_on-color)),xy=(0,0),
                                 xytext=(0.875,inc+0.005),textcoords='axes fraction',fontname='Arial',fontsize=9,
                             color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)    
                else:                    
                    plt.annotate(' '+str(int(split_on+color-5))+' to '+str(int(split_on+color)),xy=(0,0),
                                 xytext=(0.875,inc+0.005),textcoords='axes fraction',fontname='Arial',fontsize=9,
                             color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)
            elif color > 0:
                if int(color)==int(max(y)):
                    plt.annotate(' '+str(int(color+split_on))+' or above',xy=(0,0),xytext=(0.875,inc+0.005),
                                 textcoords='axes fraction',fontname='Arial',fontsize=9,
                             color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)                      
    
                else:
                    plt.annotate(' '+str(int(color+split_on))+' to '+str(int(color+5+split_on)),xy=(0,0),
                                 xytext=(0.875,inc+0.005),textcoords='axes fraction',fontname='Arial',fontsize=9,
                        color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)     
            else:
                plt.annotate(' '+str(int(color+split_on)),xy=(0,0),xytext=(0.875,inc+0.005),
                             textcoords='axes fraction',fontname='Arial',fontsize=9,
                         color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)                          
            inc+=0.05
        plt.annotate('degrees\nFahrenheit',xy=(0,0), xytext = (0.85,inc+0.02),textcoords='axes fraction',
                     fontname='Arial',fontsize=9,
                    color=(100/255.0,100/255.0,100/255.0),transform = ax.transAxes)      
    if savepath:
        df_temps.to_csv(savepath+'.csv')
        plt.savefig(savepath+".png",bbox_inches='tight',transparent=True)    
    return plt  
