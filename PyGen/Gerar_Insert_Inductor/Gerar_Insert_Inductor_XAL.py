import os
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "insert_inductor_xal_all.sql")

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
    Ex: 0.00335 -> 0R00335, 0.02195 -> 0R02195, 0.109 -> 0R109
    """
    s = str(r)
    if '.' in s:
        int_part, dec_part = s.split('.')
        return f"{int_part}R{dec_part}"
    else:
        return f"{int(r)}R"

# ==================== DADOS POR SÉRIE ====================
# Cada série: (nome_serie, lista de tuplas (part_number, indutancia_uH, dcr_ohm, corrente_A), nome_footprint)
dados_series = [
    # XAL1510
    ("XAL1510", [
        ("XAL1510-472ME", 4.7, 0.00335, 29),
        ("XAL1510-682ME", 6.8, 0.00417, 26),
        ("XAL1510-822ME", 8.2, 0.00600, 24),
        ("XAL1510-103ME", 10.0, 0.00680, 22),
        ("XAL1510-153ME", 15.0, 0.00917, 18),
        ("XAL1510-223ME", 22.0, 0.0145, 14),
        ("XAL1510-333ME", 33.0, 0.0187, 12),
    ], "MyLib_Inductor_SMD:L_Coilcraft_XAL1510"),
    # XAL1010
    ("XAL1010", [
        ("XAL1010-221ME", 0.22, 0.00045, 55.5),
        ("XAL1010-451ME", 0.45, 0.00065, 53.0),
        ("XAL1010-681ME", 0.68, 0.00087, 48.0),
        ("XAL1010-102ME", 1.0, 0.00100, 43.5),
        ("XAL1010-152ME", 1.5, 0.00160, 40.5),
        ("XAL1010-222ME", 2.2, 0.00255, 32.0),
        ("XAL1010-332ME", 3.3, 0.00370, 25.0),
        ("XAL1010-472ME", 4.7, 0.00520, 24.0),
        ("XAL1010-562ME", 5.6, 0.00630, 21.2),
        ("XAL1010-682ME", 6.8, 0.00810, 18.5),
        ("XAL1010-822ME", 8.2, 0.01170, 17.1),
        ("XAL1010-103ME", 10.0, 0.01340, 15.5),
        ("XAL1010-153ME", 15.0, 0.01690, 13.8),
    ], "MyLib_Inductor_SMD:L_Coilcraft_XAL1010"),
    # XAL7070
    ("XAL7070", [
        ("XAL7070-161ME", 0.16, 0.00075, 30.5),
        ("XAL7070-301ME", 0.30, 0.00106, 26.1),
        ("XAL7070-551ME", 0.55, 0.00142, 23.5),
        ("XAL7070-651ME", 0.65, 0.00175, 21.0),
        ("XAL7070-801ME", 0.80, 0.00208, 20.8),
        ("XAL7070-102ME", 1.0, 0.00255, 20.0),
        ("XAL7070-122ME", 1.2, 0.00310, 16.2),
        ("XAL7070-182ME", 1.8, 0.00405, 15.8),
        ("XAL7070-222ME", 2.2, 0.00573, 13.2),
        ("XAL7070-332ME", 3.3, 0.00856, 11.5),
        ("XAL7070-472ME", 4.7, 0.01296, 10.5),
        ("XAL7070-562ME", 5.6, 0.01367, 8.5),
        ("XAL7070-682ME", 6.8, 0.01784, 6.8),
        ("XAL7070-103ME", 10.0, 0.01754, 7.0),
        ("XAL7070-123ME", 12.0, 0.01933, 6.0),
        ("XAL7070-153ME", 15.0, 0.02567, 5.4),
        ("XAL7070-183ME", 18.0, 0.02854, 5.0),
        ("XAL7070-223ME", 22.0, 0.03451, 4.7),
        ("XAL7070-333ME", 33.0, 0.05398, 3.6),
        ("XAL7070-473ME", 47.0, 0.08441, 3.1),
    ], "MyLib_Inductor_SMD:L_Coilcraft_XAL7070"),
    # XAL6030
    ("XAL6030", [
        ("XAL6030-181ME", 0.18, 0.00159, 32),
        ("XAL6030-331ME", 0.33, 0.00230, 25),
        ("XAL6030-561ME", 0.56, 0.00301, 22),
        ("XAL6030-102ME", 1.0, 0.00562, 18),
        ("XAL6030-122ME", 1.2, 0.00682, 16),
        ("XAL6030-182ME", 1.8, 0.00957, 14),
        ("XAL6030-222ME", 2.2, 0.01270, 10),
        ("XAL6030-332ME", 3.3, 0.01992, 8.0),
    ], "MyLib_Inductor_SMD:L_Coilcraft_XAL6030"),
    # XAL6060
    ("XAL6060", [
        ("XAL6060-472ME", 4.7, 0.01310, 11),
        ("XAL6060-562ME", 5.6, 0.01446, 10),
        ("XAL6060-682ME", 6.8, 0.01890, 9.0),
        ("XAL6060-822ME", 8.2, 0.02400, 8.0),
        ("XAL6060-103ME", 10.0, 0.02700, 7.0),
        ("XAL6060-153ME", 15.0, 0.03977, 6.0),
        ("XAL6060-223ME", 22.0, 0.05512, 5.0),
        ("XAL6060-333ME", 33.0, 0.09568, 3.6),
    ], "MyLib_Inductor_SMD:L_Coilcraft_XAL6060"),
    # XAL5030
    ("XAL5030", [
        ("XAL5030-161ME", 0.16, 0.00215, 22.2),
        ("XAL5030-331ME", 0.33, 0.00320, 19.2),
        ("XAL5030-601ME", 0.60, 0.00411, 17.7),
        ("XAL5030-801ME", 0.80, 0.00514, 13.0),
        ("XAL5030-102ME", 1.0, 0.00850, 11.1),
        ("XAL5030-122ME", 1.2, 0.01140, 10.4),
        ("XAL5030-222ME", 2.2, 0.01320, 9.7),
        ("XAL5030-332ME", 3.3, 0.02120, 8.1),
        ("XAL5030-472ME", 4.7, 0.03600, 5.9),
    ], "MyLib_Inductor_SMD:L_Coilcraft_XAL5030"),
    # XAL5050
    ("XAL5050", [
        ("XAL5050-472ME", 4.7, 0.02195, 8.2),
        ("XAL5050-562ME", 5.6, 0.02345, 7.2),
        ("XAL5050-682ME", 6.8, 0.02675, 6.4),
        ("XAL5050-822ME", 8.2, 0.03175, 6.1),
        ("XAL5050-103ME", 10.0, 0.04090, 4.9),
        ("XAL5050-153ME", 15.0, 0.06970, 3.9),
        ("XAL5050-223ME", 22.0, 0.09060, 3.4),
    ], "MyLib_Inductor_SMD:L_Coilcraft_XAL5050"),
    # XAL4020
    ("XAL4020", [
        ("XAL4020-221ME", 0.22, 0.00581, 16.8),
        ("XAL4020-401ME", 0.40, 0.00755, 14.0),
        ("XAL4020-601ME", 0.60, 0.00950, 11.7),
        ("XAL4020-102ME", 1.0, 0.01325, 9.6),
        ("XAL4020-122ME", 1.2, 0.01775, 9.0),
        ("XAL4020-152ME", 1.5, 0.02145, 7.5),
        ("XAL4020-222ME", 2.2, 0.03520, 5.5),
    ], "MyLib_Inductor_SMD:L_Coilcraft_XAL4020"),
    # XAL4030
    ("XAL4030", [
        ("XAL4030-332ME", 3.3, 0.0260, 6.6),
        ("XAL4030-472ME", 4.7, 0.0401, 5.1),
        ("XAL4030-682ME", 6.8, 0.0674, 3.9),
    ], "MyLib_Inductor_SMD:L_Coilcraft_XAL4030"),
    # XAL4040
    ("XAL4040", [
        ("XAL4040-822ME", 8.2, 0.0608, 3.4),
        ("XAL4040-103ME", 10.0, 0.0840, 3.1),
        ("XAL4040-153ME", 15.0, 0.109, 2.8),
    ], "MyLib_Inductor_SMD:L_Coilcraft_XAL4040"),
    # XAL8080
    ("XAL8080", [
        ("XAL8080-681ME", 0.68, 0.00138, 37.0),
        ("XAL8080-841ME", 0.84, 0.00160, 35.0),
        ("XAL8080-102ME", 1.0,  0.00211, 34.1),
        ("XAL8080-222ME", 2.2,  0.00408, 21.5),
        ("XAL8080-472ME", 4.7,  0.00889, 14.6),
        ("XAL8080-682ME", 6.8,  0.0132,  11.3),
        ("XAL8080-103ME", 10.0, 0.0210,   8.7),
        ("XAL8080-123ME", 12.0, 0.0164,  10.5),
        ("XAL8080-153ME", 15.0, 0.0203,   9.4),
        ("XAL8080-183ME", 18.0, 0.0252,   8.3),
        ("XAL8080-223ME", 22.0, 0.0296,   7.6),
        ("XAL8080-333ME", 33.0, 0.0437,   6.0),
        ("XAL8080-473ME", 47.0, 0.0647,   4.8),
    ], "MyLib_Inductor_SMD:L_Coilcraft_XAL8080"),
]

# ==================== GERAÇÃO DO INSERT ====================
contador = 600400  # início após SRR1210 (último foi 600229)
created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
created_by = "Rogerio Fontanario"
symbol = "MyLib_Inductor:L_Ferrite"
manufacturer = "Coilcraft"
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

for serie, lista, footprint in dados_series:
    for part, ind, dcr, irms in lista:
        mypn = f"EL-IND-{contador:06d}"
        contador += 1

        ind_format = format_inductance(ind)
        current_format = format_current(irms)
        dcr_format = format_dcr(dcr)

        name = f"IND_{serie}_{ind_format}_{current_format}"
        description = f"Shielded Power Inductor {ind_format} {current_format}"
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
            'Family_Series': serie,
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

# Escrever arquivo
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(f"-- Inserções para a tabela Inductor_General (famílias XAL Coilcraft)\n")
    f.write(f"-- Gerado em {datetime.now()}\n\n")
    f.write(f"INSERT INTO Inductor_General (\n")
    f.write("    " + ",\n    ".join(COLUNAS) + "\n")
    f.write(") VALUES\n")
    f.write(",\n".join(linhas_sql))
    f.write(";\n\n-- Fim dos inserts\n")

print(f"Arquivo SQL gerado: {OUTPUT_FILE} (último MyPN: EL-IND-{contador-1:06d})")