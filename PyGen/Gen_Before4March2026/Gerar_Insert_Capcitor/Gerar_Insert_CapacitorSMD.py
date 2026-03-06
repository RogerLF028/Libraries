import os
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "insert_capacitor_nichicon_uwt_smd.sql")

# Lista das colunas que serão preenchidas (na ordem desejada)
COLUNAS = [
    'MyPN', 'Name', 'Description', 'Value', 'Info1', 'Info2',
    'Symbol', 'Footprint', 'Manufacturer', 'Manufacturer_PN', 'Family_Series',
    'Category', 'Subcategory', 'Mount', 'Dimensions', 'Temperature_Range',
    'RoHS_Compliant', 'Active', 'Version', 'Created_At', 'Created_By',
    'Exclude_from_BOM', 'Exclude_from_Board',
    'Capacitance', 'Voltage_Rating', 'Ripple_Current', 'Leakage_Current',
    'Tolerance', 'Unit'
]

# ==================== FUNÇÕES AUXILIARES ====================
def sql_str(val):
    if val is None:
        return 'NULL'
    return "'" + str(val).replace("'", "''") + "'"

def format_capacitance(c):
    if c == int(c):
        return f"{int(c)}u"
    else:
        return f"{c}u"

def format_voltage(v):
    if v == int(v):
        return f"{int(v)}V"
    else:
        return f"{v}V"
    
def format_voltage_display(v):
    """Formata tensão para exibição: 6.3V → '6V3', 10V → '10V', etc."""
    if v == int(v):
        return f"{int(v)}V"
    else:
        # Converte para string e troca o ponto por 'V'
        return str(v).replace('.', 'V')

def get_footprint_smd(case_size):
    """Mapeia case size para footprint SMD conforme lista fornecida."""
    # Casos especiais: alguns sizes podem não ter correspondência exata, usar aproximação.
    # Baseado na lista de footprints, criamos um mapeamento.
    mapping = {
        "4x5.4": "MyLib_Capacitor_SMD:CP_Elec_4x5.4",
        "5x5.4": "MyLib_Capacitor_SMD:CP_Elec_5x5.4",
        "6.3x5.4": "MyLib_Capacitor_SMD:CP_Elec_6.3x5.4",
        "6.3x5.8": "MyLib_Capacitor_SMD:CP_Elec_6.3x5.8",
        "6.3x7.7": "MyLib_Capacitor_SMD:CP_Elec_6.3x7.7",
        "8x5.4": "MyLib_Capacitor_SMD:CP_Elec_8x5.4",
        "8x10": "MyLib_Capacitor_SMD:CP_Elec_8x10",
        "10x10": "MyLib_Capacitor_SMD:CP_Elec_10x10",
    }
    return mapping.get(case_size, f"MyLib_Capacitor_SMD:CP_Elec_{case_size}")

# ==================== DADOS DA SÉRIE UWT (SMD) ====================
# Cada tupla: (part_number, tensão_V, capacit_uF, case_size, tan_delta, leakage_uA, ripple_mA)
uwt_data = [
    # Página 2 - 4V
    ("UWT0G220MCL1GB", 4, 22, "4x5.4", 0.40, 3, 22),
    ("UWT0G330MCL1GB", 4, 33, "5x5.4", 0.40, 3, 30),
    ("UWT0G470MCL1GB", 4, 47, "5x5.4", 0.40, 3, 36),
    ("UWT0G101MCL1GB", 4, 100, "6.3x5.4", 0.40, 4, 60),
    ("UWT0G151MCL1GS", 4, 150, "6.3x5.8", 0.40, 6, 86),
    ("UWT0G221MCL1GB", 4, 220, "8x5.4", 0.40, 8.8, 102),
    ("UWT0G221MCL6GS", 4, 220, "6.3x5.8", 0.40, 8.8, 91),
    ("UWT0G331MCL1GS", 4, 330, "6.3x7.7", 0.40, 13.2, 105),
    ("UWT0G471MNL1GS", 4, 470, "8x10", 0.40, 18.8, 210),
    ("UWT0G681MNL1GS", 4, 680, "8x10", 0.40, 27.2, 210),
    ("UWT0G102MNL1GS", 4, 1000, "8x10", 0.40, 40, 230),
    ("UWT0G152MNL1GS", 4, 1500, "10x10", 0.40, 60, 310),

    # Página 2 - 6.3V
    ("UWT0J220MCL1GB", 6.3, 22, "4x5.4", 0.30, 3, 22),
    ("UWT0J330MCL1GB", 6.3, 33, "5x5.4", 0.30, 3, 30),
    ("UWT0J470MCL1GB", 6.3, 47, "5x5.4", 0.30, 3, 36),
    ("UWT0J101MCL1GB", 6.3, 100, "6.3x5.4", 0.30, 6.3, 60),
    ("UWT0J151MCL1GS", 6.3, 150, "6.3x5.8", 0.30, 9.4, 86),
    ("UWT0J221MCL1GB", 6.3, 220, "8x5.4", 0.30, 13.8, 102),
    ("UWT0J221MCL6GS", 6.3, 220, "6.3x5.8", 0.30, 13.8, 91),
    ("UWT0J331MCL1GS", 6.3, 330, "6.3x7.7", 0.30, 20.7, 105),
    ("UWT0J471MNL1GS", 6.3, 470, "8x10", 0.30, 29.6, 210),
    ("UWT0J681MNL1GS", 6.3, 680, "8x10", 0.30, 42.8, 210),
    ("UWT0J102MNL1GS", 6.3, 1000, "8x10", 0.30, 63, 230),
    ("UWT0J152MNL1GS", 6.3, 1500, "10x10", 0.30, 94.5, 310),

    # Página 2 - 10V
    ("UWT1A220MCL1GB", 10, 22, "5x5.4", 0.24, 3, 27),
    ("UWT1A330MCL1GB", 10, 33, "5x5.4", 0.24, 3.3, 35),
    ("UWT1A470MCL1GB", 10, 47, "6.3x5.4", 0.24, 4.7, 46),
    ("UWT1A101MCL1GB", 10, 100, "6.3x5.4", 0.24, 10, 60),
    ("UWT1A151MCL1GS", 10, 150, "6.3x5.8", 0.24, 15, 86),
    ("UWT1A221MCL1GS", 10, 220, "6.3x7.7", 0.24, 22, 105),
    ("UWT1A331MNL1GS", 10, 330, "8x10", 0.24, 33, 195),
    ("UWT1A471MNL1GS", 10, 470, "8x10", 0.24, 47, 210),
    ("UWT1A681MNL1GS", 10, 680, "10x10", 0.24, 68, 310),
    ("UWT1A102MNL1GS", 10, 1000, "10x10", 0.24, 100, 310),

    # Página 2 - 16V
    ("UWT1C100MCL1GB", 16, 10, "4x5.4", 0.20, 3, 18),
    ("UWT1C220MCL1GB", 16, 22, "5x5.4", 0.20, 3.5, 30),
    ("UWT1C330MCL1GB", 16, 33, "6.3x5.4", 0.20, 5.2, 40),
    ("UWT1C470MCL1GB", 16, 47, "6.3x5.4", 0.20, 7.5, 50),
    ("UWT1C101MCL1GB", 16, 100, "6.3x5.4", 0.20, 16, 60),
    ("UWT1C151MCL1GS", 16, 150, "6.3x7.7", 0.20, 24, 95),
    ("UWT1C221MCL1GS", 16, 220, "6.3x7.7", 0.20, 35.2, 105),
    ("UWT1C331MNL1GS", 16, 330, "8x10", 0.20, 52.8, 195),
    ("UWT1C471MNL1GS", 16, 470, "8x10", 0.20, 75.2, 230),
    ("UWT1C681MNL1GS", 16, 680, "10x10", 0.20, 108.8, 310),

    # Página 3 - 25V
    ("UWT1E4R7MCL1GB", 25, 4.7, "4x5.4", 0.16, 3, 13),
    ("UWT1E100MCL1GB", 25, 10, "5x5.4", 0.16, 3, 23),
    ("UWT1E220MCL1GB", 25, 22, "6.3x5.4", 0.16, 5.5, 38),
    ("UWT1E330MCL1GB", 25, 33, "6.3x5.4", 0.16, 8.2, 48),
    ("UWT1E470MCL1GB", 25, 47, "8x5.4", 0.16, 11.7, 66),
    ("UWT1E470MCL6GS", 25, 47, "6.3x5.8", 0.16, 11.7, 59),
    ("UWT1E101MCL1GS", 25, 100, "6.3x7.7", 0.16, 25, 91),
    ("UWT1E151MNL1GS", 25, 150, "8x10", 0.16, 37.5, 140),
    ("UWT1E221MNL1GS", 25, 220, "8x10", 0.16, 55, 155),
    ("UWT1E331MNL1GS", 25, 330, "8x10", 0.16, 82.5, 190),
    ("UWT1E471MNL1GS", 25, 470, "10x10", 0.16, 117.5, 300),

    # Página 3 - 35V
    ("UWT1V4R7MCL1GB", 35, 4.7, "4x5.4", 0.14, 3, 15),
    ("UWT1V100MCL1GB", 35, 10, "5x5.4", 0.14, 3.5, 25),
    ("UWT1V220MCL1GB", 35, 22, "6.3x5.4", 0.14, 7.7, 42),
    ("UWT1V330MCL1GB", 35, 33, "8x5.4", 0.14, 11.5, 59),
    ("UWT1V330MCL6GS", 35, 33, "6.3x5.8", 0.14, 11.5, 52),
    ("UWT1V470MCL1GS", 35, 47, "6.3x5.8", 0.14, 16.4, 63),
    ("UWT1V101MCL1GS", 35, 100, "6.3x7.7", 0.14, 35, 84),
    ("UWT1V151MNL1GS", 35, 150, "8x10", 0.14, 52.5, 155),
    ("UWT1V221MNL1GS", 35, 220, "8x10", 0.14, 77, 190),
    ("UWT1V331MNL1GS", 35, 330, "10x10", 0.14, 115.5, 300),

    # Página 3 - 50V
    ("UWT1H010MCL1GB", 50, 1, "4x5.4", 0.14, 3, 6.2),
    ("UWT1H2R2MCL1GB", 50, 2.2, "4x5.4", 0.14, 3, 11),
    ("UWT1H3R3MCL1GB", 50, 3.3, "4x5.4", 0.14, 3, 14),
    ("UWT1H4R7MCL1GB", 50, 4.7, "5x5.4", 0.14, 3, 19),
    ("UWT1H100MCL1GB", 50, 10, "6.3x5.4", 0.14, 5, 30),
    ("UWT1H220MCL1GB", 50, 22, "8x5.4", 0.14, 11, 51),
    ("UWT1H220MCL6GS", 50, 22, "6.3x5.8", 0.14, 11, 45),
    ("UWT1H330MCL1GS", 50, 33, "6.3x7.7", 0.14, 16.5, 60),
    ("UWT1H470MCL1GS", 50, 47, "6.3x7.7", 0.14, 23.5, 63),
    ("UWT1H101MNL1GS", 50, 100, "8x10", 0.14, 50, 140),
    ("UWT1H151MNL1GS", 50, 150, "10x10", 0.14, 75, 180),
    ("UWT1H221MNL1GS", 50, 220, "10x10", 0.14, 110, 220),
]

# ==================== GERAÇÃO DO INSERT ====================
contador = 700000
created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
created_by = "Rogerio Fontanario"
symbol = "MyLib_Capacitor:CAP_Polarized_US"
manufacturer = "Nichicon"
category = "Capacitor"
subcategory = "Aluminum Electrolytic"
rohs = "Yes"
active = 1
version = 1
exclude_bom = 0
exclude_board = 0
tolerance = "±20%"
unit = "µF"

linhas_sql = []

for part, v, c, case, tan, leak, ripple in uwt_data:
    mypn = f"EL-CAP-{contador:06d}"
    contador += 1
    footprint = get_footprint_smd(case)
    cap_str = format_capacitance(c)
    #volt_str = format_voltage(v)
    volt_str = format_voltage_display(v)   # Ex: 6.3V → "6V3"
    name = f"CAP_POL_{cap_str}F_{volt_str}_SMD"
    description = f"Aluminum Electrolytic Capacitor {cap_str} {volt_str}"
    value = cap_str
    info1 = volt_str
    info2 = None  # em branco
    temp_range = "-55°C to +105°C"
    mount = "SMD"
    dimensions = case + "mm"

    valores = {
        'MyPN': mypn,
        'Name': name,
        'Description': description,
        'Value': value,
        'Info1': info1,
        'Info2': info2,
        'Symbol': symbol,
        'Footprint': footprint,
        'Manufacturer': manufacturer,
        'Manufacturer_PN': part,
        'Family_Series': "UWT",
        'Category': category,
        'Subcategory': subcategory,
        'Mount': mount,
        'Dimensions': dimensions,
        'Temperature_Range': temp_range,
        'RoHS_Compliant': rohs,
        'Active': active,
        'Version': version,
        'Created_At': created_at,
        'Created_By': created_by,
        'Exclude_from_BOM': exclude_bom,
        'Exclude_from_Board': exclude_board,
        'Capacitance': c,
        'Voltage_Rating': v,
        'Ripple_Current': ripple,
        'Leakage_Current': leak,
        'Tolerance': tolerance,
        'Unit': unit,
    }
    linha = [sql_str(valores.get(col)) for col in COLUNAS]
    linhas_sql.append("(" + ", ".join(linha) + ")")

# Escrever arquivo
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(f"-- Inserções para a tabela Capacitor_General (Nichicon UWT SMD)\n")
    f.write(f"-- Gerado em {datetime.now()}\n\n")
    f.write(f"INSERT INTO Capacitor_General (\n")
    f.write("    " + ",\n    ".join(COLUNAS) + "\n")
    f.write(") VALUES\n")
    f.write(",\n".join(linhas_sql))
    f.write(";\n\n-- Fim dos inserts\n")

print(f"Arquivo SQL gerado: {OUTPUT_FILE}")
print(f"Total de inserts UWT: {len(linhas_sql)}")
print(f"Último MyPN: EL-CAP-{contador-1:06d}")