# === read table (two columns: T[K], V[Å^3]) ===
def load_TV_table(path):
    pts = []
    with open(path, "r") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            s = s.replace(",", " ")
            parts = s.split()
            if len(parts) < 2:
                continue
            try:
                T = float(parts[0])
                V = float(parts[1])
                pts.append((T, V))
            except ValueError:
                pass
    if not pts:
        raise RuntimeError("No valid (T, V) rows found.")
    return pts

# === upper convex hull (Andrew's monotone chain) ===
def upper_convex_hull(points, dedup_at_same_T=True):
    """
    points: list of (T, V). Returns the upper hull as a list of (T, V) in ascending T.
    By default, if multiple points share the same T, keeps only the one with max V.
    """
    if dedup_at_same_T:
        # if multiple entries at same T, keep the highest V (your reliability heuristic)
        byT = {}
        for T, V in points:
            if T not in byT or V > byT[T]:
                byT[T] = V
        pts = sorted([(T, V) for T, V in byT.items()], key=lambda x: (x[0], x[1]))
    else:
        pts = sorted(points, key=lambda x: (x[0], x[1]))

    # cross product (o->a) x (o->b)
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])

    # build UPPER hull (keeps clockwise turns; removes concave-down violations)
    upper = []
    for p in pts:
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) >= 0:
            upper.pop()
        upper.append(p)

    # The hull is already left→right (ascending T)
    return upper

# === example driver ===
if __name__ == "__main__":
    INPUT_FILE = "table.txt"  # two columns: T[K]  V[Å^3]
    pts = load_TV_table(INPUT_FILE)
    upper = upper_convex_hull(pts)

    print("Upper convex hull (T, V[Å^3]):")
    for T, V in upper:
        print(f"{T:.3f}  {V:.6f}")

    # optional: save filtered points
    with open("table_upper_hull.txt", "w") as g:
        g.write("# T[K], V[Å^3] (upper hull only)\n")
        for T, V in upper:
            g.write(f"{T:.6f} {V:.6f}\n")
            import numpy as np

# ---------- Holmes et al. (1989) Platinum EOS (implementable core) ----------
# Ref: Vinet 300 K isotherm (Eq. 11) and simple Mie–Grüneisen lattice thermal add-on.  [oai_citation:3‡2962_1_online.pdf](sediment://file_0000000010a461faa7cb242c140fbf48)

def vinet_300K_pressure_GPa(V_m3_per_mol, V0_m3_per_mol, B_T_GPa, B_T_prime):
    """
    300 K Vinet ('universal') isotherm:
      X = (V/V0)^(1/3),
      eta = 1.5*(B_T' - 1),
      P_300 = 3*B_T * ((1 - X)/X^2) * exp[ eta*(1 - X) ]   [GPa]
    Inputs in molar units (m^3/mol) and GPa.
    """
    V, V0 = V_m3_per_mol, V0_m3_per_mol
    X = (V / V0) ** (1.0/3.0)
    eta = 1.5 * (B_T_prime - 1.0)
    return 3.0 * B_T_GPa * (1.0 - X) / (X * X) * np.exp(eta * (1.0 - X))

def lattice_thermal_pressure_GPa(V_m3_per_mol, T_K, gamma_ion=2.5, T0_K=300.0):
    """
    Simple Mie–Grüneisen lattice thermal pressure (Holmes et al. text):
      P_th ≈ (gamma / V) * ΔE_ion,   ΔE_ion ≈ 3 R (T - T0)   [per mole]
    Convert J/(mol·m^3) to GPa: divide by 1e9.
    """
    R = 8.314462618  # J/(mol·K)
    dE = 3.0 * R * (T_K - T0_K)                         # J/mol
    return (gamma_ion / V_m3_per_mol) * dE / 1e9        # GPa

def holmes1989_P_GPa(V_m3_per_mol, T_K, params, include_electronic=False):
    """
    Total pressure P(V,T) = P_300(V) + P_th(V,T) [+ P_el(V,T) if desired].
    params: dict with keys:
      V0_m3_per_mol, B_T_GPa, B_T_prime, gamma_ion (optional; default 2.5)
    """
    P300 = vinet_300K_pressure_GPa(V_m3_per_mol, params["V0_m3_per_mol"],
                                   params["B_T_GPa"], params["B_T_prime"])
    Pth  = lattice_thermal_pressure_GPa(V_m3_per_mol, T_K, params.get("gamma_ion", 2.5))
    Pel  = 0.0
    if include_electronic:
        # Electronic thermal pressure per paper depends on DOS at EF;
        # typically small for 300 K isotherms—left 0 by default.  [oai_citation:4‡2962_1_online.pdf](sediment://file_0000000010a461faa7cb242c140fbf48)
        pass
    return P300 + Pth + Pel


pt_params = {
    "V0_m3_per_mol": 9.06e-06,
    "B_T_GPa": 278.0,
    "B_T_prime": 5.61,
    "gamma_ion": 2.5
}

def cell_volume_to_molar_m3_per_mol(V_cell_A3, atoms_per_cell=4.0):
    """
    Convert crystallographic unit-cell volume from Å³ to molar volume (m³/mol).

    Parameters
    ----------
    V_cell_A3 : float or ndarray
        Unit-cell volume in Å³ (1 Å³ = 1e-30 m³).
    atoms_per_cell : float, optional
        Number of atoms per conventional unit cell.
        For fcc metals (Pt, Au, etc.), use 4.0.

    Returns
    -------
    V_m3_per_mol : float or ndarray
        Molar volume in m³/mol.
    """
    NA = 6.02214076e23  # Avogadro constant [1/mol]
    return V_cell_A3 * 1e-30 * (NA / atoms_per_cell)



import math

# --------- Conversions ----------
def cell_volume_to_molar_m3_per_mol(V_cell_A3, atoms_per_cell=4.0):
    NA = 6.02214076e23
    return V_cell_A3 * 1e-30 * (NA / atoms_per_cell)

# --------- Holmes-style EOS (Vinet@300K + lattice Debye-MG + optional electronic) ----------
def vinet_300K_pressure_GPa(V_m3_per_mol, V0_m3_per_mol, K0_GPa, Kprime0):
    X   = (V_m3_per_mol / V0_m3_per_mol)**(1.0/3.0)
    eta = 1.5 * (Kprime0 - 1.0)
    return 3.0 * K0_GPa * (1.0 - X) / (X*X) * math.exp(eta * (1.0 - X))

def lattice_thermal_pressure_GPa(V_m3_per_mol, T_K, gamma_ion=2.5, T0_K=300.0):
    R  = 8.314462618                 # J/mol/K
    dE = 3.0 * R * (T_K - T0_K)      # J/mol
    return (gamma_ion / V_m3_per_mol) * dE / 1e9

def electronic_thermal_pressure_GPa(V_m3_per_mol, T_K,
                                    gamma_el=1.8,        # Holmes: ~constant ~1.8
                                    gamma_S=6.5e-3,      # Sommerfeld coef (J/mol/K^2) ~6.5 mJ/mol/K^2 for Pt
                                    T0_K=300.0):
    # ΔE_el = 0.5 * gamma_S * (T^2 - T0^2)  [J/mol]
    dE = 0.5 * gamma_S * (T_K*T_K - T0_K*T0_K)
    return (gamma_el / V_m3_per_mol) * dE / 1e9          # -> GPa

def holmes_P_GPa(V_m3_per_mol, T_K, params,
                 include_electronic=False):
    """
    params must contain:
      V0_m3_per_mol, K0_GPa, Kprime0,
      gamma_ion (optional, default 2.5),
      gamma_el (optional, default 1.8),
      gamma_S  (optional, default 6.5e-3 J/mol/K^2),
      T0_K     (optional, default 300.0)
    """
    V0   = params["V0_m3_per_mol"]
    K0   = params["K0_GPa"]
    K0p  = params["Kprime0"]
    gion = params.get("gamma_ion", 2.5)
    gel  = params.get("gamma_el", 1.8)
    gS   = params.get("gamma_S", 6.5e-3)
    T0   = params.get("T0_K", 300.0)

    P300 = vinet_300K_pressure_GPa(V_m3_per_mol, V0, K0, K0p)
    Pth  = lattice_thermal_pressure_GPa(V_m3_per_mol, T_K, gamma_ion=gion, T0_K=T0)
    Pel  = electronic_thermal_pressure_GPa(V_m3_per_mol, T_K, gamma_el=gel, gamma_S=gS, T0_K=T0) if include_electronic else 0.0
    return P300 + Pth + Pel, (P300, Pth, Pel)

# --------- Driver for your table (two columns: T[K]  V_cell[Å^3]) ----------
def compute_pressures_from_table(input_path,
                                 atoms_per_cell=4.0,
                                 v_is_atomic=False,
                                 include_electronic=False,
                                 params=None,
                                 output_path=None):
    if params is None:
        params = {
            "V0_m3_per_mol": 9.06e-06,  # Pt ~300K
            "K0_GPa": 278.0,
            "Kprime0": 5.61,
            "gamma_ion": 2.5,
            "gamma_el": 1.8,
            "gamma_S": 6.5e-3,          # J/mol/K^2
            "T0_K": 300.0
        }

    rows = []
    with open(input_path, "r") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            s = s.replace(",", " ")
            parts = s.split()
            if len(parts) < 2:
                continue
            try:
                T = float(parts[0]); V_in = float(parts[1])
            except ValueError:
                continue
            rows.append((T, V_in))

    NA = 6.02214076e23
    def to_molar(V_A3):
        if v_is_atomic:
            return V_A3 * 1e-30 * NA            # Å^3/atom -> m^3/mol
        else:
            return cell_volume_to_molar_m3_per_mol(V_A3, atoms_per_cell=atoms_per_cell)  # Å^3/cell -> m^3/mol

    out = []
    print("   T(K)       V_in(Å^3)     V(m^3/mol)   V/V0    P300   Pth   Pel   Ptot   (GPa)")
    print("---------------------------------------------------------------------------------")
    for (T, V_in) in rows:
        V_m = to_molar(V_in)
        Ptot, (P300, Pth, Pel) = holmes_P_GPa(V_m, T, params, include_electronic=include_electronic)
        VV0 = V_m / params["V0_m3_per_mol"]
        print(f"{T:7.1f}  {V_in:12.4f}  {V_m:11.3e}  {VV0:5.3f}  {P300:6.2f} {Pth:6.2f} {Pel:6.2f} {Ptot:7.2f}")
        out.append((T, V_in, V_m, Ptot))

    if output_path:
        with open(output_path, "w") as g:
            g.write("T_K,Vcell_A3,V_m3_per_mol,P_GPa\n")
            for T, V_in, Vmol, P in out:
                g.write(f"{T:.6f},{V_in:.6f},{Vmol:.10e},{P:.6f}\n")

    return out

# ---- Example (run from IDE) ----
if __name__ == "__main__":
    INPUT_FILE = "table_upper_hull.txt"      # two columns: T[K]  V_cell[Å^3] (per fcc conventional cell by default)
    V_IS_ATOMIC = False           # set True if your volumes are per atom
    ATOMS_PER_CELL = 4.0          # fcc Pt
    INCLUDE_ELECTRONIC = True     # toggle P_el on/off

    compute_pressures_from_table(INPUT_FILE,
                                 atoms_per_cell=ATOMS_PER_CELL,
                                 v_is_atomic=V_IS_ATOMIC,
                                 include_electronic=INCLUDE_ELECTRONIC,
                                 output_path="pressures_holmes_with_Pel.csv")