from copy import deepcopy
from datetime import datetime
import requests
import hashlib
from colorsys import hls_to_rgb
import os


CACHE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    ".cached_urls",
)


def get_cached_url(url, max_age):
    cache_path = os.path.join(CACHE_DIR, hashlib.sha512(url.encode()).hexdigest()[0:10])
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    try:
        file_age = datetime.now() - datetime.fromtimestamp(int(
            os.path.getmtime(cache_path)
        ))
        assert file_age < max_age
        return open(cache_path).read()
    except (AssertionError, FileNotFoundError):
        response = requests.get(url)
        assert response.status_code == 200, f"{response.status_code}: {response.content}"
        with open(cache_path, "w") as cache_file:
            cache_file.write(response.text)
        return response.content


# From https://gist.github.com/Wilfred/7889868
def flatten(nested_list):
    """Flatten an arbitrarily nested list, without recursion (to avoid
    stack overflows). Returns a new list, the original list is unchanged.
    >> list(flatten_list([1, 2, 3, [4], [], [[[[[[[[[5]]]]]]]]]]))
    [1, 2, 3, 4, 5]
    >> list(flatten_list([[1, 2], 3]))
    [1, 2, 3]
    """
    nested_list = deepcopy(nested_list)

    while nested_list:
        sublist = nested_list.pop(0)

        if isinstance(sublist, list):
            nested_list = sublist + nested_list
        else:
            yield sublist


def hsl_to_rgbw(h, s, l):
    return [
        round(i * 255)
        for i in hls_to_rgb(h, l, s)
    ] + [0]


# From https://rosettacode.org/wiki/Map_range#Python
def map_range(a, b, s):
    (a1, a2), (b1, b2) = a, b
    return max(b1, min(b2, b1 + ((s - a1) * (b2 - b1) / (a2 - a1))))
