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
    if event.key in KEYMAP:
        f = KEYMAP[event.key]
        f(event, fig, ax)
    fig.canvas.draw()


def _normalize_fig_axes(fig, axes):
    if fig is None and axes is not None:
        fig = axes.ravel()[0].figure
    if fig is None:
        fig = plt.figure('Slice Viewer')
    if axes is None:
        ax0 = fig.add_subplot(221)
        ax1 = fig.add_subplot(223, sharex=ax0)
        ax2 = fig.add_subplot(222, sharey=ax0)
        ax3 = fig.add_subplot(224)
        axes = np.array([ax0, ax1, ax2, ax3])
    return fig, axes


class SliceViewer:
    def __init__(self, volume, spacing=None, cmap=plt.cm.gray,
                 points=None, pts_depth=2, pts_color='red',
                 labels=None, labels_cmap='random', multichannel=False,
                 fig=None, axes=None):
        if spacing is None:
            spacing = np.ones((3,))
        remove_keymap_conflicts()
        self.updating = False
        self.fig, self.axes = _normalize_fig_axes(fig, axes)
        self.raxes = self.axes.T.ravel()
        self.raxes[-1].set_axis_off()
        self.volume = volume
        self.points = points
        self.index = np.array(volume.shape[:3]) // 2
        # aspect is pixel height over pixel width
        self.raxes[0].imshow(volume[self.index[0], :, :],
                             aspect=spacing[1] / spacing[2])
        self.raxes[1].imshow(volume[:, self.index[1], :],
                             aspect=spacing[0] / spacing[2])
        self.raxes[2].imshow(volume[:, :, self.index[2]].swapaxes(0, 1),
                             aspect=spacing[1] / spacing[0])
        self.fig.canvas.mpl_connect('key_press_event', process_key)
        for ax in self.raxes:
            ax.set_autoscale_on(False)
        self.raxes[1].callbacks.connect('ylim_changed', self.ax_update)
        self.raxes[2].callbacks.connect('xlim_changed', self.ax_update)

    def ax_update(self, ax):
        if ax is self.raxes[0] or self.updating:
            return  # do nothing with main view, handled by sharex/sharey
        # Keep track of state so that we don't go back
        # and forth with each axis updating the other
        self.updating = True
        if ax is self.raxes[1]:
            plim = ax.get_ylim()
            self.raxes[2].set_xlim(*plim[::-1])
        elif ax is self.raxes[2]:
            plim = ax.get_xlim()
            self.raxes[1].set_ylim(*plim[::-1])
        self.updating = False
        ax.figure.canvas.draw_idle()


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
