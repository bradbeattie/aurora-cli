#!/usr/bin/env python3
from pprint import pprint
from local_settings import IP_ADDRESS, AUTH_TOKEN, logger
from nanoleaf import Aurora
import argparse


try:
    # Argument parsing
    parser = argparse.ArgumentParser("Aurora Controller")
    parser.add_argument("--effect")
    parser.add_argument("--brightness", type=int)
    args = parser.parse_args()
    logger.info(args)

    # Connect to Aurora
    aurora = Aurora(IP_ADDRESS, AUTH_TOKEN)

    # Brightness
    if args.brightness is not None:
        aurora.brightness = args.brightness

    # Effects
    if args.effect is not None:
        if args.effect == "random":
            aurora.effect_random()
        elif args.effect == "list":
            pprint(aurora.effects_list)
        else:
            aurora.effect = args.effect

# Error handling
except Exception as e:
    logger.exception(e)
