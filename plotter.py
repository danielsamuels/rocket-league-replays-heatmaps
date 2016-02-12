import logging
import os
from itertools import chain

import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
from matplotlib.colors import LogNorm, rgb2hex
from matplotlib.figure import Figure

logger = logging.getLogger('pyrain')

STANDARD = {
    'outline': {
        'file': '{}/resources/arena_outline.png'.format(
            os.path.dirname(os.path.realpath(__file__))
        ),
        'alpha': 1
    },
    'fieldline': {
        'file': '{}/resources/arena_fieldlines.png'.format(
            os.path.dirname(os.path.realpath(__file__))
        ),
        'alpha': 1
    },
    'boost': {
        'file': '{}/resources/arena_boost.png'.format(
            os.path.dirname(os.path.realpath(__file__))
        ),
        'alpha': 1
    },
    'xmin': -5770,
    'xmax': 5770,
    'ymin': -4096,
    'ymax': 4096,
    'aspect': 0.71
}

WASTELAND = {
    'outline': {
        'file': '{}/resources/wasteland_outline.png'.format(
            os.path.dirname(os.path.realpath(__file__))
        ),
        'alpha': 0.8
    },
    'fieldline': {
        'file': '{}/resources/wasteland_fieldlines.png'.format(
            os.path.dirname(os.path.realpath(__file__))
        ),
        'alpha': 0.3
    },
    'xmin': -5980,
    'xmax': 5980,
    'ymin': -4530,
    'ymax': 4530,
    'aspect': 0.76
}

UTOPIA_RETRO = {
    'outline': {
        'file': '{}/resources/utopia_retro_outline.png'.format(
            os.path.dirname(os.path.realpath(__file__))
        ),
        'alpha': 1,
        'scale': 1
    },
    'xmin': -4096,
    'xmax': 4096,
    'ymin': -4096,
    'ymax': 4096,
    'aspect': 1,
}

BOOST = 'boost'
OUTLINE = 'outline'
FIELDLINE = 'fieldline'

# avg car size ~118x82x32 ; Field Size(Excluding Wasteland: 10240x8192*(2000?);
# -5120 - 5120; -4096,4096; 19, 2000
# Goals are roughly 650units deep
# Field length with goals: ~11540 aspect ratio: 0.71
# bins for ~1:1 mapping:87x100x62


def graph_2d(values, mean=True):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(values['xs'], values['ys'])
    if mean:
        y_mean = [np.mean(values['ys']) for i in values['xs']]
        ax.plot(values['xs'], y_mean, linestyle='--')
    plt.show()


def lines2d(x, y, ax, mean=True):
    lines = []
    l, = ax.plot(x, y)
    lines.append(l)
    if mean:
        y_mean = [np.mean(y) for i in x]
        l, = ax.plot(x, y_mean, linestyle='--')
        lines.append(l)
    return lines


def generate_figure(data, arena, overlays=None, bins=(25, 12), hexbin=False, interpolate=True,
                    norm=False):
    fig = Figure()
    ax = fig.add_subplot(111)

    x = data['x']
    y = data['y']

    logger.info("Building Heatmap %s with %d Data Points" % (data['title_short'], len(x)))
    cmap = plt.cm.get_cmap('jet')
    norm = LogNorm() if norm else None

    interpolate = 'bilinear' if interpolate else 'none'
    bins = (bins[1], bins[0])
    heatmap, xedges, yedges = np.histogram2d(
        y,
        x,
        bins=bins,
        range=[
            (arena['ymin'], arena['ymax']),
            (arena['xmin'], arena['xmax'])
        ]
    )

    extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]

    ax.imshow(
        heatmap,
        extent=extent,
        norm=norm,
        cmap=cmap,
        interpolation=interpolate,
        origin='lower',
        aspect='auto'
    )
    ax.autoscale(False)

    if overlays:
        for overlay in overlays:
            im = plt.imread(arena[overlay]['file'])
            axi = ax.imshow(
                im,
                origin='lower',
                aspect=arena[overlay].get('scale', 'auto'),
                alpha=arena[overlay]['alpha'],
                extent=[arena['xmin'], arena['xmax'], arena['ymin'], arena['ymax']]
            )
            axi.set_zorder(-1)

    ax.axis('off')
    fig.subplots_adjust(hspace=0, wspace=0, right=1, top=1, bottom=0, left=0)
    fig.patch.set_alpha(0)
    return fig


def set_colormap(ax, colors=10, double=True):
    cm = plt.get_cmap('gist_rainbow')
    if double:
        cycle = list(chain.from_iterable((cm(1. * i / colors), cm(1. * i / colors)) for i in range(colors)))
    else:
        cycle = [cm(1. * i / colors) for i in range(colors)]
    ax.set_prop_cycle(cycler('color', cycle))


def get_rgb(line):
    return rgb2hex(line.get_color())
