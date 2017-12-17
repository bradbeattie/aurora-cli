#!/usr/bin/env python3
from local_settings import IP_ADDRESS, AUTH_TOKEN, WEATHER_FILE, PANEL_CLUSTERS, logger
from nanoleaf import Aurora
from pprint import pprint
from xml.etree.ElementTree import fromstring
from xmljson import badgerfish
from utils import flatten


# Color definitions (the last value is white balance, ignored but required)
LIGHTGREY = [200, 200, 200, 0]
LIGHTBLUE = [200, 200, 255, 0]
DARKBLUE = [20, 20, 100, 0]
LIGHTYELLOW = [255, 255, 200, 0]
MAGENTA = [255, 0, 255, 0]
BLACK = [0, 0, 0, 0]


# Custom Effect Data Format as per http://forum.nanoleaf.me/docs/openapi
# Key is the forecast condition from the weather file
# Value is the panels in the panel cluster: [Panel1, Panel2, ...]
# Panel: [Timeframe1, Timeframe2, ...]
# Timeframe: [Color, duration in 100ms increments]
FORECAST_ANIMATIONS = {
    "Rain": [
        [[DARKBLUE, 30], ],
        [[DARKBLUE, 30], ],
        [[DARKBLUE, 30], ],
    ],
    "A mix of sun and cloud": [
        [[LIGHTYELLOW, 35], [LIGHTGREY, 35]],
    ],
    "Chance of showers": [
        [[LIGHTGREY,  0], [DARKBLUE, 15], [LIGHTGREY, 30]],
        [[LIGHTGREY, 15], [DARKBLUE, 15], [LIGHTGREY, 15]],
        [[LIGHTGREY, 30], [DARKBLUE, 15], [LIGHTGREY,  0]],
    ],
    "Cloudy periods": [
        [[LIGHTGREY, 35], [LIGHTBLUE, 35]],
    ],
    "Clear": [
        [[LIGHTBLUE, 35], [LIGHTYELLOW, 35]],
    ],
    "Sunny": [
        [[LIGHTYELLOW, 35], ],
    ],
}
UNKNOWN_CONDITION = [
    [[MAGENTA, 10], ],
]


try:
    # Convert the forecast into a serios of animations
    weather = badgerfish.data(fromstring(open(WEATHER_FILE).read()))["siteData"]
    animations = []
    for period in weather["forecastGroup"]["forecast"][:len(PANEL_CLUSTERS)]:
        try:
            forecast = period["abbreviatedForecast"]["textSummary"]["$"]
            logger.info(f"""{period["period"]["$"]}: {forecast}""")
            animations.append(FORECAST_ANIMATIONS[forecast])
        except Exception as e:
            logger.exception(e)
            animations.append(UNKNOWN_CONDITION)

    # Break the animations down into per-panel instructions
    anim_data = []
    for animation, cluster in zip(animations, PANEL_CLUSTERS):
        for index, panel in enumerate(cluster):
            panel_animation = animation[index % len(animation)]
            anim_data.append([panel, len(panel_animation)] + list(panel_animation))

    # Composite the instructions into an Aurora command
    aurora = Aurora(IP_ADDRESS, AUTH_TOKEN)
    effect = {
        "command": "add",
        "animName": "Forecast",
        "animType": "custom",
        "animData": " ".join(map(str, [len(anim_data)] + list(flatten(anim_data)))),
        "loop": True,
    }

    # Set the effect
    aurora.effect_set_raw(effect)

# Error handling
except Exception as e:
    logger.exception(e)
