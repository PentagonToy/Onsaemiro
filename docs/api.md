# API reference

Onsaemiro keeps its public API small and leaves plotting operations to Matplotlib.

## API index

| Area | API | Purpose | Returns |
| --- | --- | --- | --- |
| Figures | `set_style()` | Apply publication-oriented Matplotlib defaults | `None` |
| Figures | `reset_style()` | Restore Matplotlib defaults | `None` |
| Figures | `journal_preset()` | Read a journal preset | `dict` |
| Figures | `set_journal_style()` | Apply a journal preset | Applied `dict` |
| Figures | `figsize()` | Read a journal figure size | `(width, height)` |
| Figures | `subplots()` | Create an ordinary Matplotlib figure and axes | `(Figure, Axes)` |
| Figures | `export_figure()` | Write one figure in one or more formats | `tuple[Path, ...]` |
| Visual identity | `get_palette()` | Read a named colour palette | `Palette` |
| Visual identity | `build_color_map()` | Assign colours to labels | `dict` |
| Visual identity | `build_style_map()` | Assign colour, line style, and marker combinations | `dict` |
| Visual identity | `register_palette()` | Register a palette for the current process | `Palette` |
| Portable output | `Table()` | Present and export tabular results | `Table` |
| Portable output | `Progress()` | Report manually advanced work | `Progress` |
| Portable output | `track()` | Report iterable progress | `Progress` |
| Portable output | `echo()` | Write a semantic status message | `None` |
| Portable output | `rule()` | Write a horizontal separator | `None` |

`Table` and `Progress` expose both `text/plain` and `text/html` notebook representations. Terminal control sequences are emitted only for interactive terminals.

## Styling and layout

### `set_style`

```python
set_style(base_fontsize=9.5, linewidth=1.0, figure_size=(2.24, 2.20), subplot=None, use_tex=False, auto_scale=True, scale_exponent=0.5, palette="okabe-ito") -> None
```

Update Matplotlib's global presentation defaults. `subplot` may override `left`, `bottom`, `right`, or `top`; `auto_scale` scales typography and strokes from the physical width.

| Parameter | Type | Default | Constraint or meaning |
| --- | --- | --- | --- |
| `base_fontsize` | `float` | `9.5` | Base size before optional width scaling |
| `linewidth` | `float` | `1.0` | Base stroke width before optional scaling |
| `figure_size` | `tuple[float, float]` | `(2.24, 2.20)` | Width and height in inches |
| `subplot` | mapping or `None` | `None` | Overrides fixed `left`, `bottom`, `right`, or `top` fractions |
| `use_tex` | `bool` | `False` | Enable Matplotlib TeX rendering |
| `auto_scale` | `bool` | `True` | Scale typography and strokes from figure width |
| `scale_exponent` | `float` | `0.5` | Width-scaling exponent |
| `palette` | `str` | `"okabe-ito"` | Registered palette name |

### `reset_style`

```python
reset_style() -> None
```

Restore Matplotlib defaults.

### `journal_preset`, `set_journal_style`, and `figsize`

```python
journal_preset(name="science", column="single") -> dict[str, object]
set_journal_style(name="science", column="single", **overrides) -> dict[str, object]
figsize(name="science", column="single") -> tuple[float, float]
```

Supported journal names are `nature`, `science`, `ieee`, and `aps`; supported column widths are `single` and `double`. `set_journal_style()` returns the applied options.

| Parameter | Type | Default | Allowed values |
| --- | --- | --- | --- |
| `name` | `str` | `"science"` | `science`, `nature`, `ieee`, or `aps` |
| `column` | `str` | `"single"` | `single` or `double` |

### `subplots`

```python
subplots(nrows=1, ncols=1, *, figsize=None, journal=None, column="single", subplot=None, gridspec_kw=None, widths=None, heights=None, squeeze=True, layout=None, **subplot_kw) -> tuple[Figure, Axes | ndarray]
```

Create ordinary Matplotlib objects. `widths` and `heights` are concise forms of GridSpec's `width_ratios` and `height_ratios`; do not supply both forms for the same dimension.

| Parameter | Default | Meaning |
| --- | --- | --- |
| `nrows`, `ncols` | `1`, `1` | Subplot grid dimensions |
| `figsize` | `None` | Explicit physical size in inches |
| `journal`, `column` | `None`, `"single"` | Optional journal-derived size |
| `subplot` | `None` | Fixed margin overrides |
| `gridspec_kw` | `None` | Matplotlib GridSpec options |
| `widths`, `heights` | `None` | Concise panel-ratio lists |
| `squeeze` | `True` | Apply Matplotlib axes squeezing |
| `layout` | `None` | Matplotlib layout engine name |

### `export_figure`

```python
export_figure(fig, stem, *, formats=("pdf", "png"), dpi=300, transparent=False, bbox_inches="tight", metadata=None, close=False, **savefig_kw) -> tuple[Path, ...]
```

Write every requested format. `stem` must not contain a suffix.

## Palettes

### `get_palette`

```python
get_palette(palette="okabe-ito", n=None) -> Palette
```

Return a palette with index, slice, and colour-name access. Built-in names include `okabe-ito`, `tableau10`, `paul-tol-vibrant`, `paul-tol-bright`, `paul-tol-muted`, and `ibm`.

### `build_color_map` and `build_style_map`

```python
build_color_map(labels, palette="okabe-ito") -> dict[object, str]
build_style_map(labels, palette="okabe-ito") -> dict[object, dict[str, str]]
```

Map labels in first-occurrence order. `build_style_map()` returns keyword dictionaries accepted by `Axes.plot()`.

### Custom palettes

```python
register_palette(name, colors, names=None, *, overwrite=False) -> Palette
save_palette(name, path) -> Path
load_palette(path, *, name=None, overwrite=False) -> Palette
```

`colors` may be a mapping of names to Matplotlib colours or an iterable accompanied by `names`.

## `Table`

```python
Table(title="Analysis", columns=None, mode="static", *, formatters=None)
```

`mode` is `static`, `live`, or `dynamic`. Public methods are `add_row()`, `update_row()`, `sort()`, `show()`, `finish()`, `to_text()`, `to_html()`, `to_csv()`, and `to_latex()`.

| Mode | Intermediate updates | Final redirected output |
| --- | --- | --- |
| `static` | None | Written by `show()` |
| `live` | Updated in a terminal or notebook | Written once by `finish()` |
| `dynamic` | Same behaviour as `live` | Written once by `finish()` |

Rows must match the configured column count. Formatters may be keyed by column name or index and may be format specifications or callables.

## `Progress` and `track`

```python
Progress(iterable=None, total=None, desc="", width=40, mininterval=0.1, smoothing=0.3)
track(iterable=None, **kwargs) -> Progress
```

Public methods are `update(n=1)`, `set_description(desc)`, `set(**metrics)`, `finish()`, `to_text()`, and `to_html()`. `Progress` also implements the context-manager protocol for structured cleanup around manually advanced work. `total` must be a non-negative integer or `None`; `width` must be positive; `smoothing` must be between zero and one.

| Parameter | Type | Default | Constraint or meaning |
| --- | --- | --- | --- |
| `iterable` | iterable or `None` | `None` | Source consumed by iteration |
| `total` | `int` or `None` | Inferred | Non-negative; required for sized progress when length cannot be inferred |
| `desc` | `str` | `""` | Prefix label |
| `width` | `int` | `40` | Positive terminal bar width |
| `mininterval` | `float` | `0.1` | Non-negative minimum refresh interval in seconds |
| `smoothing` | `float` | `0.3` | Rate smoothing from `0` to `1` |

## Terminal output

### `echo`

```python
echo(message, *, tone=None, color=None, bold=False, file=None) -> None
```

Write a semantic or explicitly coloured message. `tone` and `color` are mutually composable in the sense that explicit `color` takes precedence.

| Tone | Intended use |
| --- | --- |
| `info` | Neutral activity or context |
| `success` | Successful completion |
| `warning` | Recoverable concern or fallback |
| `error` | Failed operation |
| `muted` | Secondary information |

### `rule`

```python
rule(title="", *, width=None, file=None) -> None
```

Write a centred title and horizontal separator using the requested width or the detected terminal width.
