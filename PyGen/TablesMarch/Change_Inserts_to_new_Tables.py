import re
import os

COLUNAS_DESTINO = [
    'ID_Aux', 'MyPN', 'Name', 'Description', 'Value', 'Info1', 'Info2',
    'Symbol', 'Footprint', 'Footprint_Filter', 'Datasheet', 'Category',
    'Subcategory', 'Family_Series', 'Package', 'Mount', 'Dimensions',
    'Temperature_Range', 'REACH_Compliant', 'RoHS_Compliant', 'Notes',
    'Notes_to_Buyer', 'Manufacturer', 'Manufacturer_PN', 'Manufacturer_URL',
    'Alternative_PN', 'Alternative_URL', 'Digikey_PN', 'Digikey_URL',
    'Mouser_PN', 'Mouser_URL', 'LCSC_PN', 'LCSC_URL', 'Stock_Qty',
    'Stock_Location', 'Stock_Unit', 'Price', 'Currency', 'Min_Stock',
    'Max_Stock', 'Last_Purchase_Date', 'Last_Purchase_Price', 'Active',
    'Version', 'Created_At', 'Created_By', 'Modified_At', 'Modified_By',
    'Exclude_from_BOM', 'Exclude_from_Board'
]

def extrair_nome_e_colunas(linha):
    padrao = r'INSERT INTO "([^"]+)" \(([^)]+)\) VALUES'
    match = re.match(padrao, linha.strip())
    if match:
        tabela = match.group(1)
        colunas = [c.strip().strip('"') for c in match.group(2).split(',')]
        return tabela, colunas
    return None, None

def parse_valores(linha):
    """Recebe uma linha de valores e retorna lista de strings."""
    linha = linha.strip()
    if linha.startswith('('):
        linha = linha[1:]
    if linha.endswith('),'):
        linha = linha[:-2]
    elif linha.endswith(');'):
        linha = linha[:-2]
    elif linha.endswith(')'):
        linha = linha[:-1]

    valores = []
    atual = []
    entre_aspas = False
    escape = False

    for ch in linha:
        if ch == "'" and not escape:
            entre_aspas = not entre_aspas
            atual.append(ch)
        elif ch == '\\' and entre_aspas:
            escape = True
            atual.append(ch)
        else:
            if escape:
                escape = False
            if ch == ',' and not entre_aspas:
                valores.append(''.join(atual).strip())
                atual = []
            else:
                atual.append(ch)
    if atual:
        valores.append(''.join(atual).strip())
    return valores

def processar_arquivo(entrada, saida):
    with open(entrada, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    i = 0
    total = len(linhas)
    blocos = []

    while i < total:
        linha = linhas[i].strip()
        if not linha.startswith('INSERT INTO'):
            i += 1
            continue

        tabela, colunas_orig = extrair_nome_e_colunas(linha)
        if not tabela:
            i += 1
            continue

        # Índices das colunas originais
        indice_orig = {nome: idx for idx, nome in enumerate(colunas_orig)}

        # Índices a manter na ordem de COLUNAS_DESTINO
        indices_manter = [indice_orig.get(col) for col in COLUNAS_DESTINO]

        i += 1
        linhas_valores = []
        while i < total:
            linha_val = linhas[i].strip()
            if not linha_val:
                i += 1
                continue
            if linha_val.startswith('INSERT INTO'):
                break
            linhas_valores.append(linha_val)
            i += 1

        novos_valores = []
        for linha_val in linhas_valores:
            valores = parse_valores(linha_val)
            if len(valores) != len(colunas_orig):
                print(f"Aviso: número de valores ({len(valores)}) diferente de colunas ({len(colunas_orig)}) em uma linha. Pulando.")
                continue

            novos = []
            for idx_dest in indices_manter:
                if idx_dest is None:
                    novos.append('NULL')
                else:
                    val = valores[idx_dest]
                    nome_col = colunas_orig[idx_dest]
                    if nome_col == 'Version' and val == '1':
                        val = "'1.0'"
                    elif nome_col == 'Created_At':
                        val = 'CURRENT_TIMESTAMP'
                    elif nome_col == 'Created_By':
                        val = "'Rogerio Fontanario'"
                    novos.append(val)

            linha_nova = '(' + ', '.join(novos) + ')'
            if linha_val.endswith(');'):
                linha_nova += ';'
            elif linha_val.endswith('),'):
                linha_nova += ','
            novos_valores.append(linha_nova)

        colunas_destino_str = ', '.join(f'"{c}"' for c in COLUNAS_DESTINO)
        insert_novo = f'INSERT INTO "{tabela}" ({colunas_destino_str}) VALUES\n'
        insert_novo += '\n'.join(novos_valores)
        blocos.append(insert_novo)

    with open(saida, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(blocos))
    print(f"Arquivo gerado: {saida}")

if __name__ == '__main__':
    diretorio = os.path.dirname(os.path.abspath(__file__))
    entrada = os.path.join(diretorio, 'TXT.txt')
    saida = os.path.join(diretorio, 'saida.sql')
    if not os.path.exists(entrada):
        print(f"Erro: arquivo {entrada} não encontrado.")
    else:
        processar_arquivo(entrada, saida)