# ClimateChangeBot

<a rel="me" href="https://bsky.app/profile/climate-change-bot.bsky.social">@ClimateChangeBot</a> is a **Blue Sky bot** that posts daily North Atlantic Sea Surface Temperature (SST) and Antarctic Sea Ice Extent plots. It provides valuable insights into the changing climate and the impact on sea surface temperatures in the North Atlantic region as well as sea ice extent in the Antarctic.

The bot now runs **from a Docker container**! Making maintence eaiser. 

## Features
* Daily North Atlantic Sea Surface Temperature (SST) plots.
  * Two plots: Raw temperature data and Anomaly.
  * Captions with data source, origin, and date.
  * Informative hashtags for climate enthusiasts.
* Daily Antarctic Sea Ice Extent plots.
  * Two plots: Raw extent and Anomaly.
  * Captions with data source, origin, and date.
  * Informative hashtags for climate enthusiasts.

## Credits
* **North Atlantic Data**:
  * Data Source: NOAA Optimum Interpolation SST (OISST) dataset version 2.1.
  * Data Provided by: <a href="https://climatereanalyzer.org/clim/sst_daily/json/oisst2.1_natlan1_sst_day.json">ClimateReanalyzer</a>, Climate Change Institute, University of Maine.
* **Antarctic Sea Ice Data**:
  * Data Source: NOAA Sea Ice Index developed by the National Snow and Ice Data Center (NSIDC)
  * Access via: [NSIDC CSV](https://noaadata.apps.nsidc.org/NOAA/G02135/south/daily/data/S_seaice_extent_daily_v4.0.csv)

## Next Steps
- Add automatic bot replies to mentions on Blue Sky.
- Find more photogenic climate data to make daily posts from.

## Deployment
* Runs as a **Docker container** for easy setup and reliable execution.
* Dockerfile included for local deployment or cloud hosting.

## Contact
If you have any questions or feedback, please contact **Maxwell A. Fine**:

- Website: https://afinemax.github.io/afinemax1/  
- GitHub: https://github.com/afinemax  
- Email: afinemax@gmail.com  

## Disclaimer
- ClimateChangeBot is an educational project and does not provide real-time or official climate data. The data provided is for educational and awareness purposes only.

