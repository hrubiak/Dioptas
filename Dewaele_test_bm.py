import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

# -----------------------------------------------------------------------------
# 1) Constants and parameters
# -----------------------------------------------------------------------------
R = 8.314462618        # Gas constant, J/(mol·K)
MFe = 55.845           # Molar mass of iron, g/mol

# Cold (3rd-order Birch-Murnaghan) EOS parameters (example values)
V0_atom = 11.214               # Å³/atom
V0_mol = V0_atom * 1e-24 * 6.022e23  # cm³/mol, ~6.76 cm³/mol
V0_mol = 6.76                  # cm³/mol (approx)

#V0_mol = 6.92          # cm^3/mol  (reference volume at 300 K)
K0 = 165.0             # GPa       (bulk modulus)
K0p = 4.97             # dimensionless (pressure derivative)

# Thermal model parameters (Dewaele-like)
a0 = 3.7e-5            # K^-1
m_anh = 1.87
e0 = 1.95e-4           # K^-1
g_el = 1.339

gamma_0 = 1.875
gamma_inf = 1.305
beta_g = gamma_0 / (gamma_0 - gamma_inf)  # ~ 2.98
theta0 = 417.0         # K  (Debye temperature at V0)

# -----------------------------------------------------------------------------
# 2) Define EOS functions
# -----------------------------------------------------------------------------

def birch_murnaghan_3rd(V, V0, K0, K0p):
    """
    3rd-order Birch-Murnaghan cold compression curve.
    P in GPa if K0 is in GPa, volumes in cm^3/mol.
    """
    eta = (V0 / V)**(2.0/3.0)
    # 3rd-order BM expression:
    P_cold = 1.5 * K0 * (eta**(3.5) - eta**2.5) * \
             (1.0 - 0.75*(4.0 - K0p)*(eta - 1.0))
    return P_cold

def debye_integral(theta_over_T):
    """
    Integrate z^3/(exp(z)-1) from z=0 to z=(theta/T).
    """
    # For scalar or array input, use quad for each value:
    def integrand(z):
        return (z**3)/(np.exp(z) - 1.0)
    val, _ = quad(integrand, 0, theta_over_T)
    return val

def gamma_x(x):
    """Volume-dependent Grüneisen parameter gamma(V). x = V/V0."""
    return gamma_inf + (gamma_0 - gamma_inf)*x**beta_g

def thermal_pressure(V, T, V0):
    """
    Thermal pressure in GPa, using a semi-empirical Dorogokupets-style
    Debye + anharmonic + electronic model.

    V, V0 in cm^3/mol
    T in K
    """
    # Convert to array
    V = np.asarray(V)
    x = V / V0
    gamma = gamma_x(x)
    # Debye temperature variation (simplified approach):
    theta = theta0 * x**(-gamma)

    # Debye (quasi-harmonic) term
    # Vectorize the integral if V is an array:
    debye_vec = np.vectorize(debye_integral, otypes=[float])
    theta_T_ratio = theta / T
    F_D = debye_vec(theta_T_ratio)

    P_D = (9.0 * R * gamma / V) * \
          (theta/8.0 + T*(T/theta)**3 * F_D)

    # Anharmonic term
    P_anh = (3.0*R/(2.0*V)) * m_anh * a0 * x**m_anh * T**2

    # Electronic term
    P_el = (3.0*R/(2.0*V)) * g_el * e0 * x**g_el * T**2

    # Sum them up and convert J/(mol·cm^3) -> GPa
    # 1 GPa = 1e9 N/m^2 = 1e9 J/m^3
    # 1 cm^3 = 1e-6 m^3 => 1 J/(mol·cm^3) = 1e6 J/(mol·m^3)
    # So divide by 1e9 to get GPa => multiply by 1e6 / 1e9 = 1e-3
    P_th = (P_D + P_anh + P_el) * 1e-3

    return P_th

def total_pressure(V, T, V0, K0, K0p):
    """
    Total P = Cold curve (3rd BM) + Thermal pressure
    Returns pressure in GPa.
    """
    Pcold = birch_murnaghan_3rd(V, V0, K0, K0p)
    Pth = thermal_pressure(V, T, V0)
    return Pcold + Pth

# -----------------------------------------------------------------------------
# 3) Generate and plot V vs. P for two temperatures
# -----------------------------------------------------------------------------

def main():
    # We'll define a range of volumes in cm^3/mol (covering large compression).
    # This may need tuning to ensure we reach up to 300 GPa.
    V_min = 2.5
    V_max = 7.5
    n_points = 500
    V_array = np.linspace(V_min, V_max, n_points)

    # Temperatures to compare
    T_ambient = 300
    T_high = 5000

    # Compute total pressures for each T
    P_amb = total_pressure(V_array, T_ambient, V0_mol, K0, K0p)
    P_high = total_pressure(V_array, T_high, V0_mol, K0, K0p)

    # We want to focus on 50–300 GPa, so let's filter:
    def filter_P(Vvals, Pvals):
        mask = (Pvals >= 60) & (Pvals <= 390)
        return Vvals[mask], Pvals[mask]

    V_amb_filtered, P_amb_filtered = filter_P(V_array, P_amb)
    V_high_filtered, P_high_filtered = filter_P(V_array, P_high)

    # Convert volume from cm^3/mol to cm^3/g
    # V(cm^3/g) = V(cm^3/mol) / MFe(g/mol)
    V_amb_filtered_cmg = V_amb_filtered / MFe
    V_high_filtered_cmg = V_high_filtered / MFe

    # Plot: V (cm^3/g) vs P (GPa)
    plt.figure(figsize=(6,5))
    plt.plot(P_amb_filtered, V_amb_filtered_cmg, 'b-', label='300 K')
    plt.plot(P_high_filtered, V_high_filtered_cmg, 'r-', label='5000 K')

    plt.xlabel('Pressure (GPa)', fontsize=12)
    plt.ylabel('Volume (cm$^3$/g)', fontsize=12)
    plt.title('hcp-Fe: V vs. P for Two Temperatures', fontsize=14)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()