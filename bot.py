# imports
import numpy as np
import matplotlib.pyplot as plt
from mastodon import Mastodon
import requests
import requests
import matplotlib.cm as cm
from datetime import datetime,timedelta
import textwrap
# import API credentials
from mastodon_api_cred import *


def download_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for unsuccessful responses (4xx, 5xx)
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        print(f"Error downloading JSON: {e}")
        return None
    

def north_atlantic_plots(url='https://climatereanalyzer.org/clim/sst_daily/json/oisst2.1_natlan1_sst_day.json'):
    '''Downloads a .json file containing the North Atlantic Sea Surface Temperatures.
      makes a plot of the raw temperature data, and one for the anomaly.
      The mean, year, and current year are indicated

      Returns: todays anaomly (c)
    '''
    sst_daily_data = download_json(url)

    data = []
    dict_names = []
    for i in range(len(sst_daily_data)):
        dict_names.append(sst_daily_data[i]['name'])
        data.append(sst_daily_data[i]['data'])

    # convert data from list into nd arr
    data = np.asarray(data) # first index is year, 2nd index is day

    # Find the index of the first occurrence of 'None' in the array (days not yet passed)
    index_today = int(np.argmin(data[-4,:] != None))
    
    # Get today's date by adding the index to the start of the year (January 1st)
    start_of_year = datetime(datetime.today().year, 1, 1)
    today = start_of_year + timedelta(days=index_today)
    # Format the date to display only the date (year-month-day)
    today = today.strftime('%Y-%m-%d') # this removes the hours, minutes, seconds
    # Assuming you have the date in the format '2023-08-01'
    date_string = today 
    # Parse the date string into a datetime object
    date_obj = datetime.strptime(date_string, '%Y-%m-%d')
    # Format the datetime object to the desired format 'August 1st, 2023'
    today = date_obj.strftime('%B %d, %Y')

    # Convert 'None' values to 'nan'
    data[data == None] = np.nan


    # lets make some plots!
    # Raw Temps
    colormap = cm.get_cmap('Blues')
    norm = plt.Normalize(vmin=0 +1981, vmax=np.shape(data)[0] + 1981)

    plt.figure(figsize=(12,6))
    for i in range(np.shape(data)[0]):
        if sst_daily_data[i]['name'] != '1982-2011 mean':
            if sst_daily_data[i]['name'] != 'plus 2σ':
                if sst_daily_data[i]['name'] != 'minus 2σ':
                    color = colormap(norm(i +1981))
                    plt.plot(data[i, :], color=color, linewidth=2)
    plt.plot(data[-4, :], color='red', label=dict_names[-4], linewidth=2)
    plt.plot(data[-3,:], color='k', linestyle='--', linewidth =3, label='1982-2011 Mean',)
    plt.ylabel('Temperature (°C)', size=15)
    plt.xlabel('Day of Year', size=15)
    plt.grid(axis='y')
    plt.title('Daily North Atlantic (0-60N) Sea Surface Temperature (SST)\n' +str(today), size=15)
    plt.legend(fontsize=15)
    sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, )

     # Create the caption text
    data_source = '©Maxwell A. Fine, Data Source: NOAA Optimum Interpolation SST (OISST) dataset version 2.1'
    data_origin = 'Through https://climatereanalyzer.org/clim/sst_daily/, Climate Change Institute University of Maine.'
    data_up_to = f'Data up to {today}'
    caption_text = '\n'.join(textwrap.wrap(data_source + '\n' + data_origin + '\n' + data_up_to, width=120))

    # Add the caption to the figure

    plt.figtext(0.1, -0.01, caption_text, fontsize=10, ha='left', va='center', alpha=0.5, bbox=dict(facecolor='None', edgecolor='None'))
    plt.tight_layout()
    plt.savefig('NA_SSTA', dpi=300,bbox_inches='tight')


    # anomaly
    plt.figure(figsize=(12,6))

    # use included mean from data
    for i in range(np.shape(data)[0]):
        if sst_daily_data[i]['name'] != '1982-2011 mean':
            if sst_daily_data[i]['name'] != 'plus 2σ':
                if sst_daily_data[i]['name'] != 'minus 2σ':
                    color = colormap(norm(i +1981))
                    plt.plot(data[i, :]- data[-3,:], color=color, linewidth=2)
    plt.plot(data[-4, :] - data[-3,:], color='red', label=dict_names[-4], linewidth=2)
    plt.plot(data[-3,:]-data[-3,:], color='k', linestyle='--', linewidth =3, label='1982-2011 Mean',)
    plt.ylabel('Anomaly(°C)', size=15)
    plt.xlabel('Day of Year', size=15)
    plt.grid(axis='y')
    plt.title('Daily North Atlantic (0-60N) Sea Surface Temperature Anomaly (SSTA)\n' +str(today), size=15)

    plt.legend(fontsize=15)
    sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, )

    # Add the caption to the figure

    plt.figtext(0.1, -0.01, caption_text, fontsize=10, ha='left', va='center', alpha=0.5, bbox=dict(facecolor='None', edgecolor='None'))
    plt.tight_layout()
    plt.savefig('NA_SSTA_anomaly', dpi=300,bbox_inches='tight')

    
    return data[-4,index_today-1] - data[-3,index_today-1] # todays anaomly



    


# bot's actions functions
def post(message):
    mastodon.toot(message)

def reply_to_mentions():
    mentions = mastodon.notifications()
    for mention in mentions:
        if mention['type'] == 'mention':
            toot(f'@{mention["account"]["username"]} Thanks for mentioning me!')


def main():
    # Create a Mastodon object
    mastodon = Mastodon(client_id=client_id, client_secret=client_secret, access_token=access_token, api_base_url=instance_url)

    # download data, and make plots
    todays_anomaly = north_atlantic_plots()

    # Prepare post
    temperature_anomaly = f"{todays_anomaly:.2f}°C"
    data_source = "https://climatereanalyzer.org/clim/sst_daily/"  

    post_str = (
    f"🌏🔥🌡️: Today's North Atlantic Sea Surface Temperature Anomaly is {temperature_anomaly} above the 1982-2011 mean.\n"
    f"\nData source: {data_source}\n"
    "\n#ClimateChange #DataAnalysis #ClimateAwareness #globalwarming #science #climate #collapse" )


    # Upload images and get media IDs
    media_ids = [mastodon.media_post('NA_SSTA.png'), mastodon.media_post('NA_SSTA_anomaly.png')]

    # Post the toot with the caption and media IDs
    mastodon.status_post(post_str, media_ids=media_ids)


if __name__ == "__main__":
    main()
