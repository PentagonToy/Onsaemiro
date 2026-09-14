# Onsaemiro

**Publication-ready figures and portable scientific output for Python.**

Onsaemiro is a small presentation layer for Matplotlib figures, notebook output, and terminal reports. It provides journal-sized layouts, accessible visual styles, tables, progress reporting, and concise status output without wrapping Matplotlib's plotting API.

The default style follows the Science single-column preset. Other journal presets and explicit physical sizes remain available.

## Installation

```bash
pip install onsaemiro
```

## Figures

Create figures directly, then use ordinary Matplotlib methods:

```python
import onsaemiro as osm

osm.set_style(palette="okabe-ito")
fig, ax = osm.subplots(journal="science", column="single")

styles = osm.build_style_map(["baseline", "model"])
ax.plot(x, baseline, **styles["baseline"], label="Baseline")
ax.plot(x, prediction, **styles["model"], label="Model")
osm.finalize(ax)

osm.export_figure(fig, "figures/comparison", formats=("pdf", "png"))
```

`figsize(journal, column)` returns a configured physical size when only the dimensions are needed. Presets are practical starting points; always check the journal's current author instructions.

## Tables and progress

Tables provide both plain-text and HTML representations, so the same object is readable in notebooks, terminals, and redirected logs:

```python
table = osm.Table("Model comparison", ["Case", "RMSE"])
table.add_row("baseline", 0.041)
table.add_row("model", 0.018)
table.show()
```

Use `track()` for iterable work or update a progress object explicitly:

```python
for case in osm.track(cases, desc="Evaluating"):
    evaluate(case)

progress = osm.Progress(total=epochs, desc="Training")
for epoch in range(epochs):
    loss = train(epoch)
    progress.set(loss=f"{loss:.4f}")
    progress.update()
progress.finish()
```

## Terminal output

```python
osm.echo("Run completed", tone="success")
osm.rule("Summary")
```

Colour is used only when the output supports it. Redirected output remains plain, and `NO_COLOR` and `TERM=dumb` are respected.

See the [journal guide](docs/journal.md), [API reference](docs/api.md), and [changelog](CHANGELOG.md) for the complete public surface and release history.
