from matplotlib import pyplot as plt
from matplotlib import lines
import matplotlib
import numpy as np

plt.style.use('ggplot')


########################################################################
class Paradigm:
    """"""

    # ----------------------------------------------------------------------
    @classmethod
    def adjust_lightness(cls, color, amount=0.5):
        """"""
        import matplotlib.colors as mc
        import colorsys
        try:
            c = mc.cnames[color]
        except:
            c = color
        c = colorsys.rgb_to_hls(*mc.to_rgb(c))
        return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])

    # ----------------------------------------------------------------------
    @classmethod
    def build_paradigm(cls, data):
        """"""
        ax = plt.gca()
        ax.set_frame_on(False)
        ax.get_xaxis().tick_bottom()
        ax.axes.get_yaxis().set_visible(False)

        ticks = []
        ticks_label = []
        extra = []
        alpha = 1

        max_y = 0
        min_y = 0
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
            max_y = max(max_y, *level)
            min_y = min(min_y, *level)

            restart = frame.get('restart', False)

            if restart:
                ticks_label.extend([i - p[0] for i in p])
                p = [i + ticks[-1] for i in p]
            else:
                ticks_label.extend(p)

            ticks.extend(p)

            plt.fill_between([p[0], p[-1]], *level, facecolor=color,
                             alpha=alpha, linewidth=0, edgecolor=color)

            if hatch := frame.get('hatch', ''):
                plt.fill_between([p[0], p[-1]], *level, edgecolor=cls.adjust_lightness(
                    color, 0.85), facecolor='none', alpha=1, hatch=hatch, linewidth=0)

            if len(p) > 2:
                plt.fill_between(p[1:], *level, edgecolor=cls.adjust_lightness(color,
                                                                               0.85), facecolor='none', alpha=1, hatch='///', linewidth=0)
                if label_extra is None:
                    label_extra = f"\n{abs(p[1] - p[0]):.1f}s ~ {abs(p[-1]- p[0]):.1f}s"
                elif label_extra:
                    label_extra = f"\n{label_extra}"
            else:
                label_extra = ''

            if marker := frame.get('marker', False):

                lev = [1 + (0.2 * marker['level']),
                       1.2 + (0.2 * marker['level'])]
                max_y = max(max_y, *lev)
                lev = [0.1 + l for l in lev]

                q = p[0]
                extra.append(q + marker['width'])
                plt.fill_between([q, q + marker['width']], *lev,
                                 facecolor=color, alpha=alpha, linewidth=0, edgecolor=color)
                plt.fill_between([q, q + marker['width']], *lev, edgecolor=cls.adjust_lightness(
                    color, 0.85), facecolor='none', alpha=1, hatch='...', linewidth=0)
                plt.annotate(marker['label'], (np.mean([q, q + marker['width']]), np.mean(
                    lev)), ha='center', va='center', color='w', fontsize=12, zorder=999)
                plt.vlines(q, marker.get('min', 0.1),
                           lev[1], linestyle='--', linewidth=1, color='k', zorder=99)

                if marker.get('label_end', False):
                    q = p[-1]
                    extra.append(q + marker['width'])
                    plt.fill_between([q, q + marker['width']], *lev,
                                     facecolor=color, alpha=alpha, linewidth=0, edgecolor=color)
                    plt.fill_between([q, q + marker['width']], *lev, edgecolor=cls.adjust_lightness(
                        color, 0.85), facecolor='none', alpha=1, hatch='...', linewidth=0)
                    plt.annotate(marker['label_end'], (np.mean([q, q + marker['width']]), np.mean(
                        lev)), ha='center', va='center', color='w', fontsize=12, zorder=999)
                    plt.vlines(q, 0.1, lev[1], linestyle='--',
                               linewidth=1, color='k', zorder=99)

            a, b = 0, 0
            plt.annotate(f"{label}{label_extra}", (np.mean([p[0], p[-1]]) - a, np.mean(level) - b), ha=frame.get(
                'ha', 'center'), va='center', color='w', fontsize=fontsize, rotation=rotation)

        xmin, xmax = min(ticks), max(ticks + extra)

        plt.xticks([])
        ax.set_xticklabels([])
        ax.add_artist(lines.Line2D((xmin, xmax), (0, 0),
                                   color='black', linewidth=2))

        plt.xlabel('Time')
        plt.xlim(xmin, xmax)
        plt.ylim(min_y, max_y + 0.1)
        ax.arrow(0, 0, xmax, 0, fc='k', ec='none', head_width=max_y * 0.07,
                 head_length=max_y * 0.07, length_includes_head=False, clip_on=False)
