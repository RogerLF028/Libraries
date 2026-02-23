import csv
import os
import re
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, "Relay.csv")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "insert_relay.sql")

# Lista completa das colunas da tabela Relay
COLUNAS = [
    'MyPN', 'Name', 'Description', 'Value', 'Info1', 'Info2',
    'Symbol', 'Footprint', 'Footprint_Filter', 'Datasheet', 'Notes',
    'Notes_to_Buyer', 'Manufacturer', 'Manufacturer_PN', 'Manufacturer_URL',
    'Alternative_PN', 'Alternative_URL', 'Digikey_PN', 'Digikey_URL',
    'Mouser_PN', 'Mouser_URL', 'LCSC_PN', 'LCSC_URL',
    'Active', 'Version', 'Created_At', 'Created_By', 'Modified_At', 'Modified_By',
    'Exclude_from_BOM', 'Exclude_from_Board', 'Category', 'Subcategory',
    'Family_Series', 'Package', 'Mount', 'Dimensions', 'Temperature_Range',
    'REACH_Compliant', 'RoHS_Compliant',
    'Coil_Voltage', 'Coil_Resistance', 'Contact_Configuration',
    'Contact_Current_Rating', 'Contact_Voltage_Rating', 'Relay_Type',
]

# ==================== FUNÇÕES AUXILIARES ====================
def sql_str(val):
    if val is None:
        return 'NULL'
    return "'" + str(val).replace("'", "''") + "'"

def get_val(row, key):
    val = row.get(key, '').strip()
    return val if val != '' else None

def extract_type_from_name(name):
    """Extrai o tipo (PowerRelay, SignalRelay, etc.) da primeira palavra do Name original."""
    if not name:
        return "Relay"
    parts = name.split('_')
    return parts[0] if parts else "Relay"

def clean_contact_form(contact_form):
    """
    Remove qualquer texto entre parênteses e retorna apenas a parte principal.
    Ex: "DPDT (2 Form C)" -> "DPDT"
    """
    if not contact_form:
        return ''
    # Remove tudo que está entre parênteses, inclusive os parênteses
    cleaned = re.sub(r'\s*\([^)]*\)', '', contact_form).strip()
    return cleaned



def clean_coil_voltage(coil_voltage):
    """
    Formata a string de tensão da bobina:
    - Remove espaços.
    - Se houver um número decimal (ex: 4.5), substitui o ponto por 'V' e junta com o restante.
    - Se não houver decimal, apenas remove espaços.
    Exemplos:
        "4.5V DC"   -> "4V5DC"
        "12V DC"    -> "12VDC"
        "24V AC"    -> "24VAC"
        "5V"        -> "5V"
    """
    if not coil_voltage:
        return ''
    # Remove espaços primeiro para facilitar
    s = coil_voltage.replace(' ', '')
    # Procura por padrão: número (com possível ponto decimal) seguido de letras
    # Ex: "4.5VDC" -> grupos: ('4.5', 'VDC')
    match = re.match(r'^(\d*\.?\d+)([A-Za-z].*)$', s)
    if match:
        num_str, rest = match.groups()
        if '.' in num_str:
            # Divide parte inteira e decimal
            int_part, dec_part = num_str.split('.')
            # Monta novo formato: inteiro + 'V' + decimal + restante
            # (o 'V' original já está em 'rest', então precisamos remover o primeiro V de rest? Não, porque rest começa com V)
            # Ex: "4.5VDC" -> num_str="4.5", rest="VDC". Queremos "4V5DC". O 'V' original está em rest, então usamos int_part + 'V' + dec_part + rest[1:]?
            # Mas cuidado: rest pode ser "VDC", "VAC", etc. O primeiro caractere é 'V'. Precisamos remover esse 'V' para não duplicar.
            if rest.startswith('V'):
                # Remove o primeiro V para depois adicionar o nosso
                rest_sem_v = rest[1:]
                return f"{int_part}V{dec_part}{rest_sem_v}"
            else:
                # Caso raro: se não começar com V, apenas concatena
                return f"{int_part}V{dec_part}{rest}"
        else:
            # Sem ponto decimal: retorna a string sem espaços (já feito)
            return s
    else:
        # Se não encaixar no padrão, retorna a string sem espaços
        return s


def extrair_float_de_corrente(valor_str):
    """
    Extrai o valor numérico (float) de uma string contendo uma corrente,
    como '2.5A' ou '0.25A'. Remove a unidade e converte para float.
    Retorna None se nenhum número for encontrado.
    """
    if not valor_str or not isinstance(valor_str, str):
        return None
    # Expressão regular para capturar o primeiro número decimal
    # Aceita sinal opcional, parte inteira e/ou fracionária
    padrao = r"[-+]?\d*\.?\d+"
    match = re.search(padrao, valor_str)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None

def format_current(valstr):
    """Formata o valor da corrente para o nome, com mA para valores <1A e substituição do ponto por A para >=1A."""
    val = extrair_float_de_corrente(valstr)

    try:
        f = float(val)
        if f < 1.0:
            # Converte para mA
            ma = int(round(f * 1000))
            return f"{ma}mA"
        else:
            if f.is_integer():
                return f"{int(f)}A"
            else:
                # Converter para string sem zeros extras, substituir ponto por A
                s = f"{f:.3f}".rstrip('0').rstrip('.')
                if '.' in s:
                    return s.replace('.', 'A')
                else:
                    return f"{s}A"
    except:
        return str(val)

def format_temperature_range(min_temp, max_temp):
    if min_temp and max_temp:
        return f"{min_temp} to {max_temp}"
    return None

def prefix_footprint(fp):
    if fp:
        return "MyLib_" + fp
    return None

# ==================== LEITURA E PROCESSAMENTO ====================
if not os.path.exists(CSV_FILE):
    print(f"ERRO: Arquivo CSV não encontrado: {CSV_FILE}")
    exit(1)

todas_linhas = []
colunas_presentes = set()

with open(CSV_FILE, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        valores = {}

        # Mapeamento direto
        mapeamento_direto = {
            'MyPN': 'MyPN',
            'Description': 'Description',
            'Symbol': 'Symbol',
            'Footprint_Filter': 'Footprint_Filter',
            'Datasheet': 'Datasheet',
            'Notes': 'Notes',
            'Manufacturer': 'Manufacturer',
            'Manufacturer_PN': 'Manufacturer_PN',
            'Alternative_PN': 'Alternative_PN',
            'LCSC_PN': 'LCSC_PN',
            'LCSC_URL': 'LCSC_URL',
            'Mouser_PN': 'Mouser_PN',
            'Mouser_URL': 'Mouser_URL',
            'Digikey_PN': 'Digikey_PN',
            'Digikey_URL': 'Digikey_URL',
            'Category': 'Category',
            'Subcategory': 'Subcategory',
            'Series': 'Family_Series',
            'Package': 'Package',
            'Mount': 'Mount',
            'Dimensions': 'Dimensions',
            'RoHS_Compliant': 'RoHS_Compliant',
            'REACH_Compliant': 'REACH_Compliant',
            'Coil_Resistance': 'Coil_Resistance',
            'Contact_Current': 'Contact_Current_Rating',
            'Contact_Voltage': 'Contact_Voltage_Rating',
            'Type': 'Relay_Type',
        }
        for csv_col, tab_col in mapeamento_direto.items():
            v = get_val(row, csv_col)
            if v is not None:
                valores[tab_col] = v

        # --- Tratamento de Contact_Form (original no CSV) ---
        raw_contact_form = get_val(row, 'Contact_Form')
        cleaned_contact_form = clean_contact_form(raw_contact_form) if raw_contact_form else ''
        # Guardar no banco como Contact_Configuration (sem parenteses)
        if cleaned_contact_form:
            valores['Contact_Configuration'] = cleaned_contact_form

        # --- Tratamento de Coil_Voltage ---
        raw_coil_voltage = get_val(row, 'Coil_Voltage')
        cleaned_coil_voltage = clean_coil_voltage(raw_coil_voltage) if raw_coil_voltage else ''
        if cleaned_coil_voltage:
            valores['Coil_Voltage'] = cleaned_coil_voltage

        # --- Value = Manufacturer_PN (coluna Value do CSV) ---
        manufacturer_pn = get_val(row, 'Value')
        if manufacturer_pn:
            valores['Value'] = manufacturer_pn

        # --- Name: Tipo + "_" + Contact_Form (limpo) + "_" + Coil_Voltage (limpo) + "_" + Contact_Current_Rating + "_" + Value ---
        original_name = get_val(row, 'Name')
        tipo = extract_type_from_name(original_name)
        contact_current = get_val(row, 'Contact_Current') or ''
        print(f"Contact Current: {contact_current}")
        I_contact = format_current(contact_current)
        name_parts = [tipo, cleaned_contact_form, cleaned_coil_voltage, I_contact, ]
        name_parts = [p for p in name_parts if p]  # remove vazios
        if name_parts:
            valores['Name'] = '_'.join(name_parts)

        # --- Info1: Coil_Voltage, Contact_Current, Contact_Voltage (concatenados com espaço) ---
        info1_parts = []
        if cleaned_coil_voltage:
            info1_parts.append(cleaned_coil_voltage)
        if contact_current:
            info1_parts.append(contact_current)
        contact_voltage = get_val(row, 'Contact_Voltage')
        if contact_voltage:
            info1_parts.append(contact_voltage)
        if info1_parts:
            valores['Info1'] = ' '.join(info1_parts)

        # --- Info2 = Contact_Form limpo ---
        if cleaned_contact_form:
            valores['Info2'] = cleaned_contact_form

        # --- Footprint com prefixo ---
        fp_original = get_val(row, 'Footprint')
        if fp_original:
            valores['Footprint'] = prefix_footprint(fp_original)

        # --- Temperature_Range ---
        min_temp = get_val(row, 'MinTemp')
        max_temp = get_val(row, 'MaxTemp')
        temp_range = format_temperature_range(min_temp, max_temp)
        if temp_range:
            valores['Temperature_Range'] = temp_range

        # Campos padrão
        valores['Active'] = 1
        valores['Version'] = 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        valores['Created_At'] = now
        valores['Created_By'] = "Rogerio Fontanario"
        valores['Modified_At'] = now
        valores['Modified_By'] = "Rogerio Fontanario"
        valores['Exclude_from_BOM'] = 0
        valores['Exclude_from_Board'] = 0

        # Remover chaves com valor None
        valores = {k: v for k, v in valores.items() if v is not None}

        colunas_presentes.update(valores.keys())
        todas_linhas.append(valores)

# ==================== DETERMINAR COLUNAS FINAIS ====================
colunas_finais = [col for col in COLUNAS if col in colunas_presentes]

print(f"Colunas a serem inseridas ({len(colunas_finais)}): {colunas_finais}")

# ==================== GERAÇÃO DO INSERT ÚNICO ====================
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(f"-- Inserções para a tabela Relay\n")
    f.write(f"-- Gerado em {datetime.now()}\n\n")
    f.write(f"INSERT INTO Relay (\n")
    f.write("    " + ",\n    ".join(colunas_finais) + "\n")
    f.write(") VALUES\n")

    linhas_sql = []
    for valores in todas_linhas:
        linha_valores = [sql_str(valores.get(col)) for col in colunas_finais]
        linhas_sql.append("(" + ", ".join(linha_valores) + ")")

    f.write(",\n".join(linhas_sql))
    f.write(";\n\n-- Fim dos inserts\n")

print(f"Arquivo SQL gerado: {OUTPUT_FILE}")
print(f"Total de inserts: {len(todas_linhas)}")