from copy import deepcopy
from colorsys import hls_to_rgb


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
