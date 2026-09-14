# Portable output

Onsaemiro output remains readable after a notebook session ends and when output is redirected to a file. `Table` and `Progress` expose static `text/plain` and `text/html` representations; neither requires JavaScript or notebook widgets.

| Environment | Representation | Live behaviour |
| --- | --- | --- |
| Jupyter | Static HTML with plain-text fallback | Existing display output is updated |
| Interactive terminal | Unicode text and TTY control sequences | The current output is refreshed in place |
| Redirected stream or log | Plain text only | Intermediate states are suppressed |
| Saved or converted notebook | Stored HTML or text | Final state remains readable without widgets |

## Tables

```python
table = osm.Table(
    "Model comparison",
    columns=["Case", "Error"],
    formatters={"Error": ".3f"},
)
table.add_row("candidate", 0.0184)
table.add_row("baseline", 0.0412)
table.sort("Case")
table.show()
```

Use `to_text()` and `to_html()` for explicit rendering. `to_csv(path)` writes data with the header, and `to_latex(path=None, caption=None, label=None)` returns a booktabs table and optionally writes it.

For changing data, construct `Table(..., mode="live")`, update rows, and call `finish()`. Redirected live output suppresses intermediate states and writes only the final table.

## Progress

Prefer `track()` when iterating over data:

```python
for item in osm.track(items, desc="Processing"):
    process(item)
```

Use `Progress` when work advances manually:

```python
progress = osm.Progress(total=epochs, desc="Training")
for epoch in range(epochs):
    loss = train(epoch)
    progress.set(loss=f"{loss:.4f}")
    progress.update()
progress.finish()
```

`finish()` is idempotent. Calling `update()` after finishing raises `RuntimeError`. Supply `total=` for iterables without `len()`; omit it for indeterminate progress.

## Messages and separators

```python
osm.echo("Reading mesh", tone="info")
osm.echo("Fallback selected", tone="warning")
osm.echo("Run complete", tone="success")
osm.echo("Custom series", color=palette[0], bold=True)
osm.rule("Summary")
```

Supported semantic tones are `info`, `success`, `warning`, `error`, and `muted`. Explicit Matplotlib colours are accepted through `color=`. Colour is discarded for redirected output and when `NO_COLOR` is set or `TERM=dumb`.
