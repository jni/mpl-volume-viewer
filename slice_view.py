import numpy as np
from matplotlib import pyplot as plt




def _random_cmap(n=256):
    # to do: make this really map random colours
    return plt.cm.Spectral(n)


def _dscroll(event, fig, ax):
    key = event.key
    volume = ax.volume
    if key == 'down' or key == 'j':
        shift = -1
    elif key == 'up' or key == 'k':
        shift = 1
    ax.index = (ax.index + shift) % volume.shape[0]
    ax.images[0].set_array(volume[ax.index])
    if hasattr(ax, 'overlay'):
        ax.images[1].set_array(ax.overlay[ax.index])
    if ax.points is not None:
        update_points(ax)


def _toggle_overlay(event, fig, ax):
    if ax.overlay is not None:
        ax = ax.images[1]
        temp = ax.get_alpha()
        ax.set_alpha(ax.old_alpha)
        ax.old_alpha = temp


def process_key(event):
    fig = event.canvas.figure
    ax = event.inaxes or fig.axes[0]
    f = KEYMAP[event.key]
    f(event, fig, ax)
    fig.canvas.draw()


def slice_view(volume, cmap=plt.cm.gray,
               points=None, pts_depth=2, pts_color='red',
               labels=None, labels_cmap='random'):
    remove_keymap_conflicts()
    fig, ax = plt.subplots()
    ax.volume = volume
    ax.points = None
    ax.index = volume.shape[0] // 2
    ax.imshow(volume[ax.index], cmap=cmap)
    if points is not None:
        ax.points = points.T
        ax.pts_depth = pts_depth
        draw_points(ax)
    if labels is not None:
        if labels_cmap == 'random':
            cmap = _random_cmap(np.max(labels))
        ax.overlay = cmap(labels)
        ax.imshow(ax.overlay[ax.index], alpha=0.4)
        ax.old_alpha = 0
    fig.canvas.mpl_connect('key_press_event', process_key)
    return fig, ax


def draw_points(axes):
    size = plt.rcParams['lines.markersize'] ** 2
    pln, row, col = axes.points
    distance = np.abs(pln - axes.index)
    distance_nonlin = np.clip(distance - 0.5, 0, axes.pts_depth - 0.5)
    apparent_position = (np.sign(pln - axes.index) * distance_nonlin /
                         axes.pts_depth)  # between -1 and 1
    sizes = size * (1 + apparent_position**3)
    alpha = np.maximum(0, 1 - np.abs(pln - axes.index) / axes.pts_depth)
    points_collection = [axes.scatter(x, y, alpha=a)
                         for x, y, a, s in zip(col, row, alpha, sizes)]
    axes.drawn_points = points_collection


def update_points(axes):
    size = plt.rcParams['lines.markersize'] ** 2
    pln = axes.points[0]
    distance = np.abs(pln - axes.index)
    distance_nonlin = np.clip(distance - 0.5, 0, axes.pts_depth - 0.5)
    apparent_position = (np.sign(pln - axes.index) * distance_nonlin /
                         axes.pts_depth)  # between -1 and 1
    sizes = size * (1 + apparent_position**3)
    alpha = np.maximum(0, 1 - np.abs(pln - axes.index) / axes.pts_depth)
    for pt, a, s in zip(axes.drawn_points, alpha, sizes):
        pt.set_alpha(a)
        pt.set_sizes([s])


KEYMAP = {
    'down': _dscroll,
    'up': _dscroll,
    'j': _dscroll,
    'k': _dscroll,
    'f': _toggle_overlay,
}

# Remove conflicting keys in default keymap
def remove_keymap_conflicts():
    for prop in plt.rcParams:
        if prop.startswith('keymap.'):
            keys = plt.rcParams[prop]
            remove_list = []
            for key in keys:
                if key in KEYMAP:
                    remove_list.append(key)
            for key in remove_list:
                keys.remove(key)
