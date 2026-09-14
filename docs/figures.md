# Figures

## Configure presentation defaults

`set_style()` configures typography, line widths, ticks, subplot margins, and the default colour cycle. Its defaults match the Science single-column preset. It changes Matplotlib's global `rcParams`; call `reset_style()` to restore Matplotlib defaults.

```python
osm.set_style(palette="okabe-ito", use_tex=False)
```

Use `set_journal_style()` when a named physical size is the useful starting point:

```python
options = osm.set_journal_style("ieee", column="single")
```

Presets are reproducible defaults, not publisher guarantees. Verify the current author instructions before submission.

| Need | Recommended API |
| --- | --- |
| Default Science single-column figure | `osm.set_style(); osm.subplots()` |
| Named journal style | `osm.set_journal_style(name, column=...)` |
| Dimensions without changing global style | `osm.figsize(name, column=...)` |
| Explicit custom dimensions | `osm.subplots(figsize=(width, height))` |
| Journal-sized local figure | `osm.subplots(journal=name, column=...)` |

## Create layouts

`subplots()` mirrors the useful layout vocabulary of `matplotlib.pyplot.subplots()` and adds stable margins, journal sizing, and concise ratio arguments.

```python
fig, ax = osm.subplots(figsize=(4.0, 3.0))
fig, axes = osm.subplots(2, 2)
fig, axes = osm.subplots(1, 2, widths=[2, 1])
fig, axes = osm.subplots(ncols=2, layout="constrained")
```

Pass either `figsize=` or `journal=`, not both. Use `layout="constrained"` or `layout="compressed"` when Matplotlib should determine spacing; otherwise Onsaemiro applies fixed subplot margins.

| Layout | Example | Use when |
| --- | --- | --- |
| Single panel | `osm.subplots()` | One primary axes is sufficient |
| Uniform grid | `osm.subplots(2, 2)` | Panels share equal space |
| Ratio grid | `osm.subplots(1, 2, widths=[2, 1])` | Panels need different widths |
| Constrained | `osm.subplots(ncols=2, layout="constrained")` | Colour bars or long labels need adaptive spacing |

## Distinguish data series

```python
styles = osm.build_style_map(labels, palette="okabe-ito")
for label, values in series.items():
    ax.plot(x, values, **styles[label], label=label)
```

The returned mapping contains `color`, `linestyle`, and `marker` keys and preserves the first occurrence of each label.

## Finish and export

```python
osm.annotate_panels(axes)
osm.finalize(axes)
paths = osm.export_figure(fig, "figures/result", formats=("pdf", "svg", "png"))
```

The export stem must not include an extension. Vector font settings are applied during export, missing parent directories are created, and `close=True` closes the figure after every requested format is written.
