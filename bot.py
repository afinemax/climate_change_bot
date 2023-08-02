#!/usr/bin/env python3
# imports
print('made it here!')
import numpy as np
import matplotlib.pyplot as plt
from mastodon import Mastodon
import requests
import requests
import matplotlib.cm as cm
from datetime import datetime,timedelta,date
import textwrap
import time
import io
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
    plt.plot(data[-4, :], color='red', label=dict_names[-4], linewidth=3)
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
    plt.close()


    # anomaly
    plt.figure(figsize=(12,6))

    # use included mean from data
    for i in range(np.shape(data)[0]):
        if sst_daily_data[i]['name'] != '1982-2011 mean':
            if sst_daily_data[i]['name'] != 'plus 2σ':
                if sst_daily_data[i]['name'] != 'minus 2σ':
                    color = colormap(norm(i +1981))
                    plt.plot(data[i, :]- data[-3,:], color=color, linewidth=2)
    plt.plot(data[-4, :] - data[-3,:], color='red', label=dict_names[-4], linewidth=3)
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
    plt.close()

    
    return data[-4,index_today-1] - data[-3,index_today-1] # todays anaomly

def antartic_sea_ice_plot(reorganized_data, mean_extent_per_day, std_extent_per_day):
    '''takes in nicely formatted antartic sea ice data, and makes plots. returns todays anomaly, and todays std''' 

    today = date.today()
    # Format the date to display only the date (year-month-day)
    today = today.strftime('%Y-%m-%d') # this removes the hours, minutes, seconds
    # Assuming you have the date in the format '2023-08-01'
    date_string = today 
    # Parse the date string into a datetime object
    date_obj = datetime.strptime(date_string, '%Y-%m-%d')
    # Format the datetime object to the desired format 'August 1st, 2023'
    today = date_obj.strftime('%B %d, %Y')
    # Get the current date and time
    current_datetime = datetime.now()
    # Extract the year from the current date and time as a string
    current_year_str = current_datetime.strftime('%Y')

    # lets plot!
    plt.figure(figsize=(12,6))
    colormap = cm.get_cmap('Blues')
    norm = plt.Normalize(vmin=0 +1981, vmax=np.shape(reorganized_data)[0]+1981)

    for i in range(np.shape(reorganized_data)[0]):
        color = colormap(norm(i + 1981))
        plt.plot(reorganized_data[i,:], color=color, linewidth=2)

    plt.plot(reorganized_data[-1,:], color='red', label=current_year_str, linewidth=3)
    plt.plot(mean_extent_per_day, color='k', linestyle='--', label='1981-2010 Mean', linewidth=3)
    plt.ylabel('Extent (millions of square kilometers)', size=15)
    plt.xlabel('Day of Year', size=15)
    plt.grid(axis='y')
    plt.title('Antartic Sea Ice Extent ' +str(today) +'\n (Area of Ocean with at least 15% sea ice)', size=15)
    plt.legend(fontsize=15)
    sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, )

    # Create the caption text
    data_source = '©Maxwell A. Fine, Data Source: The NOAA Sea Ice Index developed by the National Snow and Ice Data Center (NSIDC)'
    data_origin = 'Through https://noaadata.apps.nsidc.org/NOAA/G02135/south/daily/data/S_seaice_extent_daily_v3.0.csv, University of Colorado Boulder'
    data_up_to = f'Data up to {today}'
    caption_text = '\n'.join(textwrap.wrap(data_source + '\n' + data_origin + '\n' + data_up_to, width=120))

    # Add the caption to the figure

    plt.figtext(0.1, -0.01, caption_text, fontsize=10, ha='left', va='center', alpha=0.5, bbox=dict(facecolor='None', edgecolor='None'))
    plt.tight_layout()
    plt.savefig('antartic_ice', dpi=300,bbox_inches='tight')
    plt.close()


    #anaomly
    plt.figure(figsize=(12,6))
    colormap = cm.get_cmap('Blues')
    norm = plt.Normalize(vmin=0 +1981, vmax=np.shape(reorganized_data)[0]+1981)

    for i in range(np.shape(reorganized_data)[0]):
        color = colormap(norm(i + 1981))
        plt.plot(reorganized_data[i,:]-mean_extent_per_day, color=color, linewidth=2)

    plt.plot(reorganized_data[-1,:]-mean_extent_per_day, color='red', label=current_year_str, linewidth=3)
    plt.plot(mean_extent_per_day-mean_extent_per_day, color='k', linestyle='--', label='1981-2010 Mean', linewidth=3)
    plt.ylabel('Anomaly (millions of square kilometers)', size=15)
    plt.xlabel('Day of Year', size=15)
    plt.grid(axis='y')
    plt.title('Antartic Sea Ice Anomaly ' +str(today), size=15)
    plt.legend(fontsize=15)
    sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, )

    # Create the caption text
    data_source = '©Maxwell A. Fine, Data Source: The NOAA Sea Ice Index developed by the National Snow and Ice Data Center (NSIDC)'
    data_origin = 'Through https://noaadata.apps.nsidc.org/NOAA/G02135/south/daily/data/S_seaice_extent_daily_v3.0.csv, University of Colorado Boulder'
    data_up_to = f'Data up to {today}'
    caption_text = '\n'.join(textwrap.wrap(data_source + '\n' + data_origin + '\n' + data_up_to, width=120))

    # Add the caption to the figure

    plt.figtext(0.1, -0.01, caption_text, fontsize=10, ha='left', va='center', alpha=0.5, bbox=dict(facecolor='None', edgecolor='None'))
    plt.tight_layout()
    plt.savefig('antartic_ice_anomaly', dpi=300,bbox_inches='tight')
    plt.close()

    nan_indices = np.where(np.isnan(reorganized_data[-1,:]))

    index_today = np.min(nan_indices)-1

    today_anomaly= reorganized_data[-1,index_today] - mean_extent_per_day[index_today]
    today_std = today_anomaly / std_extent_per_day[index_today]
    return today_anomaly, today_std


def download_csv_as_numpy_with_column_names(csv_url, usecols=None, skip_header=0):
    '''downloads csv data from url'''
    try:
        # Send a GET request to download the content of the .csv file
        response = requests.get(csv_url)

        # Check if the request was successful (status code 200 means success)
        if response.status_code == 200:
            # Get the content of the .csv file as a string
            csv_content = response.text

            # Split the content into lines
            lines = csv_content.splitlines()

            # Extract the header row (assumed to be the first row)
            column_names = lines[0].split(',')

            # Convert the string content into a NumPy array, skipping the header row
            numpy_array = np.genfromtxt(io.StringIO('\n'.join(lines[skip_header:])), delimiter=',', usecols=usecols)
            
            return column_names, numpy_array
        else:
            print(f"Failed to download the .csv file from URL: {csv_url}")
            print(f"Status Code: {response.status_code}")
            print(f"Response Content: {response.content}")
            return None, None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None, None


def get_antartic_ice_data(csv_url, usecols, skip_header):
    '''Download and reorganize .csv data for the antartic sea ice extent
    
    Returns:
    reorganized_data: arrary,
                      nicely formatted numpy array for sea ice extent
    mean_extent_per_day: array,
                         1981-2010 mean
    std_extent_per_day:  array
                         1981-2010 std'''


    column_names, csv_data = download_csv_as_numpy_with_column_names(csv_url, usecols=usecols, skip_header=skip_header)

    if column_names is not None and csv_data is not None:

        # Extract the 'Year', 'Month', 'Day', and 'Extent' columns
        years = csv_data[:, 0].astype(int)
        months = csv_data[:, 1].astype(int)
        days = csv_data[:, 2].astype(int)
        extents = csv_data[:, 3]

        # Find the unique years and their corresponding lengths
        unique_years, year_counts = np.unique(years, return_counts=True)

        # Find the maximum number of days for any year in the dataset
        max_days_in_year = np.max(year_counts)

        # Create the 2D NumPy array with missing data as NaN values
        reorganized_data = np.full((len(unique_years), max_days_in_year), np.nan)

        # Create a dictionary to map years to their indices in reorganized_data
        year_index_map = {year: i for i, year in enumerate(unique_years)}

        for year, month, day, extent in zip(years, months, days, extents):
            # Check if year is 1981 or later
            if year >= 1981:
                # Check if month and day are valid
                if 1 <= month <= 12 and 1 <= day <= 31:
                    try:
                        # Convert year, month, and day to a datetime object
                        date_object = datetime(year, month, day)

                        # Get the day difference between the current date and the first day of the year
                        day_index = (date_object - datetime(year, 1, 1)).days

                        reorganized_data[year_index_map[year], day_index] = extent
                    except ValueError:
                        # Invalid date encountered, skip this data point
                        pass
                else:
                    # Invalid month or day value encountered, skip this data point
                    pass



    # Calculate the mean values and standard deviations along the axis of years (rows)
    year_index_2010 = year_index_map.get(2010)
    mean_extent_per_day = np.nanmean(reorganized_data[:year_index_2010], axis=0)
    std_extent_per_day = np.nanstd(reorganized_data[:year_index_2010], axis=0)
    return reorganized_data, mean_extent_per_day, std_extent_per_day 


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

    # north atlantic 
    # download data, and make plots
    todays_anomaly = north_atlantic_plots()

    # Prepare post
    temperature_anomaly = f"{todays_anomaly:.2f}°C"
    data_source = "https://climatereanalyzer.org/clim/sst_daily/"  
    post_str = (
    f"🌏🔥🌡️: Today's North Atlantic Sea Surface Temperature Anomaly is {temperature_anomaly} above the 1982-2011 mean.\n"
    f"\nData source: {data_source}\n"
    "\n#ClimateChange #DataAnalysis #ClimateAwareness #globalwarming #science #climate #collapse #environment" )
    
    # Upload images and get media IDs
    media_ids = [mastodon.media_post('NA_SSTA.png'), mastodon.media_post('NA_SSTA_anomaly.png')]

    # Post the toot with the caption and media IDs
    mastodon.status_post(post_str, media_ids=media_ids)

    # make new mastodon instance 
    mastodon = Mastodon(client_id=client_id, client_secret=client_secret, access_token=access_token, api_base_url=instance_url)
    # antartic sea ice data
    # Specify the columns you want to extract ('Year', 'Month', 'Day', 'Extent')
    usecols = (0, 1, 2, 3)
    # Skip the header row (row 0 in the .csv file)
    skip_header = 2
    csv_url = 'https://noaadata.apps.nsidc.org/NOAA/G02135/south/daily/data/S_seaice_extent_daily_v3.0.csv'

    reorganized_data, mean_extent_per_day, std_extent_per_day  = get_antartic_ice_data(csv_url, usecols, skip_header)
    antartic_today_anomaly, antartic_today_std = antartic_sea_ice_plot(reorganized_data, mean_extent_per_day, std_extent_per_day)
    
    # Prepare post
    antartic_anomaly = f"{antartic_today_anomaly:.2f} Millions of Square Kilometers"
    antartic_std = f"{antartic_today_std:.2f}"
    data_source = "https://nsidc.org/home"  
    post_str = (
    f"🌏🇦🇶🔥: Today's Antartica Sea Ice Anomaly is {antartic_anomaly} ({antartic_std}σ) above the 1981-2010 mean.\n"
    f"\nData source: {data_source}\n"
    "\n#ClimateChange #DataAnalysis #ClimateAwareness #globalwarming #science #climate #collapse #environment" )
    
    # Upload images and get media IDs
    print('made it to almost end')
    media_ids = [mastodon.media_post('antartic_ice.png'), mastodon.media_post('antartic_ice_anomaly.png')]

    # Post the toot with the caption and media IDs
    mastodon.status_post(post_str, media_ids=media_ids)

if __name__ == "__main__":
    main()
