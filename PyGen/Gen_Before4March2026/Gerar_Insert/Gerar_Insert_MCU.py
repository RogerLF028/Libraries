import os
import csv
import re

# =============================================================================
# CONFIGURAÇÕES (Altere conforme necessário)
# =============================================================================
CSV_FILE = "simbolos_para_database_IC_Prog.csv"  # Nome do arquivo CSV (no mesmo diretório)
TABLE_NAME = "IC_Prog"                                    # Nome da tabela no banco de dados
OUTPUT_FILE = f"insert_{TABLE_NAME}.sql"                  # Arquivo SQL de saída
CREATED_BY = "Rogerio Fontanario"                         # Seu nome para o campo Created_By

# Prefixo do MyPN
MYPN_PREFIX = "EL-ICP-"
MYPN_DIGITS = 6

PREFIX_FOOTPRINT = "MyLib_"

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================
def add_prefix_to_footprint(footprint):
    """
    Adiciona o prefixo 'MyLib_' ao nome da biblioteca no footprint,
    se ainda não começar com ele.
    Exemplo: 'Package_SO:TSSOP-20_...' -> 'MyLib_Package_SO:TSSOP-20_...'
    """
    if not footprint or footprint == "~":
        return None
    if footprint.startswith(PREFIX_FOOTPRINT):
        return footprint
    # Separa a parte antes do primeiro ':'
    parts = footprint.split(':', 1)
    if len(parts) == 2:
        library = parts[0]
        rest = parts[1]
        return f"{PREFIX_FOOTPRINT}{library}:{rest}"
    else:
        return f"{PREFIX_FOOTPRINT}{footprint}"  # Caso não tenha ':', adiciona no início

def extract_package_from_footprint(footprint):
    """
    Extrai o tipo de encapsulamento do footprint.
    Exemplo: 'Package_QFP:TQFP-44_10x10mm_P0.8mm' -> 'TQFP-44'
    """
    if not footprint or footprint == "~":
        return None
    # Pega a parte após os dois pontos
    match = re.search(r':([^_]+)', footprint)
    if match:
        return match.group(1)
    return None

def extract_category_subcategory(symbol):
    """
    Extrai Category e Subcategory do campo Symbol.
    Exemplos:
      'CPLD_Altera:EPM1270F256' -> ('CPLD', 'Altera')
      'CPU:CDP1802ACE' -> ('CPU', None)
      'CPU_NXP_68000:MC68000FN' -> ('CPU', 'NXP_68000')
    """
    if not symbol:
        return None, None
    # Separa a parte antes dos dois pontos
    if ':' not in symbol:
        return None, None
    prefix = symbol.split(':', 1)[0]
    # Divide por underscore
    parts = prefix.split('_')
    if len(parts) == 1:
        return parts[0], None
    else:
        category = parts[0]
        subcategory = '_'.join(parts[1:])
        return category, subcategory

# =============================================================================
# LEITURA DO CSV E GERAÇÃO DOS INSERTS
# =============================================================================
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, CSV_FILE)
    output_path = os.path.join(script_dir, OUTPUT_FILE)

    # Verifica se o CSV existe
    if not os.path.isfile(csv_path):
        print(f"Erro: Arquivo {csv_path} não encontrado.")
        return

    # Lista para armazenar as linhas do INSERT
    values_lines = []
    mypn_counter = 1

    # Abre o CSV e processa
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Verifica se as colunas esperadas existem
        required_columns = ['Symbol', 'Value', 'Footprint', 'Description', 'Footprint_Filter', 'Datasheet']
        if not all(col in reader.fieldnames for col in required_columns):
            print("Erro: CSV não contém todas as colunas necessárias.")
            return

        for row in reader:
            value = row['Value'].strip()
            if not value:
                continue  # pula linhas sem valor

            # Extrai dados
            symbol = row['Symbol'].strip()
            footprint_orig = row['Footprint'].strip()
            footprint_filter = row['Footprint_Filter'].strip() if row['Footprint_Filter'] else None
            datasheet = row['Datasheet'].strip() if row['Datasheet'] else None
            description = row['Description'].strip() if row['Description'] else None

            # Aplica modificações no footprint
            footprint = add_prefix_to_footprint(footprint_orig) if footprint_orig and footprint_orig != "~" else None

            # Extrai package para Info1
            package = extract_package_from_footprint(footprint_orig) if footprint_orig else None
            info1 = package  # Info1 recebe o package (ex: TQFP-44)

            # Extrai categoria e subcategoria
            category, subcategory = extract_category_subcategory(symbol)

            # Gera MyPN
            mypn = f"{MYPN_PREFIX}{mypn_counter:06d}"
            mypn_counter += 1

            # Define campos padrão
            active = 1
            version = 1
            currency = "USD"
            stock_qty = 0
            min_stock = 0
            max_stock = 0

            # Lista de colunas e valores (apenas as que serão preenchidas)
            # As colunas não listadas ficarão NULL no INSERT (se omitidas, assumem NULL)
            # Mas precisamos incluir todas as colunas da tabela? Não, podemos listar apenas as que têm valor.
            # No SQL, se omitirmos colunas, elas recebem NULL (ou default). Vamos listar apenas as que preenchemos.
            columns = [
                "MyPN", "Name", "Description", "Value", "Info1",
                "Symbol", "Footprint", "Footprint_Filter", "Datasheet",
                "Manufacturer_PN", "Category", "Subcategory", "Package",
                "Active", "Version", "Stock_Qty", "Min_Stock", "Max_Stock", "Currency",
                "Created_At", "Created_By"
            ]

            # Valores correspondentes
            values = [
                mypn, value, description, value, info1,
                symbol, footprint, footprint_filter, datasheet,
                value, category, subcategory, package,
                active, version, stock_qty, min_stock, max_stock, currency,
                "datetime('now')", CREATED_BY
            ]

            # Converte para string SQL (escapando aspas simples)
            formatted_values = []
            for v in values:
                if v is None:
                    formatted_values.append("NULL")
                elif isinstance(v, int):
                    formatted_values.append(str(v))
                elif v == "datetime('now')":
                    formatted_values.append(v)
                else:
                    # Escapa aspas simples
                    v_escaped = str(v).replace("'", "''")
                    formatted_values.append(f"'{v_escaped}'")

            values_lines.append("(" + ", ".join(formatted_values) + ")")

    # Escreve o arquivo SQL
    if values_lines:
        header = f"INSERT INTO {TABLE_NAME} ({', '.join(columns)}) VALUES\n"
        body = ",\n".join(values_lines) + ";"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"-- Script de inserção para {TABLE_NAME}\n")
            f.write(f"-- Gerado a partir de: {CSV_FILE}\n\n")
            f.write(header)
            f.write(body)
            f.write("\n")
        print(f"Arquivo gerado: {output_path} com {len(values_lines)} inserts")
    else:
        print("Nenhum dado válido encontrado no CSV.")

if __name__ == "__main__":
    main()