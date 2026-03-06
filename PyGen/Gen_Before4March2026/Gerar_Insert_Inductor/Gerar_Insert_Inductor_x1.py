import os
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "insert_inductor_mss_srp.sql")

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
    """
    Formata indutância em µH para o formato desejado:
    - Se l < 1: converte para nH (multiplica por 1000) e retorna como inteiro com "nH" (ex: 0.33 µH → "330nH")
    - Se l >= 1:
        - se l é inteiro: retorna f"{int(l)}uH" (ex: 10 µH → "10uH")
        - senão: substitui ponto por 'u' e adiciona 'H' (ex: 3.3 µH → "3u3H")
    """
    if l < 1.0:
        # Converte para nanohenries (1 µH = 1000 nH)
        nh = int(round(l * 1000))
        return f"{nh}nH"
    else:
        if l == int(l):
            return f"{int(l)}uH"
        else:
            s = str(l)
            return s.replace('.', 'u') + 'H'

def format_current(i):
    """
    Formata corrente em A para o formato desejado:
    - Se i < 1: converte para mA e adiciona "mA" (ex: 0.73 A → "730mA")
    - Se i >= 1: substitui o ponto por 'A' e não adiciona unidade extra
                 (ex: 3.31 A → "3A31", 6.2 A → "6A2", 5 A → "5A")
    """
    if i < 1:
        # Converte para mA (valor inteiro)
        ma = int(round(i * 1000))
        return f"{ma}mA"
    else:
        if i == int(i):
            return f"{int(i)}A"
        else:
            s = str(i)
            return s.replace('.', 'A')

def format_dcr(r):
    """
    Formata resistência DC usando 'R' como separador decimal.
    Ex: 0.00584 -> 0R00584, 0.0121 -> 0R0121, 1.193 -> 1R193
    """
    s = str(r)
    if '.' in s:
        int_part, dec_part = s.split('.')
        return f"{int_part}R{dec_part}"
    else:
        return f"{int(r)}R"

# ==================== DADOS POR SÉRIE ====================

# MSS1246 (Coilcraft)
mss1246_data = [
    ("MSS1246-102ML", 1.0, 0.00584, 8.00),
    ("MSS1246-332ML", 3.3, 0.0121, 6.30),
    ("MSS1246-472ML", 4.7, 0.0191, 6.00),
    ("MSS1246-562ML", 5.6, 0.0221, 5.75),
    ("MSS1246-682ML", 6.8, 0.0249, 5.20),
    ("MSS1246-822ML", 8.2, 0.0274, 4.87),
    ("MSS1246-103ML", 10, 0.0368, 4.20),
    ("MSS1246-123ML", 12, 0.0389, 3.95),
    ("MSS1246-153ML", 15, 0.0486, 3.80),
    ("MSS1246-183ML", 18, 0.0510, 3.52),
    ("MSS1246-223ML", 22, 0.0603, 3.40),
    ("MSS1246-273ML", 27, 0.0675, 2.96),
    ("MSS1246-333ML", 33, 0.0817, 2.60),
    ("MSS1246-393ML", 39, 0.0952, 2.39),
    ("MSS1246-473ML", 47, 0.1206, 2.10),
    ("MSS1246-563ML", 56, 0.1338, 2.01),
    ("MSS1246-683ML", 68, 0.1673, 1.80),
    ("MSS1246-823ML", 82, 0.1885, 1.72),
    ("MSS1246-104ML", 100, 0.2168, 1.60),
    ("MSS1246-124KL", 120, 0.2872, 1.42),
    ("MSS1246-154KL", 150, 0.3267, 1.30),
    ("MSS1246-184KL", 180, 0.3795, 1.21),
    ("MSS1246-224KL", 220, 0.4882, 1.00),
    ("MSS1246-274KL", 270, 0.5601, 0.95),
    ("MSS1246-334KL", 330, 0.7314, 0.87),
    ("MSS1246-394KL", 390, 0.8137, 0.79),
    ("MSS1246-474KL", 470, 0.9351, 0.76),
    ("MSS1246-564KL", 560, 1.193, 0.67),
    ("MSS1246-684KL", 680, 1.370, 0.62),
    ("MSS1246-824KL", 820, 1.590, 0.58),
    ("MSS1246-105KL", 1000, 2.090, 0.50),
]

# SRP1245A (Bourns)
srp1245a_data = [
    ("SRP1245A-R20M", 0.20, 0.00055, 52),
    ("SRP1245A-R22M", 0.22, 0.00075, 52),
    ("SRP1245A-R33M", 0.33, 0.00094, 42),
    ("SRP1245A-R36M", 0.36, 0.00095, 42),
    ("SRP1245A-R39M", 0.39, 0.00095, 42),
    ("SRP1245A-R47M", 0.47, 0.00113, 38),
    ("SRP1245A-R50M", 0.50, 0.00133, 37),
    ("SRP1245A-R56M", 0.56, 0.00153, 36),
    ("SRP1245A-R68M", 0.68, 0.00173, 34),
    ("SRP1245A-R82M", 0.82, 0.00213, 31),
    ("SRP1245A-1R0M", 1.0, 0.00252, 29),
    ("SRP1245A-1R2M", 1.2, 0.00302, 28),
    ("SRP1245A-1R5M", 1.5, 0.00332, 27),
    ("SRP1245A-1R8M", 1.8, 0.00492, 21),
    ("SRP1245A-2R2M", 2.2, 0.00552, 20),
    ("SRP1245A-2R7M", 2.7, 0.00672, 17),
    ("SRP1245A-3R3M", 3.3, 0.00921, 15),
    ("SRP1245A-4R7M", 4.7, 0.0120, 12),
    ("SRP1245A-5R6M", 5.6, 0.0130, 11.5),
    ("SRP1245A-6R0M", 6.0, 0.0140, 11.5),
    ("SRP1245A-6R8M", 6.8, 0.0155, 11),
    ("SRP1245A-8R2M", 8.2, 0.0185, 9.5),
    ("SRP1245A-100M", 10, 0.0225, 9),
    ("SRP1245A-180M", 18, 0.0450, 7.5),
    ("SRP1245A-220M", 22, 0.0650, 6.5),
]

# MSS1038 (Coilcraft)
mss1038_data = [
    ("MSS1038-102NL", 1.0, 0.00601, 7.30),
    ("MSS1038-152NL", 1.5, 0.00818, 5.60),
    ("MSS1038-252NL", 2.5, 0.010, 4.65),
    ("MSS1038-382NL", 3.8, 0.013, 4.25),
    ("MSS1038-522NL", 5.2, 0.022, 3.60),
    ("MSS1038-702NL", 7.0, 0.027, 3.10),
    ("MSS1038-103NL", 10, 0.035, 2.90),
    ("MSS1038-123NL", 12, 0.041, 2.85),
    ("MSS1038-153NL", 15, 0.050, 2.70),
    ("MSS1038-183NL", 18, 0.065, 2.35),
    ("MSS1038-223NL", 22, 0.073, 1.90),
    ("MSS1038-273NL", 27, 0.089, 1.65),
    ("MSS1038-333NL", 33, 0.093, 1.60),
    ("MSS1038-393NL", 39, 0.112, 1.55),
    ("MSS1038-473NL", 47, 0.128, 1.45),
    ("MSS1038-563NL", 56, 0.180, 1.40),
    ("MSS1038-683NL", 68, 0.213, 1.15),
    ("MSS1038-823NL", 82, 0.261, 1.09),
    ("MSS1038-104NL", 100, 0.304, 1.05),
    ("MSS1038-124NL", 120, 0.380, 0.85),
    ("MSS1038-154NL", 150, 0.506, 0.80),
    ("MSS1038-184NL", 180, 0.582, 0.71),
    ("MSS1038-224NL", 220, 0.756, 0.70),
    ("MSS1038-274NL", 270, 0.926, 0.65),
    ("MSS1038-334NL", 330, 1.090, 0.50),
    ("MSS1038-394NL", 390, 1.141, 0.49),
    ("MSS1038-474NL", 470, 1.243, 0.45),
    ("MSS1038-564NL", 560, 1.696, 0.43),
    ("MSS1038-684NL", 680, 1.926, 0.36),
    ("MSS1038-824NL", 820, 2.596, 0.34),
    ("MSS1038-105NL", 1000, 2.853, 0.33),
]

# MSS1210 (Coilcraft)
mss1210_data = [
    ("MSS1210-103ML", 10, 0.038, 4.70),
    ("MSS1210-153ML", 15, 0.052, 4.20),
    ("MSS1210-223ML", 22, 0.064, 3.20),
    ("MSS1210-333ML", 33, 0.079, 2.90),
    ("MSS1210-473ML", 47, 0.095, 2.10),
    ("MSS1210-683ML", 68, 0.110, 1.80),
    ("MSS1210-823ML", 82, 0.125, 1.70),
    ("MSS1210-104ML", 100, 0.140, 1.50),
    ("MSS1210-124ML", 120, 0.155, 1.20),
    ("MSS1210-154ML", 150, 0.175, 1.10),
    ("MSS1210-184ML", 180, 0.195, 1.00),
    ("MSS1210-224ML", 220, 0.225, 0.90),
    ("MSS1210-274ML", 270, 0.260, 0.85),
    ("MSS1210-334ML", 330, 0.300, 0.80),
    ("MSS1210-394ML", 390, 0.360, 0.75),
    ("MSS1210-474ML", 470, 0.415, 0.70),
    ("MSS1210-564ML", 560, 0.480, 0.60),
    ("MSS1210-684ML", 680, 0.560, 0.55),
    ("MSS1210-824ML", 820, 0.660, 0.50),
    ("MSS1210-105ML", 1000, 0.775, 0.48),
    ("MSS1210-125ML", 1200, 0.870, 0.45),
    ("MSS1210-155ML", 1500, 1.150, 0.40),
    ("MSS1210-185ML", 1800, 1.300, 0.38),
    ("MSS1210-225ML", 2200, 1.600, 0.35),
    ("MSS1210-275ML", 2700, 1.900, 0.30),
    ("MSS1210-335ML", 3300, 2.300, 0.28),
    ("MSS1210-395ML", 3900, 2.600, 0.27),
    ("MSS1210-475ML", 4700, 3.200, 0.24),
    ("MSS1210-565ML", 5600, 3.800, 0.22),
    ("MSS1210-685ML", 6800, 4.800, 0.20),
    ("MSS1210-825ML", 8200, 5.600, 0.18),
    ("MSS1210-106ML", 10000, 6.800, 0.16),
]

# ==================== GERAÇÃO DO INSERT ====================
contador = 600500  # próximo após XAL8080 (terminou em 600327)
created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
created_by = "Rogerio Fontanario"
symbol = "MyLib_Inductor:L_Ferrite"
manufacturer_coilcraft = "Coilcraft"
manufacturer_bourns = "Bourns"
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

# Função auxiliar para adicionar uma série
def add_series(series_name, data, footprint, manufacturer):
    global contador
    for part, ind, dcr, irms in data:
        mypn = f"EL-IND-{contador:06d}"
        contador += 1
        ind_f = format_inductance(ind)
        curr_f = format_current(irms)
        dcr_f = format_dcr(dcr)
        name = f"IND_{series_name}_{ind_f}_{curr_f}"
        description = f"Shielded Power Inductor {ind_f} {curr_f}"
        valores = {
            'MyPN': mypn,
            'Name': name,
            'Description': description,
            'Value': ind_f,
            'Info1': curr_f,
            'Info2': dcr_f,
            'Symbol': symbol,
            'Footprint': footprint,
            'Manufacturer': manufacturer,
            'Manufacturer_PN': part,
            'Family_Series': series_name,
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

# Adicionar cada série
add_series("MSS1246", mss1246_data, "MyLib_Inductor_SMD:L_Coilcraft_MSS1246-XXX", manufacturer_coilcraft)
add_series("SRP1245A", srp1245a_data, "MyLib_Inductor_SMD:L_Bourns_SRP1245A", manufacturer_bourns)
add_series("MSS1038", mss1038_data, "MyLib_Inductor_SMD:L_Coilcraft_MSS1038-XXX", manufacturer_coilcraft)
add_series("MSS1210", mss1210_data, "MyLib_Inductor_SMD:L_Coilcraft_MSS1210-XXX", manufacturer_coilcraft)

# Escrever arquivo
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(f"-- Inserções para a tabela Inductor_General (séries MSS1246, SRP1245A, MSS1038, MSS1210)\n")
    f.write(f"-- Gerado em {datetime.now()}\n\n")
    f.write(f"INSERT INTO Inductor_General (\n")
    f.write("    " + ",\n    ".join(COLUNAS) + "\n")
    f.write(") VALUES\n")
    f.write(",\n".join(linhas_sql))
    f.write(";\n\n-- Fim dos inserts\n")

print(f"Arquivo SQL gerado: {OUTPUT_FILE}")
print(f"Último MyPN: EL-IND-{contador-1:06d}")