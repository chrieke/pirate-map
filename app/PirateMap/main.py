import math
import random
from typing import Dict

from colour import Color
from shapely.geometry import Polygon, MultiPolygon, Point
import cairocffi as cairo

from .poisson_disc import poisson_disc
from .xkcd import xkcdify
from . import graph
from . import layers


def make_layer():
    x = layers.Noise(8).add(layers.Constant(0.6)).clamp()
    x = x.translate(random.random() * 1000, random.random() * 1000)
    x = x.scale(0.005, 0.005)
    x = x.subtract(layers.Distance(256, 256, 256))
    return x


def render_shape(dc, shape):
    if shape.is_empty:
        return
    if isinstance(shape, MultiPolygon):
        for child in shape.geoms:
            render_shape(dc, child)
    if isinstance(shape, Polygon):
        dc.new_sub_path()
        for x, y in shape.exterior.coords:
            dc.line_to(x, y)
        dc.close_path()


def render_mark(dc, x, y):
    n = 8
    dc.move_to(x - n, y - n)
    dc.line_to(x + n, y + n)
    dc.move_to(x - n, y + n)
    dc.line_to(x + n, y - n)


def render_compass(dc, scale=1):
    w, h = 4, 32
    w, h = w * scale, h * scale
    dc.line_to(-w, 0)
    dc.line_to(0, h)
    dc.line_to(w, 0)
    dc.line_to(0, -h)
    dc.close_path()
    dc.set_source_rgb(*Color("#FFFFFF").rgb)
    dc.set_line_width(4)
    dc.stroke_preserve()
    dc.fill()
    dc.line_to(-w, 0)
    dc.line_to(w, 0)
    dc.line_to(0, -h)
    dc.close_path()
    dc.set_source_rgb(*Color("#DC3522").rgb)
    dc.fill()
    dc.save()
    dc.translate(0, -h * 3 / 2 - 8)
    w, h = 5, 15
    dc.line_to(-w, h)
    dc.line_to(-w, 0)
    dc.line_to(w, h)
    dc.line_to(w, 0)
    dc.set_source_rgb(*Color("#FFFFFF").rgb)
    dc.stroke()
    dc.restore()


def render_curve(dc, points, alpha):
    items = zip(points, points[1:], points[2:], points[3:])
    # dc.line_to(*points[0])
    # dc.line_to(*points[1])
    for (x1, y1), (x2, y2), (x3, y3), (x4, y4) in items:
        a1 = math.atan2(y2 - y1, x2 - x1)
        a2 = math.atan2(y4 - y3, x4 - x3)
        cx = x2 + math.cos(a1) * alpha
        cy = y2 + math.sin(a1) * alpha
        dx = x3 - math.cos(a2) * alpha
        dy = y3 - math.sin(a2) * alpha
        dc.curve_to(cx, cy, dx, dy, x3, y3)
    # dc.line_to(*points[-1])


def find_path(layer, points, threshold):
    x = layers.Noise(4).add(layers.Constant(0.6)).clamp()
    x = x.translate(random.random() * 1000, random.random() * 1000)
    x = x.scale(0.01, 0.01)
    g = graph.make_graph(points, threshold, x)
    end = max(points, key=lambda p: layer.get(*p))
    points.sort(key=lambda p: math.hypot(p[0] - end[0], p[1] - end[1]))
    for start in reversed(points):
        path = graph.shortest_path(g, end, start)
        if path:
            return path


def render(
    layer_config: Dict,
    seed=1,
    size=512,
    scale=2,
):
    random.seed(seed)  # Globally set in app
    width = height = size
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width * scale, height * scale)
    dc = cairo.Context(surface)
    dc.set_line_cap(cairo.LINE_CAP_ROUND)
    dc.set_line_join(cairo.LINE_JOIN_ROUND)
    dc.scale(scale, scale)
    layer = make_layer()

    # layers: sand, grass, gravel
    points = poisson_disc(0, 0, width, height, 8, 16)
    sand_shape = (
        layer.alpha_shape(points, 0.0, 1, 0.1)
        .buffer(layer_config["sand"]["area"])
        .buffer(4)
    )
    grass_shape = (
        layer.alpha_shape(points, 0.3, 1, 0.1)
        .buffer(layer_config["grass"]["area"])
        .buffer(4)
    )
    gravel_shape = (
        layer.alpha_shape(points, 0.12, 0.28, 0.1)
        .buffer(layer_config["gravel"]["area"])
        .buffer(4)
    )

    # treasure path
    points = [
        x for x in points if sand_shape.contains(Point(*x)) and layer.get(*x) >= 0.25
    ]
    path = find_path(layer, points, 16)
    mark = path[0]

    # water background
    dc.set_source_rgb(*Color("#2185C5").rgb)
    dc.paint()
    # shallow water
    n = 5
    shape = sand_shape.simplify(8).buffer(32).buffer(-16)
    shapes = [shape]
    for _ in range(n):
        shape = shape.simplify(8).buffer(64).buffer(-32)
        shape = xkcdify(shape, 2, 8)
        shapes.append(shape)
    shapes.reverse()
    c1 = Color("#4FA9E1")
    c2 = Color("#2185C5")
    for c, shape in zip(c2.range_to(c1, n), shapes):
        dc.set_source_rgb(*c.rgb)
        render_shape(dc, shape)
        dc.fill()

    # height
    dc.save()
    dc.set_source_rgb(*Color("#CFC291").rgb)
    for _ in range(5):
        render_shape(dc, sand_shape)
        dc.fill()
        dc.translate(0, 1)
    dc.restore()
    # sandy land
    dc.set_source_rgb(*Color(layer_config["sand"]["color"]).rgb)
    render_shape(dc, sand_shape)
    dc.fill()
    # grassy land
    dc.set_source_rgb(*Color(layer_config["grass"]["color"]).rgb)
    render_shape(dc, grass_shape)
    dc.fill()
    # gravel / dark sand
    dc.set_source_rgb(*Color(layer_config["gravel"]["color"]).rgb)
    render_shape(dc, gravel_shape)
    dc.fill()
    # path
    dc.set_source_rgb(*Color("#DC3522").rgb)
    render_curve(dc, path, 4)
    dc.set_dash([4])
    dc.stroke()
    dc.set_dash([])
    # mark
    dc.set_source_rgb(*Color("#DC3522").rgb)
    render_mark(dc, *mark)
    dc.set_line_width(4)
    dc.stroke()
    # compass
    dc.save()
    dc.translate(48, height - 64)
    # rotates compass
    # dc.rotate(random.random() * math.pi / 4 - math.pi / 8)
    render_compass(dc)
    dc.restore()
    return surface
