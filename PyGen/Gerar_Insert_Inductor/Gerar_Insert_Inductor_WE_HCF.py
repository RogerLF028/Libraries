import os
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "insert_inductor_we_hcf.sql")

# Lista das colunas que serão preenchidas (na ordem desejada)
COLUNAS = [
    'MyPN', 'Name', 'Description', 'Value', 'Info1', 'Info2',
    'Symbol', 'Footprint', 'Manufacturer', 'Manufacturer_PN', 'Family_Series',
    'Category', 'Subcategory', 'Mount', 'Temperature_Range',
    'RoHS_Compliant', 'Active', 'Version', 'Created_At', 'Created_By',
    'Exclude_from_BOM', 'Exclude_from_Board'
]

# ==================== FUNÇÕES AUXILIARES ====================
def sql_str(val):
    """Escapa aspas simples e retorna string formatada para SQL."""
    if val is None:
        return 'NULL'
    return "'" + str(val).replace("'", "''") + "'"

def format_inductance(l):
    """Formata indutância em µH como string com 'u' (ex: 0.7u, 10u, 1000u)."""
    if l == int(l):
        return f"{int(l)}u"
    else:
        return f"{l}u"

def format_current(i):
    """Formata corrente em A como string com 'A' (ex: 54.7A)."""
    if i == int(i):
        return f"{int(i)}A"
    else:
        return f"{i}A"

def format_dcr(r):
    """
    Formata resistência DC usando 'R' como separador decimal.
    Ex: 0.00091 -> 0R00091, 0.00144 -> 0R00144
    """
    s = str(r)
    if '.' in s:
        int_part, dec_part = s.split('.')
        return f"{int_part}R{dec_part}"
    else:
        return f"{int(r)}R"

def get_footprint(part):
    """
    Retorna o footprint baseado no padrão do part number.
    Assume que os footprints estão na pasta MyLib_Inductors_SMD_WURTH.
    """
    if part.startswith("744363"):
        return "MyLib_Inductors_SMD_WURTH:L_Wurth_WE-HCF-2013"
    elif part.startswith("7443642"):
        return "MyLib_Inductors_SMD_WURTH:L_Wurth_WE-HCF-2010"
    elif part.startswith("7443641"):
        return "MyLib_Inductors_SMD_WURTH:L_Wurth_WE-HCF-2815"
    elif part.startswith("7443640") and part.endswith("B"):
        return "MyLib_Inductors_SMD_WURTH:L_Wurth_WE-HCF-2818B"
    elif part.startswith("7443640") and not part.endswith("B"):
        # 7443640330, 7443640470, etc. (2818)
        return "MyLib_Inductors_SMD_WURTH:L_Wurth_WE-HCF-2818"
    elif part.startswith("744374"):
        return "MyLib_Inductors_SMD_WURTH:L_Wurth_WE-HCF-2920litzwire"
    elif part.startswith("744375"):
        return "MyLib_Inductors_SMD_WURTH:L_Wurth_WE-HCF-2920roundwire"
    else:
        return None

def get_series(part):
    """Retorna o nome da série baseado no part number."""
    if part.startswith("744363"):
        return "WE-HCF-2013"
    elif part.startswith("7443642"):
        return "WE-HCF-2010"
    elif part.startswith("7443641"):
        return "WE-HCF-2815"
    elif part.startswith("7443640") and part.endswith("B"):
        return "WE-HCF-2818B"
    elif part.startswith("7443640") and not part.endswith("B"):
        return "WE-HCF-2818"
    elif part.startswith("744374"):
        return "WE-HCF-2920Litz"
    elif part.startswith("744375"):
        return "WE-HCF-2920Round"
    else:
        return "WE-HCF"

# ==================== DADOS DOS COMPONENTES ====================
# Cada tupla: (part_number, indutancia_uH, dcr_ohm, irms_A)
# Fonte: tabela consolidada anteriormente
dados = [
    # WE-HCF 2013
    ("7443630070", 0.7, 0.00083, 32.0),
    ("7443630140", 1.4, 0.00119, 47.1),
    ("7443630220", 2.2, 0.00165, 39.5),
    ("7443630310", 3.1, 0.00230, 33.15),
    ("7443630420", 4.2, 0.00334, 27.0),
    ("7443630550", 5.5, 0.00440, 23.35),
    ("7443630700", 7.0, 0.00617, 19.5),
    ("7443630860", 8.6, 0.00791, 17.1),
    ("7443631000", 10.0, 0.00876, 16.15),
    ("7443631500", 15.0, 0.00957, 15.4),
    ("7443632200", 22.0, 0.01172, 13.8),

    # WE-HCF 2010
    ("7443642010100", 1.0, 0.00092, 45.0),
    ("7443642010120", 1.2, 0.00092, 47.0),
    ("7443642010200", 2.0, 0.00092, 30.0),

    # WE-HCF 2815
    ("74436410150", 1.5, 0.00144, 44.0),
    ("74436410220", 2.2, 0.00144, 44.0),
    ("74436410330", 3.3, 0.00144, 44.0),
    ("74436410470", 4.7, 0.00144, 44.0),
    ("74436410680", 6.8, 0.00144, 44.0),
    ("74436411000", 10.0, 0.00144, 44.0),
    ("74436411500", 15.0, 0.00144, 44.0),
    ("74436412200", 22.0, 0.00144, 44.0),

    # WE-HCF 2818B
    ("7443640100B", 1.0, 0.00044, 56.0),
    ("7443640150B", 1.5, 0.00048, 86.2),
    ("7443640330B", 3.3, 0.00097, 59.2),
    ("7443640470B", 4.7, 0.000968, 47.5),
    ("7443640680B", 6.8, 0.00097, 59.2),
    ("7443641000B", 10.0, 0.00097, 59.2),

    # WE-HCF 2818
    ("7443640330", 3.3, 0.00264, 34.95),
    ("7443640470", 4.7, 0.00264, 34.95),
    ("7443640680", 6.8, 0.00264, 34.95),
    ("7443641000", 10.0, 0.00264, 34.95),
    ("7443641500", 15.0, 0.00264, 34.95),
    ("7443642200", 22.0, 0.00264, 34.95),

    # WE-HCF 2920 roundwire (apenas os que temos dados completos)
    ("74437529203220", 22.0, 0.00490, 23.9),
    ("74437529203681", 680.0, 0.11830, 4.8),
]

# ==================== GERAÇÃO DO INSERT ====================
contador = 600650  # próximo após MSS/SRP (terminaram em 600445)
created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
created_by = "Rogerio Fontanario"
symbol = "MyLib_Inductor:L_Ferrite"
manufacturer = "Wurth Elektronik"
category = "Inductor"
subcategory = "Power Inductor"
mount = "SMD"
temp_range = "-40°C to +125°C"
rohs = "Yes"
active = 1
version = 1
exclude_bom = 0
exclude_board = 0

linhas_sql = []

for part, ind, dcr, irms in dados:
    footprint = get_footprint(part)
    if not footprint:
        print(f"Aviso: Footprint não encontrado para {part}. Pulando.")
        continue

    series = get_series(part)
    mypn = f"EL-IND-{contador:06d}"
    contador += 1

    ind_format = format_inductance(ind)
    current_format = format_current(irms)
    dcr_format = format_dcr(dcr)

    name = f"IND_{series}_{ind_format}_{current_format}"
    description = f"High Current Shielded Power Inductor {ind_format} {current_format}"

    valores = {
        'MyPN': mypn,
        'Name': name,
        'Description': description,
        'Value': ind_format,
        'Info1': current_format,
        'Info2': dcr_format,
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
    f.write(f"-- Inserções para a tabela Inductor_General (família WE-HCF Wurth Elektronik)\n")
    f.write(f"-- Gerado em {datetime.now()}\n\n")
    f.write(f"INSERT INTO Inductor_General (\n")
    f.write("    " + ",\n    ".join(COLUNAS) + "\n")
    f.write(") VALUES\n")
    f.write(",\n".join(linhas_sql))
    f.write(";\n\n-- Fim dos inserts\n")

print(f"Arquivo SQL gerado: {OUTPUT_FILE}")
print(f"Total de inserts: {len(linhas_sql)}")
print(f"Último MyPN: EL-IND-{contador-1:06d}")