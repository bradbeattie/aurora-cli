#!/usr/bin/env python3
from pprint import pprint
from xml.etree.ElementTree import fromstring
from local_settings import WEATHER_FILE, logger
from xmljson import badgerfish


# The WEATHER_FILE content is populated via an hourly cronjob from weather.gc.ca.
# Example:
#     curl -s http://dd.weather.gc.ca/citypage_weather/xml/BC/s0000141_e.xml > weather.html


try:
    weather = badgerfish.data(fromstring(open(WEATHER_FILE).read()))["siteData"]
    pprint(weather, width=200)

# Error handling
except Exception as e:
    logger.exception(e)
