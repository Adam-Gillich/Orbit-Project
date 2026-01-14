# python
import numpy as np
from Mecha.Orbit_project.DeltaV_calculations import find_max_not_NaN

def test_both_endpoints_nan_returns_nan():
    def f(z):
        return np.nan
    res = find_max_not_NaN(f, 0.0, 1.0, N=10)
    assert np.isnan(res)

def test_both_endpoints_valid_returns_zmax():
    def f(z):
        return z  # never NaN
    zmin, zmax = 0.0, 1.234
    res = find_max_not_NaN(f, zmin, zmax, N=5)
    assert res == zmax

def test_left_nan_right_valid_zmax_valid():
    threshold = 0.6
    def f(z):
        if z >= threshold:
            return 0.0
        return np.nan
    zmin, zmax = 0.0, 1.0
    # use larger N for finer resolution
    res = find_max_not_NaN(f, zmin, zmax, N=20)
    # result should be >= threshold and close to threshold within bisection resolution
    assert res >= threshold
    assert res - threshold <= 1e-4

def test_left_nan_right_valid_zmin_valid():
    threshold = 0.7
    def f(z):
        if z <= threshold:
            return 1.0
        return np.nan
    zmin, zmax = 0.0, 2.0
    # N == 0 should return zmax regardless of where the threshold is
    res = find_max_not_NaN(f, zmin, zmax, N=0)
    assert res == zmax