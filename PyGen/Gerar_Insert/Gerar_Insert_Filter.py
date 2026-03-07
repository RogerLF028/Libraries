import csv
import os
import re

# Mapeamento dos arquivos para os nomes das tabelas e prefixos
ARQUIVOS = [
    ('database_for_Filter.csv', 'Filter', 'FLT'),
    ('database_for_Oscillator.csv', 'Oscillator', 'OSC'),
    ('database_for_Mechanical.csv', 'Mechanical', 'MEC'),
    ('database_for_Switch.csv', 'Switch', 'SWI')
]

# Colunas que serão inseridas na tabela (exceto Info1 que é condicional)
COLUNAS_FIXAS = [
    'MyPN', 'Name', 'Description', 'Value', 'Symbol',
    'Footprint', 'Footprint_Filter', 'Datasheet', 'Notes',
    'Active', 'Version'
]

# Coluna Info1 só será incluída para Oscillator
COLUNAS_OSC = COLUNAS_FIXAS + ['Info1']

def escape_sql(valor):
    """Escapa aspas simples e trata nulos."""
    if valor is None or valor == '':
        return 'NULL'
    # Substitui aspas simples por duas aspas simples
    return "'" + str(valor).replace("'", "''") + "'"

def extrair_frequencia(texto):
    """Extrai frequência (ex: 10MHz, 32.768kHz) do texto."""
    if not texto:
        return None
    # Padrão: número (com ponto) + espaço opcional + Hz (com prefixo k, M, G)
    padrao = r'(\d+(?:\.\d+)?)\s*([kMGT]?Hz)\b'
    match = re.search(padrao, texto, re.IGNORECASE)
    if match:
        return match.group(1) + match.group(2).upper()
    return None

def processar_arquivo(caminho, tabela, prefixo):
    """Lê o CSV e retorna uma lista de tuplas com os valores para INSERT."""
    dados = []
    try:
        with open(caminho, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            # Verifica se as colunas esperadas estão presentes
            expected = {'Symbol', 'Value', 'Footprint', 'Description', 'Tags', 'Footprint_Filter', 'Datasheet'}
            if not expected.issubset(reader.fieldnames):
                print(f"Aviso: {caminho} não contém todas as colunas esperadas. Colunas encontradas: {reader.fieldnames}")

            for i, row in enumerate(reader, start=1):
                # Gerar MyPN sequencial com 6 dígitos
                mypn = f"EL-{prefixo}-{i:06d}"

                # Campos base
                name = row.get('Value', '')
                description = row.get('Description', '')
                value = row.get('Value', '')
                symbol = row.get('Symbol', '')
                footprint = row.get('Footprint', '')
                footprint_filter = row.get('Footprint_Filter', '')
                datasheet = row.get('Datasheet', '')
                notes = row.get('Tags', '')

                # Escapar todos os textos
                valores = [
                    escape_sql(mypn),
                    escape_sql(name),
                    escape_sql(description),
                    escape_sql(value),
                    escape_sql(symbol),
                    escape_sql(footprint),
                    escape_sql(footprint_filter),
                    escape_sql(datasheet),
                    escape_sql(notes),
                    '1',  # Active
                    '1'   # Version
                ]

                # Se for Oscillator, extrair Info1
                if tabela == 'Oscillator':
                    # Tenta extrair da descrição, depois do value
                    freq = extrair_frequencia(description)
                    if not freq:
                        freq = extrair_frequencia(value)
                    info1 = escape_sql(freq) if freq else 'NULL'
                    valores.append(info1)
                    colunas = COLUNAS_OSC
                else:
                    colunas = COLUNAS_FIXAS

                dados.append((colunas, valores))
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado: {caminho}")
    except Exception as e:
        print(f"Erro ao processar {caminho}: {e}")
    return dados

def localizar_arquivo(nome_arquivo):
    """
    Tenta localizar o arquivo no diretório atual ou no diretório do script.
    Retorna o caminho completo se encontrado, caso contrário None.
    """
    # Primeiro, verifica no diretório atual
    if os.path.exists(nome_arquivo):
        return os.path.abspath(nome_arquivo)
    # Se não, tenta no diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_script = os.path.join(script_dir, nome_arquivo)
    if os.path.exists(caminho_script):
        return os.path.abspath(caminho_script)
    return None

def gerar_sql(arquivo_saida='insert_components.sql'):
    """
    Gera o arquivo SQL no mesmo diretório do script (ou onde os CSVs estão).
    Se um caminho absoluto for passado, usa esse; caso contrário, junta com o diretório do script.
    """
    # Determina o diretório base (onde o script está)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Se arquivo_saida não for um caminho absoluto, junta com script_dir
    if not os.path.isabs(arquivo_saida):
        caminho_saida = os.path.join(script_dir, arquivo_saida)
    else:
        caminho_saida = arquivo_saida

    with open(caminho_saida, 'w', encoding='utf-8') as out:
        for nome_arquivo, tabela, prefixo in ARQUIVOS:
            caminho_csv = localizar_arquivo(nome_arquivo)
            if caminho_csv is None:
                print(f"Arquivo não encontrado: {nome_arquivo} (procurou no diretório atual e no diretório do script)")
                continue

            print(f"Processando {caminho_csv} -> tabela {tabela}")
            registros = processar_arquivo(caminho_csv, tabela, prefixo)

            if not registros:
                print(f"Nenhum registro válido em {nome_arquivo}")
                continue

            # Pega as colunas do primeiro registro (todas iguais)
            colunas, primeiro = registros[0]
            colunas_str = ', '.join(colunas)

            # Escreve o cabeçalho do INSERT
            out.write(f"INSERT INTO {tabela} ({colunas_str}) VALUES\n")

            # Escreve as linhas de valores
            linhas_valores = []
            for _, vals in registros:
                linha = '(' + ', '.join(vals) + ')'
                linhas_valores.append(linha)

            out.write(',\n'.join(linhas_valores))
            out.write(';\n\n')

        print(f"Arquivo SQL gerado em: {caminho_saida}")

if __name__ == '__main__':
    gerar_sql()