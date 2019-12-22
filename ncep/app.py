from flask import Flask
from flask import render_template
import io
import base64

app = Flask(__name__)


#@app.route('/')
#def hello():

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

    #return render_template('index.html', plt=myimg)


'''
map compare average temps
'''
@app.route('/')
def hello():

    fname1 = 'average_temps'
    date_starta = datetime(2019,1,29).date() #provide a valid start date YYYY, (M)M, (D)D
    date_enda = datetime(2019,2,2).date()  #provide a valid start date YYYY, (M)M, (D)D
    plt_average_temps = ncep_mapping.map_average_temps(date_starta, date_enda, '',
                                          split_on = 55,how='state',legend=True,savepath=False)
    #plt_average_temps.show()
    imga = io.BytesIO()
    plt_average_temps.savefig(imga, format='png')
    imga.seek(0)

    plot_url_avg = base64.b64encode(imga.getvalue()).decode()


    fname2 = 'compare_average_temps'
    savepath = True
    date_start = datetime(2018,1,1).date()
    date_end = datetime(2018,1,1).date()
    date_start_compare = datetime(2014,1,7).date()
    date_end_compare = datetime(2014,1,7).date()
    plt_compare = ncep_mapping.map_compare_average_temps(date_start, date_end, date_start_compare, date_end_compare,
                    '', how='stcd',legend = True)
    #plt_compare.show()


    img = io.BytesIO()
    plt_compare.savefig(img, format='png')
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()


    #myimg = '<img src="data:image/png;base64,{}">'.format(plot_url)
    return '<h3><a href="https://github.com/jason-upchurch/ncep/">https://github.com/jason-upchurch/ncep/develop/ncep</a></h3> \
           <p style="float:left; width:50%; text-align:center">{} to {} </p> \
           <p style="float:left; width:50%; text-align:center">{} to {} \
           <br> Compared to: \
           <br> {} to {}\
           </p> \
           <img src="data:image/png;base64,{}" style="border: 2px solid #ccc; width: 45%; padding-right: 25px;border-radius: 6px;float:left"> \
           <img src="data:image/png;base64,{}" style="border: 2px solid #ccc; width: 45%; padding-right: 25px;border-radius: 6px;">'.format(date_starta, date_enda, date_start, date_end, date_start_compare, date_end_compare,plot_url_avg, plot_url)
    #return render_template('index.html', plt=myimg)



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
#                             '', how='state', legend = True, savepath=False)
# plt_depart_from_normal.show()



'''
advanced: get range of heating degree days for state (illustrates interaction with
          ncep_util module
'''
# fname4 = 'default'
# date_start = datetime(2016,1,1).date()
# date_end = datetime(2016,12,31).date()
# HDD_FNAME_STATE = 'StatesCONUS.Heating.txt'
# hdd = ncep_util.retrieve_range(HDD_FNAME_STATE, date_start, date_end, '')
# hdd.to_csv(path+fname4)


if __name__ == '__main__':
    app.run(threaded=True, debug = True)
