# Journal-oriented figure guide

Onsaemiro presets provide reproducible starting dimensions and typography.
Publisher requirements change, so verify the current author instructions before
submission.

| Preset | Typical use | Single-column width | Double-column width |
|---|---|---:|---:|
| `nature` | Nature-family starting point | 3.50 in | 7.20 in |
| `science` | Science-family starting point | 3.40 in | 7.00 in |
| `ieee` | IEEE two-column papers | 3.50 in | 7.16 in |
| `aps` | APS journals | 3.40 in | 7.00 in |

## Recommended workflow

```python
import matplotlib.pyplot as plt
import onsaemiro as osm

osm.set_journal_style("ieee", column="single")

with osm.fixed_frame() as (fig, ax):
    ax.plot([0, 1], [0, 1])
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Response")
    osm.finalize(ax)

osm.export_figure(fig, "figures/response.pdf")
```

Prefer PDF or SVG for line art and plots. Use PNG for raster-heavy content,
usually at 300 DPI or the journal's requested resolution. `export_figure()`
sets PDF/PS TrueType embedding and creates missing output directories.

## Multi-panel figures

Use fixed fractions when panel geometry must remain identical across figures:

```python
with osm.fixed_frame(nrows=2, ncols=2) as (fig, axes):
    ...
```

Use GridSpec ratios for unequal panels:

```python
with osm.fixed_frame(
    ncols=2,
    gridspec_kw={"width_ratios": [2, 1]},
) as (fig, axes):
    ...
```

Use `layout="constrained"` for figures with colorbars, long labels, or nested
axes where Matplotlib should determine spacing dynamically.

## Submission checklist

- Render the figure at its final physical width.
- Confirm that labels remain legible at 100% scale.
- Check color meaning in grayscale and with a color-vision simulator.
- Avoid relying on color alone; combine color with markers or line styles.
- Inspect PDF/SVG font embedding before submission.
- Confirm panel labels, units, and caption references.
- Follow the journal's current file-format and size limits.

