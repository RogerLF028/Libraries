import os
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Arquivos de saída
OUTPUT_SRR1260 = os.path.join(SCRIPT_DIR, "insert_inductor_srr1260.sql")
OUTPUT_SRR1208 = os.path.join(SCRIPT_DIR, "insert_inductor_srr1208.sql")
OUTPUT_SRR1210 = os.path.join(SCRIPT_DIR, "insert_inductor_srr1210.sql")

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
        # Remove zeros à direita desnecessários? Ex: 0.47 -> "0.47u"
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

# ==================== DADOS SRR1260 ====================
# Cada tupla: (part_number, indutancia_µH, corrente_rms_A, dcr_ohms)
# dcr convertido de mΩ para Ω (dividido por 1000)
dados_srr1260 = [
    ("SRR1260-1R0Y", 1.0, 8.9, 0.0070),
    ("SRR1260-1R2Y", 1.2, 8.20, 0.0080),
    ("SRR1260-1R5Y", 1.5, 7.80, 0.0095),
    ("SRR1260-2R2Y", 2.2, 7.20, 0.0105),
    ("SRR1260-2R4Y", 2.4, 7.00, 0.0115),
    ("SRR1260-3R3Y", 3.3, 6.60, 0.0120),
    ("SRR1260-3R5Y", 3.5, 6.50, 0.0130),
    ("SRR1260-4R7Y", 4.7, 5.80, 0.0155),
    ("SRR1260-5R6Y", 5.6, 5.70, 0.0162),
    ("SRR1260-6R1Y", 6.1, 5.60, 0.0170),
    ("SRR1260-6R8Y", 6.8, 5.30, 0.0180),
    ("SRR1260-7R6Y", 7.6, 5.00, 0.0190),
    ("SRR1260-8R2Y", 8.2, 4.70, 0.0195),
    ("SRR1260-100M", 10.0, 4.50, 0.0200),
    ("SRR1260-120M", 12.0, 4.20, 0.0230),
    ("SRR1260-150M", 15.0, 4.00, 0.0270),
    ("SRR1260-180M", 18.0, 3.20, 0.0360),
    ("SRR1260-220M", 22.0, 3.00, 0.0430),
    ("SRR1260-270M", 27.0, 2.80, 0.0450),
    ("SRR1260-330M", 33.0, 2.50, 0.0600),
    ("SRR1260-390M", 39.0, 2.30, 0.0700),
    ("SRR1260-470M", 47.0, 2.20, 0.0860),
    ("SRR1260-560M", 56.0, 2.00, 0.1000),
    ("SRR1260-680M", 68.0, 1.80, 0.1100),
    ("SRR1260-820M", 82.0, 1.60, 0.1450),
    ("SRR1260-101M", 100.0, 1.50, 0.1800),
    ("SRR1260-121K", 120.0, 1.40, 0.2100),
    ("SRR1260-151K", 150.0, 1.30, 0.2600),
    ("SRR1260-181K", 180.0, 1.20, 0.3200),
    ("SRR1260-221K", 220.0, 1.10, 0.3800),
    ("SRR1260-271K", 270.0, 1.00, 0.4500),
    ("SRR1260-331K", 330.0, 0.95, 0.5800),
    ("SRR1260-391K", 390.0, 0.90, 0.7000),
    ("SRR1260-471K", 470.0, 0.85, 0.8200),
    ("SRR1260-561K", 560.0, 0.80, 1.0000),
    ("SRR1260-681K", 680.0, 0.75, 1.1500),
    ("SRR1260-821K", 820.0, 0.70, 1.5000),
    ("SRR1260-102K", 1000.0, 0.65, 1.7000),
]

# ==================== DADOS SRR1208 ====================
# dcr já em ohms
dados_srr1208 = [
    ("SRR1208-2R5ML", 2.5, 7.50, 0.011),
    ("SRR1208-4R5ML", 4.5, 6.50, 0.014),
    ("SRR1208-6R5ML", 6.5, 6.00, 0.018),
    ("SRR1208-100ML", 10.0, 5.00, 0.021),
    ("SRR1208-120ML", 12.0, 4.80, 0.025),
    ("SRR1208-150ML", 15.0, 4.00, 0.036),
    ("SRR1208-180ML", 18.0, 3.80, 0.040),
    ("SRR1208-220ML", 22.0, 3.50, 0.043),
    ("SRR1208-270ML", 27.0, 3.00, 0.048),
    ("SRR1208-330YL", 33.0, 2.80, 0.062),
    ("SRR1208-390YL", 39.0, 2.50, 0.076),
    ("SRR1208-470YL", 47.0, 2.20, 0.085),
    ("SRR1208-560YL", 56.0, 2.00, 0.110),
    ("SRR1208-680YL", 68.0, 1.80, 0.135),
    ("SRR1208-820YL", 82.0, 1.60, 0.150),
    ("SRR1208-101YL", 100.0, 1.50, 0.170),
    ("SRR1208-121YL", 120.0, 1.40, 0.190),
    ("SRR1208-151YL", 150.0, 1.30, 0.240),
    ("SRR1208-181YL", 180.0, 1.20, 0.270),
    ("SRR1208-221KL", 220.0, 1.10, 0.380),
    ("SRR1208-271KL", 270.0, 0.95, 0.400),
    ("SRR1208-331KL", 330.0, 0.85, 0.650),
    ("SRR1208-391KL", 390.0, 0.80, 0.670),
    ("SRR1208-471KL", 470.0, 0.70, 0.850),
    ("SRR1208-561KL", 560.0, 0.65, 0.900),
    ("SRR1208-681KL", 680.0, 0.60, 1.00),
    ("SRR1208-821KL", 820.0, 0.55, 1.15),
    ("SRR1208-102KL", 1000.0, 0.50, 1.65),
    ("SRR1208-122KL", 1200.0, 0.40, 2.00),
    ("SRR1208-152KL", 1500.0, 0.36, 2.35),
    ("SRR1208-182KL", 1800.0, 0.46, 3.40),
    ("SRR1208-222KL", 2200.0, 0.40, 4.20),
    ("SRR1208-272KL", 2700.0, 0.35, 5.20),
    ("SRR1208-332KL", 3300.0, 0.32, 6.40),
    ("SRR1208-392KL", 3900.0, 0.30, 7.80),
    ("SRR1208-472KL", 4700.0, 0.28, 9.60),
    ("SRR1208-562KL", 5600.0, 0.25, 12.0),
    ("SRR1208-682KL", 6800.0, 0.22, 15.2),
    ("SRR1208-822KL", 8200.0, 0.20, 17.0),
    ("SRR1208-103KL", 10000.0, 0.18, 19.2),
]

# ==================== DADOS SRR1210 ====================
# DCR convertido de mΩ para Ω
dados_srr1210 = [
    ("SRR1210-1R0Y", 1.0, 11.0, 0.0060),
    ("SRR1210-1R8Y", 1.8, 10.2, 0.0075),
    ("SRR1210-2R2Y", 2.2, 9.5, 0.0090),
    ("SRR1210-3R3Y", 3.3, 9.0, 0.010),
    ("SRR1210-4R7Y", 4.7, 8.5, 0.012),
    ("SRR1210-5R6Y", 5.6, 8.0, 0.014),
    ("SRR1210-6R8Y", 6.8, 7.9, 0.015),
    ("SRR1210-8R2Y", 8.2, 7.3, 0.017),
    ("SRR1210-100M", 10.0, 6.5, 0.018),
    ("SRR1210-120M", 12.0, 6.3, 0.022),
    ("SRR1210-150M", 15.0, 5.8, 0.032),
    ("SRR1210-180M", 18.0, 5.5, 0.035),
    ("SRR1210-220M", 22.0, 5.2, 0.038),
    ("SRR1210-270M", 27.0, 5.0, 0.040),
    ("SRR1210-330M", 33.0, 4.4, 0.052),
    ("SRR1210-390M", 39.0, 4.2, 0.066),
    ("SRR1210-470M", 47.0, 3.8, 0.072),
    ("SRR1210-560M", 56.0, 3.4, 0.090),
    ("SRR1210-680M", 68.0, 3.0, 0.102),
    ("SRR1210-820M", 82.0, 2.8, 0.112),
    ("SRR1210-101M", 100.0, 2.5, 0.135),
    ("SRR1210-121M", 120.0, 2.3, 0.170),
    ("SRR1210-151M", 150.0, 2.2, 0.190),
    ("SRR1210-181M", 180.0, 1.9, 0.250),
    ("SRR1210-221M", 220.0, 1.7, 0.315),
    ("SRR1210-271M", 270.0, 1.5, 0.410),
    ("SRR1210-331M", 330.0, 1.4, 0.450),
    ("SRR1210-391M", 390.0, 1.3, 0.600),
    ("SRR1210-471M", 470.0, 1.2, 0.820),
    ("SRR1210-561M", 560.0, 1.1, 0.900),
    ("SRR1210-681M", 680.0, 1.0, 1.200),
    ("SRR1210-821M", 820.0, 0.85, 1.320),
    ("SRR1210-102M", 1000.0, 0.75, 1.650),
]

# ==================== FUNÇÃO PARA GERAR INSERT ====================
def gerar_insert(series, dados, start_mypn, output_file, symbol):
    contador = start_mypn
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    created_by = "Rogerio Fontanario"
    footprint = f"MyLib_Inductor_SMD:L_Bourns_{series}"
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

    linhas_sql = []
    for part, ind, irms, dcr in dados:
        mypn = f"EL-IND-{contador:06d}"
        contador += 1

        ind_format = format_inductance(ind)
        current_format = format_current(irms)
        dcr_format = format_dcr(dcr)

        name = f"IND_{series}_{ind_format}_{current_format}"
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

    # Escrever arquivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"-- Inserções para a tabela Inductor_General (série {series})\n")
        f.write(f"-- Gerado em {datetime.now()}\n\n")
        f.write(f"INSERT INTO Inductor_General (\n")
        f.write("    " + ",\n    ".join(COLUNAS) + "\n")
        f.write(") VALUES\n")
        f.write(",\n".join(linhas_sql))
        f.write(";\n\n-- Fim dos inserts\n")

    print(f"Arquivo SQL gerado: {output_file} (último MyPN: EL-IND-{contador-1:06d})")
    return contador

# ==================== EXECUÇÃO ====================
print("Gerando arquivos SQL para as séries SRR1260, SRR1208 e SRR1210...")
prox = 600200  # após SRF1260 (terminou em 600118)

# SRR1260
prox = gerar_insert("SRR1260", dados_srr1260, prox, OUTPUT_SRR1260, "MyLib_Inductor:L")

# SRR1208
prox = gerar_insert("SRR1208", dados_srr1208, prox, OUTPUT_SRR1208, "MyLib_Inductor:L")

# SRR1210
prox = gerar_insert("SRR1210", dados_srr1210, prox, OUTPUT_SRR1210, "MyLib_Inductor:L")

print("Todos os arquivos gerados com sucesso.")