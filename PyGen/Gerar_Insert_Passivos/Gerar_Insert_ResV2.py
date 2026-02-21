import os

# =============================================================================
# CONSTANTES BASEADAS NO DATASHEET YAGEO RC (SÉRIE RC_L)
# =============================================================================

E24_VALUES = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7,
    3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
]

E96_VALUES = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
    1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
    1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
    2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
    3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
    5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
    7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76
]

DECADES = [10**i for i in range(-1, 8)]  # 0.1 a 10M

TOLERANCE = "1%"
MANUFACTURER = "Yageo"
CATEGORY = "Resistor"
SUBCATEGORY = "Thick Film"
MOUNT = "SMD"
UNIT = "Ohm"
TECH_MATERIAL = "Thick Film"
TEMP_COEFF = "±100ppm/°C"
TEMP_RANGE = "-55°C ~ 155°C"
REACH = "Yes"
ROHS = "Yes"
CREATED_BY = "Rogerio Fontanario"
DATASHEET_URL = "https://yageogroup.com/content/datasheet/asset/file/PYU-RC_GROUP_51_ROHS_L"

RESISTOR_SPECS = {
    "0402": {"powers": ["1/16W"], "r_min": 1.0, "r_max": 10_000_000,
             "footprint": "myLib_Resistor_SMD:R_0402_1005Metric", "footprint_filter": "R_0402*"},
    "0603": {"powers": ["1/10W"], "r_min": 1.0, "r_max": 10_000_000,
             "footprint": "myLib_Resistor_SMD:R_0603_1608Metric", "footprint_filter": "R_0603*"},
    "0805": {"powers": ["1/8W"], "r_min": 1.0, "r_max": 10_000_000,
             "footprint": "myLib_Resistor_SMD:R_0805_2012Metric", "footprint_filter": "R_0805*"},
    "1206": {"powers": ["1/4W"], "r_min": 1.0, "r_max": 10_000_000,
             "footprint": "myLib_Resistor_SMD:R_1206_3216Metric", "footprint_filter": "R_1206*"},
    "1210": {"powers": ["1/2W"], "r_min": 1.0, "r_max": 10_000_000,
             "footprint": "myLib_Resistor_SMD:R_1210_3225Metric", "footprint_filter": "R_1210*"},
    "2010": {"powers": ["3/4W"], "r_min": 1.0, "r_max": 10_000_000,
             "footprint": "myLib_Resistor_SMD:R_2010_5025Metric", "footprint_filter": "R_2010*"},
    "2512": {"powers": ["1W", "2W"], "r_min": 1.0, "r_max": 10_000_000,
             "footprint": "myLib_Resistor_SMD:R_2512_6332Metric", "footprint_filter": "R_2512*"},
}

# =============================================================================
# FUNÇÃO DE FORMATAÇÃO CORRIGIDA
# =============================================================================
def format_resistance(value_ohms):
    """
    Converte valor em ohms para string no formato padrão:
    - < 1Ω: 0RXX (duas casas)
    - 1Ω a 999Ω: XXR, XXRX, XXRXX (conforme necessário)
    - 1kΩ a 999kΩ: XXK, XXKX, XXKXX
    - ≥ 1MΩ: XXM, XXMX, XXMXX
    """
    v = round(value_ohms, 6)
    
    if v < 1:
        cent = int(round(v * 100))
        return f"0R{cent:02d}"
    elif v < 1000:
        if abs(v - round(v)) < 1e-6:
            return f"{int(round(v))}R"
        else:
            s = f"{v:.6f}".rstrip('0').rstrip('.')
            return s.replace('.', 'R')
    elif v < 1e6:
        k = v / 1000.0
        if abs(k - round(k)) < 1e-6:
            return f"{int(round(k))}K"
        else:
            s = f"{k:.6f}".rstrip('0').rstrip('.')
            return s.replace('.', 'K')
    else:
        m = v / 1e6
        if abs(m - round(m)) < 1e-6:
            return f"{int(round(m))}M"
        else:
            s = f"{m:.6f}".rstrip('0').rstrip('.')
            return s.replace('.', 'M')

# =============================================================================
# FUNÇÃO PARA GERAR VALORES ÚNICOS (usando a string formatada como chave)
# =============================================================================
def generate_unique_resistance_values(series_values, decades, r_min, r_max):
    unique = {}
    for mult in decades:
        for val in series_values:
            r = val * mult
            if r_min <= r <= r_max:
                r_str = format_resistance(r)
                r_rounded = round(r, 6)
                if r_str not in unique:
                    unique[r_str] = r_rounded
    return unique

# =============================================================================
# FUNÇÃO PARA GERAR PART NUMBER YAGEO
# =============================================================================
def generate_yageo_pn(size, res_str, tol):
    tol_code = {"1%": "F"}.get(tol, "F")
    return f"RC{size}{tol_code}-07{res_str}L"

# =============================================================================
# GERAÇÃO PRINCIPAL
# =============================================================================
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mypn_counter = 1
    base_counter_per_package = 0

    for size, spec in RESISTOR_SPECS.items():
        mypn_counter = base_counter_per_package + 1

        unique_e24 = generate_unique_resistance_values(E24_VALUES, DECADES, spec["r_min"], spec["r_max"])
        unique_e96 = generate_unique_resistance_values(E96_VALUES, DECADES, spec["r_min"], spec["r_max"])
        combined = {**unique_e24, **unique_e96}
        sorted_items = sorted(combined.items(), key=lambda x: x[1])  # (string, valor)

        columns = [
            "MyPN", "Name", "Description", "Value", "Info1", "Info2",
            "Symbol", "Footprint", "Footprint_Filter", "Datasheet",
            "Manufacturer", "Manufacturer_PN",
            "Category", "Subcategory", "Package", "Mount",
            "Temperature_Range", "REACH_Compliant", "RoHS_Compliant",
            "Unit", "Tolerance", "Power_Rating", "Temperature_Coefficient",
            "Resistance", "Technology_Material",
            "Created_At", "Created_By"
        ]

        values_lines = []
        unique_powers = set(spec["powers"])

        for power in sorted(unique_powers):
            for res_str, res_ohms in sorted_items:
                name = f"RES_{size}_{res_str}_{TOLERANCE}"
                description = f"Resistor SMD {size} {res_str} {TOLERANCE} {power}"
                value = res_str
                info1 = TOLERANCE
                info2 = power
                mypn = f"EL-RES-{mypn_counter:06d}"
                mypn_counter += 1

                mfg_pn = generate_yageo_pn(size, res_str, TOLERANCE)

                values = [
                    mypn, name, description, value, info1, info2,
                    "myLib_Resistor:RES_US",
                    spec["footprint"],
                    spec["footprint_filter"],
                    DATASHEET_URL,
                    MANUFACTURER,
                    mfg_pn,
                    CATEGORY,
                    SUBCATEGORY,
                    size,
                    MOUNT,
                    TEMP_RANGE,
                    REACH,
                    ROHS,
                    UNIT,
                    TOLERANCE,
                    power,
                    TEMP_COEFF,
                    res_str,
                    TECH_MATERIAL,
                    "datetime('now')",
                    CREATED_BY
                ]

                formatted = []
                for v in values:
                    if v is None:
                        formatted.append("NULL")
                    elif isinstance(v, int):
                        formatted.append(str(v))
                    elif v == "datetime('now')":
                        formatted.append(v)
                    else:
                        v_escaped = str(v).replace("'", "''")
                        formatted.append(f"'{v_escaped}'")
                values_lines.append("(" + ", ".join(formatted) + ")")

        if values_lines:
            output_file = os.path.join(script_dir, f"insert_resistor_{size}.sql")
            header = f"INSERT INTO Resistor_{size} ({', '.join(columns)}) VALUES\n"
            body = ",\n".join(values_lines) + ";"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"-- Script de inserção para Resistor_{size}\n")
                f.write(f"-- Baseado no datasheet YAGEO RC série\n")
                f.write(f"-- Tolerância: 1% (séries E24 e E96)\n\n")
                f.write(header)
                f.write(body)
                f.write("\n")
            print(f"Arquivo gerado: {output_file} com {len(values_lines)} inserts")

        base_counter_per_package += 100000

if __name__ == "__main__":
    main()