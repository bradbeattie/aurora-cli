#!/usr/bin/env python3
from local_settings import IP_ADDRESS, AUTH_TOKEN, WEATHER_FILE, PANEL_CLUSTERS, logger
from nanoleaf import Aurora
from xml.etree.ElementTree import fromstring
from xmljson import badgerfish
from utils import flatten, hsl_to_rgbw

# Constants
DURATION_IN_SECONDS = 10
RAIN = hsl_to_rgbw(.7, .6, .3)
SUN = hsl_to_rgbw(.2, .6, .6)
CLEARNIGHT = hsl_to_rgbw(.2, .6, .6)
CLOUD = hsl_to_rgbw(0, 0, .6)
SNOW = hsl_to_rgbw(.5, .6, .6)


# Custom Effect Data Format as per http://forum.nanoleaf.me/docs/openapi
# Key is the forecast condition from the weather file
# Value is the panels in the panel cluster: [Panel1, Panel2, ...]
# Panel: [Timeframe1, Timeframe2, ...]
# Timeframe: [Color, duration in 100ms increments]
# Dict keys as per https://weather.gc.ca/weathericons/<XX>.gif
FORECAST_ANIMATIONS = {
    6: [
        [[RAIN, 0.3], [CLOUD, 0.3], [CLOUD, 0.3]],
        [[CLOUD, 0.3], [RAIN, 0.3], [CLOUD, 0.3]],
        [[CLOUD, 0.3], [CLOUD, 0.3], [RAIN, 0.3]],
    ],
    15: [
        [[SNOW, 0.3], [RAIN, 0.3], [RAIN, 0.3]],
        [[RAIN, 0.3], [SNOW, 0.3], [RAIN, 0.3]],
        [[RAIN, 0.3], [RAIN, 0.3], [SNOW, 0.3]],
    ],
    0: [
        [[SUN, 1.0]],
    ],
    30: [
        [[CLEARNIGHT, 1.0]],
    ],
    32: [
        [[RAIN, 0.3], [CLEARNIGHT, 0.3], [CLEARNIGHT, 0.3]],
        [[CLEARNIGHT, 0.3], [RAIN, 0.3], [CLEARNIGHT, 0.3]],
        [[CLEARNIGHT, 0.3], [CLEARNIGHT, 0.3], [RAIN, 0.3]],
    ],
    12: [
        [[RAIN, 1.0]],
    ],
}
UNKNOWN_CONDITION = [
    [[[255, 0, 255, 0], 1.0]],
]


try:
    # Convert the forecast into a serios of animations
    weather = badgerfish.data(fromstring(open(WEATHER_FILE).read()))["siteData"]
    animations = []
    for period in weather["forecastGroup"]["forecast"]:
        try:
            forecast = period["abbreviatedForecast"]["iconCode"]["$"]
            logger.info(f"""{period["period"]["$"]}: {period["abbreviatedForecast"]["textSummary"]["$"]} ({period["abbreviatedForecast"]["iconCode"]["$"]})""")
            animations.append(FORECAST_ANIMATIONS[forecast])
        except Exception as e:
            logger.exception(e)
            animations.append(UNKNOWN_CONDITION)

    # Break the animations down into per-panel instructions
    anim_data = []
    for animation, cluster in zip(animations, PANEL_CLUSTERS):
        for index, panel in enumerate(cluster):
            panel_animation = [
                frame[0] + [round(frame[1] * DURATION_IN_SECONDS * 10)]
                for frame in animation[len(anim_data) % len(animation)]
            ]
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
