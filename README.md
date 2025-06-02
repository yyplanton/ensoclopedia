# Analysis for a chapter on ENSO in an Encyclopedia

## Getting started
#### Install
This method uses [pip](https://pip.pypa.io/en/stable/installation/)  
Download the repository: `git clone <repo>`  
Enter the directory: `cd ensoclopedia`  
If you haven't already installed virtualenv: `pip install virtualenv`  
Create your new environment (called 'ensoclopedia'): `virtualenv ensoclopedia`  
Activate your new environment: `source ensoclopedia/bin/activate`  
Install the requirements in the current environment: `pip install -r requirements.txt`
#### Download data
To download data: `python download_data.py`  
To download the sea surface height data you need an account. Using the
[download tab](https://cds.climate.copernicus.eu/datasets/reanalysis-oras5?tab=download), you need at least 3 batches
(alternatively you can use the [API](https://cds.climate.copernicus.eu/how-to-api)):  
1) download 1980-1999
   * Product type: `Consolidated`  
   * Vertical resolution: `Single level`  
   * Variable: `Sea surface height`  
   * Year: `1980-1999`  
   * Month: `Select all`  
   Then press `Submit form`
2) download 2000-2014  
   * Product type: `Consolidated`  
   * Vertical resolution: `Single level`  
   * Variable: `Sea surface height`  
   * Year: `2000-2014`  
   * Month: `Select all`  
Then press `Submit form`
3) download 2015-2024  
   * Product type: `Operational`  
   * Vertical resolution: `Single level`  
   * Variable: `Sea surface height`  
   * Year: `2015-2024`  
   * Month: `Select all`  
Then press `Submit form`   

Then move all files to the 'data_input' directory: `mv sossheig_control_monthly_highres_2D_*_v0.1.nc ensoclopedia/data_input`

## El Niño Southern Oscillation (ENSO): leading mode of earth’s year-to-year climate fluctuations
#### Abstract
To come
#### Links
URL or DOI: to come
#### Figure 1
a) First principal pattern from an empirical orthogonal function (EOF) analysis of SST anomalies computed over 1980-2024
(linearly detrended); insert indicates the percentage of explained variance of the first five patterns.  
b) Time series of GSAT relative to 1961-1990 (12-month moving average); grey shading indicate the 95% confidence
interval, red and blue vertical shading indicate respectively El Niño and La Niña events according to the
[Climate Prediction Center](https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php).  
c) GSAT anomalies (linearly detrended) regressed on NDJ averaged Niño3.4 rSST normalized anomalies computed over
1980-2024.  
d) JJA averaged PRA (linearly detrended) relative to JJA mean climatology regressed on NDJ averaged Niño3.4 rSST
normalized anomalies computed over 1980-2024.  
e) Same as d) but using NDJ precipitations.
#### Figure 7
a) ENSO oceanic precursors regressed on NDJ averaged Niño3.4 rSST normalized anomalies computed over 1980-2024;
solid black, dashed red and dash-dotted blue lines represent respectively Niño3.4 rSSH anomalies, equatorial
Pacific rSSH anomalies and western equatorial Pacific rSSH anomalies.
#### Definitions
- Anomalies vs. normalized anomalies:
  * anomalies: monthly mean seasonal cycle removed
  * normalized anomalies: monthly mean seasonal cycle removed then divided by monthly standard deviation seasonal cycle
- Detrending:
  * linear: polynomial of degree 1 (computed using the least square fit) removed from time series
  * relative: tropic mean removed at each time step ('r' added to variable name, e.g., rSST for relative sea surface
temperature)
- Regions:
  * equatorial Pacific (EP): [5S-5N ; 120E-80W]
  * Niño3.4 (N3.4): [5S-5N ; 120-170W]
  * tropic: [20S-20N ; 0-360E]
  * western equatorial Pacific (WEP): [5S-5N ; 120E-155W]
- Seasons:
  * JJA: June-July-August average
  * NDJ: November-December-January average
- Variables:
  * global surface air temperature (GSAT) from [HadCRUT5](https://www.metoffice.gov.uk/hadobs/hadcrut5/)
  * precipitation (PR) from [GPCPv2.3](https://psl.noaa.gov/data/gridded/data.gpcp.html)
  * sea surface height (SSH) from [ORAS5](https://cds.climate.copernicus.eu/datasets/reanalysis-oras5?tab=overview)
  * sea surface temperature (SST) from [HadISST](https://www.metoffice.gov.uk/hadobs/hadisst/)
  * 'r' prefix: tropic mean removed at each time step ('r' for relative, e.g., rSST for relative sea
  surface temperature)