"""Package information utilities."""

import numpy as np
import matplotlib.pyplot as plt

from ._version import __version__, __date__


def info():
    """Print version and dependency info."""
    text = (
        f"Onsaemiro  v{__version__}  ({__date__})\n"
        f"  matplotlib  {plt.matplotlib.__version__}\n"
        f"  numpy       {np.__version__}"
    )
    print(text)
    return text
