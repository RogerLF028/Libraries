import os
import csv
import re

# =============================================================================
# CONFIGURAÇÕES (Altere conforme necessário)
# =============================================================================
CSV_FILE = "simbolos_para_database_IC_Other.csv"  # Nome do arquivo CSV
TABLE_NAME = "IC_Other"                                    # Nome da tabela
OUTPUT_FILE = f"insert_{TABLE_NAME}.sql"                  # Arquivo SQL de saída
CREATED_BY = "Rogerio Fontanario"                         # Seu nome

# Prefixo do MyPN (único para toda a tabela)
MYPN_PREFIX = "EL-ICX-"
MYPN_DIGITS = 6

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================
def add_prefix_to_footprint(footprint):
    """
    Adiciona o prefixo 'MyLib_' ao nome da biblioteca no footprint,
    se ainda não começar com ele.
    Exemplo: 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm' -> 'MyLib_Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'
    """
    if not footprint or footprint == "~":
        return None
    if footprint.startswith("MyLib_"):
        return footprint
    parts = footprint.split(':', 1)
    if len(parts) == 2:
        library = parts[0]
        rest = parts[1]
        return f"MyLib_{library}:{rest}"
    else:
        return f"MyLib_{footprint}"

def extract_package_from_footprint(footprint):
    """
    Extrai o tipo de encapsulamento do footprint, procurando por padrões como 'TQFP-44', 'SOIC-8', etc.
    Exemplo: 'Package_QFP:TQFP-44_10x10mm_P0.8mm' -> 'TQFP-44'
    """
    if not footprint or footprint == "~":
        return None
    # Pega a parte após os dois pontos
    match = re.search(r':(.+)', footprint)
    if not match:
        return None
    rest = match.group(1)
    # Procura por padrão de encapsulamento: letras maiúsculas seguidas de hífen e números
    # Ex: TQFP-44, SOIC-8, LQFP-64, etc.
    pkg_match = re.search(r'([A-Z]{2,}-\d+)', rest)
    if pkg_match:
        return pkg_match.group(1)
    # Se não encontrar, tenta um padrão mais genérico (ex: DIP-8, QFN-16)
    pkg_match = re.search(r'([A-Z]+-\d+)', rest)
    if pkg_match:
        return pkg_match.group(1)
    # Fallback: pegar a parte antes do primeiro underscore
    parts = rest.split('_')
    if parts:
        # Às vezes o primeiro elemento é o fabricante, então pegar o segundo?
        # Ex: "Infineon_PQFN-44-31-5EP" -> o segundo é "PQFN-44-31-5EP"
        if len(parts) > 1:
            # Tenta extrair novamente do segundo elemento
            second = parts[1]
            pkg_match = re.search(r'([A-Z]+-\d+)', second)
            if pkg_match:
                return pkg_match.group(1)
        return parts[0]  # último recurso
    return None

def extract_category_subcategory(symbol):
    """
    Extrai Category e Subcategory do campo Symbol.
    Exemplos:
      'Amplifier_Audio:IR4302' -> ('Amplifier', 'Audio')
      'Analog_ADC:AD574A' -> ('Analog', 'ADC')
      'Audio:AD1853' -> ('Audio', None)
    """
    if not symbol or ':' not in symbol:
        return None, None
    prefix = symbol.split(':', 1)[0]
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

    if not os.path.isfile(csv_path):
        print(f"Erro: Arquivo {csv_path} não encontrado.")
        return

    values_lines = []
    mypn_counter = 1

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        required_columns = ['Symbol', 'Value', 'Footprint', 'Description', 'Footprint_Filter', 'Datasheet']
        if not all(col in reader.fieldnames for col in required_columns):
            print("Erro: CSV não contém todas as colunas necessárias.")
            return

        for row in reader:
            value = row['Value'].strip()
            if not value:
                continue

            symbol = row['Symbol'].strip()
            footprint_orig = row['Footprint'].strip()
            footprint_filter = row['Footprint_Filter'].strip() if row['Footprint_Filter'] else None
            datasheet = row['Datasheet'].strip() if row['Datasheet'] else None
            description = row['Description'].strip() if row['Description'] else None

            # Modifica o footprint
            footprint = add_prefix_to_footprint(footprint_orig) if footprint_orig and footprint_orig != "~" else None

            # Extrai package para Info1
            package = extract_package_from_footprint(footprint_orig) if footprint_orig else None
            info1 = package  # Info1 recebe o package

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

            # Colunas que serão preenchidas (as demais ficam NULL)
            columns = [
                "MyPN", "Name", "Description", "Value", "Info1",
                "Symbol", "Footprint", "Footprint_Filter", "Datasheet",
                "Manufacturer_PN", "Category", "Subcategory", "Package",
                "Active", "Version", "Stock_Qty", "Min_Stock", "Max_Stock", "Currency",
                "Created_At", "Created_By"
            ]

            values = [
                mypn, value, description, value, info1,
                symbol, footprint, footprint_filter, datasheet,
                value, category, subcategory, package,
                active, version, stock_qty, min_stock, max_stock, currency,
                "datetime('now')", CREATED_BY
            ]

            # Formata para SQL
            formatted = []
            for v in values:
                if v is None:
                    formatted.append("NULL")
                elif isinstance(v, int):
                    formatted.append(str(v))
                elif v == "datetime('now')":
                    formatted.append(v)
                else:
                    v_escaped = str(v).replace("'", "''")
                    formatted.append(f"'{v_escaped}'")

            values_lines.append("(" + ", ".join(formatted) + ")")

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