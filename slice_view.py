from matplotlib import pyplot as plt

def process_key(event):
    fig = event.canvas.figure
    ax = event.inaxes or fig.axes[0]
    volume = ax.volume
    if event.key == 'down' or event.key == 'left':
        shift = -1
    elif event.key == 'up' or event.key == 'right':
        shift = 1
    ax.index = (ax.index + shift) % volume.shape[0]
    ax.images[0].set_array(volume[ax.index])
    fig.canvas.draw()


def slice_view(volume, cmap=plt.cm.viridis):
    fig, ax = plt.subplots()
    ax.volume = volume
    ax.index = volume.shape[0] // 2
    ax.imshow(volume[ax.index], cmap=cmap)
    fig.canvas.mpl_connect('key_press_event', process_key)
    return fig, ax
