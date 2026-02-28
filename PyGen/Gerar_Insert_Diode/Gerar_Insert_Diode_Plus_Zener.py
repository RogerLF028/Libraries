import os
import re
from datetime import datetime

# Configurações
script_dir = os.path.dirname(os.path.abspath(__file__))
input_sql = os.path.join(script_dir, 'insert_diode_zener.sql')
output_sql = os.path.join(script_dir, 'insert_diode_zener_BZT52H.sql')

# Lista completa dos tipos BZT52H (extraída da tabela de marcação do datasheet)
tipos_bzt52h = [
    # Série B
    'BZT52H-B2V4', 'BZT52H-B2V7', 'BZT52H-B3V0', 'BZT52H-B3V3', 'BZT52H-B3V6',
    'BZT52H-B3V9', 'BZT52H-B4V3', 'BZT52H-B4V7', 'BZT52H-B5V1', 'BZT52H-B5V6',
    'BZT52H-B6V2', 'BZT52H-B6V8', 'BZT52H-B7V5', 'BZT52H-B8V2', 'BZT52H-B9V1',
    'BZT52H-B10', 'BZT52H-B11', 'BZT52H-B12', 'BZT52H-B13', 'BZT52H-B15',
    'BZT52H-B16', 'BZT52H-B18', 'BZT52H-B20', 'BZT52H-B22', 'BZT52H-B24',
    'BZT52H-B27', 'BZT52H-B30', 'BZT52H-B33', 'BZT52H-B36', 'BZT52H-B39',
    'BZT52H-B43', 'BZT52H-B47', 'BZT52H-B51', 'BZT52H-B56', 'BZT52H-B62',
    'BZT52H-B68', 'BZT52H-B75',
    # Série C
    'BZT52H-C2V4', 'BZT52H-C2V7', 'BZT52H-C3V0', 'BZT52H-C3V3', 'BZT52H-C3V6',
    'BZT52H-C3V9', 'BZT52H-C4V3', 'BZT52H-C4V7', 'BZT52H-C5V1', 'BZT52H-C5V6',
    'BZT52H-C6V2', 'BZT52H-C6V8', 'BZT52H-C7V5', 'BZT52H-C8V2', 'BZT52H-C9V1',
    'BZT52H-C10', 'BZT52H-C11', 'BZT52H-C12', 'BZT52H-C13', 'BZT52H-C15',
    'BZT52H-C16', 'BZT52H-C18', 'BZT52H-C20', 'BZT52H-C22', 'BZT52H-C24',
    'BZT52H-C27', 'BZT52H-C30', 'BZT52H-C33', 'BZT52H-C36', 'BZT52H-C39',
    'BZT52H-C43', 'BZT52H-C47', 'BZT52H-C51', 'BZT52H-C56', 'BZT52H-C62',
    'BZT52H-C68', 'BZT52H-C75'
]

# Funções auxiliares
def extrair_tensao(nome):
    """Extrai o valor numérico da tensão a partir do nome do tipo."""
    suffix = nome.replace('BZT52H-', '')
    valor_str = suffix[1:]  # remove a letra B ou C
    if 'V' in valor_str:
        partes = valor_str.split('V')
        if len(partes) == 2 and partes[1]:
            return float(partes[0]) + float(partes[1]) / 10.0
        return float(partes[0])
    return float(valor_str)

def formatar_info1(tensao_float):
    """Formata a tensão no estilo '2V4' ou '10V'."""
    if tensao_float.is_integer():
        return f"{int(tensao_float)}V"
    inteiro = int(tensao_float)
    decimal = int(round((tensao_float - inteiro) * 10))
    return f"{inteiro}V{decimal}"

def escape_quotes(s):
    if s is None:
        return ''
    return s.replace("'", "''")

# Descobrir o último MyPN usado
ultimo_numero = 200104
if os.path.exists(input_sql):
    with open(input_sql, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(r"EL-DIO-(\d{6})", content)
        if matches:
            ultimo_numero = max(int(m) for m in matches)
print(f"Último MyPN encontrado: EL-DIO-{ultimo_numero:06d}")

# Dados fixos para todos os componentes
POTENCIA = '830mW'
SIMBOLO = 'MyLib_Diode:D_Zener'
FOOTPRINT = 'MyLib_Diode_SMD:D_SOD-123F'
FOOTPRINT_FILTER = 'SOD?123F*'
DATASHEET = 'https://assets.nexperia.com/documents/data-sheet/BZT52H_SER.pdf'
FABRICANTE = 'Nexperia'
CATEGORIA = 'Semiconductors'
SUBCATEGORIA = 'Diodes'
PACKAGE = 'SOD-123F'
MOUNT = 'SMD'
DIMENSIONS = '2.6mm x 1.6mm'
TEMP_RANGE = '-65°C to 150°C'
FORWARD_VOLTAGE = '0.9V'
CREATED_BY = 'System'
CREATED_AT = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Lista para armazenar as linhas de valores
linhas = []
contador = ultimo_numero + 1

for tipo in tipos_bzt52h:
    tensao_float = extrair_tensao(tipo)
    tensao_str = f"{tensao_float:.1f}V".replace('.0V', 'V')
    info1 = formatar_info1(tensao_float)

    mypn = f"EL-DIO-{contador:06d}"
    name = tipo
    description = f"Zener Diode {tensao_str} {POTENCIA} SOD-123F"
    value = tipo
    manufacturer_pn = tipo

    # Escapar strings
    name_esc = escape_quotes(name)
    description_esc = escape_quotes(description)
    value_esc = escape_quotes(value)
    info1_esc = escape_quotes(info1)
    info2_esc = escape_quotes(POTENCIA)
    fabricante_esc = escape_quotes(FABRICANTE)
    manufacturer_pn_esc = escape_quotes(manufacturer_pn)
    category_esc = escape_quotes(CATEGORIA)
    subcategory_esc = escape_quotes(SUBCATEGORIA)
    package_esc = escape_quotes(PACKAGE)
    mount_esc = escape_quotes(MOUNT)
    dimensions_esc = escape_quotes(DIMENSIONS)
    temp_range_esc = escape_quotes(TEMP_RANGE)
    forward_voltage_esc = escape_quotes(FORWARD_VOLTAGE)
    power_dissipation_esc = escape_quotes(POTENCIA)
    zener_voltage_esc = escape_quotes(tensao_str)
    created_by_esc = escape_quotes(CREATED_BY)

    # Montar a lista de valores (apenas colunas preenchidas)
    valores = [
        f"'{mypn}'",
        f"'{name_esc}'",
        f"'{description_esc}'",
        f"'{value_esc}'",
        f"'{info1_esc}'",
        f"'{info2_esc}'",
        f"'{SIMBOLO}'",
        f"'{FOOTPRINT}'",
        f"'{FOOTPRINT_FILTER}'",
        f"'{DATASHEET}'",
        f"'{fabricante_esc}'",
        f"'{manufacturer_pn_esc}'",
        '1',                               # Active
        f"'{CREATED_AT}'",
        f"'{created_by_esc}'",
        '0',                               # Exclude_from_BOM
        '0',                               # Exclude_from_Board
        f"'{category_esc}'",
        f"'{subcategory_esc}'",
        f"'{package_esc}'",
        f"'{mount_esc}'",
        f"'{dimensions_esc}'",
        f"'{forward_voltage_esc}'",
        f"'{power_dissipation_esc}'",
        f"'{temp_range_esc}'",
        f"'{zener_voltage_esc}'"
    ]

    linhas.append("    (" + ", ".join(valores) + ")")
    contador += 1

# Escrever o arquivo SQL
with open(output_sql, 'w', encoding='utf-8') as f:
    f.write(f"-- Inserções para diodos Zener BZT52H (séries B e C)\n")
    f.write(f"-- Gerado em {CREATED_AT}\n\n")
    f.write(f"INSERT INTO Diode_Zener (\n")
    f.write(f"    MyPN, Name, Description, Value, Info1, Info2,\n")
    f.write(f"    Symbol, Footprint, Footprint_Filter, Datasheet,\n")
    f.write(f"    Manufacturer, Manufacturer_PN,\n")
    f.write(f"    Active, Created_At, Created_By,\n")
    f.write(f"    Exclude_from_BOM, Exclude_from_Board,\n")
    f.write(f"    Category, Subcategory, Package, Mount, Dimensions,\n")
    f.write(f"    Forward_Voltage, Power_Dissipation, Temperature_Range,\n")
    f.write(f"    Zener_Voltage\n")
    f.write(f") VALUES\n")
    f.write(",\n".join(linhas))
    f.write(";\n\n")
    f.write("-- Fim dos inserts\n")

print(f"Arquivo gerado: {output_sql} com {len(linhas)} inserts.")