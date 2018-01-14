from datetime import datetime, timedelta
from utils_generic import get_cached_url, map_range
from xml.etree.ElementTree import fromstring
from xmljson import badgerfish
import subprocess


def get_canadian_weather(city, province=None):

    # Get city list
    entries = badgerfish.data(fromstring(
        get_cached_url(
            "http://dd.weather.gc.ca/citypage_weather/xml/siteList.xml",
            timedelta(days=30),
        )
    ))["siteList"]["site"]
    matching_entries = [
        entry
        for entry in entries
        if entry["nameEn"]["$"] == city and (
            province is None or
            entry["provinceCode"]["$"] == province
        )
    ]
    assert len(matching_entries) == 1, f"Your provided city/province matched {len(matching_entries)} entries: {matching_entries}"
    entry = matching_entries[0]

    # Get city forecast
    forecast = badgerfish.data(fromstring(
        get_cached_url(
            f"""http://dd.weather.gc.ca/citypage_weather/xml/{entry["provinceCode"]["$"]}/{entry["@code"]}_e.xml""",
            timedelta(hours=1),
        )
    ))["siteData"]
    return forecast


def get_tides(tide_station):

    # Fetch the raw tide data
    tides = {}
    height_range = []
    for row in subprocess.run(
        ["/usr/bin/tide", "-l", tide_station, "-m", "r"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.splitlines():
        timestamp, height = row.decode().split()
        moment = datetime.fromtimestamp(int(timestamp))
        height = float(height)
        tides[moment] = {"meters": height}
        height_range.append(height)

    # Supplement with percentage range estimates
    min_height = min(height_range)
    max_height = max(height_range)
    for k, v in tides.items():
        v["percentage"] = map_range(
            (min_height, max_height),
            (0, 1),
            v["meters"],
        )

    return tides


if __name__ == "__main__":
    get_canadian_weather("Vancouver")
    get_tides("Vancouver, British Columbia")
