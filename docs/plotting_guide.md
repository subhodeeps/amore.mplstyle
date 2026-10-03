# Plotting guide for amore

The plot style `amore` is in `src/amore/`:

- `amore.mplstyle` sets the fonts, the colour cycle, the frame, the ticks and the grid.
- `__init__.py` adds the named palettes and the helpers `use`, `figure`, `palette`, `cmap`,
  `fakeparulapastel`, `afmhot10us`, `afmhot10usgrey`, `diverging`, `colorbar`, `shade`, `inset`,
  `tag` and `save`.
- `examples.py` makes the eight example figures and the palette chart in `README.md`
  (`python -m amore.examples`). Read it before you make your first figure.

## Rules

1. Import `amore` and call `amore.use()` before you make a figure. Do not set the fonts, the
   frame width, the tick direction or the grid by hand. The style owns them.
2. Take each colour from a palette: `amore.palette(name)` with `name` one of `red`, `amber`,
   `olive`, `green`, `teal`, `blue`, `plum` or `slate` (8 palettes, 32 colours, shown in
   `docs/figures/amore_palettes.png`). Each palette has four tones:
   - `ink` for a reference or an exact curve
   - `main` for the computed result
   - `light` for a fill
   - `shade` for a background band
3. Choose palettes that work together. For two quantities, use teal and amber
   (split-complementary) or red and green (complementary). For three quantities, use teal,
   amber and plum (close to a triad, about 120 degrees apart). Blue and olive stand alone. Use
   slate, a neutral, for reference data such as an earlier result. Do not put two neighbouring
   hues (blue and teal, for example) on two different quantities.
   A new colour must pass the rules in `tests/test_amore.py`: lightness steps, ink
   contrast and the distance to the other palettes.
4. For a contour plot or an image, use `amore.cmap(name)`. For a field with a wide range, use
   `amore.fakeparulapastel()`, a pastel map from violet to yellow. For an intensity image (a
   brightness that is zero where there is no signal), use `amore.afmhot10us()`, and see
   guideline 10; `amore.afmhot10usgrey()` is its grey version, with the same lightness at every
   point, for print in black and white. For a signed field, use
   `amore.diverging("red", "green")` with `vmin = -vmax`, so that zero is at the centre.
   Make a map with `amore.figure(colorbar=True)` and put the bar above the plot with
   `amore.colorbar()`. The bar covers no data, and the plot keeps the same size as a line plot.
   A colour bar beside the axes makes the plot smaller than its neighbours, unless all the
   panels of a wide figure have the same size, as in the double-slit and Airy examples.
5. Draw a line on top of a colour map (flow lines, guides) in `amore.OVERLAY` at
   `amore.OVERLAY_ALPHA`. This is a dark neutral grey. White vanishes on the light centre of a
   map. Black competes with the contour lines. A coloured line looks like a quantity.
   On `afmhot10us` the choice depends on where the line runs: `OVERLAY` is lost where the map is
   between about L* 13 and 26 (the lowest fifth of the scale), and white is lost only over the
   brightest tones (above about L* 90). Use white over the dark and middle of the map and
   `OVERLAY` over the bright core.
6. Use one palette for one family of figures. Then one quantity has one colour in the whole
   document.
7. Write each axis label, legend entry and mathematical symbol in LaTeX. Write a text note
   inside the axes in monospace. `amore.shade(ax, x0, x1, "label")` does this, or use
   `\texttt{...}`.
8. Mark a region with `amore.shade()`. Show a detail with `amore.inset()`. Put a status line,
   for example the figure that you reproduce, with `amore.tag(ax, text, loc)`. Choose the corner
   where it hides no data.
9. Save with `amore.save(fig, path)`. It writes a PDF for the paper and a PNG for review, side
   by side. For figures that sit side by side, use `layout="constrained"` and
   `exact_size=True`, so that each file has the same size.
10. A script makes each figure from its data. Never edit a figure by hand.

## Colour theory guidelines

These are defaults. You can override any of them; write the reason in a comment next to the
colours. Rules 2 to 6 above say which colours exist and which pairs work.
The guidelines here say how to choose among them.

The HSV hue and the CIELAB lightness L* of each main tone (`amore.lab()` gives L*):

| palette | red | amber | olive | green | teal | blue | plum | slate |
|---|---|---|---|---|---|---|---|---|
| hue (deg) | 352 | 38 | 66 | 148 | 181 | 204 | 288 | 210 |
| L* | 59 | 68 | 64 | 65 | 60 | 62 | 52 | 55 |

1. **One colour, one meaning.** A colour stands for one quantity in every figure of the
   document (rule 6). Do not use a colour only to make a plot pretty.
2. **Keep the hue count low.** Use at most four hues in one plot. Above that, separate the
   curves with line style, markers or labels, because the reader cannot match five colours to a
   legend.
3. **Give the data a full palette and give the reference a different hue.** The data gets one
   palette in all its tones (`light` for points, `main` for fills, `ink` for outlines). Means,
   truth values and guides get other hues, or `slate`.
4. **Choose the pair by the relation of the quantities.**
   - Two sets that you compare directly: complementary hues, about 180 degrees apart (red and
     green; plum and olive are 138 degrees apart, the nearest pair in the palettes).
   - Three sets: a triad, about 120 degrees apart (plum, teal and amber).
   - One quantity that changes in steps, for example an overtone number n: neighbouring hues
     (analogous), or the tones of one palette. Do not use unrelated hues for an ordered series.
5. **Hue alone is not enough.** The main tones have nearly the same lightness (L* 52 to 68), so
   two curves in different hues can look alike in a grey print and for a reader with a colour
   vision deficiency. Add a second cue: a dashed line, a marker, or a different tone (`ink` on
   `light`). Red and green need this most. Check with `amore.lab()` that two colours that must
   be told apart differ in L*, or use a second cue.
6. **Warm for the focus, cool for the context.** Warm hues (red, amber) come forward. Cool hues
   (teal, blue, plum) and neutrals recede. Draw the result of the figure in a warm hue or in
   the `ink` tone. Draw the comparison data in a cool hue or in `slate`.
7. **Match the map to the data.**
   - Ordered values: a sequential map (`amore.cmap(name)`).
   - Values with a wide range: `amore.fakeparulapastel()`. Never use a rainbow map such as jet,
     because its lightness is not monotonic and it makes false edges.
   - Brightness or intensity: `amore.afmhot10us()`, whose lightness rises at every step from
     L* 6 to 100 (guideline 10). Its grey version `amore.afmhot10usgrey()` has the same L* at
     every point, so the figure keeps its meaning in black and white.
   - Values with a meaningful zero: a diverging map with a neutral centre
     (`amore.diverging()`), and `vmin = -vmax`.
8. **Fills are light and lines are dark.** A fill uses `light` or `shade`, with a line in `main`
   or `ink` on top. Text on a fill needs contrast, and `amore.contrast_on_white()` gives the
   ratio. A marker on a dark fill gets an edge in its own `ink` tone.
9. **Do not use a colour that is not in a palette**, and do not use pure grey for a quantity.
   Grey is for the frame, the grid and `amore.OVERLAY` only.
10. **Use `afmhot10us` for a brightness image whose zero is dark.** The map is for a quantity
    that cannot be negative, where zero means no signal and the largest value should look
    brightest. Use it for:
    - images of the light around a black hole: the shadow and the photon ring, from a simulation
      (an intensity map) or from observation (a radio or VLBI brightness image). The ehtplot
      package made these maps for such images, and its notebook compares them on a black-hole
      simulation;
    - other astrophysical images of emission: jets, accretion discs, radio maps, surface
      brightness and emission-line maps, images of stars and of close binaries (the Rayleigh
      limit in the Airy example), anything where "hot" is bright;
    - Fourier optics and wave optics: the intensity or the amplitude of a diffraction or
      interference pattern, a point spread function such as the Airy rings, a focal spot or
      speckle (the double-slit and Airy examples).

    Why it works: its lightness rises at every step, so a feature in the image is a feature in
    the data and not a step in the map, and its floor is lifted to L* 6, so the darkest values
    stay apart from a black frame and a dim feature stays visible. Its limits:
    - Do not use it for a signed field (use `diverging`), or for a field with no natural zero
      (use `fakeparulapastel`).
    - Set `vmin = 0`, so that zero is the dark end, and say on the colour bar what the colour
      shows and how it is scaled, for example `|Psi| / |Psi|_max`. If the image is mostly black on
      a linear scale, plot a root or a logarithm of the value and say so in the label; for a
      logarithm, state the floor, as the Airy example does (10^-4).
    - Use `afmhot10usgrey` for print in black and white, or to check that the figure reads
      without its hues. The two maps have the same lightness at every value, so they can share
      a figure, as in the Airy example, if each panel has its own colour bar.
    - The map starts almost black, so the image is a dark panel on the page. Choose the colour of
      anything drawn over it as rule 5 says.

## Look at the figure before you call it done

Inspect (or if you are a Large Language Model, then Read) the PNG. Look for these faults:

- a label or an annotation that touches a curve
- an inset that hides data, a label or the legend
- tick labels that overlap
- a legend on top of data
- a marker that is not at the point that it marks
- a colour that is not in a palette

Fix each fault and render again. A figure that you did not look at is not finished.

## Requirement

The style uses LaTeX for all text, so it needs `latex` and `dvipng` (and the `type1cm`,
`cm-super` and `amsmath` TeX packages). `scripts/check.sh` reports them. If they are missing,
install them. Do not switch off LaTeX to get a figure, because then the figure does not
match the document.

## Credit

The Physical Review style sheet of
[hosilva/physrev_mplstyle](https://github.com/hosilva/physrev_mplstyle) inspired this style.