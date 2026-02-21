import csv
import os
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "insert_inductor_dr_series.sql")

# Lista das colunas que serão preenchidas (na ordem desejada)
COLUNAS = [
    'MyPN', 'Name', 'Description', 'Value', 'Info1', 'Info2',
    'Symbol', 'Footprint', 'Manufacturer', 'Manufacturer_PN', 'Family_Series',
    'Category', 'Subcategory', 'Mount', 'Temperature_Range',
    'RoHS_Compliant', 'Active', 'Version', 'Created_At', 'Created_By',
    'Exclude_from_BOM', 'Exclude_from_Board'
]

# Dados extraídos do datasheet (part number, inductance µH, Irms A, DCR ohms)
# Organizados por série
dados = [
    # DR73
    ("DR73-R33-R", 0.33, 6.2, 0.0073),
    ("DR73-1R0-R", 1.0, 5.28, 0.0102),
    ("DR73-1R5-R", 1.5, 4.67, 0.0130),
    ("DR73-2R2-R", 2.2, 4.15, 0.0165),
    ("DR73-3R3-R", 3.3, 3.31, 0.0259),
    ("DR73-4R7-R", 4.7, 3.09, 0.0297),
    ("DR73-6R8-R", 6.8, 2.55, 0.0435),
    ("DR73-8R2-R", 8.2, 2.19, 0.0592),
    ("DR73-100-R", 10.0, 2.08, 0.0656),
    ("DR73-150-R", 15.0, 1.83, 0.0844),
    ("DR73-220-R", 22.0, 1.62, 0.107),
    ("DR73-330-R", 33.0, 1.31, 0.166),
    ("DR73-470-R", 47.0, 1.08, 0.241),
    ("DR73-680-R", 68.0, 0.89, 0.358),
    ("DR73-820-R", 82.0, 0.86, 0.384),
    ("DR73-101-R", 100.0, 0.73, 0.527),
    ("DR73-151-R", 150.0, 0.58, 0.851),
    ("DR73-221-R", 220.0, 0.52, 1.05),
    ("DR73-331-R", 330.0, 0.42, 1.59),
    ("DR73-471-R", 470.0, 0.35, 2.36),
    ("DR73-681-R", 680.0, 0.29, 3.47),
    ("DR73-821-R", 820.0, 0.27, 3.93),
    ("DR73-102-R", 1000.0, 0.26, 4.34),

    # DR74
    ("DR74-R33-R", 0.33, 6.26, 0.0074),
    ("DR74-1R0-R", 1.0, 5.39, 0.0099),
    ("DR74-1R5-R", 1.5, 4.94, 0.0118),
    ("DR74-2R2-R", 2.2, 4.76, 0.0126),
    ("DR74-3R3-R", 3.3, 3.94, 0.0183),
    ("DR74-4R7-R", 4.7, 3.34, 0.0254),
    ("DR74-6R8-R", 6.8, 2.60, 0.0418),
    ("DR74-8R2-R", 8.2, 2.53, 0.0441),
    ("DR74-100-R", 10.0, 2.41, 0.0489),
    ("DR74-150-R", 15.0, 2.11, 0.0637),
    ("DR74-220-R", 22.0, 1.75, 0.0925),
    ("DR74-330-R", 33.0, 1.41, 0.143),
    ("DR74-470-R", 47.0, 1.15, 0.216),
    ("DR74-680-R", 68.0, 1.03, 0.265),
    ("DR74-820-R", 82.0, 0.91, 0.345),
    ("DR74-101-R", 100.0, 0.86, 0.383),
    ("DR74-151-R", 150.0, 0.69, 0.591),
    ("DR74-221-R", 220.0, 0.56, 0.907),
    ("DR74-331-R", 330.0, 0.45, 1.41),
    ("DR74-471-R", 470.0, 0.40, 1.74),
    ("DR74-681-R", 680.0, 0.33, 2.58),
    ("DR74-821-R", 820.0, 0.31, 2.93),
    ("DR74-102-R", 1000.0, 0.27, 3.89),

    # DR125
    ("DR125-R47-R", 0.47, 17.6, 0.0018),
    ("DR125-1R0-R", 1.0, 15.0, 0.0024),
    ("DR125-1R5-R", 1.5, 13.8, 0.0029),
    ("DR125-2R2-R", 2.2, 10.9, 0.0045),
    ("DR125-3R3-R", 3.3, 9.26, 0.0063),
    ("DR125-4R7-R", 4.7, 7.18, 0.0105),
    ("DR125-6R8-R", 6.8, 6.64, 0.0123),
    ("DR125-8R2-R", 8.2, 5.54, 0.0176),
    ("DR125-100-R", 10.0, 5.35, 0.0189),
    ("DR125-150-R", 15.0, 4.27, 0.0298),
    ("DR125-180-R", 18.0, 3.81, 0.0377),
    ("DR125-220-R", 22.0, 3.70, 0.0396),
    ("DR125-330-R", 33.0, 3.28, 0.0505),
    ("DR125-470-R", 47.0, 2.71, 0.0740),
    ("DR125-560-R", 56.0, 2.31, 0.102),
    ("DR125-680-R", 68.0, 2.22, 0.101),
    ("DR125-820-R", 82.0, 2.05, 0.128),
    ("DR125-101-R", 100.0, 1.78, 0.170),
    ("DR125-151-R", 150.0, 1.48, 0.248),
    ("DR125-221-R", 220.0, 1.19, 0.384),
    ("DR125-331-R", 330.0, 1.06, 0.482),
    ("DR125-471-R", 470.0, 0.87, 0.718),
    ("DR125-681-R", 680.0, 0.70, 1.10),
    ("DR125-821-R", 820.0, 0.60, 1.49),
    ("DR125-102-R", 1000.0, 0.57, 1.69),
    ("DR125-472-R", 4700.0, 0.268, 7.53),
    ("DR125-124-R", 12000.0, 0.060, 150.0),

    # DR127
    ("DR127-R47-R", 0.47, 17.9, 0.00195),
    ("DR127-1R0-R", 1.0, 15.5, 0.00313),
    ("DR127-1R5-R", 1.5, 13.5, 0.0034),
    ("DR127-2R2-R", 2.2, 12.5, 0.0040),
    ("DR127-3R3-R", 3.3, 10.5, 0.0056),
    ("DR127-4R7-R", 4.7, 8.25, 0.00917),
    ("DR127-6R8-R", 6.8, 7.34, 0.0116),
    ("DR127-8R2-R", 8.2, 6.32, 0.0157),
    ("DR127-100-R", 10.0, 6.04, 0.0172),
    ("DR127-150-R", 15.0, 5.03, 0.0247),
    ("DR127-220-R", 22.0, 4.00, 0.0391),
    ("DR127-330-R", 33.0, 3.23, 0.0600),
    ("DR127-470-R", 47.0, 2.95, 0.0719),
    ("DR127-680-R", 68.0, 2.44, 0.105),
    ("DR127-820-R", 82.0, 2.09, 0.143),
    ("DR127-101-R", 100.0, 1.96, 0.163),
    ("DR127-151-R", 150.0, 1.59, 0.247),
    ("DR127-221-R", 220.0, 1.29, 0.376),
    ("DR127-331-R", 330.0, 1.04, 0.574),
    ("DR127-471-R", 470.0, 0.85, 0.861),
    ("DR127-681-R", 680.0, 0.76, 1.08),
    ("DR127-821-R", 820.0, 0.65, 1.47),
    ("DR127-102-R", 1000.0, 0.61, 1.66),
]

# ==================== FUNÇÕES AUXILIARES ====================
def sql_str(val):
    """Escapa aspas simples e retorna string formatada para SQL."""
    if val is None:
        return 'NULL'
    return "'" + str(val).replace("'", "''") + "'"

def format_inductance(l):
    """Formata indutância em µH como string com 'u' (ex: 0.33u, 10u, 1000u)."""
    if l == int(l):
        return f"{int(l)}u"
    else:
        return f"{l}u"

def format_current(i):
    """Formata corrente em A como string com 'A' (ex: 6.2A)."""
    if i == int(i):
        return f"{int(i)}A"
    else:
        return f"{i}A"

def format_dcr(r):
    """
    Formata resistência DC usando 'R' como separador decimal.
    Ex: 0.0073 -> 0R0073, 1.05 -> 1R05, 150.0 -> 150R
    """
    s = str(r)
    if '.' in s:
        int_part, dec_part = s.split('.')
        return f"{int_part}R{dec_part}"
    else:
        return f"{int(r)}R"

def get_series(part):
    """Extrai a série do part number (ex: DR73 de DR73-150-R)."""
    return part.split('-')[0]

def get_footprint(part):
    """Retorna o footprint baseado na série."""
    series = get_series(part)
    if series.startswith("DR73") or series.startswith("DR74"):
        return "MyLib_Inductor_SMD:L_7.3x7.3_H4.5"
    elif series.startswith("DR125") or series.startswith("DR127"):
        return "MyLib_Inductor_SMD:L_12x12mm_H8mm"
    else:
        return None

# ==================== GERAÇÃO DO INSERT ====================
linhas_sql = []
contador = 600000  # base para MyPN
created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
created_by = "Rogerio Fontanario"

for part, ind, irms, dcr in dados:
    mypn = f"EL-IND-{contador:06d}"
    contador += 1

    series = get_series(part)
    ind_format = format_inductance(ind)
    current_format = format_current(irms)
    dcr_format = format_dcr(dcr)

    name = f"IND_{series}_{ind_format}_{current_format}"
    description = f"Shielded Power Inductor {ind_format} {current_format}"
    value = ind_format
    info1 = current_format
    info2 = dcr_format
    symbol = "MyLib_Inductor:L"
    footprint = get_footprint(part)
    manufacturer = "Eaton"
    manufacturer_pn = part
    category = "Inductor"
    subcategory = "Power Inductor"
    mount = "SMD"
    temp_range = "-40°C to +125°C"
    rohs = "Yes"
    active = 1
    version = 1
    exclude_bom = 0
    exclude_board = 0

    # Construir dicionário de valores
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
        'Manufacturer_PN': manufacturer_pn,
        'Family_Series': series,
        'Category': category,
        'Subcategory': subcategory,
        'Mount': mount,
        'Temperature_Range': temp_range,
        'RoHS_Compliant': rohs,
        'Active': active,
        'Version': version,
        'Created_At': created_at,
        'Created_By': created_by,
        'Exclude_from_BOM': exclude_bom,
        'Exclude_from_Board': exclude_board,
    }

    # Gerar lista de valores na ordem das colunas
    linha = []
    for col in COLUNAS:
        linha.append(sql_str(valores.get(col)))
    linhas_sql.append("(" + ", ".join(linha) + ")")

# Escrever arquivo SQL
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(f"-- Inserções para a tabela Inductor_General (série DR)\n")
    f.write(f"-- Gerado em {datetime.now()}\n\n")
    f.write(f"INSERT INTO Inductor_General (\n")
    f.write("    " + ",\n    ".join(COLUNAS) + "\n")
    f.write(") VALUES\n")
    f.write(",\n".join(linhas_sql))
    f.write(";\n\n-- Fim dos inserts\n")

print(f"Arquivo SQL gerado: {OUTPUT_FILE}")