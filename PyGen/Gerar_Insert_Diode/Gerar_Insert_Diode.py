import csv
import os
import re
from collections import defaultdict
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, "Diode.csv")
OUTPUT_DIR = SCRIPT_DIR

# Mapeamento de tipos para categorias e bases de MyPN
TYPE_MAP = {
    'Switching':      ('general', 100000),
    'Rectifier':      ('general', 100000),
    'Fast Recovery':  ('general', 100000),
    'Ultra Fast':     ('general', 100000),
    'Varicap':        ('general', 100000),
    'PIN':            ('general', 100000),
    'Zener':          ('zener',   200000),
    'TVS':            ('tvs',     300000),
    'Schottky':       ('schottky',400000),
}

# Nomes dos arquivos de saída
OUTPUT_FILES = {
    'general':   'insert_diode_general.sql',
    'zener':     'insert_diode_zener.sql',
    'tvs':       'insert_diode_tvs.sql',
    'schottky':  'insert_diode_schottky.sql',
}

# Lista fixa de colunas na ordem em que aparecerão no INSERT
# (baseada nas colunas da tabela que podem ser preenchidas)
COLUNAS = [
    'MyPN', 'Name', 'Description', 'Value', 'Info1', 'Info2',
    'Symbol', 'Footprint', 'Footprint_Filter', 'Datasheet', 'Notes',
    'Manufacturer', 'Manufacturer_PN', 'LCSC_PN', 'LCSC_URL',
    'Mouser_PN', 'Mouser_URL', 'Digikey_PN', 'Digikey_URL', 'Alternative_PN',
    'Stock_Qty', 'Stock_Unit', 'Price', 'Currency', 'Min_Stock', 'Max_Stock',
    'Last_Purchase_Date', 'Last_Purchase_Price', 'Active', 'Version',
    'Created_At', 'Created_By', 'Modified_At', 'Modified_By',
    'Exclude_from_BOM', 'Exclude_from_Board', 'Category', 'Subcategory',
    'Package', 'Mount', 'Dimensions', 'REACH_Compliant', 'RoHS_Compliant',
    'Tolerance', 'Forward_Voltage', 'Reverse_Recovery_Time', 'Power_Dissipation',
    'Termination_Style', 'Family_Series', 'Stock_Location',
    'Reverse_Leakage', 'Junction_Capacitance', 'Breakdown_Voltage',
    'Reverse_Standoff_Voltage', 'Clamping_Voltage', 'Temperature_Range',
    'Voltage_Rating', 'Current_Rating', 'Power_Rating', 'Zener_Voltage'
]

# ==================== FUNÇÕES AUXILIARES ====================
def get_val(row, key):
    """Retorna o valor da coluna ou None se vazio."""
    val = row.get(key, '').strip()
    return val if val != '' else None

def sql_str(val):
    """Escapa aspas simples e retorna string formatada para SQL."""
    if val is None:
        return 'NULL'
    return "'" + str(val).replace("'", "''") + "'"

def generate_name(row, cat):
    """Gera o campo Name personalizado conforme o tipo."""
    value = row.get('Value', '').strip()
    typ = row.get('Type', '').strip()
    package = row.get('Package', '').strip()
    pkg_clean = re.sub(r'[^a-zA-Z0-9]', '', package) if package else ''

    if cat == 'zener':
        bv = row.get('Breakdown_Voltage', '').strip()
        pd = row.get('Power_Dissipation', '').strip()
        return f"{value}_Zener_{bv}_{pd}_{pkg_clean}"
    elif cat == 'tvs':
        sv = row.get('Standoff_Voltage', '').strip()
        pd = row.get('Power_Dissipation', '').strip()
        return f"{value}_TVS_{sv}_{pd}_{pkg_clean}"
    elif cat == 'schottky':
        rv = row.get('Reverse_Voltage', '').strip()
        fc = row.get('Forward_Current', '').strip()
        return f"{value}_Schottky_{rv}_{fc}_{pkg_clean}"
    else:  # general
        rv = row.get('Reverse_Voltage', '').strip()
        fc = row.get('Forward_Current', '').strip()
        if not rv:
            rv = row.get('Breakdown_Voltage', '').strip()
        return f"{value}_{typ}_{rv}_{fc}_{pkg_clean}"

def get_info1_info2(row, cat):
    """
    Retorna uma tupla (info1, info2) conforme as regras do arquivo de instruções.
    """
    typ = row.get('Type', '').strip()
    if cat == 'zener':
        info1 = row.get('Breakdown_Voltage', '').strip()
        info2 = row.get('Power_Dissipation', '').strip()
    elif cat == 'tvs':
        info1 = row.get('Standoff_Voltage', '').strip()
        info2 = None  # Peak_Pulse_Current não disponível
    else:  # general e schottky
        info1 = row.get('Forward_Current', '').strip()
        info2 = row.get('Reverse_Voltage', '').strip()  # opcional
    return info1, info2

# ==================== LEITURA DO CSV ====================
if not os.path.exists(CSV_FILE):
    print(f"ERRO: Arquivo CSV não encontrado: {CSV_FILE}")
    exit(1)

# Agrupar linhas por categoria
categorias = defaultdict(list)  # categoria -> lista de dicionários
with open(CSV_FILE, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        typ = row.get('Type', '').strip()
        info = TYPE_MAP.get(typ)
        if info:
            cat, base = info
            categorias[cat].append(row)
        else:
            print(f"Tipo ignorado: {typ}")

# ==================== GERAÇÃO DOS ARQUIVOS ====================
for cat, linhas in categorias.items():
    if not linhas:
        continue
    out_file = os.path.join(OUTPUT_DIR, OUTPUT_FILES[cat])
    base_number = TYPE_MAP[next(t for t, (c, b) in TYPE_MAP.items() if c == cat)][1]

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(f"-- Inserções para diodos {cat.upper()}\n")
        f.write(f"-- Gerado em {datetime.now()}\n\n")

        # Cabeçalho do INSERT
        f.write(f"INSERT INTO Diode_{cat.capitalize()} (\n")
        f.write("    " + ",\n    ".join(COLUNAS) + "\n")
        f.write(") VALUES\n")

        valores_linhas = []
        for idx, row in enumerate(linhas):
            # Gerar MyPN sequencial
            mypn = f"EL-DIO-{base_number + idx:06d}"

            # Gerar Name
            name = generate_name(row, cat)

            # Obter Info1 e Info2
            info1, info2 = get_info1_info2(row, cat)

            # Mapeamento direto de colunas CSV -> tabela
            mapeamento = {
                'Description': 'Description',
                'Symbol': 'Symbol',
                'Footprint': 'Footprint',
                'Footprint_Filter': 'Footprint_Filter',
                'Datasheet': 'Datasheet',
                'Notes': 'Notes',
                'Manufacturer': 'Manufacturer',
                'Manufacturer_PN': 'Manufacturer_PN',
                'LCSC_PN': 'LCSC_PN',
                'LCSC_URL': 'LCSC_URL',
                'Mouser_PN': 'Mouser_PN',
                'Mouser_URL': 'Mouser_URL',
                'Digikey_PN': 'Digikey_PN',
                'Digikey_URL': 'Digikey_URL',
                'Alternative_PN': 'Alternative_PN',
                'StockQty': 'Stock_Qty',
                'Stock_Unit': 'Stock_Unit',
                'Price': 'Price',
                'Currency': 'Currency',
                'Min_Stock': 'Min_Stock',
                'Max_Stock': 'Max_Stock',
                'Last_Purchase_Date': 'Last_Purchase_Date',
                'Last_Purchase_Price': 'Last_Purchase_Price',
                'Active': 'Active',
                'Version': 'Version',
                'CreatedAt': 'Created_At',
                'CreatedBy': 'Created_By',
                'ModifiedAt': 'Modified_At',
                'ModifiedBy': 'Modified_By',
                'Exclude_from_BOM': 'Exclude_from_BOM',
                'Exclude_from_Board': 'Exclude_from_Board',
                'Category': 'Category',
                'Subcategory': 'Subcategory',
                'Package': 'Package',
                'Mount': 'Mount',
                'Dimensions': 'Dimensions',
                'REACH_Compliant': 'REACH_Compliant',
                'RoHS_Compliant': 'RoHS_Compliant',
                'Tolerance': 'Tolerance',
                'Forward_Voltage': 'Forward_Voltage',
                'Reverse_Recovery_Time': 'Reverse_Recovery_Time',
                'Power_Dissipation': 'Power_Dissipation',
                'Termination': 'Termination_Style',
                'Series': 'Family_Series',
                'StockPlace': 'Stock_Location',
            }

            # Construir dicionário com os valores que temos
            valores = {}
            for csv_col, tab_col in mapeamento.items():
                v = get_val(row, csv_col)
                if v is not None:
                    valores[tab_col] = v

            # Mapeamentos especiais
            rev_curr = get_val(row, 'Reverse_Current')
            if rev_curr:
                valores['Reverse_Leakage'] = rev_curr

            cap = get_val(row, 'Capacitance')
            if cap:
                valores['Junction_Capacitance'] = cap

            bv = get_val(row, 'Breakdown_Voltage')
            if bv:
                valores['Breakdown_Voltage'] = bv

            sv = get_val(row, 'Standoff_Voltage')
            if sv:
                valores['Reverse_Standoff_Voltage'] = sv

            cv = get_val(row, 'Clamping_Voltage')
            if cv:
                valores['Clamping_Voltage'] = cv

            # Temperature Range
            min_t = get_val(row, 'Min_Temp')
            max_t = get_val(row, 'Max_Temp')
            if min_t and max_t:
                valores['Temperature_Range'] = f"{min_t} to {max_t}"

            # Voltage_Rating
            if cat == 'zener':
                v_rating = bv
            elif cat == 'tvs':
                v_rating = sv
            else:
                v_rating = get_val(row, 'Reverse_Voltage') or bv
            if v_rating:
                valores['Voltage_Rating'] = v_rating

            # Current_Rating (apenas general e schottky)
            if cat in ('general', 'schottky'):
                c_rating = get_val(row, 'Forward_Current')
                if c_rating:
                    valores['Current_Rating'] = c_rating

            # Power_Rating
            p_rating = get_val(row, 'Power_Dissipation')
            if p_rating:
                valores['Power_Rating'] = p_rating

            # Zener_Voltage
            if cat == 'zener' and bv:
                valores['Zener_Voltage'] = bv

            # Agora montar a lista de valores na ordem de COLUNAS
            linha_valores = []
            for col in COLUNAS:
                if col == 'MyPN':
                    linha_valores.append(sql_str(mypn))
                elif col == 'Name':
                    linha_valores.append(sql_str(name))
                elif col == 'Value':
                    linha_valores.append(sql_str(row.get('Value', '').strip()))
                elif col == 'Info1':
                    linha_valores.append(sql_str(info1))
                elif col == 'Info2':
                    linha_valores.append(sql_str(info2))
                else:
                    # Pega do dicionário valores, se existir
                    linha_valores.append(sql_str(valores.get(col)))
            valores_linhas.append("(" + ", ".join(linha_valores) + ")")

        # Escrever todas as linhas separadas por vírgula
        f.write(",\n".join(valores_linhas))
        f.write(";\n\n-- Fim dos inserts\n")

    print(f"Arquivo gerado: {out_file}")

print("Processamento concluído.")