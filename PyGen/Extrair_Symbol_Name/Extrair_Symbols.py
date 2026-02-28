#!/usr/bin/env python3
"""
Script para gerar lista de símbolos a partir das pastas .kicad_sym do KiCad
Versão com debug para identificar problemas
"""

import os
import csv
import re
from pathlib import Path

def extrair_todos_simbolos(arquivo):
    """
    Extrai TODOS os símbolos PRINCIPAIS de um arquivo .kicad_sym
    Versão com debug e mais robusta
    """
    simbolos_info = []
    
    try:
        with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
            conteudo = f.read()
        
        print(f"   📊 Tamanho do arquivo: {len(conteudo)} caracteres")
        
        # Método 1: Dividir por símbolos (mais confiável)
        # Primeiro, encontra todos os blocos que começam com (symbol
        import re
        blocos_raw = re.finditer(r'\(\s*symbol\s+', conteudo)
        posicoes = [m.start() for m in blocos_raw]
        
        print(f"   🔍 Encontradas {len(posicoes)} ocorrências de '(symbol'")
        
        # Se não encontrou com regex, tenta método alternativo
        if len(posicoes) == 0:
            print("   ⚠️ Regex não encontrou símbolos, tentando método alternativo...")
            linhas = conteudo.split('\n')
            dentro_simbolo = False
            simbolo_atual = []
            nome_simbolo = ""
            
            for i, linha in enumerate(linhas):
                if '(symbol' in linha and not dentro_simbolo:
                    dentro_simbolo = True
                    simbolo_atual = [linha]
                    # Tenta extrair nome
                    match = re.search(r'\(\s*symbol\s+"([^"]+)"', linha)
                    if match:
                        nome_simbolo = match.group(1)
                    else:
                        nome_simbolo = f"simbolo_{i}"
                
                elif dentro_simbolo:
                    simbolo_atual.append(linha)
                    # Fecha o símbolo (quando encontra fechamento no nível correto)
                    if linha.strip() == ')' and simbolo_atual.count('(') <= simbolo_atual.count(')'):
                        # Processa o símbolo
                        bloco_conteudo = '\n'.join(simbolo_atual)
                        
                        # Pula se parecer sub-símbolo
                        if re.search(r'_\d+_\d+$', nome_simbolo):
                            print(f"     ⏭️ Ignorando sub-símbolo: {nome_simbolo}")
                        else:
                            info = {
                                'simbolo': nome_simbolo,
                                'value': '',
                                'footprint': '',
                                'description': '',
                                'keywords': '',
                                'fp_filters': '',
                                'datasheet': ''
                            }
                            
                            # Extrai propriedades
                            info = extrair_propriedades(bloco_conteudo, info)
                            simbolos_info.append(info)
                            print(f"     ✓ Encontrado: {nome_simbolo}")
                        
                        dentro_simbolo = False
                        simbolo_atual = []
        
        else:
            # Método com posições (original melhorado)
            for i, start in enumerate(posicoes):
                # Encontra o fim do símbolo (balanceando parênteses)
                balance = 1
                pos = start + 8  # pula '(symbol '
                
                while balance > 0 and pos < len(conteudo):
                    if conteudo[pos] == '(':
                        balance += 1
                    elif conteudo[pos] == ')':
                        balance -= 1
                    pos += 1
                
                bloco_conteudo = conteudo[start:pos]
                
                # Extrai nome do símbolo
                match_nome = re.search(r'\(\s*symbol\s+"([^"]+)"', bloco_conteudo)
                if not match_nome:
                    match_nome = re.search(r'\(\s*symbol\s+([^\s\(]+)', bloco_conteudo)
                
                if match_nome:
                    nome_simbolo = match_nome.group(1)
                    
                    # Pula sub-símbolos
                    if re.search(r'_\d+_\d+$', nome_simbolo):
                        print(f"     ⏭️ Ignorando sub-símbolo: {nome_simbolo}")
                        continue
                    
                    info = {
                        'simbolo': nome_simbolo,
                        'value': '',
                        'footprint': '',
                        'description': '',
                        'keywords': '',
                        'fp_filters': '',
                        'datasheet': ''
                    }
                    
                    info = extrair_propriedades(bloco_conteudo, info)
                    simbolos_info.append(info)
                    print(f"     ✓ Encontrado: {nome_simbolo}")
                else:
                    print(f"     ⚠️ Não foi possível extrair nome do símbolo {i+1}")
        
    except Exception as e:
        print(f"   ❌ Erro ao processar {arquivo.name}: {e}")
        import traceback
        traceback.print_exc()
    
    return simbolos_info

def extrair_propriedades(bloco_conteudo, info):
    """Extrai todas as propriedades de um bloco de símbolo"""
    
    # Extrai Value
    value_match = re.search(r'\(\s*property\s+"Value"\s+"([^"]*)"', bloco_conteudo)
    if value_match:
        info['value'] = value_match.group(1)
    
    # Extrai Footprint
    footprint_match = re.search(r'\(\s*property\s+"Footprint"\s+"([^"]*)"', bloco_conteudo)
    if footprint_match:
        info['footprint'] = footprint_match.group(1)
    
    # Extrai Description
    description_match = re.search(r'\(\s*property\s+"Description"\s+"([^"]*)"', bloco_conteudo)
    if description_match:
        info['description'] = description_match.group(1)
    
    # Extrai ki_keywords (Tags)
    keywords_match = re.search(r'\(\s*property\s+"ki_keywords"\s+"([^"]*)"', bloco_conteudo)
    if keywords_match:
        info['keywords'] = keywords_match.group(1)
    
    # Extrai ki_fp_filters (Footprint_Filter)
    fp_filters_match = re.search(r'\(\s*property\s+"ki_fp_filters"\s+"([^"]*)"', bloco_conteudo)
    if fp_filters_match:
        info['fp_filters'] = fp_filters_match.group(1)
    
    # Extrai Datasheet
    datasheet_match = re.search(r'\(\s*property\s+"Datasheet"\s+"([^"]*)"', bloco_conteudo)
    if datasheet_match:
        info['datasheet'] = datasheet_match.group(1)
    
    return info

def gerar_simbolos_csv(caminho_pasta, arquivo_saida="simbolos_para_database.csv"):
    """
    Gera CSV com informações dos símbolos .kicad_sym
    """
    pasta_path = Path(caminho_pasta)
    
    if not pasta_path.exists():
        print(f"❌ Pasta não encontrada: {pasta_path}")
        return
    
    todos_simbolos = []
    
    print(f"\n📁 Analisando: {pasta_path}")
    print("=" * 60)
    
    # Estatísticas
    total_arquivos = 0
    total_simbolos = 0
    
    # Processa arquivos .kicad_sym na pasta
    for arquivo in sorted(pasta_path.glob("*.kicad_sym")):
        total_arquivos += 1
        
        print(f"\n📄 [{total_arquivos}] {arquivo.name}")
        print("-" * 40)
        
        try:
            # Extrai TODOS os símbolos deste arquivo
            simbolos = extrair_todos_simbolos(arquivo)
            
            if not simbolos:
                print(f"   ⚠️ Nenhum símbolo encontrado em {arquivo.name}")
            
            for info in simbolos:
                total_simbolos += 1
                
                # Cria o Database_Symbol
                nome_arquivo = arquivo.stem
                database_symbol = f"{nome_arquivo}:{info['simbolo']}"
                
                todos_simbolos.append({
                    'database_symbol': database_symbol,
                    'value': info['value'],
                    'footprint': info['footprint'],
                    'description': info['description'],
                    'tags': info['keywords'],
                    'footprint_filter': info['fp_filters'],
                    'datasheet': info['datasheet']
                })
                
        except Exception as e:
            print(f"   ❌ Erro fatal em {arquivo.name}: {e}")
            continue
    
    # Salva CSV
    with open(arquivo_saida, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(['Symbol', 'Value', 'Footprint', 'Description', 'Tags', 'Footprint_Filter', 'Datasheet'])
        
        for info in sorted(todos_simbolos, key=lambda x: x['database_symbol']):
            writer.writerow([
                info['database_symbol'],
                info['value'],
                info['footprint'],
                info['description'],
                info['tags'],
                info['footprint_filter'],
                info['datasheet']
            ])
    
    print(f"\n" + "=" * 60)
    print(f"✅ RESUMO:")
    print(f"   Arquivos .kicad_sym processados: {total_arquivos}")
    print(f"   Símbolos encontrados: {total_simbolos}")
    print(f"   Arquivo gerado: {os.path.abspath(arquivo_saida)}")

# EXECUTAR
if __name__ == "__main__":
    print("🔍 GERADOR DE SÍMBOLOS PARA DATABASE (DEBUG MODE)")
    print("=" * 60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_pasta = os.path.join(script_dir, 'symbols')
    arquivo_saida = os.path.join(script_dir, 'simbolos_possiveis_Transistor.csv')
    
    print(f"📁 Script em: {script_dir}")
    print(f"📁 Pasta Connectores: {caminho_pasta}")
    print(f"📁 Arquivo de saída: {arquivo_saida}")
    print("=" * 60)
    
    if not os.path.exists(caminho_pasta):
        print(f"\n❌ Pasta 'Connectores' não encontrada")
    else:
        # Mostra todos os arquivos .kicad_sym encontrados
        arquivos = list(Path(caminho_pasta).glob("*.kicad_sym"))
        print(f"\n📁 Encontrados {len(arquivos)} arquivos .kicad_sym:")
        for i, arq in enumerate(arquivos, 1):
            print(f"   {i:2d}. {arq.name}")
        
        print("\n🚀 Iniciando processamento...")
        gerar_simbolos_csv(caminho_pasta, arquivo_saida)
        
        print("\n✨ Processo concluído!")