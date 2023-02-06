""" Display function codes"""
import warnings
from contextlib import contextmanager
from importlib import import_module

from magpylib._src.display.traces_generic import get_frames
from magpylib._src.display.traces_generic import MagpyMarkers
from magpylib._src.display.traces_utility import process_show_input_objs
from magpylib._src.input_checks import check_dimensions
from magpylib._src.input_checks import check_excitations
from magpylib._src.input_checks import check_format_input_backend
from magpylib._src.input_checks import check_format_input_vector
from magpylib._src.input_checks import check_input_animation
from magpylib._src.input_checks import check_input_zoom
from magpylib._src.utility import test_path_format


class RegisterBackend:
    """Base class for display backends"""

    backends = {}

    def __init__(
        self,
        *,
        name,
        show_func,
        supports_animation,
        supports_subplots,
        supports_colorgradient,
    ):
        self.name = name
        self.show_func = show_func
        self.supports = {
            "animation": supports_animation,
            "subplots": supports_subplots,
            "colorgradient": supports_colorgradient,
        }
        self._register_backend(name)

    def _register_backend(self, name):
        self.backends[name] = self

    @classmethod
    def show(
        cls,
        *objs,
        backend,
        zoom=0,
        max_rows=None,
        max_cols=None,
        subplot_specs=None,
        **kwargs,
    ):
        """Display function of the current backend"""
        self = cls.backends[backend]
        conditions = {
            "animation": {"animation": False},
            "subplots": {"row": None, "col": None},
        }
        for name, params in conditions.items():
            condition = not all(kwargs.get(k, v) == v for k, v in params.items())
            if condition and not self.supports[name]:
                supported = [k for k, v in self.backends.items() if v.supports[name]]
                warnings.warn(
                    f"The {backend} backend does not support {name}, "
                    f"you can use one of {supported} backends instead."
                    f"\nfalling back to: {params}"
                )
                kwargs.update(params)
        data = get_frames(
            objs,
            supports_colorgradient=self.supports["colorgradient"],
            backend=backend,
            **kwargs,
        )
        kwargs.pop("animation", None)
        self.show_func()(
            data,
            zoom=zoom,
            max_rows=max_rows,
            max_cols=max_cols,
            subplot_specs=subplot_specs,
            **kwargs,
        )


def get_show_func(backend):
    """Return the bakcend show function"""
    # defer import to show call. Importerror should only fail if unavalaible backend is called
    return lambda: getattr(
        import_module(f"magpylib._src.display.backend_{backend}"), f"display_{backend}"
    )


RegisterBackend(
    name="matplotlib",
    show_func=get_show_func("matplotlib"),
    supports_animation=True,
    supports_subplots=True,
    supports_colorgradient=False,
)


RegisterBackend(
    name="plotly",
    show_func=get_show_func("plotly"),
    supports_animation=True,
    supports_subplots=True,
    supports_colorgradient=True,
)

RegisterBackend(
    name="pyvista",
    show_func=get_show_func("pyvista"),
    supports_animation=True,
    supports_subplots=True,
    supports_colorgradient=True,
)


class DisplayContext:
    """Display context class"""

    def __init__(self, isrunning=False):
        self.isrunning = isrunning
        self.objects = ()
        self.objects_from_ctx = ()
        self.kwargs = {}
        self.canvas = None

    def reset(self):
        """Reset display context"""
        self.isrunning = False
        self.objects = ()
        self.objects_from_ctx = ()
        self.kwargs = {}


ctx = DisplayContext()


RCO_NAMES = ("row", "col", "output", "sumup", "pixel_agg")


def _show(
    *objects,
    zoom=0,
    animation=False,
    markers=None,
    backend=None,
    **kwargs,
):
    """Display objects and paths graphically.

    See `show` function for docstring details.
    """

    # process input objs
    objects, obj_list_flat, max_rows, max_cols, subplot_specs = process_show_input_objs(
        objects, **{k: v for k, v in kwargs.items() if k in RCO_NAMES}
    )
    kwargs = {k: v for k, v in kwargs.items() if k not in RCO_NAMES}
    kwargs["max_rows"], kwargs["max_cols"] = max_rows, max_cols
    kwargs["subplot_specs"] = subplot_specs

    # test if all source dimensions and excitations have been initialized
    check_dimensions(obj_list_flat)
    check_excitations(obj_list_flat)

    # test if every individual obj_path is good
    test_path_format(obj_list_flat)

    # input checks
    backend = check_format_input_backend(backend)
    check_input_zoom(zoom)
    check_input_animation(animation)
    check_format_input_vector(
        markers,
        dims=(2,),
        shape_m1=3,
        sig_name="markers",
        sig_type="array_like of shape (n,3)",
        allow_None=True,
    )

    if markers:
        objects = list(objects) + [
            {
                "objects": [MagpyMarkers(*markers)],
                "row": 1,
                "col": 1,
                "output": "model3d",
            }
        ]

    return RegisterBackend.show(
        backend=backend,
        *objects,
        zoom=zoom,
        animation=animation,
        **kwargs,
    )


def show(*objects, **kwargs):
    """Display objects and paths graphically.

    Global graphic styles can be set with kwargs as style dictionary or using
    style underscore magic.

    Parameters
    ----------
    objects: Magpylib objects (sources, collections, sensors)
        Objects to be displayed.

    zoom: float, default=`0`
        Adjust plot zoom-level. When zoom=0 3D-figure boundaries are tight.

    animation: bool or float, default=`False`
        If `True` and at least one object has a path, the paths are rendered.
        If input is a positive float, the animation time is set to the given value.
        This feature is only available for the plotly backend.

    markers: array_like, shape (n,3), default=`None`
        Display position markers in the global coordinate system.

    backend: string, default=`None`
        Define plotting backend. Must be one of `'matplotlib'`, `'plotly'`. If not
        set, parameter will default to `magpylib.defaults.display.backend` which is
        `'matplotlib'` by installation default.

    canvas: matplotlib.pyplot `AxesSubplot` or plotly `Figure` object, default=`None`
        Display graphical output on a given canvas:
        - with matplotlib: `matplotlib.axes._subplots.AxesSubplot` with `projection=3d.
        - with plotly: `plotly.graph_objects.Figure` or `plotly.graph_objects.FigureWidget`.
        By default a new canvas is created and immediately displayed.

    return_fig: bool, default=False
        If True, the function call returns the figure object.
        - with matplotlib: `matplotlib.figure.Figure`.
        - with plotly: `plotly.graph_objects.Figure` or `plotly.graph_objects.FigureWidget`.
        - with pyvista: `pyvista.Plotter`.

    Returns
    -------
    `None` or figure object

    Examples
    --------

    Display multiple objects, object paths, markers in 3D using Matplotlib or Plotly:

    >>> import magpylib as magpy
    >>> src = magpy.magnet.Sphere(magnetization=(0,0,1), diameter=1)
    >>> src.move([(0.1*x,0,0) for x in range(50)])
    Sphere...
    >>> src.rotate_from_angax(angle=[*range(0,400,10)], axis='z', anchor=0, start=11)
    Sphere...
    >>> ts = [-.4,0,.4]
    >>> sens = magpy.Sensor(position=(0,0,2), pixel=[(x,y,0) for x in ts for y in ts])
    >>> magpy.show(src, sens) # doctest: +SKIP
    >>> magpy.show(src, sens, backend='plotly') # doctest: +SKIP
    >>> # graphic output

    Display output on your own canvas (here a Matplotlib 3d-axes):

    >>> import matplotlib.pyplot as plt
    >>> import magpylib as magpy
    >>> my_axis = plt.axes(projection='3d')
    >>> magnet = magpy.magnet.Cuboid(magnetization=(1,1,1), dimension=(1,2,3))
    >>> sens = magpy.Sensor(position=(0,0,3))
    >>> magpy.show(magnet, sens, canvas=my_axis, zoom=1)
    >>> plt.show() # doctest: +SKIP
    >>> # graphic output

    Use sophisticated figure styling options accessible from defaults, as individual object styles
    or as global style arguments in display.

    >>> import magpylib as magpy
    >>> src1 = magpy.magnet.Sphere((1,1,1), 1, [(0,0,0), (0,0,3)])
    >>> src2 = magpy.magnet.Sphere((1,1,1), 1, [(1,0,0), (1,0,3)], style_path_show=False)
    >>> magpy.defaults.display.style.magnet.magnetization.size = 2
    >>> src1.style.magnetization.size = 1
    >>> magpy.show(src1, src2, style_color='r') # doctest: +SKIP
    >>> # graphic output

    Use a context manager to jointly animate 3d and 2d subplots

    >>> import magpylib as magpy
    >>> import numpy as np
    >>> import plotly.graph_objects as go
    >>> path_len = 40
    >>> sensor = magpy.Sensor()
    >>> cyl1 = magpy.magnet.Cylinder(
    ...    magnetization=(100, 0, 0),
    ...    dimension=(1, 2),
    ...    position=(4, 0, 0),
    ...    style_label="Cylinder1",
    ... )
    >>> sensor.move(np.linspace((0, 0, -3), (0, 0, 3), path_len), start=0)
    Sensor(id=...)
    >>> cyl1.rotate_from_angax(angle=np.linspace(0, 300, path_len), start=0, axis="z", anchor=0)
    Cylinder(id=...)
    >>> cyl2 = cyl1.copy().move((0, 0, 5))
    >>> fig = go.Figure()
    >>> with magpy.show_context(cyl1, cyl2, sensor, canvas=fig, backend="plotly", animation=True):
    ...    magpy.show(col=1, output="model3d")
    ...    magpy.show(col=2, output="Bxy", sumup=True)
    ...    magpy.show(col=3, output="Bz", sumup=False)
    >>> fig.show() # doctest: +SKIP
    >>> # graphic output
    """

    if ctx.isrunning:
        rco = {k: v for k, v in kwargs.items() if k in RCO_NAMES}
        ctx.kwargs.update({k: v for k, v in kwargs.items() if k not in RCO_NAMES})
        ctx_objects = tuple({**o, **rco} for o in ctx.objects_from_ctx)
        objects, *_ = process_show_input_objs(ctx_objects + objects, **rco)
        ctx.objects += tuple(objects)
        return None
    return _show(*objects, **kwargs)


@contextmanager
def show_context(*objects, **kwargs):
    """Context manager to temporarily set display settings in the `with` statement context.

    You need to invoke as ``show_context(pattern1=value1, pattern2=value2)``.
    """
    # pylint: disable=protected-access
    try:
        ctx.isrunning = True
        rco = {k: v for k, v in kwargs.items() if k in RCO_NAMES}
        objects, *_ = process_show_input_objs(objects, **rco)
        ctx.objects_from_ctx += tuple(objects)
        ctx.kwargs.update({k: v for k, v in kwargs.items() if k not in RCO_NAMES})
        yield ctx
        _show(*ctx.objects, **ctx.kwargs)
    finally:
        ctx.reset()
