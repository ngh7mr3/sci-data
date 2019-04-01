# sci-data
Simple parser for solar and Earth's magnetic sci data

## Data source
[SPACE WEATHER PREDICTION CENTER](https://www.swpc.noaa.gov/)

[IZMIRAN](http://forecast.izmiran.rssi.ru/)

## Requirements
Python 3.4+

## Usage
```shell 
$ main.py DD/MM/YYYY DURATION
```
DD/MM/YYYY – start date for search

## Output
CSV file "DD_MM_YYYY_+DURATION.csv"

## File structure
|Hour from start|Proton Density|Bulk Speed|IMFV Bx|IMFV By|IMFV Bz|Earth Bx|Earth By|Earth Bz|
|---|---|---|---|---|---|---|---|---|
|Providers|SWEPAM|SWEPAM|Mag|Mag|Mag|IZMIRAN|IZMIRAN|IZMIRAN|
|Measurements|p/cc|km/s|nT|nT|nT|nT|nT|nT|
