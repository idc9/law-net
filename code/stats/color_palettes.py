from seaborn.apionly import color_palette
import pandas as pd


def div_palette_zero_centered(values):
    """
    Returns a blue-red divergent palette

    blue = most negative value
    red = most positive value
    zero = white

    Parameters
    ---------
    values: list of numbers, must include both negative and positive values

    Output
    ------
    colors: list of (r,g,b) values on 0-1 scale

    """

    if len([v for v in values if v < 0]) == 0:
        print 'no negative values'
    if len([v for v in values if v > 0]) == 0:
        print 'no positive values'

    min_v = min(values)
    max_v = max(values)

    colors = []
    for v in values:
        if v < 0:
            alpha = 1 - v/min_v
            colors.append((alpha, alpha, 1))
        else:
            alpha = 1 - v/max_v
            colors.append((1, alpha, alpha))

    return colors


def to_256_scale(pal):
    """
    Given a list of RGB tuples that are on the 0-1 scale returns a
    list of RRB tuples on the 256 that stupid plot.ly wants
    """
    pal_256 = []
    for i in range(len(pal)):
        s = 'rgb(%d, %d, %d)' % (int(256 * pal[i][0]),
                                 int(256 * pal[i][1]),
                                 int(256 * pal[i][2]))
        pal_256.append(s)

    return pal_256


def sequential_palette(y, color='grey', n_bins=100):
    """
    Returns the color palette for a continuous variable y

    https://stanford.edu/~mwaskom/software/seaborn/tutorial/color_palettes.html
    """

    if color == 'grey':
        palette = color_palette('Greys_r', n_colors=n_bins)
    elif color == 'blue':
        palette = color_palette('Blues', n_colors=n_bins)
    else:
        raise ValueError('invalid color type')

    # palette = color_palette('RdBu_r', n_colors=len(y))
    bin_assignments = pd.cut(y, n_bins, labels=range(n_bins))

    # return [palette[int(k-1)] for k in y.rank(method='min')]

    return [palette[bin_assignments[k]] for k in range(len(y))]


def divergent_palette(y, n_bins=100):
    """
    Returns the color palette for a continuous variable y

    https://stanford.edu/~mwaskom/software/seaborn/tutorial/color_palettes.html
    """
    # palette = color_palette('Blues', n_colors=len(y))

    palette = color_palette('RdBu_r', n_colors=len(y))

    bin_assignments = pd.cut(y, n_bins, labels=range(n_bins))

    # return [palette[int(k-1)] for k in y.rank(method='min')]

    return [palette[bin_assignments[k]] for k in range(n_bins)]


def two_class_palette(x):
    """
    Returns the color palette for two class labels.

    0: blue
    1: red
    """
    if set(x) != set([0, 1]):
        raise ValueError('class labels not 0-1')

    pal = []
    for i in range(len(x)):
        if x[i] == 0:
            pal.append('blue')
        else:
            pal.append('red')
    return pal


def two_category_palette(x):
    vals = set(x)
    if len(vals) > 2:
        raise ValueError('more than two values')

    pal = ['red'] * len(x)

    for i in range(len(x)):
        if x[i] == x[0]:
            pal[i] = 'blue'

    return pal
