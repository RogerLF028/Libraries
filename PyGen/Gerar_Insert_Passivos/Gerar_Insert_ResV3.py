import os
from datetime import datetime

# =============================================================================
# CONSTANTES GLOBAIS
# =============================================================================
# Séries de valores normalizados (1 a 10) para a série AA
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

# Décadas para gerar valores (de 1 a 10M) para a série AA
DECADES_AA = [10**i for i in range(0, 8)]  # 1, 10, 100, ... 10M

# =============================================================================
# FUNÇÕES DE FORMATAÇÃO DE RESISTÊNCIA
# =============================================================================
def format_aa_resistance(value_ohms):
    """
    Formata valor em ohms para o padrão Yageo AA (automotive).
    Exemplos:
        0.5Ω  -> 0R5
        100Ω  -> 100R
        1.2kΩ -> 1K2
        10kΩ  -> 10K
        2.2MΩ -> 2M2
        1MΩ   -> 1M
    """
    v = round(value_ohms, 12)
    if v < 1:
        s = f"{v:.12f}".rstrip('0').rstrip('.')
        return s.replace('.', 'R')
    elif v < 1000:
        if abs(v - round(v)) < 1e-9:
            return f"{int(round(v))}R"
        else:
            s = f"{v:.12f}".rstrip('0').rstrip('.')
            return s.replace('.', 'R')
    elif v < 1e6:
        k = v / 1000.0
        if abs(k - round(k)) < 1e-9:
            return f"{int(round(k))}K"
        else:
            s = f"{k:.12f}".rstrip('0').rstrip('.')
            return s.replace('.', 'K')
    else:
        m = v / 1e6
        if abs(m - round(m)) < 1e-9:
            return f"{int(round(m))}M"
        else:
            s = f"{m:.12f}".rstrip('0').rstrip('.')
            return s.replace('.', 'M')

def format_pa_resistance(value_ohms):
    """
    Formata valor em ohms para o padrão Yageo PA (current sensor).
    Utiliza 'R' como ponto decimal, sem abreviações K/M.
    Exemplos:
        0.0005Ω -> 0R0005
        0.003Ω  -> 0R003
        0.1Ω    -> 0R1
    """
    s = f"{value_ohms:.12f}".rstrip('0').rstrip('.')
    return s.replace('.', 'R')

# =============================================================================
# CONFIGURAÇÕES POR SÉRIE (baseadas nos datasheets)
# =============================================================================
# Série AA (Automotive Grade) - datasheet PYU-AA_51_ROHS_L.pdf
AA_SPECS = {
    "0201": {
        "power": "1/20W",
        "r_min": 1.0,
        "r_max": 10_000_000,       # 10MΩ
        "footprint": "MyLib_Resistor_SMD:R_0201_0603Metric",
        "footprint_filter": "R_0201*",
        "packaging": "R",           # paper tape
        "temp_range": "-55°C ~ 155°C",
    },
    "0402": {
        "power": "1/16W",
        "r_min": 1.0,
        "r_max": 10_000_000,
        "footprint": "MyLib_Resistor_SMD:R_0402_1005Metric",
        "footprint_filter": "R_0402*",
        "packaging": "R",
        "temp_range": "-55°C ~ 155°C",
    },
    "0603": {
        "power": "1/10W",
        "r_min": 1.0,
        "r_max": 10_000_000,
        "footprint": "MyLib_Resistor_SMD:R_0603_1608Metric",
        "footprint_filter": "R_0603*",
        "packaging": "R",
        "temp_range": "-55°C ~ 155°C",
    },
    "0805": {
        "power": "1/8W",
        "r_min": 1.0,
        "r_max": 10_000_000,
        "footprint": "MyLib_Resistor_SMD:R_0805_2012Metric",
        "footprint_filter": "R_0805*",
        "packaging": "R",
        "temp_range": "-55°C ~ 155°C",
    },
    "1206": {
        "power": "1/4W",
        "r_min": 1.0,
        "r_max": 10_000_000,
        "footprint": "MyLib_Resistor_SMD:R_1206_3216Metric",
        "footprint_filter": "R_1206*",
        "packaging": "R",
        "temp_range": "-55°C ~ 155°C",
    },
    "1210": {
        "power": "1/2W",
        "r_min": 1.0,
        "r_max": 10_000_000,
        "footprint": "MyLib_Resistor_SMD:R_1210_3225Metric",
        "footprint_filter": "R_1210*",
        "packaging": "R",
        "temp_range": "-55°C ~ 155°C",
    },
    "1218": {
        "power": "1W",
        "r_min": 1.0,
        "r_max": 1_000_000,        # 1MΩ (conforme datasheet)
        "footprint": "MyLib_Resistor_SMD:R_1218_3246Metric",  # Ajuste conforme sua biblioteca
        "footprint_filter": "R_1218*",
        "packaging": "K",           # embossed tape
        "temp_range": "-55°C ~ 155°C",
    },
    "2010": {
        "power": "3/4W",
        "r_min": 1.0,
        "r_max": 10_000_000,
        "footprint": "MyLib_Resistor_SMD:R_2010_5025Metric",
        "footprint_filter": "R_2010*",
        "packaging": "K",
        "temp_range": "-55°C ~ 155°C",
    },
    "2512": {
        "power": "1W",
        "r_min": 1.0,
        "r_max": 10_000_000,
        "footprint": "MyLib_Resistor_SMD:R_2512_6332Metric",
        "footprint_filter": "R_2512*",
        "packaging": "K",
        "temp_range": "-55°C ~ 155°C",
    }
}

# Série PA (Current Sensor) - datasheet PYU-PA_E_51_ROHS.pdf
PA_SPECS = {
    "2512": {
        "powers": ["1W", "2W", "3W"],
        "tcrs": [50, 75, 100],          # ppm/°C
        "r_min": 0.0005,                 # 0.5mΩ
        "r_max": 0.1,                    # 100mΩ
        "footprint": "MyLib_Resistor_SMD:R_2512_6332Metric",
        "footprint_filter": "R_2512*",
        "packaging": "K",                 # embossed tape
        "temp_range": "-55°C ~ 170°C",
    }
}

# =============================================================================
# FUNÇÕES AUXILIARES PARA GERAÇÃO DE VALORES
# =============================================================================
def generate_aa_resistances(spec):
    """
    Gera dicionário {str_resistencia: valor_ohms} para a série AA,
    combinando E24 e E96 e filtrando pelo range do tamanho.
    """
    unique = {}
    for mult in DECADES_AA:
        for val in E24_VALUES + E96_VALUES:
            r = val * mult
            if spec["r_min"] <= r <= spec["r_max"]:
                r_rounded = round(r, 12)
                unique[r_rounded] = r_rounded
    sorted_items = sorted(unique.items())
    return {format_aa_resistance(v): v for _, v in sorted_items}

def generate_pa_resistances(spec):
    """
    Gera dicionário {str_resistencia: valor_ohms} para a série PA,
    usando a lista real de valores disponíveis (não E24/E96).
    """
    # Lista de valores em ohms (0.0005 = 0.5mΩ) baseada em produtos comerciais
    pa_values = [
        0.0005, 0.00075, 0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009,
        0.01, 0.012, 0.015, 0.018, 0.02, 0.022, 0.027, 0.03, 0.033, 0.039, 0.04,
        0.047, 0.05, 0.056, 0.068, 0.075, 0.082, 0.091, 0.1
    ]
    resistances = {}
    for r in pa_values:
        if spec["r_min"] <= r <= spec["r_max"]:
            resistances[format_pa_resistance(r)] = r
    return resistances

# =============================================================================
# FUNÇÃO PARA DETERMINAR TCR DA SÉRIE AA (conforme tabela do datasheet)
# =============================================================================
def get_aa_tcr(size, res_ohms):
    """
    Retorna a string do TCR baseado no tamanho e no valor da resistência.
    Conforme página 5 do datasheet AA.
    """
    if size in ["0201", "0402"]:
        if res_ohms <= 10:
            return "-100/+400ppm/°C"
        else:
            return "±300ppm/°C"
    else:  # 0603, 0805, 1206, 1210, 1218, 2010, 2512
        if res_ohms <= 10:
            return "±200ppm/°C"
        else:
            return "±150ppm/°C"

# =============================================================================
# GERAÇÃO DOS ARQUIVOS SQL
# =============================================================================
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mypn_counter = 1
    base_counter = 0  # Para separar os blocos de cada série/tamanho

    # -------------------------------------------------------------------------
    # Série AA
    # -------------------------------------------------------------------------
    for size, spec in AA_SPECS.items():
        mypn_counter = base_counter + 1
        resistances = generate_aa_resistances(spec)

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
        tolerance = "1%"
        manufacturer = "Yageo"
        category = "Resistor"
        subcategory = "Thick Film"          # conforme datasheet AA
        mount = "SMD"
        unit = "Ohm"
        tech_material = "Thick Film"
        reach = "Yes"
        rohs = "Yes"
        created_by = "Rogerio Fontanario"
        datasheet_url = "https://yageogroup.com/content/datasheet/asset/file/PYU-AA_51_ROHS_L.pdf"
        symbol = "MyLib_Resistor:RES_US"

        for res_str, res_ohms in resistances.items():
            tcr = get_aa_tcr(size, res_ohms)
            packaging = spec["packaging"]
            mfg_pn = f"AA{size}F{packaging}-07{res_str}L"  # 07 = 7" reel

            name = f"RES_{size}_{res_str}_{tolerance}"
            description = f"Resistor SMD {size} {res_str} {tolerance} {spec['power']}"
            value = res_str
            info1 = tolerance
            info2 = spec["power"]
            mypn = f"EL-RES-{mypn_counter:06d}"
            mypn_counter += 1

            values = [
                mypn, name, description, value, info1, info2,
                symbol,
                spec["footprint"],
                spec["footprint_filter"],
                datasheet_url,
                manufacturer,
                mfg_pn,
                category,
                subcategory,
                size,
                mount,
                spec["temp_range"],
                reach,
                rohs,
                unit,
                tolerance,
                spec["power"],
                tcr,
                res_str,
                tech_material,
                "datetime('now')",
                created_by
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
            output_file = os.path.join(script_dir, f"insert_resistor_AA_{size}.sql")
            header = f"INSERT INTO Resistor_{size} ({', '.join(columns)}) VALUES\n"
            body = ",\n".join(values_lines) + ";"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"-- Script de inserção para Resistor AA série - tamanho {size}\n")
                f.write(f"-- Baseado no datasheet Yageo AA (Automotive Grade)\n")
                f.write(f"-- Tolerância: 1% (séries E24 e E96)\n\n")
                f.write(header)
                f.write(body)
                f.write("\n")
            print(f"Arquivo gerado: {output_file} com {len(values_lines)} inserts")

        base_counter += 100000

    # -------------------------------------------------------------------------
    # Série PA (Current Sensor)
    # -------------------------------------------------------------------------
    size = "2512"
    spec = PA_SPECS[size]
    mypn_counter = base_counter + 1
    resistances = generate_pa_resistances(spec)

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
    tolerance = "1%"
    manufacturer = "Yageo"
    category = "Resistor"
    subcategory = "Current Sensor"        # conforme datasheet PA
    mount = "SMD"
    unit = "Ohm"
    tech_material = "Metal Strip"          # construção típica de current sensor
    reach = "Yes"
    rohs = "Yes"
    created_by = "Rogerio Fontanario"
    datasheet_url = "https://yageogroup.com/content/datasheet/asset/file/PYU-PA_E_51_ROHS.pdf"
    symbol = "MyLib_Resistor:RES_US"

    # Mapeamentos conforme datasheet PA
    tcr_code = {50: "E", 75: "M", 100: "F"}
    power_taping = {"1W": "07", "2W": "7W", "3W": "7T"}  # 07, 7W, 7T

    for res_str, res_ohms in resistances.items():
        for power in spec["powers"]:
            for tcr in spec["tcrs"]:
                mfg_pn = f"PA{size}F{spec['packaging']}{tcr_code[tcr]}{power_taping[power]}{res_str}E"
                name = f"RES_PA{size}_{res_str}_{tolerance}_{power}_{tcr}ppm"
                description = f"Current Sensor Resistor {size} {res_str} {tolerance} {power} {tcr}ppm"
                value = res_str
                info1 = tolerance
                info2 = power
                mypn = f"EL-RES-{mypn_counter:06d}"
                mypn_counter += 1

                values = [
                    mypn, name, description, value, info1, info2,
                    symbol,
                    spec["footprint"],
                    spec["footprint_filter"],
                    datasheet_url,
                    manufacturer,
                    mfg_pn,
                    category,
                    subcategory,
                    size,
                    mount,
                    spec["temp_range"],
                    reach,
                    rohs,
                    unit,
                    tolerance,
                    power,
                    f"±{tcr}ppm/°C",
                    res_str,
                    tech_material,
                    "datetime('now')",
                    created_by
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
        output_file = os.path.join(script_dir, f"insert_resistor_PA_{size}.sql")
        header = f"INSERT INTO Resistor_{size} ({', '.join(columns)}) VALUES\n"
        body = ",\n".join(values_lines) + ";"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"-- Script de inserção para Resistor PA série - tamanho {size}\n")
            f.write(f"-- Baseado no datasheet Yageo PA (Current Sensor)\n")
            f.write(f"-- Tolerância: 1% (valores reais da série)\n\n")
            f.write(header)
            f.write(body)
            f.write("\n")
        print(f"Arquivo gerado: {output_file} com {len(values_lines)} inserts")

    print("Geração concluída.")

if __name__ == "__main__":
    main()