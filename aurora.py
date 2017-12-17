#!/usr/bin/env python3
from local_settings import IP_ADDRESS, AUTH_TOKEN, logger
from nanoleaf import Aurora
from pprint import pprint
import argparse
import json


try:
    # Argument parsing
    parser = argparse.ArgumentParser("Aurora Controller")
    parser.add_argument("--effect")
    parser.add_argument("--brightness", type=int)
    parser.add_argument("--identify", action="store_true")
    parser.add_argument("--info", action="store_true")
    args = parser.parse_args()
    logger.info(args)

    # Connect to Aurora
    aurora = Aurora(IP_ADDRESS, AUTH_TOKEN)

    if args.brightness is not None:
        aurora.brightness = args.brightness
    if args.effect:
        if args.effect == "random":
            aurora.effect_random()
        else:
            aurora.effect = args.effect
    if args.identify:
        aurora.identify()
    if args.info:
        print(json.dumps(aurora.info, sort_keys=True, indent=4))

# Error handling
except Exception as e:
    logger.exception(e)
