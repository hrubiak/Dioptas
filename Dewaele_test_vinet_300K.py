import numpy as np
import matplotlib.pyplot as plt

###############################################################################
# 1) Vinet EOS (cold, no thermal terms)
###############################################################################
def vinet_pressure(V, V0, K0, K0p):
    """
    Computes P(V) in GPa from the Vinet equation of state:
      P = 3K0 * (1 - x)/x^2 * exp[3/2*(K0p - 1)*(1 - x)]
    where x = (V/V0)^(1/3).
    
    Parameters
    ----------
    V   : float or array
          Volume in cm^3/mol
    V0  : float
          Reference volume (cm^3/mol)
    K0  : float
          Bulk modulus at reference volume (GPa)
    K0p : float
          Derivative of the bulk modulus
    
    Returns
    -------
    P   : float or array
          Pressure in GPa
    """
    x = (V / V0)**(1.0/3.0)
    return 3.0*K0*(1.0 - x)/(x**2) * np.exp((3.0/2.0)*(K0p - 1.0)*(1.0 - x))

###############################################################################
# 2) Parameters and Conversions
###############################################################################
# V0 in Å^3/atom -> first convert to cm^3/mol
#   1 Å^3 = 1e-24 cm^3
#   multiply by Avogadro's number 6.022e23 to get cm^3/mol
V0_atom = 11.214
V0_mol  = V0_atom * 1e-24 * 6.022e23  # ~6.76 cm^3/mol
V0_mol  = 6.76  # We'll just use ~6.76 from your reference

K0  = 163.4  # GPa
K0p = 5.38   # dimensionless

# Molar mass of iron:
MFe = 55.845  # g/mol

# Conversion factor: from Å^3/atom -> cm^3/g
#   (Å^3/atom) * (1e-24 cm^3/Å^3) * (6.022e23 atoms/mol) / (55.845 g/mol)
conversion_factor = (1e-24 * 6.022e23) / MFe  # ~0.01078

###############################################################################
# 3) Experimental Data (P in GPa, V in Å^3/atom)
###############################################################################
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

exp_P = exp_raw_data[:, 0]        # GPa
exp_VA3 = exp_raw_data[:, 1]      # Å^3/atom
exp_V_cmg = exp_VA3 * conversion_factor  # cm^3/g

###############################################################################
# 4) Generate the "cold" Vinet curve
###############################################################################
def main():
    # We'll do a volume sweep in cm^3/mol and compute P(V) using vinet_pressure.
    # Then we'll plot in the range ~10–300 GPa for clarity.

    # Volume range (cm^3/mol)
    V_min = 1.0
    V_max = 8.0
    n_points = 600
    V_array = np.linspace(V_min, V_max, n_points)

    # Compute P(V) from the Vinet EOS
    P_vinet = vinet_pressure(V_array, V0_mol, K0, K0p)

    # Filter for, say, 10–300 GPa so we can see the main region
    mask = (P_vinet >= 10) & (P_vinet <= 300)
    V_plot = V_array[mask]
    P_plot = P_vinet[mask]

    # Convert volumes from cm^3/mol -> cm^3/g for plotting
    V_cmg = V_plot / MFe

    # Plot
    plt.figure(figsize=(6,5))
    # Vinet EOS
    plt.plot(P_plot, V_cmg, 'b-', label='Vinet (cold)')

    # Experimental data
    plt.scatter(exp_P, exp_V_cmg, color='k', marker='o', label='Exp. Data')

    plt.xlabel('Pressure (GPa)', fontsize=12)
    plt.ylabel('Volume (cm$^3$/g)', fontsize=12)
    plt.title('hcp-Fe: Plain Vinet EOS vs. 300 K Data', fontsize=14)
    plt.xlim(10, 310)
    plt.ylim(0.07, 0.10)  # Adjust as needed
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()