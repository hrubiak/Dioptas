import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

###############################################################################
# 1) Vinet EOS (300 K Baseline)
###############################################################################
def vinet_300K_pressure(V, V0, K0, K0p):
    """
    Published 300 K Vinet fit that already matches 300 K data.
    V and V0 in cm^3/mol; returns pressure in GPa.
    """
    x = (V / V0)**(1.0/3.0)
    return 3.0 * K0 * (1.0 - x) / (x**2) * np.exp(1.5 * (K0p - 1.0) * (1.0 - x))

###############################################################################
# 2) Standard Thermal Pressure (Mie–Grüneisen–Debye)
###############################################################################
def debye_integral(zmax):
    """
    Evaluate the Debye integral: ∫₀^(zmax) z³/(exp(z)-1) dz.
    """
    def integrand(z):
        return z**3 / (np.exp(z) - 1.0)
    val, _ = quad(integrand, 0, zmax)
    return val

def usual_thermal_pressure(V, T, V0, theta0, gamma0, gamma_inf, beta_g,
                           a0, m_anh, e0, g_el, R=8.314462618):
    """
    Compute the full thermal pressure (in GPa) using a standard Dorogokupets/Dewaele‐like 
    Mie–Grüneisen–Debye model. V and V0 in cm^3/mol, T in K.
    """
    x = V / V0
    # Volume-dependent Grüneisen parameter:
    gamma_val = gamma_inf + (gamma0 - gamma_inf) * x**beta_g
    # Exact integral approach for Debye temperature:
    theta = theta0 * (x**(-gamma_inf)) * np.exp(- (gamma0 - gamma_inf) / beta_g * (x**beta_g - 1.0))
    # Debye integral:
    th_ratio = theta / T
    F_D = np.vectorize(debye_integral, otypes=[float])(th_ratio)
    # Quasi-harmonic Debye term in J/(mol·cm^3)
    P_D = (9.0 * R * gamma_val / V) * (theta/8.0 + T * (T/theta)**3 * F_D)
    # Anharmonic term:
    P_anh = (3.0 * R / (2.0 * V)) * m_anh * a0 * (x**m_anh) * T**2
    # Electronic term:
    P_el  = (3.0 * R / (2.0 * V)) * g_el * e0 * (x**g_el) * T**2
    # Convert from J/(mol·cm^3) to GPa: 1 J/(mol·cm^3) = 1e-3 GPa
    return (P_D + P_anh + P_el) * 1e-3

###############################################################################
# 3) Thermal Pressure with Zero at 300 K
###############################################################################
def thermal_pressure_zero_at_300K(V, T, V0, theta0, gamma0, gamma_inf, beta_g,
                                  a0, m_anh, e0, g_el, R=8.314462618):
    """
    Returns the extra thermal pressure at T relative to 300 K:
      P_th*(V,T) = usual_thermal_pressure(V,T) - usual_thermal_pressure(V,300 K)
    so that at T=300 K this term is zero.
    """
    return (usual_thermal_pressure(V, T, V0, theta0, gamma0, gamma_inf, beta_g,
                                   a0, m_anh, e0, g_el, R)
            - usual_thermal_pressure(V, 300.0, V0, theta0, gamma0, gamma_inf, beta_g,
                                     a0, m_anh, e0, g_el, R))

###############################################################################
# 4) Full EOS: Baseline + Extra Thermal Pressure
###############################################################################
def total_pressure(V, T,
                   V0=6.76, K0=163.4, K0p=5.38,
                   theta0=417.0, gamma0=1.875, gamma_inf=1.305,
                   beta_g=None, a0=3.7e-5, m_anh=1.87, e0=1.95e-4, g_el=1.339,
                   R=8.314462618):
    """
    Computes the full EOS:
      P(V,T) = Vinet_300K(V) + [P_th(V,T) - P_th(V,300 K)].
    At T=300 K the extra thermal pressure is zero.
    """
    if beta_g is None:
        beta_g = gamma0 / (gamma0 - gamma_inf)  # e.g. ~3.289
    P_baseline = vinet_300K_pressure(V, V0, K0, K0p)
    extra_P_th = thermal_pressure_zero_at_300K(V, T, V0, theta0, gamma0, gamma_inf, beta_g,
                                               a0, m_anh, e0, g_el, R)
    return P_baseline + extra_P_th

###############################################################################
# 5) Raw Experimental Data (Ambient, 300 K)
###############################################################################
# (P in GPa, V_hcp in Å^3/atom) from ambient experiments
exp_raw_data = np.array([
    [17.7, 10.296],
    [17.8, 10.282],
    [19.9, 10.201],
    [21.4, 10.148],
    [22.9, 10.086],
    [24.1, 10.042],
    [27.3, 9.936],
    [28.1, 9.8802],
    [29.0, 9.857],
    [30.3, 9.8338],
    [30.4, 9.841],
    [33.6, 9.742],
    [36.1, 9.674],
    [36.3, 9.652],
    [38.0, 9.593],
    [42.9, 9.464],
    [47.2, 9.356],
    [47.5, 9.366],
    [53.0, 9.201],
    [55.2, 9.1604],
    [56.3, 9.155],
    [65.0, 8.963],
    [71.2, 8.854],
    [76.7, 8.752],
    [78.4, 8.74],
    [82.4, 8.659],
    [88.9, 8.553],
    [90.0, 8.565],
    [105.0, 8.3254],
    [106.0, 8.332],
    [122.0, 8.1093],
    [127.0, 8.071],
    [133.0, 8.01],
    [136.0, 7.9487],
    [143.0, 7.899],
    [146.0, 7.8436],
    [154.0, 7.778],
    [157.0, 7.7307],
    [163.0, 7.701],
    [167.0, 7.6604],
    [172.0, 7.618],
    [176.0, 7.5693],
    [181.0, 7.539],
    [188.0, 7.4474],
    [189.0, 7.478],
    [195.0, 7.426],
    [197.0, 7.3906],
    [201.0, 7.356],
    [202.0, 7.358],
    [205.0, 7.33]
])
exp_P = exp_raw_data[:, 0]       # in GPa
exp_V_A3 = exp_raw_data[:, 1]      # in Å^3/atom

# Convert ambient experimental volume to cm^3/g:
# Conversion: (Å^3/atom) * (1e-24 cm^3/Å^3) * (6.022e23 atoms/mol) / (55.845 g/mol)
conversion_factor = (1e-24 * 6.022e23) / 55.845  # ~0.01078
exp_V_cmg = exp_V_A3 * conversion_factor

###############################################################################
# 6) Digitized 5000 K Data from Dewaele et al. (units: GPa, (cm^3/g)/1000)
###############################################################################
digitized_5000 = np.array([
    [103.27868852459017, 98.69402985074626],
    [117.21311475409836, 95.74626865671641],
    [139.34426229508196, 91.86567164179104],
    [153.68852459016392, 89.73880597014926],
    [172.54098360655738, 87.20149253731343],
    [198.36065573770492, 84.25373134328358],
    [227.8688524590164, 81.38059701492537],
    [258.60655737704917, 78.76865671641791],
    [290.5737704918033, 76.45522388059702],
    [329.0983606557377, 73.99253731343283],
    [361.0655737704918, 72.23880597014926]
])
digitized_P = digitized_5000[:, 0]  # in GPa
digitized_V_div1000 = digitized_5000[:, 1]  # in (cm^3/g)/1000
# Convert to cm^3/g by multiplying by 1e-3:
digitized_V = digitized_V_div1000 * 1e-3

###############################################################################
# 7) Plot EOS for 300, 5000, 6000, and 7000 K with Experimental Data
###############################################################################
def main():
    # Generate a volume range in cm^3/mol for the EOS curves.
    V_min = 1.0
    V_max = 8.0
    n_points = 600
    V_array = np.linspace(V_min, V_max, n_points)
    
    # Define temperatures to plot:
    temperatures = [300, 5000, 6000, 7000]
    labels = ['300 K', '5000 K', '6000 K', '7000 K']
    colors = ['blue', 'red', 'green', 'magenta']
    
    plt.figure(figsize=(8,7))
    for T, label, color in zip(temperatures, labels, colors):
        P_curve = total_pressure(V_array, T,
                                 V0=6.76, K0=163.4, K0p=5.38,
                                 theta0=417.0, gamma0=1.875, gamma_inf=1.305,
                                 beta_g=None, a0=3.7e-5, m_anh=1.87,
                                 e0=1.95e-4, g_el=1.339)
        # Convert V_array (cm^3/mol) to cm^3/g by dividing by molar mass 55.845
        V_cmg = V_array / 55.845
        
        # Filter for plotting in the pressure range 10–310 GPa
        mask = (P_curve >= 10) & (P_curve <= 310)
        P_plot = P_curve[mask]
        V_plot = V_cmg[mask]
        
        plt.plot(P_plot, V_plot, '-', color=color, lw=2, label=label)
    
    # Overlay ambient (300 K) experimental data:
    plt.scatter(exp_P, exp_V_cmg, c='black', marker='o', s=50, label='Exp. (300 K)')
    
    # Overlay digitized 5000 K data:
    plt.scatter(digitized_P, digitized_V, facecolors='none', edgecolors='red',
                marker='s', s=70, label='Digitized (5000 K)')
    
    plt.xlabel('Pressure (GPa)', fontsize=12)
    plt.ylabel('Volume (cm$^3$/g)', fontsize=12)
    plt.title('hcp-Fe: EOS Curves and Experimental Data', fontsize=14)
    plt.xlim(10, 310)
    plt.ylim(0.07, 0.10)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()