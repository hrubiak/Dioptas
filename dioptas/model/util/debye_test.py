from __future__ import absolute_import
# This file is part of BurnMan - a thermoelastic and thermodynamic toolkit for the Earth and Planetary Sciences
# Copyright (C) 2012 - 2017 by the BurnMan team, released under the GNU
# GPL v2 or later.

import numpy as np
import scipy.optimize as opt

from burnman.eos import equation_of_state as eos
#from burnman.tools import bracket
import warnings
#from burnman.eos.birch_murnaghan import bulk_modulus, birch_murnaghan, volume

from scipy.integrate import quad

'''def debye_integral( zmax):
    def integrand(z):
        return z**3 / (np.exp(z) - 1.0)
    val, _ = quad(integrand, 0, zmax)
    return val'''

def integrand(z):
    return z**3 / (np.exp(z) - 1.0)
print(quad(integrand, 0, 1.39, epsabs=1e-10, epsrel=1e-10))