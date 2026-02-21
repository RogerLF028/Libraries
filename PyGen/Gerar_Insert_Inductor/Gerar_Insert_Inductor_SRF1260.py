import os
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "insert_inductor_srf1260.sql")

# Lista das colunas que serão preenchidas (na ordem desejada)
COLUNAS = [
    'MyPN', 'Name', 'Description', 'Value', 'Info1', 'Info2',
    'Symbol', 'Footprint', 'Manufacturer', 'Manufacturer_PN', 'Family_Series',
    'Category', 'Subcategory', 'Mount', 'Temperature_Range',
    'RoHS_Compliant', 'Active', 'Version', 'Created_At', 'Created_By',
    'Exclude_from_BOM', 'Exclude_from_Board'
]

# Dados extraídos do datasheet (part number, inductance µH, Irms A, DCR ohms)
# Valores da configuração paralela (Parallel Rating)
dados = [
    ("SRF1260-R47Y", 0.47, 17.6, 0.0053),
    ("SRF1260-1R0Y", 1.0, 15.0, 0.0062),
    ("SRF1260-1R5Y", 1.5, 13.8, 0.0073),
    ("SRF1260-2R2Y", 2.2, 10.9, 0.0085),
    ("SRF1260-3R3Y", 3.3, 9.26, 0.0101),
    ("SRF1260-4R7Y", 4.7, 7.18, 0.0137),
    ("SRF1260-6R8Y", 6.8, 6.64, 0.0186),
    ("SRF1260-8R2Y", 8.2, 5.54, 0.0194),
    ("SRF1260-100M", 10.0, 5.35, 0.0246),
    ("SRF1260-150M", 15.0, 4.27, 0.0329),
    ("SRF1260-220M", 22.0, 3.7, 0.0451),
    ("SRF1260-330M", 33.0, 3.28, 0.0618),
    ("SRF1260-470M", 47.0, 2.71, 0.086),
    ("SRF1260-680M", 68.0, 2.22, 0.117),
    ("SRF1260-820M", 82.0, 2.05, 0.15),
    ("SRF1260-101M", 100.0, 1.78, 0.171),
    ("SRF1260-151M", 150.0, 1.48, 0.254),
    ("SRF1260-221M", 220.0, 1.19, 0.354),
    ("SRF1260-331M", 330.0, 1.06, 0.574),
    ("SRF1260-471M", 470.0, 0.87, 0.83),
    ("SRF1260-681M", 680.0, 0.7, 1.212),
    ("SRF1260-821M", 820.0, 0.6, 1.46),
    ("SRF1260-102M", 1000.0, 0.57, 1.854),
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
    Ex: 0.0053 -> 0R0053, 1.854 -> 1R854
    """
    s = str(r)
    if '.' in s:
        int_part, dec_part = s.split('.')
        return f"{int_part}R{dec_part}"
    else:
        return f"{int(r)}R"

# ==================== GERAÇÃO DO INSERT ====================
linhas_sql = []
contador = 600100  # próximo após o último da série DR (600095)
created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
created_by = "Rogerio Fontanario"
symbol = "MyLib_Inductor:L_Coupled_1324"   # símbolo para indutor acoplado (dual winding)
footprint = "MyLib_Inductor_SMD:L_Bourns_SRF1260"
manufacturer = "Bourns"
category = "Inductor"
subcategory = "Power Inductor"
mount = "SMD"
temp_range = "-40°C to +125°C"
rohs = "Yes"
active = 1
version = 1
exclude_bom = 0
exclude_board = 0

for part, ind, irms, dcr in dados:
    mypn = f"EL-IND-{contador:06d}"
    contador += 1

    series = "SRF1260"
    ind_format = format_inductance(ind)
    current_format = format_current(irms)
    dcr_format = format_dcr(dcr)

    name = f"IND_{series}_{ind_format}_{current_format}"
    description = f"Dual Winding Shielded Power Inductor {ind_format} {current_format}"
    value = ind_format
    info1 = current_format
    info2 = dcr_format

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

    linha = [sql_str(valores.get(col)) for col in COLUNAS]
    linhas_sql.append("(" + ", ".join(linha) + ")")

# Escrever arquivo SQL
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(f"-- Inserções para a tabela Inductor_General (série SRF1260)\n")
    f.write(f"-- Gerado em {datetime.now()}\n\n")
    f.write(f"INSERT INTO Inductor_General (\n")
    f.write("    " + ",\n    ".join(COLUNAS) + "\n")
    f.write(") VALUES\n")
    f.write(",\n".join(linhas_sql))
    f.write(";\n\n-- Fim dos inserts\n")

print(f"Arquivo SQL gerado: {OUTPUT_FILE}")