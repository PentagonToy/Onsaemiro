# Onsaemiro

Onsaemiro is a small scientific presentation layer for publication-ready Matplotlib figures and portable notebook or terminal output. It standardises physical figure sizes, accessible series styles, exports, tables, progress reporting, and status messages while leaving plotting operations to Matplotlib.

## Design promises

- **Ordinary Matplotlib objects:** `subplots()` returns an ordinary figure and axes, so the full Matplotlib API remains available.
- **Portable output:** `Table` and `Progress` provide both `text/plain` and `text/html` representations without widgets or front-end state.
- **Readable logs:** ANSI control sequences are emitted only to interactive terminals; redirected output remains plain text.
- **Accessible distinctions:** `build_style_map()` combines colour, line style, and marker rather than relying on colour alone.
- **Small public surface:** Onsaemiro provides presentation policy, not wrappers for `plot()`, `scatter()`, `contour()`, or domain-specific analysis.

The default style is the Science single-column preset. Select another journal or pass explicit style values when a different target is required.

## Start here

Install Onsaemiro and create a first figure in the [getting-started guide](getting-started.md). Use the [figure guide](figures.md) for layouts and exports, the [portable-output guide](output.md) for tables and progress, and the [API reference](api.md) when exact signatures or return values matter.
