# Onsaemiro

**Publication-quality matplotlib styling for Academic Research.**

Onsaemiro provides a streamlined interface for generating figures that meet the rigorous standards of scientific journals. It handles font scaling, consistent subplot positioning, colour-blind friendly palettes, and GitHub-safe progress bars — all with minimal boilerplate.

***

## Key Features

* **Fixed-Fraction Layout**: Prevents axes jumping between figures by enforcing consistent subplot dimensions.
* **Automatic Scaling**: Adjusts font sizes, line widths, and tick marks based on the physical figure width.
* **Academic Palettes**: Built-in support for Okabe-Ito, Paul Tol (Vibrant, Muted, Bright), and IBM palettes.
* **TableMaker**: Renders LaTeX-style "booktabs" tables directly in Jupyter notebooks or the terminal.
* **ProgressBar / `track()`**: Static-HTML progress bar that survives GitHub's notebook renderer — no ipywidgets required.
* **Context Management**: Use `fixed_frame` for one-off figures with specific dimensions without affecting global settings.

***

## Installation

Install Onsaemiro from PyPI:

```bash
pip install onsaemiro
```

The package is published on PyPI and can also be installed directly from a local clone.

For local development, clone the repository, move into the package directory, and run:

```bash
pip install -e .
```

The `-e` (editable) flag means changes to the Onsaemiro source are reflected immediately — no reinstall needed.

***

## Quick Start

```python
import onsaemiro as osm
import matplotlib.pyplot as plt
import numpy as np

# 1. Global setup
osm.set_style(figure_size=(3.5, 2.5), palette="okabe-ito")

# 2. Get the palette
colors = osm.get_palette()

# 3. Plotting
x = np.linspace(0, 10, 100)
fig, ax = plt.subplots()

ax.plot(x, np.sin(x), color=colors['blue'], label='Signal A')
ax.plot(x, np.cos(x), color=colors['orange'], label='Signal B')

ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude (V)')
ax.legend()

# 4. Finalise (handles legend borders and origin overlaps)
osm.finalize(ax)
plt.show()
```

***

## Core Components

### 1. Global Styling (`set_style`)

Configures `plt.rcParams` for publication. Unlike standard matplotlib behaviour, it disables `autolayout` to ensure that labels do not shift the axes box. Defaults to a Times-style serif font.

```python
osm.set_style(
    base_fontsize=12.5,
    linewidth=1.2,
    figure_size=(3.5, 2.5),
    use_tex=False
)
```

### 2. Colour Palettes (`Palette`)

Access colours by name or index. Supports fuzzy name matching.

* `okabe-ito` (Default, colour-blind safe)
* `paul-tol-vibrant` | `paul-tol-bright` | `paul-tol-muted`
* `ibm`
* `tableau10`

```python
p = osm.get_palette("vibrant")
color = p['red']    # Name access
color = p[0]        # Index access (wraps around)
```

### 3. Layout Control (`fixed_frame`)

A context manager for creating figures with precise axes placement.

```python
with osm.fixed_frame(figure_size=(5, 4)) as (fig, ax):
    ax.scatter(data_x, data_y)
    # Axes position is determined by internal fractions,
    # ensuring consistent whitespace across different plots.
```

### 4. TableMaker

Creates professional tables for results analysis. In Jupyter, renders a monochrome theme inspired by academic journals (booktabs style). In terminals, renders via `rich`.

```python
table = osm.TableMaker(
    title="Performance Metrics",
    columns=["Metric", "Result", "Unit"]
)
table.add_row("R-Squared", "0.9942", "—")
table.add_row("RMSE", "0.021", "m/s")
table.display()
```

For live updates during a loop (e.g. training), use `mode="live"`:

```python
table = osm.TableMaker(title="Training Log", columns=["Epoch", "Loss"], mode="live")
for epoch in range(10):
    loss = train_one_epoch()
    table.add_row(str(epoch), f"{loss:.4f}")
```

### 5. ProgressBar and `track()`

A static-HTML progress bar designed for Jupyter notebooks. Unlike `tqdm.auto`, it renders as plain `text/html` output — so the **completed bar is preserved when notebooks are committed to GitHub**, rather than showing an empty widget placeholder.

#### Simple iterator (tqdm-style)

```python
for x in osm.track(range(1000), desc="Training"):
    osm.sleep(0.001)
```

#### Context manager (manual `update`)

Use this when the loop body controls iteration (e.g. custom data loaders).

```python
with osm.ProgressBar(total=N, desc="Sweep") as pb:
    for i in range(N):
        compute(i)
        pb.update()
```

#### Joblib parallel jobs

When using `joblib.Parallel`, pass `return_as="generator"` and wrap with `osm.track()`.
Results are yielded as each job completes, so the progress bar advances in real time.

```python
from joblib import Parallel, delayed

def process(i):
    osm.sleep(0.05)   # simulate work
    return i ** 2

results = list(
    osm.track(
        Parallel(n_jobs=-1, return_as="generator")(
            delayed(process)(i) for i in range(100)
        ),
        total=100,
        desc="Parallel",
    )
)
```

> **Note**: `return_as="generator"` requires joblib ≥ 1.2. The progress bar advances as
> jobs *complete*, not as they are dispatched — so the count accurately reflects finished work.

#### Key parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `iterable` | `None` | Wrap any iterable for iterator-style use |
| `total` | `len(iterable)` | Total iterations (required when `iterable` has no `len`) |
| `desc` | `""` | Prefix label shown before the bar |
| `mininterval` | `0.1` s | Minimum time between HTML refreshes — prevents rendering from bottlenecking tight loops |
| `width` | `40` | Bar width in characters (terminal mode only) |

***

## API Reference

| Function / Class | Description |
|------------------|-------------|
| `set_style(...)` | Initialises global matplotlib parameters. |
| `reset_style()` | Restores matplotlib defaults. |
| `get_palette(name)` | Returns a `Palette` object with fuzzy name matching. |
| `build_color_map(labels)` | Maps a list of unique labels to palette colours. |
| `finalize(ax)` | Polishes the plot: legend frames, origin overlaps, optional grid/minor ticks. |
| `fixed_frame(...)` | Context manager for isolated figure styling with fixed axes placement. |
| `annotate_panels(axes)` | Automatically adds `(a)`, `(b)`, `(c)` labels to subplots. |
| `style_colorbar(cb)` | Applies publication styling to a colorbar. |
| `enable_minor_ticks(ax)` | Adds AutoMinorLocator ticks to both axes. |
| `apply_grid(ax)` | Adds a subtle dotted grid. |
| `TableMaker(...)` | Renders academic-style tables in the console or Jupyter. |
| `ProgressBar(...)` | Static-HTML progress bar; GitHub-safe in Jupyter. |
| `track(iterable)` | `tqdm`-style shorthand for `ProgressBar`. |
| `sleep(s)` | Re-export of `time.sleep` — avoids a separate import in notebooks. |
| `info()` | Prints version and dependency information. |

***

## Version History

* **v1.0.0 (24 Jul 2026)**: Initial Onsaemiro release, based on the final DataGraph 3.1.0 implementation.

***

*Created and maintained by Hanseul Kang.*
