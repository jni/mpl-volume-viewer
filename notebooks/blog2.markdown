An interactive matplotlib volume viewer, part two: orthogonal views
===================================================================

In [Part One](), we looked at how to add interactivity to Matplotlib's image viewer in order to scan up and down a volume. When viewing a volume, though, it sometimes helps to see *orthogonal slices*, which are views along different cuts through the same data volume. (Think about slicing cucumbers length-ways or into slices.) Viewer's such as [ITK-SNAP]() provide orthogonal views by default. After the last post, I wondered how hard it would be to do the same thing with orthogonal views.

It turns out, quite a bit harder! But the magic of open source development is that we only need to do it once. In this post I'll document how I achieved this, with the hope that it'll be a useful template for other interactive plot functionality.

1. Getting the plots
--------------------

We start by the simplest case, which has no interactivity. Please refer to the [previous post]() for how to download the data and read it with `nibabel`. Here we'll skip right to reading:

```python
filename = 'attention/structural/nsM00587_0002.hdr'
struct = nibabel.load(filename)
struct_arr = struct.get_data()
```

This array is 3-dimensional:

```python
print(struct_arr.shape)
```

We also saw in the previous post that this data has different resolution along the depth, row, and column dimensions, so that plotting a single slice, by default, looks squishy:

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.imshow(struct_arr[50])
```

How do we check the resolution of the different dimensions? NiBabel has helpfully loaded them in the "affine" matrix:

```python
print(struct.affine)
```

We don't have time to go into details of [homogeneous transforms]() in this piece, but it turns out that the first three diagonal elements contain the aspect ratios of the column, row, and depth dimensions. We can extract these with NumPy:

```python
import numpy as np

raw_scales = np.diag(struct.affine)[:3]
```

To keep things simple, we are going to ignore the orientation of the dimensions, so we will take the absolute value of the raw scale values. In real life, left-right asymmetry is very very important, and you should *not* ignore this value, and you should spend an inordinate amount of time making sure that the orientation of your image is correct. Neurosurgeons have drilled into the [wrong side of a patient's skull]() because of software that didn't take due care with this, so never brush this off outside of little internet tutorials!

Ok, now that we're done with that warning, let's throw out the orientation information:

```python
scales = np.abs(raw_scales)
```

Finally, in NumPy, it is more convenient to have the leading dimension be the anisotropic one (the one with the different scale). (In Matlab, the opposite is true.) Therefore, let's transpose the last axis to be in the leading position:

```python
scales = scales[[2, 0, 1]]
struct_arr = np.transpose(struct_arr, [2, 0, 1])
```

Now we have everything we need for our orthogonal plot. The key is to decide on a slice to take along each axis, and then plot the remaining to axes on a Matplotlib... um... axis. This post is going to be fun, I can tell. Anyway, we'll start with the central plane along each axis:

```python
fig, ax = plt.subplots(nrows=2, ncols=2)

center = np.array(struct_arr.shape // 2)

ax[0, 0].imshow(struct_arr[center[0]], aspect=scales[1]/scales[2])
ax[1, 0].imshow(struct_arr[center[1]], aspect=scales[0]/scales[2])
ax[0, 1].imshow(struct_arr[center[2]], aspect=scales[0]/scales[1])
```

Let's add some horizontal lines to make it a bit clearer what's going on:

```python
ax[0, 0].hlines(center[1], 0, struct_arr.shape[2])
```
