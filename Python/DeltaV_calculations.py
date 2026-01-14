import yaml
import numpy as np
from scipy.optimize import brentq, minimize_scalar

g = 9.81


# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------

# Config open
def config_open(name: str):
    Configfile = r"./Orbit_project_conf.yaml"

    with open(Configfile, "r") as file:
        config = yaml.safe_load(file)

    cfg = config[name]
    # ----------------
    # Constants
    # ----------------

    R = float(cfg["R"])
    mu = float(cfg["mu"])
    h = float(cfg["h"])

    # ----------------
    # Vehicle parameters
    # ----------------

    # Total mass of the stage
    M1 = float(cfg["M1"])
    M2 = float(cfg["M2"])
    # Dry mass of 2nd stage
    M2_dry = float(cfg["M2_dry"])
    # Final mass of 1st stage
    M1_f = float(cfg["M1_f"])

    # Thrust of 2nd stage
    Thrust2 = float(cfg["Thrust2"])

    # Specific Impulse
    Isp_1 = float(cfg["Isp_1"])
    Isp_2 = float(cfg["Isp_2"])

    # Initial TWR
    n01 = float(cfg["n01"])
    n02 = float(cfg["n02"])

    # Burnout time of 1st stage
    tb_1 = float(cfg["tb_1"])

    return R, mu, h, M1, M2, M2_dry, M1_f, Thrust2, Isp_1, Isp_2, n01, n02, tb_1

# Constructors
def n_constructor(n_ini, U_mass):
    n_loc = (n_ini/(1-U_mass)) * np.log(1/U_mass)
    return n_loc


def U_constructor(M_ini, M_fin):
    U_loc = M_fin / M_ini
    return U_loc


def z_constructor(gamma):
    chi = np.pi/2 - gamma
    z = np.tan(chi/2)
    return z


def A1_constructor(t_b, z, n_):
    frac1 = (z ** (n_ - 1)) / (n_ - 1)
    frac2 = (z ** (n_ + 1)) / (n_ + 1)
    A = g * t_b * ((frac1 + frac2)**(-1))
    return A


def V_constructor(A, z, n_):
    V_at_z = A * (z**(n_ - 1)) * (1 + z**2)
    return V_at_z


def F_constructor(z, n_):
    frac1 = (z**(n_ - 1)) / (n_ - 1)
    frac2 = (z**(n_ + 1)) / (n_ + 1)
    F = frac1 + frac2
    return F


def H_constructor(z, n_):
    frac1 = (z**(2*n_ - 2)) / (2*n_ - 2)
    frac2 = (z**(2*n_ + 2)) / (2*n_ + 2)
    H = frac1 - frac2
    return H


# Vehicle constructors
def M_f(M_ini, M_dry, percent):
    M_p = M_ini - M_dry
    M_p_used = M_p * (percent/100)
    M_p_left = M_p - M_p_used
    M_used = M_dry + M_p_left
    return M_used


def burnout_time(M_ini, M_f, Isp, Thrust):
    tb = ((M_ini - M_f) * g * Isp) / Thrust
    return tb


# Bracket finders
def find_bracket(f, zmin, zmax, N=100):
    """
    Returns the valid subdomain for the inflection point. (to 0 value)
    :param f: Target function
    :param zmin: Domain minimum
    :param zmax: Domain maximum
    :param N: Number of z values.
    :return: Domain
    """
    zs = np.linspace(zmin, zmax, N)
    fs = np.array([f(z) for z in zs])

    for i in range(len(zs)-1):
        if np.isnan(fs[i]) or np.isnan(fs[i+1]):
            continue
        if fs[i] * fs[i+1] < 0:
            return zs[i], zs[i+1]

    raise RuntimeError("No sign change found in z20 interval")


def invalid_to_nan(f, x):
    try:
        return f(x)
    except:
        return np.nan


def find_max_not_NaN(f, zmin, zmax, N=15):
    """
    Returns z, where f(z) is not np.isnan.
    The concept for finding z is similar to bisect.
    Supports NaN only at zmax.
    """

    if N == 15:
        if np.isnan(invalid_to_nan(f, zmin)) and np.isnan(invalid_to_nan(f, zmax)):
            return np.nan

        if not np.isnan(invalid_to_nan(f, zmin)) and not np.isnan(invalid_to_nan(f, zmax)):
            return zmax

    if N == 0:
        return zmin

    zmid = (zmin + zmax) / 2.0
    fmid = invalid_to_nan(f, zmid)
    if np.isnan(fmid):
        return find_max_not_NaN(f, zmin, zmid, N=N - 1)
    else:
        return find_max_not_NaN(f, zmid, zmax, N=N-1)


# DeltaV calculators
def vis_viva(mu, r_Ap, r_Pe, mode):  # made for Hohmann transfer
    # Means you want to make an ellipse from a circular orbit --> r_Ap, and r_Pe are AFTER the maneuver
    if mode == "e":
        v = (mu / r_Pe)**(1/2)
        dV = v*(((2*r_Ap)/(r_Ap + r_Pe))**(1/2) - 1)
        return dV
    # Means you want to circularize an elliptical orbit --> r_Ap, and r_Pe are BEFORE the maneuver
    if mode == "c":
        v = (mu/r_Ap)**(1/2)
        dV = v*(1 - ((2*r_Pe) / (r_Ap + r_Pe)))
        return dV


def Hohmann_comparison(mu, R, h):
    r = R+h
    v = (mu / R)**(1/2)
    burn1 = vis_viva(mu, r, R, "e")
    burn2 = vis_viva(mu, r, R, "c")
    Hohmann_dV = v + burn1 + burn2
    return Hohmann_dV

# ----------------------------------------------------------------------------------
# The calculations
# ----------------------------------------------------------------------------------


def core_calculations(M_percent, gamma):
    """
    Makes the core trajectory calculations, and mid-flight angle fitting. Prints the results.
    :param M_percent: Second Stage Used
    :param gamma: End flight path angle
    :return: f_Ap: difference between desired and calculated Apoapsis, TotalDeltaV
    """
    R, mu, h, M1, M2, M2_dry, M1_f, Thrust2, Isp_1, Isp_2, n01, n02, tb_1 = config_open(name)

    # Calculated constants
    M2_f = M_f(M2, M2_dry, M_percent)
    tb_2 = burnout_time(M2, M2_f, Isp_2, Thrust2)  # Original: 136.4, Alt: 136.4-55

    # Mass Ratios
    U1 = U_constructor(M1, M1_f)
    U2 = U_constructor(M2, M2_f)

    # ------------------------------------------------
    # DeltaV of the stages
    DeltaV1 = g * Isp_1 * np.log(1/U1)
    DeltaV2 = g * Isp_2 * np.log(1/U2)

    # z construction
    z2f = z_constructor(gamma)
    # n_ construction
    n1_ = n_constructor(n01, U1)
    n2_ = n_constructor(n02, U2)

    # f(z20)
    def root_z20(z):
        """
        Calculates the mid-flight path angle differences. The target of the optimization will be returned 0.
        :param z: Mid-flight path angle
        :return: The flight path angle difference between the 1st and 2nd stage.
        """

        # A construction
        try:
            A1 = A1_constructor(tb_1, z, n1_)
            A2 = A1 * (z**(n1_-n2_))

            F1_z20 = F_constructor(z, n1_)
            f1 = (A1 / g) * F1_z20

            F2_z2f = F_constructor(z2f, n2_)
            F2_z20 = F_constructor(z, n2_)
            f2 = (A2 / g) * (F2_z2f - F2_z20)

            # If this is 0 then we have z20
            f = tb_2/tb_1 - f2/f1
            return f
        except ValueError:
            return np.nan

    # Optimizing z20
    z20_iter = 5000
    zmin = 1e-6
    zmax = z2f*(1 - 1e-6)
    # Finds domain of z20
    z20_a, z20_b = find_bracket(root_z20, zmin, zmax)
    # Solves f(z20) = 0
    z20 = brentq(f=root_z20, a=z20_a, b=z20_b, maxiter=z20_iter)

    # Recomputing A1, A2
    A1 = A1_constructor(tb_1, z20, n1_)
    A2 = A1 * z20 ** (n1_ - n2_)

    # V(z)
    V_at_z20 = V_constructor(A1, z20, n1_)
    V_at_z2f = V_constructor(A2, z2f, n2_)

    # h(z)
    H1_0 = H_constructor(0, n1_)
    H1_z20 = H_constructor(z20, n1_)
    h_at_z20 = (A1**2 / g) * (H1_z20 - H1_0)

    H2_z20 = H_constructor(z20, n2_)
    H2_z2f = H_constructor(z2f, n2_)
    h_at_z2f = h_at_z20 + ((A2**2 / g) * (H2_z2f - H2_z20))

    DeltaV_g = DeltaV1 + DeltaV2 - V_at_z2f

    # ----------------------------------
    # Apoapsis and Periapsis

    L = (R + h_at_z2f) * V_at_z2f * (2*z2f / (1 + z2f**2))
    E = (V_at_z2f**2 / 2) - (mu / (R + h_at_z2f))
    e = (1 + (2*E * L**2) / mu**2)**(1/2)
    a = - mu / (2*E)

    r_Ap = (a*(1 + e))
    r_Pe = (a*(1 - e))

    r_h = R + h  # Target height

    DeltaV_c = vis_viva(mu, r_Ap, r_Pe, "c")  # dV needed for circularization

    f_Ap = r_h - r_Ap  # If this is 0 we've reached the desired Apoapsis

    TotalDeltaV = DeltaV1 + DeltaV2 + DeltaV_c  # The dV spent + for circularization

    print("╔════════════════════════════════════════════════════════════╗")
    print("║                    DELTA-V CALCULATIONS                    ║")
    print("╠════════════════════════════════════════════════════════════╝")
    print(f"║  Total DeltaV              = {DeltaV1 + DeltaV2 + DeltaV_c:>15.2f} m/s    ")
    print("║                                                            ")
    print("║  ──────────────── Stage Delta-V ────────────────────────  ")
    print(f"║  DeltaV1                   = {DeltaV1:>15.2f} m/s    ")
    print(f"║  DeltaV2                   = {DeltaV2:>15.2f} m/s    ")
    print(f"║  DeltaV_g                  = {DeltaV_g:>15.2f} m/s    ")
    print(f"║  Circ dV                   = {DeltaV_c:>15.2f} m/s    ")
    print("║                                                            ")
    print("║  ──────────────── Velocities ───────────────────────────  ")
    print(f"║  V(z2_0)                   = {V_at_z20:>15.2f} m/s    ")
    print(f"║  V(z2_f)                   = {V_at_z2f:>15.2f} m/s    ")
    print("║                                                            ")
    print("║  ──────────────── Heights ──────────────────────────────  ")
    print(f"║  h(z20)                    = {h_at_z20 / 1000:>15.3f} km      ")
    print(f"║  h(z2f)                    = {h_at_z2f / 1000:>15.3f} km      ")
    print("║                                                            ")
    print("║  ──────────────── Angles ───────────────────────────────  ")
    print(f"║  z20                       = {z20 * 180 / np.pi:>15.2f} °      ")
    print(f"║  z2f                       = {z2f * 180 / np.pi:>15.2f} °      ")
    print(f"║  g20                       = {(np.pi/2 - 2*np.atan(z20)) * 180 / np.pi:>15.2f} °      ")
    print(f"║  g2f                       = {(np.pi/2 - 2*np.atan(z2f)) * 180 / np.pi:>15.2f} °      ")
    print("║                                                            ")
    print("║  ──────────────── Orbit Parameters ─────────────────────  ")
    print(f"║  eccentricity              = {e:>15.2f}         ")
    print(f"║  h_Ap                      = {(r_Ap-R) / 1000:>15.1f} km     ")
    print(f"║  h_Pe                      = {(r_Pe-R) / 1000:>15.3f} km     ")
    print("║                                                            ")
    print("║  ──────────────── Second Stage Used ────────────────────  ")
    print(f"║  M_percent                 = {M_percent:>15.3f} %      ")
    print("║                                                            ")
    print("║  ──────────────── Comparison ───────────────────────────  ")
    print(f"║  Hohmann comparison        = {Hohmann_comparison(mu, R, h):>15.2f} m/s    ")
    print(f"║  Hohmann + DeltaV_g        = {Hohmann_comparison(mu, R, h) + DeltaV_g:>15.2f} m/s    ")
    print("╚═════════════════════════════════════════════════════════════")

    return f_Ap, TotalDeltaV


def calc_TotalDeltaV(M_percent):
    """
    Calculates the optimal end flight path angle to reach the desired Apoapsis.
    :param M_percent: Second Stage Used
    :return: TotalDeltaV
    """

    gamma_iter = 1000

    def root_gamma(gamma):
        """
        Extracts difference between desired and calculated Apoapsis. The target of the optimization will be returned 0.
        :param gamma: End flight path angle.
        :return: Difference between desired and calculated Apoapsis.
        """
        f_Ap, TotalDeltaV = core_calculations(M_percent, gamma)
        return f_Ap

    # Optimizing gamma
    gmax = np.pi/2-0.0001
    gmin = 0.0001
    # Finds domain of the end flight path angle
    gamma_a, gamma_b = find_bracket(root_gamma, gmin, gmax)
    # Solves gamma = 0
    gamma = brentq(f=root_gamma, a=gamma_a, b=gamma_b, maxiter=gamma_iter)

    f_Ap, TotalDeltaV = core_calculations(M_percent, gamma)

    return TotalDeltaV


name = ""


def main():
    """
    Starts the optimized Trajectory calculation
    """

    global name
    name = "Earth"  # Alternative: "Kerbin"

    # Iterate valid boundaries
    M_per_max = find_max_not_NaN(calc_TotalDeltaV, 1, 99)
    
    print("\n" * 50)
    print(f"M_percent max = {M_per_max}")
    input("\n Press enter to start the calculation: ")

    # Find optimal Trajectory
    minimize_scalar(calc_TotalDeltaV, bounds=(1, M_per_max))


if __name__ == "__main__":
    main()
