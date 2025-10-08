{
    "title": "Generating multimedia from Python",
    "description": "Generating images and video from Python using Pycairo and OpenCV.",
    "date": "2025-03-23",
    "show": true
}


Using the right libraries, it is not very hard to generate multimedia from Python.

[Pycairo](https://pycairo.readthedocs.io) is a Python library that provides bindings for [cairo](https://cairographics.org), a 2D graphics library which supports many output devices.


## Getting started

Installation is as simple as `pip install pycairo`.

For drawing, we first have to create a *surface*. The most useful surfaces are
  - The `ImageSurface`, which draws to an in-memory buffer and can be initialized as `surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)`
  - Surfaces that draw to a file (`PDFSurface`, `PSSurface`, `SVGSurface`), which are initialized as `cairo.PDFSurface("output.pdf", width, height)`. Note that the width and height are in points rather than pixels.

After drawing, `surface.finish()` should be called. Alternatively, surfaces can be used as context managers:
```
with cairo.SVGSurface("example.svg", 200, 200) as surface:
    # draw stuff here
```

Before we can draw, we have to create a `context` from the surface:
```
ctx = cairo.Context(surface)
```


## Drawing examples

Pycairo is stateful and has the concepts of paths and subpaths. I will not try to accurately describe these, but rather show some examples.

Setting the background color to white:
```
ctx.set_source_rgb(1, 1, 1)
ctx.paint()
```

Drawing a red line:
```
ctx.set_source_rgb(1, 0, 0)
ctx.set_line_width(5)
ctx.move_to(10, 50)
ctx.line_to(256, 320)
ctx.stroke()
```

Drawing a yellow polygon:
```
ctx.set_source_rgb(1, 1, 0)
ctx.move_to(400, 100)
ctx.line_to(500, 50)
ctx.line_to(600, 100)
ctx.line_to(550, 200)
ctx.close_path()
ctx.fill()
```

Drawing a green rectangle:
```
ctx.set_source_rgb(0, 1, 1)
ctx.rectangle(50, 100, 150, 100)
ctx.fill()
```

Drawing a blue circle:
```
ctx.set_source_rgb(0, 0, 1)
ctx.arc(300, 150, 50, 0, 2 * 3.1416)
ctx.fill()
```

Drawing text:
```
ctx.set_source_rgb(0, 0, 0)
ctx.select_font_face("Sans",
    cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
ctx.set_font_size(32)
ctx.move_to(100, 300)
ctx.show_text("Hello, Cairo!")
ctx.stroke()
```

Note the following:
  - When we draw a polygon "manually", we have to call `ctx.close_path()` before we call `ctx.fill()`. When we are drawing circles (with `ctx.arc`) or rectangles (with `ctx.rectangle`) it is not necessary to call `ctx.fill()`.
  - If we don't want to fill, but just want the outline of the circle and rectangle, we could have used `ctx.stroke()` (but in this case we probably want to call `ctx.set_line_width` explicitly).
  - There are much more methods to change the state of the context, see the [Pycairo documentation for the `Context` class](https://pycairo.readthedocs.io/en/latest/reference/context.html).

It is also possible to manipulate the image data of an `ImageSurface` directly.
```
from PIL import Image
import cairo

w, h = 256, 256
with cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h) as surface:
    data = surface.get_data()
    for y in range(0, h):
        for x in range(0, w):
            index = y * surface.get_stride() + x * 4
            c = 0 if (x-128)**2 + (y-128)**2 < 10000 else 255
            data[index] = c        # R
            data[index + 1] = c    # G
            data[index + 2] = c    # B
            data[index + 3] = 255  # A

    img = Image.frombytes("RGBA", (w, h), surface.get_data())

img.show()
img.close()
```


## Exporting the data

### Exporting an image

Some surfaces (`PDFSurface`, `PSSurface`, `SVGSurface`) are explicitly created to write to a file. Any variable `surface` that is an instance of the `Surface` class can also export the surface to a PNG by doing `surface.write_to_png("image.png")`.

Exporting to a SVG file:
```
import cairo

with cairo.SVGSurface("output.svg", 128, 128) as surface:
    ctx = cairo.Context(surface)

    # draw a blue circle
    ctx.set_source_rgb(0, 0, 1)
    ctx.arc(128, 128, 100, 0, 2 * 3.1416)
    ctx.fill()
```

Using an `ImageSurface` and exporting to a PNG:
```
import cairo

w, h = 256, 256
with cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h) as surface:
    ctx = cairo.Context(surface)

    # draw a blue circle
    ctx.set_source_rgb(0, 0, 1)
    ctx.arc(128, 128, 100, 0, 2 * 3.1416)
    ctx.fill()

	ctx.write_to_png("output.png")
```

If we want to show the image from Python, we have to use an external library. For example, using Pillow (`pip install pillow`), we can do
```
from PIL import Image
import cairo

w, h = 256, 256
with cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h) as surface:
    ctx = cairo.Context(surface)

    # draw a blue circle
    ctx.set_source_rgb(0, 0, 1)
    ctx.arc(128, 128, 100, 0, 2 * 3.1416)
    ctx.fill()

    img = Image.frombytes("RGBA", (w, h), surface.get_data())

img.show()
img.close()
```

### Exporting a video

For this, we can use `opencv-python`, which is a library that provides Python bindings for OpenCV. It expects frame as a `numpy` array, so we'll need that library as well:
```
pip install opencv-python numpy
```

Now, to output video, we create a `VideoWriter`:
```
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
videowriter = cv2.VideoWriter(
	'output_video.mp4', fourcc, fps, (w, h))
```

For context: A "fourcc" is an abbreviation for a "four character code" that identifies a codec.

Now, we can write a frame with
```
buf = surface.get_data()
img = np.frombuffer(buf, dtype=np.uint8).reshape((h, w, 4))
img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
```

Once we are done, we call `videowriter.release()` to release the video writer, and our output video is ready.

Complete example:
```
import cairo
import cv2
import numpy as np

w, h = 640, 480
fps = 60
num_frames = 300

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
videowriter = cv2.VideoWriter(
	"output.mp4", fourcc, fps, (w, h))

for frame in range(num_frames):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surface)
    
    # white background
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    # moving red line
    ctx.set_source_rgb(1, 0, 0)
    ctx.set_line_width(5)
    ctx.move_to(50 + frame * 2 , 50)
    ctx.line_to(200 + frame * 2, 50)
    ctx.stroke()

    # convert Cairo surface to OpenCV format
    buf = surface.get_data()
    img = np.frombuffer(buf, dtype=np.uint8).reshape((h, w, 4))
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    videowriter.write(img)

videowriter.release()
```
