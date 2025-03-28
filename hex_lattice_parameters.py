def hexagonal_lattice_parameters(V_mol, c_over_a):
    import numpy as np
    N_A = 6.022e23
    # The conventional hcp unit cell (with 2 atoms) has volume:
    V_cell = 2 * V_mol / N_A  # in m³
    # For a hexagonal cell: V_cell = (sqrt(3)/2) * a² * c, with c = (c_over_a)*a.
    # Hence, a³ = (2 * V_cell) / (sqrt(3) * c_over_a)
    a_m = ((2 * V_cell) / (np.sqrt(3) * c_over_a)) ** (1/3)
    a = a_m * 1e10  # convert m to Å
    b = a
    c = c_over_a * a
    return a, b, c

# Example:
# V_mol = 6.753e-06 m³/mol and c/a ~ 1.6
a, b, c = hexagonal_lattice_parameters(6.753e-06, 1.6)
print("a =", a, "Å, b =", b, "Å, c =", c, "Å")