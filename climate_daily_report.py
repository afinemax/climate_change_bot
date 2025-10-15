#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import requests
import textwrap
from datetime import datetime, timedelta, date
import io

from dotenv import load_dotenv
load_dotenv()

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# -------------------- DATA DOWNLOAD -------------------- #
def download_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error downloading JSON: {e}")
        return None


def download_csv_as_numpy_with_column_names(csv_url, usecols=None, skip_header=0):
    try:
        response = requests.get(csv_url)
        response.raise_for_status()
        csv_content = response.text
        lines = csv_content.splitlines()
        column_names = lines[0].split(',')
        numpy_array = np.genfromtxt(io.StringIO('\n'.join(lines[skip_header:])), delimiter=',', usecols=usecols)
        return column_names, numpy_array
    except Exception as e:
        print(f"Error downloading CSV: {e}")
        return None, None


# -------------------- NORTH ATLANTIC SST -------------------- #
def make_na_sst_plot(url='https://climatereanalyzer.org/clim/sst_daily/json_2clim/oisst2.1_natlan_sst_day.json'):
    data_json = download_json(url)
    if data_json is None:
        return None

    data = np.array([d['data'] for d in data_json])
    names = [d['name'] for d in data_json]

    data[data == None] = np.nan

    # Today's index → the most recent non-NaN value
    # Safely convert to float (invalid entries become np.nan)
    row = np.array(data[-4, :], dtype=float)

    # Now this works fine:
    valid_indices = np.where(~np.isnan(row))[0]

    if len(valid_indices) > 0:
        index_today = valid_indices[-1]
    else:
        index_today = None

    print(f'index_today: {index_today}')
        # Really the most recent
   # index_today = int(np.argmin(data[-4, :] != None)) # this is 0 which is wrong tis really ~ october 
    start_of_year = datetime(datetime.today().year, 1, 1)

    # Print index

    today = datetime.today().strftime('%B %d %Y')

    # Colormap
    colormap = plt.colormaps['Blues']
    norm = plt.Normalize(vmin=1981, vmax=np.shape(data)[0] + 1981)

    # --- Raw SST ---
    fig, ax = plt.subplots(figsize=(12, 6))
    for i, name in enumerate(names):
        if name not in ['1982-2011 mean', 'plus 2σ', 'minus 2σ', 'Preliminary', '1982-2010', '1991-2020']:
            ax.plot(data[i, :], color=colormap(norm(i + 1981)), linewidth=2)

        if name == '1982-2010':
            data_mean = data[i,:]
    ax.plot(data[-4, :], color='red', label=names[-4], linewidth=3)
    ax.plot(data_mean, color='k', linestyle='--', label='1982-2010 Mean', linewidth=3)

    ax.set_title(f"North Atlantic SST ({today})", size=15)
    ax.set_xlabel("Day of Year", size=15)
    ax.set_ylabel("Temperature (°C)", size=15)
    ax.grid(axis='y')
    ax.legend(fontsize=12)

    # Colorbar
    sm = cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax)

    # Caption
    caption = (
        "©Maxwell A. Fine\n"
        "Data Source: NOAA OISST 2.1 via https://climatereanalyzer.org/clim/sst_daily/\n"
        f"Data up to {today}"
    )
    fig.text(0.1, -0.01, caption, fontsize=10, ha='left', va='center', alpha=0.5)

    raw_path = os.path.join(OUTPUT_DIR, "NA_SST.png")
    plt.tight_layout()
    plt.savefig(raw_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    # --- SST Anomaly ---
    fig, ax = plt.subplots(figsize=(12, 6))
    for i, name in enumerate(names):
        if name not in ['1982-2011 mean', 'plus 2σ', 'minus 2σ', 'Preliminary', '1982-2010', '1991-2020']:
            ax.plot(data[i, :] - data_mean, color=colormap(norm(i + 1981)), linewidth=2)
    ax.plot(data[-4, :] - data_mean, color='red', label=names[-4], linewidth=3)
    ax.plot(data_mean - data_mean, color='k', linestyle='--', label='1982-2010 Mean', linewidth=3)

    ax.set_title(f"North Atlantic SST Anomaly ({today})", size=15)
    ax.set_xlabel("Day of Year", size=15)
    ax.set_ylabel("Anomaly (°C)", size=15)
    ax.grid(axis='y')
    ax.legend(fontsize=12)

    sm = cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax)

    fig.text(0.1, -0.01, caption, fontsize=10, ha='left', va='center', alpha=0.5)

    anomaly_path = os.path.join(OUTPUT_DIR, "NA_SST_anomaly.png")
    plt.tight_layout()
    plt.savefig(anomaly_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Markdown caption
    today_val =data[-4:][:, index_today][0]
    anomaly_val = today_val - data_mean[index_today]
    social_caption = (
        f"🌏🔥🌡️: Today's North Atlantic Sea Surface Temperature Anomaly is {anomaly_val:.2f}°C above the 1982–2010 mean.\n\n"
        "#ClimateChange #NorthAtlantic #SST #GlobalWarming #greenhouse #science #dataanalysis " 
    )

    # Markdown caption
    md_path = os.path.join(OUTPUT_DIR, "NA_SST.md")
    with open(md_path, "w") as f:
        f.write(f"{social_caption}\n\n")

    return anomaly_val, social_caption, md_path


# -------------------- ANTARCTIC SEA ICE -------------------- #
def get_antartic_ice_data(csv_url, usecols=(0, 1, 2, 3), skip_header=2):
    columns, csv_data = download_csv_as_numpy_with_column_names(csv_url, usecols, skip_header)
    if csv_data is None:
        return None, None, None

    years, months, days, extents = csv_data[:, 0].astype(int), csv_data[:, 1].astype(int), csv_data[:, 2].astype(int), csv_data[:, 3]
    unique_years = np.unique(years)
    max_days = max(np.bincount(years - unique_years[0]))
    data_arr = np.full((len(unique_years), max_days), np.nan)
    year_map = {year: i for i, year in enumerate(unique_years)}

    for y, m, d, e in zip(years, months, days, extents):
        if y >= 1981:
            try:
                day_index = (datetime(y, m, d) - datetime(y, 1, 1)).days
                data_arr[year_map[y], day_index] = e
            except:
                pass

    year_index_2010 = year_map.get(2010, -1)
    mean_extent = np.nanmean(data_arr[:year_index_2010], axis=0)
    std_extent = np.nanstd(data_arr[:year_index_2010], axis=0)
    return data_arr, mean_extent, std_extent


def make_antartic_ice_plot(reorganized_data, mean_extent_per_day, std_extent_per_day):
    today = date.today().strftime('%B %d, %Y')
    colormap = plt.colormaps['Blues']
    norm = plt.Normalize(vmin=1981, vmax=np.shape(reorganized_data)[0] + 1981)

    # --- Raw ---
    fig, ax = plt.subplots(figsize=(12, 6))
    for i in range(np.shape(reorganized_data)[0]):
        ax.plot(reorganized_data[i, :], color=colormap(norm(i + 1981)), linewidth=2)
    ax.plot(reorganized_data[-1, :], color='red', linewidth=3, label=str(datetime.today().year))
    ax.plot(mean_extent_per_day, color='k', linestyle='--', label='1981-2010 Mean', linewidth=3)

    ax.set_title(f"Antarctic Sea Ice Extent ({today})", size=15)
    ax.set_xlabel("Day of Year", size=15)
    ax.set_ylabel("Extent (millions km²)", size=15)
    ax.grid(axis='y')
    ax.legend(fontsize=12)
    sm = cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax)

    raw_path = os.path.join(OUTPUT_DIR, "antartic_ice.png")
    plt.tight_layout()
    plt.savefig(raw_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    # --- Anomaly ---
    fig, ax = plt.subplots(figsize=(12, 6))
    for i in range(np.shape(reorganized_data)[0]):
        ax.plot(reorganized_data[i, :] - mean_extent_per_day, color=colormap(norm(i + 1981)), linewidth=2)
    ax.plot(reorganized_data[-1, :] - mean_extent_per_day, color='red', linewidth=3, label=str(datetime.today().year))
    ax.plot(np.zeros_like(mean_extent_per_day), color='k', linestyle='--', label='1981-2010 Mean', linewidth=3)

    ax.set_title(f"Antarctic Sea Ice Anomaly ({today})", size=15)
    ax.set_xlabel("Day of Year", size=15)
    ax.set_ylabel("Anomaly (millions km²)", size=15)
    ax.grid(axis='y')
    ax.legend(fontsize=12)
    sm = cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax)

    anomaly_path = os.path.join(OUTPUT_DIR, "antartic_ice_anomaly.png")
    plt.tight_layout()
    plt.savefig(anomaly_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


    nan_indices = np.where(np.isnan(reorganized_data[-1, :]))
    index_today = np.min(nan_indices) - 1
    today_anomaly = reorganized_data[-1, index_today] - mean_extent_per_day[index_today]
    today_std = today_anomaly / std_extent_per_day[index_today]

    social_caption = (
        f"🌏🇦🇶🔥: Today's Antarctic Sea Ice Anomaly is {today_anomaly:.2f} Million Square Kilometers "
        f"({today_std:.2f}σ) above the 1981–2010 mean.\n\n"
        "#ClimateCrisis #SeaIce #Antarctica #Greenhouse #science #dataanalysis"
    )

    # Markdown
    md_path = os.path.join(OUTPUT_DIR, "antartic_ice.md")
    with open(md_path, "w") as f:
        f.write(f"{social_caption}\n\n")

    return today_anomaly, today_std, raw_path, anomaly_path, md_path, social_caption


# -------------------- MAIN -------------------- #
def main():
    print("Generating North Atlantic SST plots...")
    na_anomaly, na_caption, na_md_path = make_na_sst_plot()
    print(f"Today's NA SST anomaly: {na_anomaly:.2f} °C")
    print(na_caption)

    print("Generating Antarctic Sea Ice plots...")
    csv_url = "https://noaadata.apps.nsidc.org/NOAA/G02135/south/daily/data/S_seaice_extent_daily_v4.0.csv"
    
    reorganized_data, mean_extent, std_extent = get_antartic_ice_data(csv_url)
    ant_anomaly, ant_std, raw_path, anom_path, ant_md_path, ant_caption = make_antartic_ice_plot(
        reorganized_data, mean_extent, std_extent
    )
    print(f"Today's Antarctic anomaly: {ant_anomaly:.2f} M km² ({ant_std:.2f}σ)")
    print(ant_caption)

    print(f"\nMarkdown saved to:\n- {na_md_path}\n- {ant_md_path}")
    print("\nAll plots and captions saved in ./output")


if __name__ == "__main__":
    main()
 
