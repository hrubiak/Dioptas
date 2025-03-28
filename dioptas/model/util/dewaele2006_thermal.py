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

class Dewaele2006(eos.EquationOfState):
    """
    Class implementing the Dewaele et al. (2006) Mie–Grüneisen–Debye EOS.
    The EOS is defined as:
      P(V,T) = P_Vinet,300K(V) + [P_th(V,T) - P_th(V,300K)]
    where the 300 K baseline P_Vinet,300K(V) is a Vinet fit and the thermal
    pressure P_th is computed using a Debye model (with anharmonic and electronic terms).
    """
    def __init__(self):
        self.order = 3

    def vinet_300K_pressure(self, V, V0, K0, Kprime_0):
        # V and V0 are in cm³/mol, K0 in GPa; returns pressure in GPa.
        x = (V / V0) ** (1.0 / 3.0)
        return 3.0 * K0 * (1.0 - x) / (x ** 2) * np.exp(1.5 * (Kprime_0 - 1.0) * (1.0 - x))

    def debye_integral(self, zmax):
        def integrand(z):
            return z ** 3 / (np.exp(z) - 1.0)
        val, _ = quad(integrand, 0, zmax)
        return val

    def usual_thermal_pressure(self, V, T, V0, theta0, gamma0, gamma_inf, beta, a0, m_anh, e0, g_el, R=8.314462618):
        # V and V0 in cm³/mol, T in K; returns pressure in GPa.
        x = V / V0
        gamma_val = gamma_inf + (gamma0 - gamma_inf) * (x ** beta)
        theta = theta0 * (x ** (-gamma_inf)) * np.exp(- (gamma0 - gamma_inf) / beta * (x ** beta - 1.0))
        th_ratio = theta / T
        F_D = np.vectorize(self.debye_integral, otypes=[float])(th_ratio)
        P_D = (9.0 * R * gamma_val / V) * (theta / 8.0 + T * (T / theta) ** 3 * F_D)
        P_anh = (3.0 * R / (2.0 * V)) * m_anh * a0 * (x ** m_anh) * T ** 2
        P_el  = (3.0 * R / (2.0 * V)) * g_el * e0 * (x ** g_el) * T ** 2
        return (P_D + P_anh + P_el) * 1e-3  # Convert J/(mol·cm³) to GPa

    def thermal_pressure_zero_at_300K(self, V, T, V0, theta0, gamma0, gamma_inf, beta, a0, m_anh, e0, g_el, R=8.314462618):
        return self.usual_thermal_pressure(V, T, V0, theta0, gamma0, gamma_inf, beta, a0, m_anh, e0, g_el, R) - \
               self.usual_thermal_pressure(V, 300.0, V0, theta0, gamma0, gamma_inf, beta, a0, m_anh, e0, g_el, R)

    def total_pressure(self, V, T, params):
        # Convert input V_0 and K_0 to internal units.
        # Internal V_0 (cm³/mol) = params['V_0'] [m³/mol] * 1e6.
        # Internal K_0 (GPa) = params['K_0'] [Pa] / 1e9.
        V0_internal = params['V_0'] * 1e6
        K0_internal = params['K_0'] / 1e9
        # Use the internal values in the Vinet baseline.
        P_baseline = self.vinet_300K_pressure(V, V0_internal, K0_internal, params['Kprime_0'])
        extra_P_th = self.thermal_pressure_zero_at_300K(V, T, V0_internal, params['Debye_0'],
                                                        params['grueneisen_0'], params['gamma_inf'],
                                                        params['q_0'], params['a0'], params['m_anh'],
                                                        params['e0'], params['g_el'])
        return P_baseline + extra_P_th

    def dewaele_inverse(self, v0_v):
        # v0_v = V_0/V; V = V_0/v0_v, where internal V_0 is in cm³/mol.
        V = self.params_internal['V_0'] / v0_v
        P_calc = self.total_pressure(V, self.T, self.params)
        return (P_calc - self.P_target) ** 2

    def volume(self, pressure, temperature, params):
        """
        Returns volume in Å³ (per formula unit) as a function of pressure [Pa] and temperature [K].
        The inversion is performed on V (in cm³/mol) and then converted:
            V_Å³ = (V_cm3/mol * 1e24) / N_A,
        with N_A ~ 6.022e23.
        The input parameters are provided with:
           V_0 in m³/mol and K_0 in Pa.
        """
        # Convert target pressure from Pa to GPa.
        self.P_target = pressure / 1e9
        self.T = temperature
        # Convert V_0 and K_0 to internal units.
        self.params = params
        self.params_internal = {}
        self.params_internal['V_0'] = params['V_0'] * 1e6  # m³/mol -> cm³/mol
        self.params_internal['K_0'] = params['K_0'] / 1e9    # Pa -> GPa
        # Copy other parameters unchanged.
        for key in ['Kprime_0', 'Debye_0', 'grueneisen_0', 'gamma_inf', 'q_0', 'a0', 'm_anh', 'e0', 'g_el', 'molar_mass', 'n']:
            self.params_internal[key] = params[key]
        
        if pressure == 0.:
            V_found = self.params_internal['V_0']
        elif pressure < 0:
            if self.params_internal['K_0'] <= 0.:
                V_found = self.params_internal['V_0']
            else:
                V_found = self.params_internal['V_0'] * (1 - pressure / (self.params_internal['K_0'] * 1e9))
        else:
            res = opt.minimize(self.dewaele_inverse, 1.0, bounds=[(1e-6, None)])
            v0_v = res.x[0]
            V_found = self.params_internal['V_0'] / v0_v  # in cm³/mol
     
        
        return V_found *1e-6 # m³/mol 

    def pressure(self, temperature, volume, params):
        """
        Returns pressure [Pa] as a function of temperature [K] and volume [m³].
        """
        # Convert volume from m³ to cm³/mol.
        V_cm3 = volume * 1e6
        # Convert V_0 and K_0 in params to internal units:
        params_internal = {}
        params_internal['V_0'] = params['V_0'] * 1e6
        params_internal['K_0'] = params['K_0'] / 1e9
        for key in ['Kprime_0', 'Debye_0', 'grueneisen_0', 'gamma_inf', 'q_0', 'a0', 'm_anh', 'e0', 'g_el', 'molar_mass', 'n']:
            params_internal[key] = params[key]
        P_GPa = self.total_pressure(V_cm3, temperature, params_internal)
        return P_GPa * 1e9

    def validate_parameters(self, params):
        required_keys = ['V_0', 'K_0', 'Kprime_0', 'Debye_0', 'grueneisen_0', 'q_0', 'a0', 'm_anh', 'e0', 'g_el', 'molar_mass', 'n', 'gamma_inf']
        for k in required_keys:
            if k not in params:
                raise KeyError("Missing parameter: " + k)
        if params['V_0'] <= 0.:
            warnings.warn("V_0 must be positive", stacklevel=2)
        if params['K_0'] <= 0.:
            warnings.warn("K_0 must be positive", stacklevel=2)