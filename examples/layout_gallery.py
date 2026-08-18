"""Generate a small Onsaemiro layout and export gallery."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import onsaemiro as osm


def main(output_dir="gallery-output"):
    output = Path(output_dir)
    x = np.linspace(0, 2 * np.pi, 200)

    for journal in ("nature", "science", "ieee", "aps"):
        osm.set_journal_style(journal, column="double")

        with osm.fixed_frame(
            ncols=2,
            gridspec_kw={"width_ratios": [2, 1]},
        ) as (fig, axes):
            axes[0].plot(x, np.sin(x), label="sin(x)")
            axes[0].plot(x, np.cos(x), label="cos(x)")
            axes[0].set(xlabel="x", ylabel="response")
            axes[0].legend()

            palette = osm.get_palette()
            axes[1].bar(
                ["A", "B", "C"],
                [1.0, 1.7, 1.3],
                color=palette[:3],
            )
            axes[1].set_ylabel("score")

            osm.annotate_panels(axes)
            osm.finalize(axes)

        osm.export_figure(fig, output / f"{journal}.pdf", close=True)

    plt.close("all")


if __name__ == "__main__":
    main()
