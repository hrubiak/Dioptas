import numpy as np
from math import exp
from scipy.integrate import quad

# ====== EOS (Pt, Matsui 2009) ======
class PtMatsui2009:
    def __init__(self):
        pass

    @staticmethod
    def _to_internal_units(params):
        p = dict(params)
        p["_V0_cm3mol"] = p["V_0"] * 1e6   # m^3/mol -> cm^3/mol
        p["_K0_GPa"] = p["K_0"] / 1e9      # Pa -> GPa
        return p

    @staticmethod
    def _vinet_300K_pressure(V_cm3mol, V0_cm3mol, K0_GPa, Kp0):
        x = (V_cm3mol / V0_cm3mol)**(1.0/3.0)
        return 3.0 * K0_GPa * (1.0 - x) / (x**2) * exp(1.5 * (Kp0 - 1.0) * (1.0 - x))

    @staticmethod
    def _debye_integral(zmax):
        if zmax < 1e-6:
            return zmax**3 / 3.0
        def f(z): return z**3 / (np.exp(z) - 1.0)
        val, _ = quad(f, 0.0, zmax, epsabs=1e-10, epsrel=1e-10)
        return val

    @staticmethod
    def _gamma_V(gamma0, q, V_cm3mol, V0_cm3mol):
        return gamma0 * (V_cm3mol / V0_cm3mol)**q

    @staticmethod
    def _theta_V(theta0, gamma0, q, gammaV):
        return theta0 * exp((gamma0 - gammaV) / q)

    def Pth_GPa(self, V_cm3mol, T, p):
        # Lattice thermal pressure (zeroed at 300 K)
        R = 8.314462618
        gV = self._gamma_V(p["grueneisen_0"], p["q_0"], V_cm3mol, p["_V0_cm3mol"])
        theta = self._theta_V(p["Debye_0"], p["grueneisen_0"], p["q_0"], gV)
        def Eth(Tin):
            zmax = theta / Tin
            I = self._debye_integral(zmax)
            return 9.0 * p["n"] * R * Tin * (Tin / theta)**3 * I  # J/mol
        dE = Eth(T) - Eth(300.0)
        return gV / V_cm3mol * dE * 1e-3  # J/(mol·cm^3) → GPa

    @staticmethod
    def DeltaPel_GPa(T):
        # Electronic term disabled:
        return 0.0
        # To re-enable later, replace with:
        # s = 0.00613  # GPa/K
        # return s * (T - 300.0)

    def pressure_terms_GPa(self, T, V_m3_per_mol, params_SI):
        """Return tuple: (P300, Pth, Pel, Ptotal) in GPa."""
        p = self._to_internal_units(params_SI)
        V_cm3mol = V_m3_per_mol * 1e6
        P300 = self._vinet_300K_pressure(V_cm3mol, p["_V0_cm3mol"], p["_K0_GPa"], p["Kprime_0"])
        Pth  = self.Pth_GPa(V_cm3mol, T, p)
        Pel  = self.DeltaPel_GPa(T)
        return P300, Pth, Pel, P300 + Pth + Pel

# ====== Default Pt parameters (Matsui 2009) ======
PT_PARAMS = {
    "V_0": 9.06e-06,   # m^3/mol  (~9.06 cm^3/mol ≈ fcc Pt at 300 K)
    "K_0": 273e9,      # Pa
    "Kprime_0": 5.20,
    "Debye_0": 230.0,  # K
    "grueneisen_0": 2.70,
    "q_0": 1.10,
    "n": 1,
    "molar_mass": 0.195084
}

# ====== USER SETTINGS ======
INPUT_FILE = "table.txt"        # two columns: T[K], V (Å^3) per atom OR per conventional fcc cell
V_IS_ATOMIC = False             # True if the second column is Å^3/atom; False if Å^3 per conventional fcc cell
FCC_ATOMS_PER_CELL = 4.0        # conventional fcc has 4 atoms
SET_V0_FROM_ROW = None          # e.g., 0 to use the first row’s volume (converted) as V0; or None to keep PT_PARAMS["V_0"]

# ====== Load table ======
rows = []
with open(INPUT_FILE, "r") as f:
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
            V_in = float(parts[1])
            rows.append((T, V_in))
        except ValueError:
            continue

if not rows:
    raise RuntimeError("No valid numeric rows found in table.")

# ====== Conversion helpers ======
NA = 6.02214076e23

def to_molar_volume_m3_per_mol(V_input_A3, atomic=False):
    """
    Convert input Å^3 value to molar volume (m^3/mol).
    atomic=False: input is per conventional fcc cell (Å^3/cell)
    atomic=True:  input is per atom (Å^3/atom)
    """
    if atomic:
        V_atom_m3 = V_input_A3 * 1e-30
        return V_atom_m3 * NA               # molar (per mol of atoms)
    else:
        V_cell_m3 = V_input_A3 * 1e-30
        return V_cell_m3 * (NA / FCC_ATOMS_PER_CELL)

# ====== Optional: anchor V0 to a row in your table ======
if SET_V0_FROM_ROW is not None:
    V0_row = to_molar_volume_m3_per_mol(rows[SET_V0_FROM_ROW][1], atomic=V_IS_ATOMIC)
    PT_PARAMS["V_0"] = V0_row
    print(f"[info] V_0 set from row {SET_V0_FROM_ROW}: {V0_row:.6e} m^3/mol")

# ====== Compute and print ======
eos = PtMatsui2009()
print("   T(K)       Vin(Å^3)     V(m^3/mol)   V/V0    P300  Pth   Pel   Ptot  (all GPa)")
print("----------------------------------------------------------------------------------")
for T, V_in in rows:
    V_m3_per_mol = to_molar_volume_m3_per_mol(V_in, atomic=V_IS_ATOMIC)
    P300, Pth, Pel, Ptot = eos.pressure_terms_GPa(T, V_m3_per_mol, PT_PARAMS)
    VV0 = V_m3_per_mol / PT_PARAMS["V_0"]
    print(f"{T:7.1f}  {V_in:12.4f}  {V_m3_per_mol:11.3e}  {VV0:5.3f}  {P300:5.2f} {Pth:5.2f} {Pel:5.2f} {Ptot:6.2f}")