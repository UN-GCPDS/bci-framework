from matplotlib import pyplot as plt
from matplotlib import lines
import matplotlib
import numpy as np

plt.style.use('ggplot')


def adjust_lightness(color, amount=0.5):
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])


def build_paradigm(data):
#     ax = plt.subplot(111)

    ax = plt.gca()

#     ax = plt.axes(frameon=False)
    ax.set_frame_on(False)
    ax.get_xaxis().tick_bottom()
    ax.axes.get_yaxis().set_visible(False)

    Y = 1
    ticks = []
    extra = []
    alpha = 1

    max_y = 0
    for i, frame in enumerate(data):

        p = frame['time']
        alpha = frame.get('alpha', 1)
        label = frame['label']
        label_extra = frame.get('label_extra', None)
        color = frame.get('color', f'C{i}')

        rotation = frame.get('rotation', 0)
        fontsize = frame.get('fontsize', 14)

        level = frame.get('level', (0, 1))
        level = [0.1 + l for l in level]
        max_y = max(max_y, level[1])
        ticks.extend(p)

        plt.fill_between([p[0], p[-1]], *level, facecolor=color,
                         alpha=alpha, linewidth=0, edgecolor=color)

        if len(p) > 2:
            plt.fill_between(p[1:], *level, edgecolor=adjust_lightness(color,
                                                                       0.85), facecolor='none', alpha=1, hatch='///', linewidth=0)
#             if label_extra is None:
#                 label_extra = f'{1000*(p[2]-p[1]):.0f} ms'
            label_extra = f"\n{abs(p[1]):.1f}s ~ {abs(p[-1]):.1f}s"
#             if label_extra != '':
#                 plt.annotate(label_extra, (np.mean(p[1:]), np.mean(level)), ha='center', va='center', color='w', fontsize=fontsize, rotation=rotation)
        else:
            label_extra = ''

        plt.annotate(f"{label}{label_extra}", (np.mean(p), np.mean(
            level)), ha='center', va='center', color='w', fontsize=fontsize, rotation=rotation)

    plt.xticks(list(set(ticks)))
    ax.set_xticklabels([f"{i:.1f}s" for i in list(set(ticks))])

    xmin, xmax = min(ticks), max(ticks + extra)
    ax.add_artist(lines.Line2D((xmin, xmax), (0, 0),
                               color='black', linewidth=2))

    plt.xlim(xmin, xmax)

    plt.ylim(0, max_y + 0.1)
