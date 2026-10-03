"""Tests of the physics behind the example figures in src/python/amore/examples.py.

black_hole_charges() draws the field of test charges near extremal black holes. These tests check
the function that it uses, mp_test_field(), in three dimensions and against separate formulas:

- for one hole it equals the closed form of Frolov and Zelnikov, Phys. Rev. D 85, 064032, Eq. (4.21);
- it solves Maxwell's equation d_a (U^2 d_a A_0) = 0 away from the sources;
- the flux of U^2 grad Phi gives the charge of the test charge, the charge at infinity, and zero
  change of the charge of each hole;
- the coefficients C_k = M_k / rho'_k that the paper prints for Eq. (4.14) do change the charges
  of the holes when there are several holes.
"""

import numpy as np
import pytest

pytest.importorskip("matplotlib")
from amore import examples  # noqa: E402

THREE_HOLES = [(1.5, -0.5, 1 / 3, 1.0), (-1.0, 0.5, -0.25, 0.7), (0.2, 1.6, 0.9, 0.5)]   # x, y, z, M
CHARGE = (0.2, -1 / 3, 0.5, 1.0)                                                          # x', y', z', e'


def sphere_flux(field, centre, radius, nt=80, nph=160):
    """Flux of U^2 grad Phi through a sphere, divided by 4 pi (Gauss-Legendre in cos(theta))."""
    nodes, weights = np.polynomial.legendre.leggauss(nt)
    phi = (np.arange(nph) + 0.5) * 2 * np.pi / nph
    c, p = np.meshgrid(nodes, phi, indexing="ij")
    s = np.sqrt(1 - c ** 2)
    n = [s * np.cos(p), s * np.sin(p), c]
    point = [centre[a] + radius * n[a] for a in range(3)]
    _, grad, big_u = field(*point)
    integrand = big_u ** 2 * sum(grad[a] * n[a] for a in range(3))
    return float(np.sum(weights[:, None] * integrand) * (2 * np.pi / nph) * radius ** 2) / (4 * np.pi)


def paper_field(holes, charge):
    """The same field with the coefficients C_k = M_k / rho'_k of Eq. (4.14) of the paper."""
    holes = np.asarray(holes, float)
    pos, mass = holes[:, :3], holes[:, 3]
    cpos, e = np.array(charge[:3]), charge[3]
    rp = np.linalg.norm(pos - cpos, axis=1)
    up = 1 + np.sum(mass / rp)

    def field(x, y, z):
        pt = [x, y, z]
        rho = [np.sqrt(sum((pt[a] - pos[k, a]) ** 2 for a in range(3))) for k in range(len(mass))]
        big_u = 1 + sum(mass[k] / rho[k] for k in range(len(mass)))

        def phi_at(q):
            rq = [np.sqrt(sum((q[a] - pos[k, a]) ** 2 for a in range(3))) for k in range(len(mass))]
            uq = 1 + sum(mass[k] / rq[k] for k in range(len(mass)))
            rr = np.sqrt(sum((q[a] - cpos[a]) ** 2 for a in range(3)))
            return e * (1 / rr + sum(mass[k] / rp[k] / rq[k] for k in range(len(mass)))) / (uq * up)

        h = 1e-6
        grad = [(phi_at([pt[b] + h * (a == b) for b in range(3)]) - phi_at([pt[b] - h * (a == b) for b in range(3)]))
                / (2 * h) for a in range(3)]
        return phi_at(pt), grad, big_u
    return field


def test_one_hole_equals_the_closed_form_of_the_paper():
    hole, charge = (0.0, 0.0, 0.0, 1.3), (1.1, -0.4, 0.7, 1.0)
    field = examples.mp_test_field([hole], [charge])
    x, y, z = 0.6, 0.9, -0.5
    rho, rho_c = np.sqrt(x * x + y * y + z * z), np.sqrt(1.1 ** 2 + 0.4 ** 2 + 0.7 ** 2)
    big_u, big_u_c = 1 + 1.3 / rho, 1 + 1.3 / rho_c
    r = np.sqrt((x - 1.1) ** 2 + (y + 0.4) ** 2 + (z - 0.7) ** 2)
    expected = (1 / r + 1.3 / (rho * rho_c)) / (big_u * big_u_c)           # Eq. (4.21), D = 4
    assert field(x, y, z)[0] == pytest.approx(expected, rel=1e-12)


def test_the_potential_solves_maxwells_equation():
    field = examples.mp_test_field(THREE_HOLES, [CHARGE, (-2.0, -1.0, -0.4, -1.0)])

    def flux_density(x, y, z):
        _, grad, big_u = field(x, y, z)
        return [big_u ** 2 * g for g in grad]

    h = 1e-4
    for point in ((1.0, 1.0, 1.0), (-2.5, 0.3, 0.8), (0.4, -1.7, -1.2)):
        div = 0.0
        for a in range(3):
            up, dn = list(point), list(point)
            up[a] += h
            dn[a] -= h
            div += (flux_density(*up)[a] - flux_density(*dn)[a]) / (2 * h)
        assert abs(div) < 1e-5


def test_the_gradient_is_the_gradient_of_phi():
    field = examples.mp_test_field(THREE_HOLES, [CHARGE])
    point, h = np.array([0.7, 0.9, -0.6]), 1e-6
    _, grad, _ = field(*point)
    for a in range(3):
        step = np.zeros(3)
        step[a] = h
        numeric = (field(*(point + step))[0] - field(*(point - step))[0]) / (2 * h)
        assert grad[a] == pytest.approx(numeric, rel=1e-6)


def test_the_charge_is_e_and_no_horizon_changes_its_charge():
    field = examples.mp_test_field(THREE_HOLES, [CHARGE])
    assert sphere_flux(field, CHARGE[:3], 0.01) == pytest.approx(-1.0, abs=1e-6)       # the test charge
    assert sphere_flux(field, (0, 0, 0), 300.0) == pytest.approx(-1.0, abs=2e-3)        # at infinity
    for hole in THREE_HOLES:
        for radius in (0.02, 0.2):
            assert abs(sphere_flux(field, hole[:3], radius)) < 1e-6


def test_the_coefficients_printed_in_the_paper_change_the_horizon_charges():
    field = paper_field(THREE_HOLES, CHARGE)
    induced = [sphere_flux(field, h[:3], 0.02) for h in THREE_HOLES]
    assert max(abs(q) for q in induced) > 0.02                                        # 0.036 for hole 1
    assert sum(induced) == pytest.approx(0.0, abs=1e-6)                               # the total is kept
    # the formula dQ_k = -(M_k / U') sum_{j != k} (M_j / d_jk)(1 / rho'_j - 1 / rho'_k)
    pos, mass = np.array(THREE_HOLES)[:, :3], np.array(THREE_HOLES)[:, 3]
    rp = np.linalg.norm(pos - np.array(CHARGE[:3]), axis=1)
    up = 1 + np.sum(mass / rp)
    for k in range(3):
        predicted = -(mass[k] / up) * sum(mass[j] / np.linalg.norm(pos[j] - pos[k]) * (1 / rp[j] - 1 / rp[k])
                                          for j in range(3) if j != k)
        assert -induced[k] == pytest.approx(predicted, abs=2e-4)                     # flux = -(charge change)


def one_step(k, phi, p):
    """One step of the standard map, without the mod 2 pi."""
    p_new = p + k * np.sin(phi)
    return phi + p_new, p_new


def test_standard_map_orbits_match_the_map_and_repeat():
    """standard_map_orbits() takes the steps of p' = p + k sin(phi), phi' = phi + p' (mod 2 pi)."""
    phi, p = examples.standard_map_orbits(0.97, 6, 40)
    again = examples.standard_map_orbits(0.97, 6, 40)
    assert np.array_equal(phi, again[0]) and np.array_equal(p, again[1])
    assert np.all(np.abs(phi) <= np.pi) and np.all(np.abs(p) <= np.pi)
    start_p = -np.pi + (np.arange(6) + 0.5) * 2 * np.pi / 6
    new_phi, new_p = one_step(0.97, np.zeros(6), start_p)
    wrap = lambda x: (x + np.pi) % (2 * np.pi) - np.pi
    assert np.allclose(phi[:, 0], wrap(new_phi)) and np.allclose(p[:, 0], wrap(new_p))


def test_standard_map_conserves_area_and_k_zero_keeps_p():
    """The map has Jacobian determinant 1 (finite differences), and p stays fixed for k = 0."""
    h = 1e-6
    for phi0, p0 in [(0.3, -1.2), (2.0, 0.7), (-2.5, 2.9)]:
        f = lambda a, b: np.array(one_step(0.97, a, b))
        jac = np.column_stack([(f(phi0 + h, p0) - f(phi0 - h, p0)) / (2 * h),
                               (f(phi0, p0 + h) - f(phi0, p0 - h)) / (2 * h)])
        assert abs(np.linalg.det(jac) - 1) < 1e-8
    _, p = examples.standard_map_orbits(0.0, 5, 30)
    start_p = -np.pi + (np.arange(5) + 0.5) * 2 * np.pi / 5
    assert np.allclose(p, np.repeat(start_p[:, None], 30, axis=1))


def test_standard_map_image_colours_and_repeat():
    """The image repeats, has the right shape, and has only amore colours and white."""
    import amore
    a = examples.standard_map_image(0.97, shape=(120, 120), grid=(40, 40), steps=200)
    b = examples.standard_map_image(0.97, shape=(120, 120), grid=(40, 40), steps=200)
    assert a.shape == (120, 120, 3) and np.array_equal(a, b)
    allowed = {tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for tones in amore.PALETTES.values()
               for c in tones.values()} | {(255, 255, 255)}
    seen = {tuple(np.round(px * 255).astype(int)) for px in a.reshape(-1, 3)}
    assert seen <= allowed
    assert len({px for px in seen if px != (255, 255, 255)}) > 10     # many colours, not one


def test_standard_map_image_k_zero_is_all_regular():
    """For k = 0 every orbit is a horizontal line: no chaotic sea, so only band colours (not shade)."""
    import amore
    img = examples.standard_map_image(0.0, shape=(90, 90), grid=(30, 30), steps=100)
    shade = {tuple(int(amore.palette(n)["shade"][i:i + 2], 16) for i in (1, 3, 5))
             for n in amore.PALETTES}
    seen = {tuple(np.round(px * 255).astype(int)) for px in img.reshape(-1, 3)}
    assert not (seen & shade)


def test_standard_map_image_window_rows_are_p():
    """For k = 0 the orbit of a row is a horizontal line: with one initial point per pixel row, each
    row of a window image has one colour besides white, and the shape is the shape asked for."""
    img = examples.standard_map_image(0.0, phi_range=(-1.0, 1.0), p_range=(-1.7, 0.1), shape=(30, 60),
                                      grid=(60, 30), steps=300)
    assert img.shape == (30, 60, 3)
    for row in img:
        colours = {tuple(np.round(px * 255).astype(int)) for px in row} - {(255, 255, 255)}
        assert len(colours) == 1

def test_standard_map_image_whole_phase_space_window():
    """The window of chirikov_square(): phi from 0 to 2 pi, centred on pi, outside [-pi, pi].
    For k = 0 every row of the image is one horizontal orbit, so it has one colour besides white."""
    img = examples.standard_map_image(0.0, phi_range=(0.0, 2 * np.pi), shape=(60, 60),
                                      grid=(60, 60), steps=300)
    assert img.shape == (60, 60, 3)
    for row in img:
        colours = {tuple(np.round(px * 255).astype(int)) for px in row} - {(255, 255, 255)}
        assert len(colours) == 1
        
def test_pendulum_orbits_conserve_energy_and_have_the_right_kinds():
    """pendulum_orbits() keeps E = y^2 / 2 - cos(x); librations stay in |x| < pi, rotations run on."""
    x, y = examples.pendulum_orbits([0.0, 0.0, 5 * np.pi, -5 * np.pi], [1.95, -0.5, -1.0, 2.0], 45.0, 1000)
    energy = y ** 2 / 2 - np.cos(x)
    assert np.max(np.abs(energy - energy[:, :1])) < 1e-9
    assert np.all(np.abs(x[:2]) < np.pi)                    # librations: inside the separatrix
    assert np.all(np.diff(x[2]) < 0) and np.all(np.diff(x[3]) > 0)   # rotations: one direction
    assert np.max(np.abs(energy[:, 0] - np.array([1.95 ** 2 / 2 - 1, 0.125 - 1, 1.5, 3.0]))) < 1e-12

# --- the double slit (double_slit): Fresnel diffraction with one FFT -------------------------
# Lengths in mm. The values are those of the post that the example follows.
WAVELENGTH, DISTANCE = 18.5e-7, 5000.0
CELL = 1e-3


def slit_grid(nx=2800, ny=2000):
    return CELL * (np.arange(nx) - nx // 2), CELL * (np.arange(ny) - ny // 2)


def slit_pattern(slits):
    x, y = slit_grid()
    aperture = examples.slit_aperture(x, y, slits)
    xs, ys, intensity = examples.fresnel_pattern(aperture, CELL, CELL, WAVELENGTH, DISTANCE)
    return aperture, xs, ys, intensity


def test_slit_aperture_has_the_exact_open_area_even_off_the_grid():
    x, y = slit_grid(400, 300)
    for width, height, x0 in ((0.0227, 0.0713, 0.0), (0.0227, 0.0713, 0.0431), (0.05, 0.05, -0.1)):
        aperture = examples.slit_aperture(x, y, [(x0, 0.0, width, height)])
        assert abs(aperture.sum() * CELL * CELL - width * height) < 1e-12


def test_fresnel_pattern_conserves_energy():
    """Parseval: the intensity integrated over the screen is dx dy sum(aperture^2), and that is
    within 3 % of the open area (the difference is the cells on the slit edges)."""
    aperture, xs, ys, intensity = slit_pattern([(-0.064, 0, 0.022, 0.088), (0.064, 0, 0.022, 0.088)])
    power = intensity.sum() * (xs[1] - xs[0]) * (ys[1] - ys[0])
    assert abs(power / (CELL * CELL * np.sum(aperture ** 2)) - 1) < 1e-9
    assert abs(power / (2 * 0.022 * 0.088) - 1) < 0.03


def test_one_slit_gives_the_sinc_squared_in_x():
    """Along y = 0 the pattern of one slit is sinc^2(a x / (wavelength z)); the Fresnel number
    of the slit width is 0.013, so the far field holds in x (it does not in y)."""
    _, xs, ys, intensity = slit_pattern([(0, 0, 0.022, 0.088)])
    row = intensity[ys.size // 2]
    ratio = row / row[xs.size // 2]
    near = np.abs(xs) < 0.8
    expected = np.sinc(0.022 * xs / (WAVELENGTH * DISTANCE)) ** 2
    assert np.abs(ratio - expected)[near].max() < 0.01


def test_double_slit_fringes_are_wavelength_z_over_d_apart():
    """The central fringe maxima are at x = m wavelength z / D, to one screen cell (3.3 um).
    The envelope pulls the maxima by up to 0.75 cell, so this fixes D only to about 3 %: it
    fails for D = 0.125 mm but not for 0.130 mm. The sinc test above is the sharp one."""
    separation = 0.128
    _, xs, ys, intensity = slit_pattern([(-separation / 2, 0, 0.022, 0.088),
                                         (separation / 2, 0, 0.022, 0.088)])
    row = intensity[ys.size // 2]
    peaks = [i for i in range(1, row.size - 1)
             if row[i] > row[i - 1] and row[i] >= row[i + 1] and 0 <= xs[i] < 0.25]
    found = xs[peaks]
    spacing = WAVELENGTH * DISTANCE / separation
    assert len(found) == 4                                   # m = 0, 1, 2, 3
    assert np.all(np.abs(found - spacing * np.arange(4)) <= xs[1] - xs[0])


def test_fresnel_pattern_refuses_a_grid_that_is_too_coarse():
    x, y = 0.01 * (np.arange(400) - 200), 0.01 * (np.arange(400) - 200)
    aperture = examples.slit_aperture(x, y, [(0, 0, 0.5, 0.5)])
    with pytest.raises(ValueError):
        examples.fresnel_pattern(aperture, 0.01, 0.01, WAVELENGTH, DISTANCE)

# --- Airy rings (airy_rings): the pattern of a circular aperture ------------------------------
# Lengths in units of lambda / D. Hill's expression is checked against identities that do not
# use it: the zeros of J1, the enclosed energy 1 - J0^2 - J1^2, and the FFT of a real aperture.


def test_airy_pattern_has_unit_peak_and_zeros_at_the_zeros_of_j1():
    from scipy.special import jn_zeros
    assert float(examples.airy_pattern(0.0)) == 1.0
    zeros = jn_zeros(1, 4) / np.pi                     # 1.21967, 2.23313, 3.23832, 4.24106
    assert abs(zeros[0] - 1.21967) < 1e-5              # the Rayleigh radius
    assert np.all(examples.airy_pattern(zeros) < 1e-20)
    assert np.all(examples.airy_pattern(np.linspace(0.05, 6, 400)) > 0)


def test_airy_energy_inside_the_first_dark_ring_is_83_8_percent():
    """The energy inside rho is 1 - J0(x)^2 - J1(x)^2 of the total 4 / pi (x = pi rho)."""
    from scipy.special import j0, j1, jn_zeros
    x1 = jn_zeros(1, 1)[0]
    exact = 1 - j0(x1) ** 2 - j1(x1) ** 2
    assert abs(exact - 0.838) < 1e-3                   # the number every optics text quotes
    h = 0.005
    grid = h * np.arange(-280, 281)                    # -1.4 ... 1.4
    gx, gy = np.meshgrid(grid, grid)
    image = examples.point_sources(gx, gy, [(0.0, 0.0)])
    inside = np.hypot(gx, gy) < x1 / np.pi
    assert abs(image[inside].sum() * h * h / (4 / np.pi) - exact) < 1e-3


def test_airy_pattern_equals_the_fft_of_a_circular_aperture():
    """fresnel_pattern() from the double-slit example, far from a round hole, gives the Airy
    pattern: here the Fresnel number is 2e-4. The agreement is 2e-5 of the peak; a rho that is
    5 % too large or too small gives 0.04."""
    wavelength, distance, diameter, n, across = 5e-4, 1e5, 0.2, 2048, 128    # mm; 128 cells
    cell = diameter / across
    x = cell * (np.arange(n) - n // 2)
    gx, gy = np.meshgrid(x, x)
    aperture = np.clip(0.5 + (diameter / 2 - np.hypot(gx, gy)) / cell, 0, 1)
    xs, _, intensity = examples.fresnel_pattern(aperture, cell, cell, wavelength, distance)
    row = intensity[n // 2] / intensity[n // 2, n // 2]
    rho = xs * diameter / (wavelength * distance)      # angle in units of lambda / D
    near = np.abs(rho) <= 4
    assert np.abs(row - examples.airy_pattern(rho))[near].max() < 1e-3
    assert np.abs(row - examples.airy_pattern(1.05 * rho))[near].max() > 0.02


def test_two_sources_at_the_rayleigh_distance_have_a_dip_of_73_5_percent():
    """The criterion: the sources are one first-zero radius apart, so each is at a zero of the
    other, the maximum is 1, and the saddle between them is 0.735 of it."""
    from scipy.special import jn_zeros
    rayleigh = jn_zeros(1, 1)[0] / np.pi
    x = np.linspace(-2, 2, 4001)
    cut = examples.point_sources(x, 0 * x, [(-rayleigh / 2, 0.0), (rayleigh / 2, 0.0)])
    assert abs(cut.max() - 1.0) < 1e-3
    assert abs(cut[2000] / cut.max() - 0.735) < 1e-3   # x = 0 is the middle sample


def test_two_sources_closer_than_the_rayleigh_distance_merge():
    """At half the Rayleigh distance the middle is the maximum, and the profile falls to each
    side: one blob."""
    x = np.linspace(0, 1.5, 1501)
    cut = examples.point_sources(x, 0 * x, [(-0.305, 0.0), (0.305, 0.0)])
    assert cut.argmax() == 0
    assert np.all(np.diff(cut[:1000]) < 0)