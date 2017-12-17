#!/home/bradbeattie/Projects/Aurora/.env/bin/python3
from pprint import pprint
from local_settings import IP_ADDRESS, AUTH_TOKEN
from nanoleaf import Aurora
from xml.etree.ElementTree import fromstring
from xmljson import badgerfish
import argparse
import os


try:
    aurora = Aurora(IP_ADDRESS, AUTH_TOKEN)
    pathname = os.path.dirname(os.path.realpath(__file__))

    parser = argparse.ArgumentParser("Aurora Controller")
    parser.add_argument("--effect")
    parser.add_argument("--brightness", type=int)
    args = parser.parse_args()

    if args.brightness is not None:
        aurora.brightness = args.brightness

    if args.effect is not None:
        if args.effect == "random":
            print(aurora.effect_random())
        elif args.effect == "list":
            pprint(aurora.effects_list)
        else:
            aurora.effect = args.effect

    weather = badgerfish.data(fromstring(open(os.path.join(pathname, "weather.html")).read()))["siteData"]

except:
    pass
