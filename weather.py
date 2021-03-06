#!/usr/bin/env python3
from local_settings import IP_ADDRESS, AUTH_TOKEN, WEATHER_CITY, WEATHER_PROVINCE, PANEL_CLUSTERS, logger
from nanoleaf import Aurora
from utils_generic import flatten, hsl_to_rgbw
from utils_specific import get_canadian_weather


# Constants
DURATION_IN_SECONDS = 12
RAIN = hsl_to_rgbw(.7, .9, .5)
SUN = hsl_to_rgbw(.145, .9, .5)
CLEARNIGHT = hsl_to_rgbw(.7, 0, 0)
CLOUD = hsl_to_rgbw(0, 0, .5)
SNOW = hsl_to_rgbw(.5, .5, .5)
FOG = hsl_to_rgbw(.4, .9, .5)


# Custom Effect Data Format as per http://forum.nanoleaf.me/docs/openapi
# Key is the forecast condition from the weather file
# Value is the panels in the panel cluster: [Panel1, Panel2, ...]
# Panel: [Timeframe1, Timeframe2, ...]
# Timeframe: [Color, duration in 100ms increments]
# Dict keys as per https://weather.gc.ca/weathericons/<XX>.gif
def rotate(*args):
    augmented = [
        [arg, 1.0 / len(args)]
        for arg in args
    ]
    return [
        augmented[-n:] + augmented[:-n]
        for n in range(len(args))
    ]
FORECAST_ANIMATIONS = {
    0: rotate(SUN),
    1: rotate(SUN, SUN, CLOUD),
    2: rotate(SUN, SUN, CLOUD),
    3: rotate(CLOUD, CLOUD, SUN),
    4: rotate(CLOUD, CLOUD, SUN),
    5: rotate(SUN, SUN, CLOUD),
    6: rotate(CLOUD, CLOUD, RAIN),
    7: rotate(CLOUD, RAIN, SNOW),
    10: rotate(CLOUD),
    12: rotate(RAIN),
    15: rotate(CLOUD, SNOW, RAIN),
    16: rotate(CLOUD, CLOUD, SNOW),
    17: rotate(SNOW),
    20: rotate(FOG, CLOUD, CLOUD),
    24: rotate(FOG, FOG, CLOUD),
    28: rotate(CLOUD, CLOUD, RAIN),
    30: rotate(CLEARNIGHT),
    31: rotate(CLEARNIGHT, CLEARNIGHT, CLOUD),
    32: rotate(CLEARNIGHT, CLEARNIGHT, RAIN),
    33: rotate(CLEARNIGHT, CLOUD, CLOUD),
    34: rotate(CLEARNIGHT, CLOUD, CLOUD),
    35: rotate(CLEARNIGHT, CLEARNIGHT, CLOUD),
    36: rotate(CLEARNIGHT, CLEARNIGHT, RAIN),
}
UNKNOWN_CONDITION = rotate([255, 0, 255, 0])


try:
    # Convert the forecast into a serios of animations
    weather = get_canadian_weather(WEATHER_CITY, WEATHER_PROVINCE)
    animations = []
    for period in weather["forecastGroup"]["forecast"]:
        forecast = period["abbreviatedForecast"]["iconCode"]["$"]
        try:
            logger.info(f"""{period["period"]["$"]}: {period["abbreviatedForecast"]["textSummary"]["$"]} ({period["abbreviatedForecast"]["iconCode"]["$"]})""")
            animations.append(FORECAST_ANIMATIONS[forecast])
        except KeyError:
            logger.exception(f"""No known animation for https://weather.gc.ca/weathericons/{forecast}.gif""")
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
