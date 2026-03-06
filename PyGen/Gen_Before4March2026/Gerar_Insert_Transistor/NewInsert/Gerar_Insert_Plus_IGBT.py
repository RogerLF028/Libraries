import csv
import os
import re
from datetime import datetime

# Obtém o diretório onde este script está localizado
script_dir = os.path.dirname(os.path.abspath(__file__))

# Caminho completo para o arquivo CSV de entrada
csv_path = os.path.join(script_dir, 'lista_para_database_Transistor.csv')

# Mapeamento de prefixo do símbolo para (nome da tabela, subcategoria)
TABLE_MAP = {
    'Transistor_BJT:': ('Transistor_BJT', 'BJT'),
    'Transistor_FET:': ('Transistor_FET', 'FET'),
    'Transistor_FET_Other:': ('Transistor_FET', 'FET'),
    'Transistor_IGBT:': ('Transistor_IGBT', 'IGBT'),
}

# Lista de todas as tabelas que serão geradas
TABLES = ['Transistor_BJT', 'Transistor_FET', 'Transistor_IGBT', 'Transistor_General']

# Dicionário para armazenar as linhas de valores de cada tabela
table_values = {table: [] for table in TABLES}

# Dicionário para contadores de MyPN por tabela (inicia em 100000)
counters = {table: 100000 for table in TABLES}

# Função para escapar aspas simples
def escape_quotes(s):
    if s is None:
        return ''
    return s.replace("'", "''")

# Funções de extração de parâmetros elétricos
def extract_voltage(desc):
    # Padrão: número seguido de V, opcionalmente com Vce, Vds, Vgs
    pattern = r'(\d+(?:\.\d+)?)\s*V\s*(?:Vce|Vds|Vgs)?'
    match = re.search(pattern, desc, re.IGNORECASE)
    if match:
        return match.group(1) + 'V'
    return None

def extract_current(desc):
    # Padrão: número seguido de A, opcionalmente com Ic, Id
    pattern = r'(\d+(?:\.\d+)?)\s*A\s*(?:Ic|Id)?'
    match = re.search(pattern, desc, re.IGNORECASE)
    if match:
        return match.group(1) + 'A'
    return None

def extract_resistance(desc):
    # Padrão: número seguido de (m?Ohm|m?Ω) (opcionalmente com Ron/Rds)
    pattern = r'(\d+(?:\.\d+)?)\s*(m?)(Ohm|Ω)'
    match = re.search(pattern, desc, re.IGNORECASE)
    if match:
        value = match.group(1)
        prefix = match.group(2).lower()  # 'm' ou vazio
        if prefix == 'm':
            return value + 'mR'
        else:
            return value + 'R'
    return None

# Função para determinar o tipo do transistor (Info1) baseado nas tags e descrição
def get_transistor_type(tags, desc):
    tags_lower = tags.lower() if tags else ''
    desc_lower = desc.lower() if desc else ''
    
    # Verifica primeiro por tags específicas
    if 'nmos' in tags_lower or 'n-mos' in tags_lower or 'n-channel mosfet' in tags_lower:
        return 'MOSFET_N'
    if 'pmos' in tags_lower or 'p-mos' in tags_lower or 'p-channel mosfet' in tags_lower:
        return 'MOSFET_P'
    if 'njfet' in tags_lower or 'n-jfet' in tags_lower or 'n-channel jfet' in tags_lower:
        return 'JFET_N'
    if 'pjfet' in tags_lower or 'p-jfet' in tags_lower or 'p-channel jfet' in tags_lower:
        return 'JFET_P'
    if 'igbt' in tags_lower:
        # Verifica se tem N ou P (geralmente N)
        if 'n-igbt' in tags_lower or 'n channel' in desc_lower:
            return 'IGBT_N'
        else:
            return 'IGBT_N'  # Assume N como padrão
    if 'bjt' in tags_lower or 'transistor' in tags_lower:
        if 'npn' in tags_lower or 'npn' in desc_lower:
            return 'BJT_NPN'
        if 'pnp' in tags_lower or 'pnp' in desc_lower:
            return 'BJT_PNP'
        return 'BJT'
    
    # Se não achou nas tags, busca na descrição
    # MOSFET
    if 'n-channel mosfet' in desc_lower or 'n-channel power mosfet' in desc_lower or 'n-channel trenchmos' in desc_lower:
        return 'MOSFET_N'
    if 'p-channel mosfet' in desc_lower or 'p-channel power mosfet' in desc_lower:
        return 'MOSFET_P'
    
    # JFET – consideramos "n-channel fet" como JFET, desde que não seja claramente MOSFET
    if 'n-channel jfet' in desc_lower:
        return 'JFET_N'
    if 'p-channel jfet' in desc_lower:
        return 'JFET_P'
    # Se aparecer "n-channel fet" e não houver menção a "mosfet" nas tags ou descrição, assumimos JFET
    if 'n-channel fet' in desc_lower and 'mosfet' not in tags_lower and 'mosfet' not in desc_lower:
        return 'JFET_N'
    if 'p-channel fet' in desc_lower and 'mosfet' not in tags_lower and 'mosfet' not in desc_lower:
        return 'JFET_P'
    
    # BJT
    if 'npn' in desc_lower and ('transistor' in desc_lower or 'bjt' in desc_lower):
        return 'BJT_NPN'
    if 'pnp' in desc_lower and ('transistor' in desc_lower or 'bjt' in desc_lower):
        return 'BJT_PNP'
    
    # IGBT
    if 'igbt' in desc_lower:
        return 'IGBT_N'
    
    # Se ainda não achou, retorna None (será tratado depois)
    return None

# Abre o CSV
with open(csv_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    
    for row in reader:
        symbol = row['Symbol'].strip()
        value = row['Value'].strip()
        desc = row['Description'].strip()
        tags = row['Tags'].strip()
        footprint = row['Footprint'].strip()
        footprint_filter = row['Footprint_Filter'].strip()
        datasheet = row['Datasheet'].strip()

        # Determina a tabela de destino
        target_table = None
        subcategory = None
        for prefix, (table, sub) in TABLE_MAP.items():
            if symbol.startswith(prefix):
                target_table = table
                subcategory = sub
                break
        if target_table is None:
            target_table = 'Transistor_General'
            subcategory = 'General'

        # Incrementa o contador e gera o MyPN no formato EL-TRA-XXXXXX
        counters[target_table] += 1
        mypn = f"EL-TRA-{counters[target_table]:06d}"

        # Extrai parâmetros elétricos
        voltage = extract_voltage(desc)
        current = extract_current(desc)
        resistance = extract_resistance(desc)

        # Monta Info2: concatena os parâmetros encontrados
        info2_parts = []
        if voltage:
            info2_parts.append(voltage)
        if current:
            info2_parts.append(current)
        if resistance:
            info2_parts.append(resistance)
        info2 = ' '.join(info2_parts) if info2_parts else None

        # Determina Info1 (tipo)
        transistor_type = get_transistor_type(tags, desc)
        if transistor_type is None:
            # Fallback baseado na subcategoria da tabela
            if subcategory == 'BJT':
                transistor_type = 'BJT'
            elif subcategory == 'FET':
                transistor_type = 'FET'
            elif subcategory == 'IGBT':
                transistor_type = 'IGBT_N'
            else:
                transistor_type = 'TRANSISTOR'
        info1 = transistor_type

        # Monta os valores escapados (para strings)
        name = escape_quotes(value)
        description = escape_quotes(desc)
        symbol_esc = escape_quotes(symbol)
        footprint_esc = escape_quotes(footprint)
        footprint_filter_esc = escape_quotes(footprint_filter)
        datasheet_esc = escape_quotes(datasheet)
        created_by = 'Rogerio Fontanario'

        # Prepara os valores para SQL: strings entre aspas, NULL sem aspas
        def sql_value(val):
            if val is None:
                return 'NULL'
            return f"'{escape_quotes(val)}'"

        mypn_sql = sql_value(mypn)
        name_sql = sql_value(name)
        description_sql = sql_value(description)
        symbol_sql = sql_value(symbol_esc)
        footprint_sql = sql_value(footprint_esc)
        footprint_filter_sql = sql_value(footprint_filter_esc)
        datasheet_sql = sql_value(datasheet_esc)
        category_sql = "'Transistor'"
        subcategory_sql = sql_value(subcategory)
        info1_sql = sql_value(info1)
        info2_sql = sql_value(info2)
        created_by_sql = sql_value(created_by)

        # Cria a tupla de valores para o INSERT
        values_tuple = f"({mypn_sql}, {name_sql}, {description_sql}, {symbol_sql}, {footprint_sql}, {footprint_filter_sql}, {datasheet_sql}, {category_sql}, {subcategory_sql}, {info1_sql}, {info2_sql}, datetime('now'), {created_by_sql}, 1, 1, 0, 'USD')"
        
        table_values[target_table].append(values_tuple)

# Gera os arquivos de saída com um único INSERT por tabela
for table in TABLES:
    if not table_values[table]:
        continue  # Se não houver registros, não cria arquivo
    
    # Define o nome do arquivo de saída
    if table == 'Transistor_BJT':
        output_file = os.path.join(script_dir, 'insert_bjt.sql')
    elif table == 'Transistor_FET':
        output_file = os.path.join(script_dir, 'insert_fet.sql')
    elif table == 'Transistor_IGBT':
        output_file = os.path.join(script_dir, 'insert_igbt.sql')
    else:  # Transistor_General
        output_file = os.path.join(script_dir, 'insert_general.sql')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('-- Script gerado em {}\n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        f.write('-- Created by Rogerio Fontanario\n\n')
        
        f.write(f"INSERT INTO {table} (\n")
        f.write("    MyPN, Name, Description, Symbol, Footprint, Footprint_Filter, Datasheet,\n")
        f.write("    Category, Subcategory, Info1, Info2, Created_At, Created_By,\n")
        f.write("    Active, Version, Stock_Qty, Currency\n")
        f.write(") VALUES\n")
        
        # Escreve todas as linhas separadas por vírgula
        for i, values in enumerate(table_values[table]):
            if i == len(table_values[table]) - 1:
                f.write(f"    {values};\n")  # Última linha termina com ponto e vírgula
            else:
                f.write(f"    {values},\n")
        
        f.write("\n-- Fim do script\n")

print("Arquivos SQL gerados com sucesso!")