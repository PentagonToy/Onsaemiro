# Getting started

## Installation

Onsaemiro requires Python 3.10 or newer.

```bash
python -m pip install onsaemiro
```

Install the documentation dependencies only when building this site locally:

```bash
python -m pip install "onsaemiro[docs]"
mkdocs serve
```

## First figure

```python
import numpy as np
import onsaemiro as osm

x = np.linspace(0.0, 2.0 * np.pi, 200)
styles = osm.build_style_map(["sin", "cos"])

osm.set_style()
fig, ax = osm.subplots()
ax.plot(x, np.sin(x), **styles["sin"], label="sin(x)")
ax.plot(x, np.cos(x), **styles["cos"], label="cos(x)")
ax.set(xlabel="x", ylabel="response")
osm.finalize(ax)

outputs = osm.export_figure(fig, "figures/trigonometry", formats=("pdf", "png"))
```

`outputs` is a tuple containing the written paths. Parent directories are created automatically.

`set_style()` uses the Science single-column preset by default. Use `set_journal_style("nature")`, another named preset, or explicit values when targeting different author instructions.

## First portable report

```python
table = osm.Table("Errors", columns=["Model", "RMSE"])
table.add_row("baseline", 0.041)
table.add_row("candidate", 0.018)
table.show()

for case in osm.track(cases, desc="Evaluating"):
    evaluate(case)

osm.echo("Evaluation complete", tone="success")
```

The table and progress output render as HTML in Jupyter and plain text in terminals and logs.
