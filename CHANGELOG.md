# Changelog

This changelog records user-visible Onsaemiro changes in reverse chronological order.

## [1.1.0] - 2026-09-14

### Presentation API

- `subplots()` now creates ordinary Matplotlib figures and axes with stable margins, journal sizing, GridSpec options, and concise width or height ratios.
- `figsize()` returns configured journal dimensions, and the Science single-column preset is the default style.
- `build_style_map()` assigns colour, line style, and marker combinations so plotted series remain distinguishable in greyscale and for colour-vision deficiencies.
- `export_figure()` writes one figure to multiple requested formats from a common extension-free stem.

### Portable output

- `Table` provides plain-text and HTML representations, static or live display, sorting, formatting, CSV export, and booktabs LaTeX export without Rich.
- `Progress` and `track()` provide portable plain-text and HTML progress reporting, optional metrics, throttled updates, explicit `finish()`, and structured context-manager cleanup.
- `echo()` writes semantic or explicitly coloured messages while respecting redirected output, `NO_COLOR`, and `TERM=dumb`; `rule()` writes compact separators.

### Breaking changes

Onsaemiro 1.1 removes compatibility aliases so introspection, documentation, and downstream type checking expose only the supported API.

| Before 1.1 | Onsaemiro 1.1 |
| --- | --- |
| `with osm.fixed_frame() as (fig, ax):` | `fig, ax = osm.subplots()` |
| `osm.TableMaker(...)` | `osm.Table(...)` |
| `table.display()` | `table.show()` |
| `table.close()` | `table.finish()` |
| `osm.ProgressBar(...)` | `osm.Progress(...)` |
| `progress.close()` | `progress.finish()` |
| `export_figure(fig, "figure.pdf")` | `export_figure(fig, "figure", formats=("pdf",))` |

## [1.0.5] - 2026-08-18

- Added journal presets, multi-panel figure layouts, portable progress output, richer table operations, custom palette persistence, and figure export helpers.
