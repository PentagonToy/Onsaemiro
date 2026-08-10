"""Colour palettes and colour mapping utilities."""

import warnings

import numpy as np


_PALETTES = {
    "tableau10": {
        "colors": [
            "#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
            "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac",
        ],
        "names": [
            "blue", "orange", "red", "teal", "green",
            "yellow", "purple", "pink", "brown", "grey",
        ],
    },
    "okabe-ito": {
        "colors": [
            "#0072B2", "#E69F00", "#D55E00", "#009E73",
            "#56B4E9", "#F0E442", "#CC79A7", "#000000",
        ],
        "names": [
            "blue", "orange", "red", "green",
            "cyan", "yellow", "purple", "black",
        ],
    },
    "paul-tol-vibrant": {
        "colors": [
            "#0077BB", "#33BBEE", "#009988", "#EE7733",
            "#CC3311", "#EE3377", "#BBBBBB",
        ],
        "names": [
            "blue", "cyan", "teal", "orange",
            "red", "magenta", "grey",
        ],
    },
    "paul-tol-bright": {
        "colors": [
            "#4477AA", "#EE6677", "#228833", "#CCBB44",
            "#66CCEE", "#AA3377", "#BBBBBB",
        ],
        "names": [
            "blue", "red", "green", "yellow",
            "cyan", "purple", "grey",
        ],
    },
    "paul-tol-muted": {
        "colors": [
            "#332288", "#88CCEE", "#44AA99", "#117733",
            "#999933", "#DDCC77", "#CC6677", "#882255", "#AA4499",
        ],
        "names": [
            "indigo", "cyan", "teal", "green",
            "olive", "sand", "rose", "wine", "purple",
        ],
    },
    "ibm": {
        "colors": ["#648FFF", "#785EF0", "#DC267F", "#FE6100", "#FFB000"],
        "names": ["blue", "indigo", "magenta", "orange", "gold"],
    },
}


class Palette:
    """Colour palette with both name-based and index-based access."""

    def __init__(self, names, colors):
        self._names = list(names)
        self._colors = list(colors)
        self._map = dict(zip(self._names, self._colors))

    def __repr__(self):
        pairs = ", ".join(f"{n}={c}" for n, c in zip(self._names, self._colors))
        return f"Palette({pairs})"

    def __getitem__(self, key):
        if isinstance(key, (int, np.integer)):
            return self._colors[key % len(self._colors)]
        if isinstance(key, slice):
            return self._colors[key]
        if isinstance(key, str):
            return self._map[key.lower()]
        raise KeyError(key)

    def __contains__(self, key):
        if isinstance(key, str):
            return key.lower() in self._map
        if isinstance(key, (int, np.integer)):
            return -len(self._colors) <= key < len(self._colors)
        return False

    def __iter__(self):
        return iter(self._colors)

    def __len__(self):
        return len(self._colors)

    def keys(self):
        return self._map.keys()

    def values(self):
        return self._map.values()

    def items(self):
        return self._map.items()


def _resolve_palette(name):
    p = str(name).lower()
    if "vibrant" in p:                return "paul-tol-vibrant"
    if "bright" in p:                 return "paul-tol-bright"
    if "muted" in p:                  return "paul-tol-muted"
    if "tol" in p or "paul" in p:     return "paul-tol-vibrant"
    if "tab" in p or "tableau" in p:  return "tableau10"
    if "ibm" in p:                    return "ibm"
    if "okabe" in p or "ito" in p:    return "okabe-ito"
    warnings.warn(
        f"Unrecognised palette name {name!r}; falling back to 'okabe-ito'. "
        f"Known palettes: {sorted(_PALETTES)}",
        UserWarning,
        stacklevel=3,
    )
    return "okabe-ito"


def get_palette(palette="okabe-ito", n=None):
    """Return a Palette object. Supports fuzzy name matching."""
    key = _resolve_palette(palette)
    entry = _PALETTES[key]
    limit = len(entry["colors"]) if n is None else min(n, len(entry["colors"]))
    return Palette(entry["names"][:limit], entry["colors"][:limit])


def build_color_map(labels, palette="okabe-ito"):
    """Map unique labels to palette colours."""
    pal = get_palette(palette=palette)
    return {lab: pal[i] for i, lab in enumerate(labels)}
