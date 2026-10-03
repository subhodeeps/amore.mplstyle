# `amore` - yet another MPL Stylesheet

This repository presents `amore`, an opinionated Matplotlib plotting style developed over the last couple of years while working on figures for my research. It features LaTeX-rendered text, heavy plot frames, inward ticks, 32 muted colours across 8 palettes, custom colormaps, and small helper functions for shaded regions, insets, colour bars, and figure saving.

<p align="center">
  <img src="docs/figures/amore_blue.png" width="49%" alt="Example figure in the blue palette">
  <img src="docs/figures/amore_teal.png" width="49%" alt="Example figure in the teal, amber and plum palettes">
</p>
<p align="center">
  <img src="docs/figures/amore_green.png" width="49%" alt="Example contour figure with the diverging red and green map: the potential of test charges near two extremal black holes">
  <img src="docs/figures/amore_parula.png" width="49%" alt="Example density plot with contours in the fakeparulapastel map: the curvature invariant of a Kerr black hole">
</p>

<p align="center">
  <img src="docs/figures/amore_corner.png" width="70%" alt="Example corner plot in the plum, olive, teal and amber palettes">
  <img src="docs/figures/amore_chirikov.png" width="27.5%" alt="Example phase-space plot of the Chirikov standard map at K = 0.971635 in all 32 colours">
</p>

<p align="center">
  <img src="docs/figures/amore_pendulum.png" width="98%" alt="Example phase portrait of the pendulum: teal streamlines and red orbits">
</p>

<p align="center">
  <img src="docs/figures/amore_diffraction.png" width="98%" alt="Example Fresnel diffraction of a double slit in the afmhot10us map: amplitude map, and the cut along its axis with the single-slit envelope">
</p>

<p align="center">
  <img src="docs/figures/amore_airy.png" width="98%" alt="Example Airy pattern of a circular aperture in the grey afmhot10us map on a log scale, and two point sources at and below the Rayleigh limit in the afmhot10us colour map">
</p>

The 32 colours, with their hex codes and lightness:

<p align="center">
  <img src="docs/figures/amore_palettes.png" width="80%" alt="All 32 colours of the amore palettes, with their hex codes, lightness and colour maps">
</p>

## Install

You need Python 3.10 or newer. For the text, the style needs LaTeX (`latex` and `dvipng`, with
the TeX packages `type1cm`, `cm-super` and `amsmath`).

```bash
git clone https://github.com/subhodeeps/amore.mplstyle.git
cd amore
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
```

## Use

```python
import amore
import matplotlib.pyplot as plt

amore.use()                                   # apply the style to all figures after this call
c = amore.palette("blue")                     # tones: ink, main, light, shade
fig, ax = amore.figure()                      # the standard plot area
ax.plot(x, y, color=c["main"])
amore.shade(ax, x0, x1, "transient", palette="blue")
amore.save(fig, "path/without/suffix")        # writes a PDF and a PNG
```

The functions are `use`, `figure`, `palette`, `cmap`, `diverging`, `fakeparulapastel`,
`afmhot10us`, `afmhot10usgrey`, `colorbar`, `shade`, `inset`, `tag` and `save`. `docs/plotting_guide.md` has the rules and the
colour theory guidelines. `src/amore/examples.py` makes every figure above; read it before you
make your first figure.

## Check that it works

The tests are in `tests/`. Two ways to run them.

**With the script.** It makes `.venv`, installs the package, and runs the tests:

```bash
scripts/check.sh               # install and run the tests
scripts/check.sh --examples    # also regenerate the example figures (about 40 s; needs LaTeX)
```

**By hand.** These are the same steps:

```bash
python3 --version                           # 3.10 or newer
latex --version && dvipng --version         # LaTeX; without it, the figure-drawing tests skip
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"                    # pytest and scipy; add ",examples" for corner too
pytest -q -rs                               # -rs shows the reason for each skip
```

What the tests check:

- `tests/test_amore.py`: at least 30 colours, four hex tones in each palette, a colour map for
  each palette, the lightness steps inside each palette, the contrast of each ink, the distance
  between palettes, the `fakeparulapastel`, afmhot and diverging maps, the colour bar above the plot,
  the neutral overlay grey, the style file (LaTeX and the frame), the exact figure size, and
  the drawing and saving of a figure as PDF and PNG. The test that draws a figure needs LaTeX;
  without it, it SKIPs, and a skip is not a pass.
- `tests/test_examples_physics.py`: the physics behind the examples. The black hole figure
  (field of test charges near extremal black holes: Maxwell's equation, the flux through each
  horizon, and a possible correction to Eq. (4.14) of Frolov and Zelnikov), the standard map (area
  conservation, repeatability, colours from the palettes), the pendulum solver (energy
  conservation), the double-slit diffraction (energy, the single-slit sinc, the fringe spacing),
  and the Airy pattern (the enclosed energy, the FFT of a circular aperture, the Rayleigh dip).
  It needs `numpy`, `matplotlib` and `scipy`; the `test` extra installs them.

All tests pass: `pytest` prints `passed`, with no failures. If the output says `skipped`, run
`pytest -rs` to see the reason.

## Regenerate the examples

```bash
pip install -e ".[examples]"      # scipy and corner
python -m amore.examples          # writes docs/figures/*.png and *.pdf (about 40 s)
```

The PNGs are the same bytes on each run. The PDFs are not (TeX font subsets get a random name),
and they are large, so `.gitignore` leaves them out.

## Layout

```
src/amore/
    __init__.py       palettes, colour maps and helpers
    amore.mplstyle    fonts, colour cycle, frame, ticks, grid
    data/             the afmhot_10us colour table
    examples.py       the example figures and the palette chart
tests/                pytest tests
scripts/check.sh      install and run the tests
docs/                 figures and the plotting guide
```

## Colours, sources and credits

Every data colour in the examples is one of the 32 colours. The neutrals (black, white, grey,
`amore.OVERLAY`) and the interpolated colour maps are not. `fakeparulapastel` is a separate map:
a pastel version of the "fake parula" map of
[BIDS/colormap](https://github.com/BIDS/colormap) (CC0, by Nathaniel Smith and Stefan van der
Walt); MATLAB's own parula belongs to MathWorks and is not used.
`afmhot10us` is the `afmhot_10us` map of [ehtplot](https://github.com/liamedeiros/ehtplot) (Chi-kwan Chan, Steward Observatory, GPL-3.0; commit `7a05674`), and `afmhot10usgrey` is its grey version, with the same lightness at every point. The double-slit example follows a post by Rafael de la Fuente (2020) and Goodman, *Introduction to Fourier Optics*, sec. 3.5. The Airy-ring example uses the expression of problem P8.1.2 in Christian Hill, *Learning Scientific Programming with Python* (2nd edition, [scipython.com](https://scipython.com/books/book2/chapter-8-scipy/problems/the-airy-disc/), CC BY 4.0), adapted here.
The docstring of each example
cites its sources (papers, a blog post, a Wikimedia picture) and records how its colours were
chosen. The Physical Review style sheet of
[hosilva/physrev_mplstyle](https://github.com/hosilva/physrev_mplstyle) inspired the style.
The author used Generative AI in setting up and organizing this repository.

## Copying

All files are under the MIT licence (`LICENSE-MIT.txt`), unless a file states otherwise or
contains third-party material, which stays under its own licence and notice. As an option, the
documentation, the figures and the images in `docs/` are also available under CC BY 4.0
(`LICENSE-CC-BY.txt`). The dual licence is inspired by a
[Q&A on the Software Engineering Stack Exchange site](https://softwareengineering.stackexchange.com/questions/318777/mit-license-vs-creative-commons-for-images-and-other-assets).
The colour table `src/amore/data/afmhot_10us.ctab` is copied from
[ehtplot](https://github.com/liamedeiros/ehtplot) (Copyright (C) 2018--2019 Chi-kwan Chan and
Steward Observatory) and remains under the GNU General Public License, version 3 or later.

## Author Info

- Name: Subhodeep Sarkar. 
- Affiliation: IIT Gandhinagar. 
- Contact: <subhodeep.sarkar1@gmail.com>.
- GitHub Repo: <https://github.com/subhodeeps/amore>. 
- Author Website: <https://subhodeeps.github.io/>.