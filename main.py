import json
import math
import sys
import tempfile
import uuid

import analyser
import plotter
import requests
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from pyrope import Replay

# Download the replay file.
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {
    'user-agent': user_agent
}

if sys.argv[1].startswith('/var/www/rocket_league_media/'):
    # /var/www/rocket_league_media/uploads/replay_files/AF2161A04845ABAAE48669986FE1F5B6.replay
    # https://www.rocketleaguereplays.com/media/uploads/replay_files/AF2161A04845ABAAE48669986FE1F5B6.replay

    # Download the file from `url`, save it in a temporary directory and get the
    # path to it (e.g. '/tmp/tmpb48zma.txt') in the `file_path` variable:
    url = sys.argv[1].replace('/var/www/rocket_league_', 'https://www.rocketleaguereplays.com/')

    r = requests.get(url, headers=headers)
    f = tempfile.TemporaryFile('wb')

    f.write(r.content)
    f.seek(0)

    file_path = f.name
elif sys.argv[1].startswith('http'):
    r = requests.get(sys.argv[1], headers=headers)
    f = tempfile.TemporaryFile('wb')

    f.write(r.content)
    f.seek(0)

    file_path = f.name
else:
    file_path = sys.argv[1]

replay = Replay(path=file_path)
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
elif 'labs_utopia_p' in replay_analyser.replay.header['MapName']:
    arena = plotter.UTOPIA_RETRO
    overlays = [plotter.OUTLINE]
else:
    arena = plotter.STANDARD
    overlays = [plotter.OUTLINE, plotter.FIELDLINE, plotter.BOOST]

hexbin = False
interpolate = False

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
