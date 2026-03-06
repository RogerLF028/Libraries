import os

# ------------------------------------------------------------
# Constantes comuns
# ------------------------------------------------------------
# Série E24 (valores normalizados de 1.0 a 9.1)
E24_VALUES = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7,
    3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
]

# Série E96 (valores normalizados de 1.0 a 9.76)
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

# Valores abaixo de 1Ω (comuns em resistores)
LOW_VALUES = [0.1, 0.15, 0.22, 0.33, 0.47, 0.68, 0.82]

# Décadas (10^0 a 10^6) → 1Ω a 10MΩ
DECADES = [10**i for i in range(7)]  # 1, 10, 100, 1000, 10000, 100000, 1000000

# Tolerância fixa (1%)
TOLERANCE = "1%"

# Fabricante fixo
MANUFACTURER = "Yageo"

# Symbol
SYMBOL = "myLib_Resistor:RES_US"

# Categoria e subcategoria
CATEGORY = "Resistor"
SUBCATEGORY = "Thick Film"
MOUNT = "SMD"
UNIT = "Ohm"
TECH_MATERIAL = "Thick Film"
TEMP_COEFF = "±100ppm/°C"
TEMP_RANGE = "-55°C ~ 155°C"
REACH = "Yes"
ROHS = "Yes"

# Created_By fixo
CREATED_BY = "Rogerio Fontanario"

# Lista de pacotes com seus parâmetros específicos e offset inicial para MyPN
PACKAGES = [
    {
        "name": "0402",
        "table": "Resistor_0402",
        "power": "1/16W",
        "footprint": "myLib_Resistor_SMD:R_0402_1005Metric",
        "filter": "R_0402*",
        "datasheet": "https://www.yageo.com/upload/media/product/products/datasheet/RC0402.pdf",
        "offset": 0  # MyPN começa em 000001
    },
    {
        "name": "0603",
        "table": "Resistor_0603",
        "power": "1/10W",
        "footprint": "myLib_Resistor_SMD:R_0603_1608Metric",
        "filter": "R_0603*",
        "datasheet": "https://www.yageo.com/upload/media/product/products/datasheet/RC0603.pdf",
        "offset": 100000  # MyPN começa em 100001
    },
    {
        "name": "0805",
        "table": "Resistor_0805",
        "power": "1/8W",
        "footprint": "myLib_Resistor_SMD:R_0805_2012Metric",
        "filter": "R_0805*",
        "datasheet": "https://www.yageo.com/upload/media/product/products/datasheet/RC0805.pdf",
        "offset": 200000
    },
    {
        "name": "1206",
        "table": "Resistor_1206",
        "power": "1/4W",
        "footprint": "myLib_Resistor_SMD:R_1206_3216Metric",
        "filter": "R_1206*",
        "datasheet": "https://www.yageo.com/upload/media/product/products/datasheet/RC1206.pdf",
        "offset": 300000
    },
    {
        "name": "2010",
        "table": "Resistor_2010",
        "power": "3/4W",
        "footprint": "myLib_Resistor_SMD:R_2010_5025Metric",
        "filter": "R_2010*",
        "datasheet": "https://www.yageo.com/upload/media/product/products/datasheet/RC2010.pdf",
        "offset": 400000
    },
    {
        "name": "2512",
        "table": "Resistor_2512",
        "power": "1W",
        "footprint": "myLib_Resistor_SMD:R_2512_6332Metric",
        "filter": "R_2512*",
        "datasheet": "https://www.yageo.com/upload/media/product/products/datasheet/RC2512.pdf",
        "offset": 500000
    }
]

# ------------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------------
def format_resistance(value_ohms):
    """
    Converte valor em ohms para string no formato:
    - < 1Ω: 0R47, 0R68, etc.
    - 1Ω a 999Ω: 10R, 1R2, 100R
    - 1kΩ a 999kΩ: 1K, 1K2, 10K, 100K
    - ≥ 1MΩ: 1M, 1M2, 10M
    """
    if value_ohms < 1:
        cent = int(round(value_ohms * 100))
        return f"0R{cent:02d}"
    elif value_ohms < 1000:
        if value_ohms == int(value_ohms):
            return f"{int(value_ohms)}R"
        else:
            dec = int(round((value_ohms - int(value_ohms)) * 10))
            return f"{int(value_ohms)}R{dec}"
    elif value_ohms < 1e6:
        k_val = value_ohms / 1000.0
        if k_val == int(k_val):
            return f"{int(k_val)}K"
        else:
            dec = int(round((k_val - int(k_val)) * 10))
            return f"{int(k_val)}K{dec}"
    else:
        m_val = value_ohms / 1e6
        if m_val == int(m_val):
            return f"{int(m_val)}M"
        else:
            dec = int(round((m_val - int(m_val)) * 10))
            return f"{int(m_val)}M{dec}"

def generate_unique_resistance_values():
    """Gera uma lista única de valores de resistência (em ohms) combinando E24, E96 e baixos valores."""
    resistencias = set()
    # Adiciona E24
    for mult in DECADES:
        for val in E24_VALUES:
            resistencias.add(val * mult)
    # Adiciona E96
    for mult in DECADES:
        for val in E96_VALUES:
            resistencias.add(val * mult)
    # Adiciona baixos valores
    for val in LOW_VALUES:
        resistencias.add(val)
    # Ordenar para consistência
    return sorted(resistencias)

def generate_yageo_pn(res_ohms, package_name, tol):
    """Gera part number estilo Yageo: RC{package}FR-07xxxxL (simplificado)"""
    tol_code = "FR"  # 1%
    val_str = format_resistance(res_ohms)
    return f"RC{package_name}{tol_code}-07{val_str}L"

# ------------------------------------------------------------
# Geração principal
# ------------------------------------------------------------
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resistencias = generate_unique_resistance_values()
    print(f"Total de valores únicos por pacote: {len(resistencias)}")

    # Para cada pacote, gerar arquivo SQL
    for pkg in PACKAGES:
        output_file = os.path.join(script_dir, f"insert_resistor_{pkg['name']}.sql")
        
        # Lista de colunas relevantes
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
        # Contador interno para este pacote, começando em 1
        seq = 1
        for res_ohms in resistencias:
            res_str = format_resistance(res_ohms)
            # Nome e descrição com o pacote
            name = f"RES_{pkg['name']}_{res_str}_{TOLERANCE}"
            description = f"Resistor SMD {pkg['name']} {res_str} {TOLERANCE} {pkg['power']}"
            info1 = TOLERANCE
            info2 = pkg['power']
            # MyPN = offset + seq
            mypn_number = pkg['offset'] + seq
            mypn = f"EL-RES-{mypn_number:06d}"
            seq += 1

            mfg_pn = generate_yageo_pn(res_ohms, pkg['name'], TOLERANCE)

            values = [
                mypn,                           # MyPN
                name,                           # Name
                description,                    # Description
                res_str,                         # Value
                info1,                           # Info1
                info2,                           # Info2
                SYMBOL,                          # Symbol
                pkg['footprint'],                 # Footprint
                pkg['filter'],                    # Footprint_Filter
                pkg['datasheet'],                 # Datasheet
                MANUFACTURER,                     # Manufacturer
                mfg_pn,                           # Manufacturer_PN
                CATEGORY,                         # Category
                SUBCATEGORY,                      # Subcategory
                pkg['name'],                       # Package
                MOUNT,                            # Mount
                TEMP_RANGE,                       # Temperature_Range
                REACH,                            # REACH_Compliant
                ROHS,                             # RoHS_Compliant
                UNIT,                             # Unit
                TOLERANCE,                        # Tolerance
                pkg['power'],                      # Power_Rating
                TEMP_COEFF,                       # Temperature_Coefficient
                res_str,                          # Resistance
                TECH_MATERIAL,                    # Technology_Material
                "datetime('now')",                 # Created_At (função SQL)
                CREATED_BY                         # Created_By
            ]

            # Formatar valores
            formatted_values = []
            for v in values:
                if v is None:
                    formatted_values.append("NULL")
                elif isinstance(v, int):
                    formatted_values.append(str(v))
                elif v == "datetime('now')":
                    formatted_values.append(v)
                else:
                    v_escaped = str(v).replace("'", "''")
                    formatted_values.append(f"'{v_escaped}'")

            values_lines.append("(" + ", ".join(formatted_values) + ")")

        # Escrever arquivo
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"-- Script de inserção para {pkg['table']}\n")
            f.write(f"-- Baseado nas séries E24 e E96 + valores <1Ω, tolerância 1%, potência {pkg['power']}\n")
            f.write(f"-- Fabricante: Yageo (part numbers simulados)\n\n")
            f.write(f"INSERT INTO {pkg['table']} ({', '.join(columns)}) VALUES\n")
            f.write(",\n".join(values_lines))
            f.write(";\n")

        print(f"Arquivo gerado: {output_file} com {len(values_lines)} inserts")

if __name__ == "__main__":
    main()