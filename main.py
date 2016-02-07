import json
import math
import sys
import uuid

import analyser
import plotter
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from pyrope import Replay

replay = Replay(path=sys.argv[1])
replay_id = replay.header['Id']
replay.parse_netstream()


def _extract_data(replay, replay_analyser, player):
    datasets = {}
    lst_plots = []
    slicing = False
    data = replay_analyser.get_actor_pos(player, slicing)

    new_datasets = analyser.AnalyserUtils.filter_coords(data, True, True, False)
    for entry in new_datasets:
        if entry['title_short'] in datasets:
            print("Dataset already in Plotlist")
            continue
        lst_plots.append(entry['title_short'])
        datasets[entry['title_short']] = entry

    return datasets


plot_types = ['Hexbin', 'Histogram - Blur', 'Histogram - Clear']
plot_type = 'Histogram - Clear'

replay_analyser = analyser.Analyser(replay)
if 'Wasteland' in replay_analyser.replay.header['MapName']:
    arena = plotter.WASTELAND
    overlays = [plotter.OUTLINE, plotter.FIELDLINE]
else:
    arena = plotter.STANDARD
    overlays = [plotter.OUTLINE, plotter.FIELDLINE, plotter.BOOST]

hexbin = True if plot_type == 'Hexbin' else False
interpolate = True if 'Blur' in plot_type else False

# 0.1 - 5
scale = 4.5
bins = (math.ceil(scale * 15), math.ceil(scale * 15 * arena['aspect']))

files = {}
for player in replay_analyser.player_data.keys():
    datasets = _extract_data(replay, replay_analyser, player)

    log = True

    plot = plotter.generate_figure(
        datasets[list(datasets.keys())[0]],
        arena,
        overlays=overlays,
        bins=bins,
        norm=log,
        interpolate=interpolate,
        hexbin=hexbin
    )

    filename = '/tmp/{}-{}.png'.format(
        replay_id,
        uuid.uuid4()
    )

    fig = FigureCanvas(plot)
    fig.print_png(filename, transparent=True)
    files[player] = filename

print(json.dumps(files))
