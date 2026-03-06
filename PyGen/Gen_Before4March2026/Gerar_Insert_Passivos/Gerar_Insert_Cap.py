import os
import math
from collections import defaultdict

# ------------------------------------------------------------
# URLs dos Datasheets (ATUALIZADAS com os links fornecidos)
# ------------------------------------------------------------
DATASHEET_URLS = {
    "C0G": "https://octopart.com/datasheet/yageo-group/CC0603JRNPO9BN100",  # Link original (pode estar offline)
    "X5R": "https://octopart.com/datasheet/yageo-group/CC0402KRX5R6BB224",
    "X7R": "https://octopart.com/datasheet/yageo-group/CC0805KRX7R9BB104"
}
# Nota: O link do C0G retorna erro 403. Mantive o link original para referência.
# Caso prefira, pode substituir por um link genérico da YAGEO.

# ------------------------------------------------------------
# Constantes - séries de valores (mesmas do script anterior)
# ------------------------------------------------------------
C0G_VALUES_PF = [0.22, 0.47, 0.82, 1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2,
                 10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82,
                 100, 120, 150, 180, 220, 270, 330, 390, 470, 560, 680, 820,
                 1000, 1200, 1500, 1800, 2200, 2700, 3300, 3900, 4700, 5600, 6800, 8200,
                 10000, 12000, 15000, 18000, 22000, 27000, 33000, 39000, 47000, 56000, 68000, 82000,
                 100000]

X5R_X7R_VALUES_PF = [100, 150, 220, 330, 470, 680,
                      1000, 1500, 2200, 3300, 4700, 6800,
                      10000, 15000, 22000, 33000, 47000, 68000,
                      100000, 150000, 220000, 330000, 470000, 680000,
                      1000000, 1500000, 2200000, 3300000, 4700000, 6800000,
                      10000000, 15000000, 22000000, 33000000, 47000000, 68000000,
                      100000000, 150000000, 220000000, 330000000, 470000000]

# ------------------------------------------------------------
# Limites extraídos dos datasheets YAGEO (MANTIDOS da versão anterior)
# ------------------------------------------------------------
LIMITS = {
    ("0201", "C0G"): {25: 100, 50: 100},
    ("0402", "C0G"): {16: 100_000, 25: 100_000, 50: 10_000},
    ("0603", "C0G"): {16: 100_000, 25: 100_000, 50: 100_000},
    ("0805", "C0G"): {16: 100_000, 25: 100_000, 50: 100_000},
    ("1206", "C0G"): {16: 100_000, 25: 100_000, 50: 100_000},
    ("1210", "C0G"): {16: 100_000, 25: 100_000, 50: 100_000},
    ("1812", "C0G"): {50: 100_000},
    ("2220", "C0G"): {},

    ("0201", "X5R"): {4: 4_700_000, 6.3: 4_700_000, 10: 4_700_000, 16: 4_700_000, 25: 4_700_000, 50: 4_700_000},
    ("0402", "X5R"): {4: 22_000_000, 6.3: 22_000_000, 10: 22_000_000, 16: 22_000_000, 25: 22_000_000, 50: 22_000_000},
    ("0603", "X5R"): {4: 100_000_000, 6.3: 100_000_000, 10: 100_000_000, 16: 100_000_000, 25: 100_000_000, 50: 100_000_000},
    ("0805", "X5R"): {4: 100_000_000, 6.3: 100_000_000, 10: 100_000_000, 16: 100_000_000, 25: 100_000_000, 50: 100_000_000},
    ("1206", "X5R"): {6.3: 220_000_000, 10: 220_000_000, 16: 220_000_000, 25: 220_000_000, 50: 220_000_000},
    ("1210", "X5R"): {6.3: 220_000_000, 10: 220_000_000, 16: 220_000_000, 25: 220_000_000, 50: 220_000_000},
    ("1812", "X5R"): {},
    ("2220", "X5R"): {},

    ("0201", "X7R"): {6.3: 2_200_000, 10: 2_200_000, 16: 2_200_000, 25: 2_200_000, 50: 2_200_000},
    ("0402", "X7R"): {6.3: 2_200_000, 10: 2_200_000, 16: 2_200_000, 25: 2_200_000, 50: 2_200_000, 100: 2_200_000},
    ("0603", "X7R"): {6.3: 10_000_000, 10: 10_000_000, 16: 10_000_000, 25: 10_000_000, 50: 2_200_000, 100: 1_000_000, 200: 100_000},
    ("0805", "X7R"): {6.3: 10_000_000, 10: 10_000_000, 16: 10_000_000, 25: 10_000_000, 50: 10_000_000, 100: 4_700_000, 200: 1_000_000, 250: 1_000_000},
    ("1206", "X7R"): {6.3: 22_000_000, 10: 22_000_000, 16: 22_000_000, 25: 22_000_000, 50: 10_000_000, 100: 4_700_000, 200: 2_200_000, 250: 1_000_000},
    ("1210", "X7R"): {6.3: 47_000_000, 10: 47_000_000, 16: 47_000_000, 25: 47_000_000, 50: 22_000_000, 100: 10_000_000, 200: 4_700_000, 250: 2_200_000},
    ("1812", "X7R"): {50: 1_000_000, 100: 470_000, 200: 220_000, 250: 100_000},
    ("2220", "X7R"): {50: 1_000_000, 100: 470_000, 200: 220_000, 250: 100_000},
}

# ------------------------------------------------------------
# Códigos YAGEO (baseado nos datasheets)
# ------------------------------------------------------------
VOLTAGE_CODES = {4: '4', 6.3: '5', 10: '6', 16: '7', 25: '8', 50: '9', 100: '1', 200: '2', 250: 'A'}
TOLERANCE_CODES = {"C0G": {"1%": "F", "5%": "J"}, "X5R": {"10%": "K", "20%": "M"}, "X7R": {"10%": "K", "20%": "M"}}
DIELECTRIC_CODES = {"C0G": "NPO", "X5R": "X5R", "X7R": "X7R"}
TOLERANCES = {"C0G": ["1%", "5%"], "X5R": ["10%", "20%"], "X7R": ["10%", "20%"]}

METRIC_CODES = {
    "0201": "0603",
    "0402": "1005",
    "0603": "1608",
    "0805": "2012",
    "1206": "3216",
    "1210": "3225",
    "1812": "4532",
    "2220": "5750"
}

# ------------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------------
def capacitance_code(pF):
    if pF < 1:
        cent = int(round(pF * 100))
        return f"0R{cent:02d}"
    elif pF < 10:
        int_part = int(pF)
        dec = int(round((pF - int_part) * 10))
        return f"{int_part}R{dec}"
    else:
        exp = int(math.floor(math.log10(pF)))
        divisor = 10 ** (exp - 1)
        digits = int(round(pF / divisor))
        return f"{digits:02d}{exp-1}"

def format_capacitance(value_pF):
    if value_pF < 1000:
        if value_pF == int(value_pF):
            return f"{int(value_pF)}p"
        else:
            int_part = int(value_pF)
            dec = int(round((value_pF - int_part) * 10))
            return f"{int_part}p{dec}"
    elif value_pF < 1e6:
        n_val = value_pF / 1000.0
        if n_val == int(n_val):
            return f"{int(n_val)}n"
        else:
            int_part = int(n_val)
            dec = int(round((n_val - int_part) * 10))
            return f"{int_part}n{dec}"
    else:
        u_val = value_pF / 1e6
        if u_val == int(u_val):
            return f"{int(u_val)}u"
        else:
            int_part = int(u_val)
            dec = int(round((u_val - int_part) * 10))
            return f"{int_part}u{dec}"

def generate_yageo_pn(size, dielectric, cap_pF, voltage, tolerance):
    tol_code = TOLERANCE_CODES[dielectric][tolerance]
    die_code = DIELECTRIC_CODES[dielectric]
    v_code = VOLTAGE_CODES.get(voltage, '9')
    cap_code = capacitance_code(cap_pF)
    return f"CC{size}{tol_code}R{die_code}{v_code}BB{cap_code}"

# ------------------------------------------------------------
# Função principal (com a NOVA REGRA para capacitores ≥ 1µF)
# ------------------------------------------------------------
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sizes = [ "0402", "0603", "0805", "1206", "1210", "1812", "2220"]
    dielectrics = ["C0G", "X5R", "X7R"]

    mypn_counter = 1
    base_counter_per_package = 0

    for size in sizes:
        all_combos = []
        for dielectric in dielectrics:
            key = (size, dielectric)
            if key not in LIMITS or not LIMITS[key]:
                continue
            limits = LIMITS[key]
            voltages = sorted(limits.keys())
            values_pF = C0G_VALUES_PF if dielectric == "C0G" else X5R_X7R_VALUES_PF

            # Agrupa as tensões disponíveis por valor de capacitância
            groups = defaultdict(list)
            for cap_pF in values_pF:
                for voltage in voltages:
                    if cap_pF <= limits[voltage]:
                        groups[(cap_pF, dielectric)].append(voltage)

            # Aplica a regra de filtragem: para capacitores >= 1µF (1.000.000 pF), mantém TODAS as tensões
            for (cap_pF, die), vlist in groups.items():
                if cap_pF >= 1_000_000:  # 1µF ou mais
                    # Mantém todas as tensões disponíveis
                    for v in vlist:
                        all_combos.append((dielectric, cap_pF, v))
                else:
                    # Para capacitores menores, aplica a regra anterior: 50V, 100V e a maior tensão
                    avail = set(vlist)
                    keep = set()
                    for v in [50, 100]:
                        if v in avail:
                            keep.add(v)
                    keep.add(max(avail))
                    for v in keep:
                        all_combos.append((dielectric, cap_pF, v))

        if not all_combos:
            continue

        all_combos.sort(key=lambda x: (x[0], x[1], x[2]))

        columns = [
            "MyPN", "Name", "Description", "Value", "Info1", "Info2",
            "Symbol", "Footprint", "Footprint_Filter", "Datasheet",
            "Manufacturer", "Manufacturer_PN",
            "Category", "Subcategory", "Package", "Mount",
            "Temperature_Range", "REACH_Compliant", "RoHS_Compliant",
            "Unit", "Tolerance", "Voltage_Rating", "Temperature_Coefficient",
            "Capacitance", "Dielectric_Type",
            "Created_At", "Created_By"
        ]

        values_lines = []
        for dielectric, cap_pF, voltage in all_combos:
            cap_str = format_capacitance(cap_pF)
            tolerance = TOLERANCES[dielectric][0]  # usa a primeira tolerância
            name = f"CAP_{size}_{cap_str}F_{tolerance}_{dielectric}_{voltage}V"
            description = f"Capacitor Ceramic SMD {size} {cap_str}F {tolerance} {voltage}V {dielectric}"
            value = cap_str
            info2 = f"{tolerance}{dielectric}"
            info1 = f"{voltage}V"
            mypn = f"EL-CAP-{mypn_counter:06d}"
            mypn_counter +=1
            mfg_pn = generate_yageo_pn(size, dielectric, cap_pF, voltage, tolerance)

            metric = METRIC_CODES[size]
            footprint = f"MyLib_Capacitor_SMD:C_{size}_{metric}Metric"
            footprint_filter = f"C_{size}*"

            # Seleciona o link do datasheet correto
            datasheet_url = DATASHEET_URLS.get(dielectric, "https://www.yageo.com")

            if dielectric == "C0G":
                temp_range = "-55°C ~ 125°C"
                temp_coeff = "±30ppm/°C"
            elif dielectric == "X7R":
                temp_range = "-55°C ~ 125°C"
                temp_coeff = "±15%"
            else:  # X5R
                temp_range = "-55°C ~ 85°C"
                temp_coeff = "±15%"

            values = [
                mypn, name, description, value, info1, info2,
                "MyLib_Capacitor:CAP_US", footprint, footprint_filter, datasheet_url,
                "Yageo", mfg_pn,
                "Capacitor", "Ceramic", size, "SMD",
                temp_range, "Yes", "Yes",
                "Farad", tolerance, f"{voltage}V", temp_coeff,
                cap_str, dielectric,
                "datetime('now')", "Rogerio Fontanario"
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

        output_file = os.path.join(script_dir, f"insert_capacitor_{size}.sql")
        header = f"INSERT INTO Capacitor_{size} ({', '.join(columns)}) VALUES\n"
        body = ",\n".join(values_lines) + ";"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"-- Script de inserção para Capacitor_{size}\n")
            f.write(f"-- Baseado nos datasheets YAGEO (links atualizados)\n")
            f.write(f"-- Para capacitores >= 1µF, TODAS as tensões foram mantidas.\n\n")
            f.write(header)
            f.write(body)
            f.write("\n")
        print(f"Arquivo gerado: {output_file} com {len(values_lines)} inserts")

        base_counter_per_package += 100000
        mypn_counter = base_counter_per_package +1

        print(f"Arquivo {size} gerado com {len(values_lines)} inserts. Novo base_counter = {base_counter_per_package + 100000}")

if __name__ == "__main__":
    main()