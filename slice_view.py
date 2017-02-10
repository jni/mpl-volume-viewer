import numpy as np
from matplotlib import pyplot as plt


def _dscroll(key, axes):
    volume = axes.volume
    if key == 'down' or key == 'j':
        shift = -1
    elif key == 'up' or key == 'k':
        shift = 1
    axes.index = (axes.index + shift) % volume.shape[0]
    axes.images[0].set_array(volume[axes.index])
    if axes.points is not None:
        update_points(axes)


def process_key(event):
    fig = event.canvas.figure
    ax = event.inaxes or fig.axes[0]
    if event.key in ['up', 'down', 'j', 'k']:
        _dscroll(event.key, ax)
    fig.canvas.draw()


def slice_view(volume, points=None, pts_depth=2, cmap=plt.cm.viridis):
    fig, ax = plt.subplots()
    ax.volume = volume
    ax.points = None
    ax.index = volume.shape[0] // 2
    ax.imshow(volume[ax.index], cmap=cmap)
    if points is not None:
        ax.points = points.T
        ax.pts_depth = pts_depth
        draw_points(ax)
    fig.canvas.mpl_connect('key_press_event', process_key)
    return fig, ax


def draw_points(axes):
    pln, row, col = axes.points
    alpha = np.maximum(0, 1 - np.abs(pln - axes.index) / axes.pts_depth)
    points_collection = [axes.scatter(x, y, alpha=a)
                         for x, y, a in zip(col, row, alpha)]
    axes.drawn_points = points_collection


def update_points(axes):
    pln = axes.points[0]
    alpha = np.maximum(0, 1 - np.abs(pln - axes.index) / axes.pts_depth)
    for pt, a in zip(axes.drawn_points, alpha):
        pt.set_alpha(a)
