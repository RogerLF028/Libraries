#!/usr/bin/env python3
"""
Script para gerar lista de footprints a partir das pastas .pretty do KiCad
Autor: Rogerio
Data: 2024
"""

import os
import csv
import re
from pathlib import Path

def extrair_nome_footprint(arquivo):
    """
    Extrai o nome do footprint do arquivo .kicad_mod de forma robusta
    Lidando com aspas, vírgulas e caracteres especiais
    """
    try:
        with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
            conteudo = f.read()
        
        # Primeira tentativa: captura conteúdo entre aspas (caso mais comum)
        match = re.search(r'\(\s*module\s+"([^"]+)"', conteudo)
        if match:
            nome = match.group(1)
            return nome
        
        # Segunda tentativa: captura conteúdo sem aspas
        match = re.search(r'\(\s*module\s+([^\s\(]+)', conteudo)
        if match:
            nome = match.group(1)
            # Remove aspas residuais (caso algo tenha escapado)
            nome = nome.replace('"', '').replace("'", '')
            return nome
        
        # Fallback: usa o nome do arquivo se não encontrar no conteúdo
        return arquivo.stem
        
    except Exception as e:
        print(f"   ⚠️ Erro ao ler {arquivo.name}: {e}")
        return arquivo.stem

def limpar_nome_footprint(nome):
    """
    Limpa o nome do footprint removendo caracteres problemáticos
    Apenas remove aspas, mantém vírgulas e outros caracteres originais
    """
    # Remove apenas aspas duplas e simples
    nome = nome.replace('"', '').replace("'", '')
    
    # Remove espaços extras no início e fim
    nome = nome.strip()
    
    return nome

def gerar_footprints_csv(caminho_package, arquivo_saida="footprints_para_database.csv"):
    """
    Gera CSV com footprints no formato: NomeDaPasta:nomedofootprint
    Remove automaticamente a extensão .pretty do nome da pasta
    TODAS as linhas são envolvidas por aspas para consistência
    """
    package_path = Path(caminho_package)
    
    if not package_path.exists():
        print(f"❌ Pasta não encontrada: {package_path}")
        return
    
    footprints = []
    erros = []
    
    print(f"\n📁 Analisando: {package_path}")
    print("=" * 60)
    
    # Estatísticas
    total_arquivos = 0
    total_pastas = 0
    
    # Percorre subpastas
    for pasta in sorted(package_path.iterdir()):
        if pasta.is_dir():
            total_pastas += 1
            
            # Remove .pretty do nome da pasta se existir
            nome_pasta = pasta.name
            if nome_pasta.endswith('.pretty'):
                nome_pasta = nome_pasta[:-7]  # Remove os 7 caracteres '.pretty'
            
            print(f"\n📂 {nome_pasta} (original: {pasta.name})")
            
            # Procura arquivos .kicad_mod
            arquivos_kicad = list(pasta.glob("*.kicad_mod"))
            
            if not arquivos_kicad:
                print(f"   ⚠️ Nenhum arquivo .kicad_mod encontrado")
                continue
            
            for arquivo in sorted(arquivos_kicad):
                total_arquivos += 1
                
                # Extrai nome do footprint
                nome_footprint = extrair_nome_footprint(arquivo)
                nome_footprint = limpar_nome_footprint(nome_footprint)
                
                # Verifica se o nome parece válido
                if not nome_footprint or len(nome_footprint) < 2:
                    print(f"   ⚠️ Nome suspeito para {arquivo.name}: '{nome_footprint}'")
                    erros.append(f"{pasta.name}:{arquivo.name} -> '{nome_footprint}'")
                
                # Formato: NomeDaPasta (sem .pretty):nome_footprint
                footprint_completo = f"{nome_pasta}:{nome_footprint}"
                footprints.append(footprint_completo)
                print(f"   ✓ {footprint_completo}")
    
    # Remove duplicatas mantendo a ordem
    footprints_unicos = []
    vistos = set()
    for fp in footprints:
        if fp not in vistos:
            vistos.add(fp)
            footprints_unicos.append(fp)
    
    # Salva CSV com QUOTE_ALL para colocar aspas em TODAS as linhas
    with open(arquivo_saida, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)  # QUOTE_ALL força aspas em tudo
        writer.writerow(['Footprint'])
        for fp in sorted(footprints_unicos):
            writer.writerow([fp])
    
    print(f"\n" + "=" * 60)
    print(f"✅ RESUMO:")
    print(f"   Pastas processadas: {total_pastas}")
    print(f"   Arquivos .kicad_mod encontrados: {total_arquivos}")
    print(f"   Footprints únicos salvos: {len(footprints_unicos)}")
    print(f"   Arquivo gerado: {os.path.abspath(arquivo_saida)}")
    print(f"   Formato: TODAS as linhas com aspas (QUOTE_ALL)")
    
    if erros:
        print(f"\n⚠️ {len(erros)} footprints com possíveis problemas:")
        for erro in erros[:10]:  # Mostra apenas os primeiros 10
            print(f"   {erro}")
        if len(erros) > 10:
            print(f"   ... e mais {len(erros)-10}")

def listar_estrutura_pastas(caminho_package):
    """
    Função auxiliar para listar a estrutura de pastas encontrada
    """
    package_path = Path(caminho_package)
    
    if not package_path.exists():
        print(f"❌ Pasta não encontrada: {package_path}")
        return
    
    print(f"\n📁 Estrutura de pastas em: {package_path}")
    print("=" * 60)
    
    for pasta in sorted(package_path.iterdir()):
        if pasta.is_dir():
            arquivos = list(pasta.glob("*.kicad_mod"))
            nome_pasta = pasta.name
            if nome_pasta.endswith('.pretty'):
                nome_pasta = nome_pasta[:-7]
            
            print(f"📂 {pasta.name} -> {nome_pasta} ({len(arquivos)} footprints)")

# EXECUTAR
if __name__ == "__main__":
    print("🔍 GERADOR DE FOOTPRINTS PARA DATABASE")
    print("=" * 60)
    
    # Pega o diretório onde o script está localizado
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define o caminho completo para a pasta Connectors
    caminho_package = os.path.join(script_dir, 'Led')
    
    # Define o nome do arquivo de saída
    arquivo_saida = os.path.join(script_dir, 'footprints_para_database_Led.csv')
    
    print(f"📁 Script em: {script_dir}")
    print(f"📁 Pasta Connectors: {caminho_package}")
    print(f"📁 Arquivo de saída: {arquivo_saida}")
    print("=" * 60)
    
    # Verifica se a pasta Connectors existe
    if not os.path.exists(caminho_package):
        print(f"\n❌ Pasta 'Connectors' não encontrada em: {caminho_package}")
        print("   Certifique-se que o script está na mesma pasta que a pasta 'Connectors'")
        print("\n   Estrutura esperada:")
        print("   ./")
        print("   ├── Setup_Database_Generator.py (este script)")
        print("   └── Connectors/")
        print("       ├── Connector_Phoenix.pretty/")
        print("       ├── Connector_Molex.pretty/")
        print("       └── ...")
        
        # Pergunta se quer listar o que existe no diretório atual
        print("\n📁 Conteúdo do diretório atual:")
        for item in sorted(Path(script_dir).iterdir()):
            if item.is_dir():
                print(f"   📂 {item.name}/")
            else:
                print(f"   📄 {item.name}")
    else:
        # Opcional: listar estrutura antes de processar
        listar_estrutura_pastas(caminho_package)
        
        # Executa a função principal
        print("\n🚀 Iniciando processamento...")
        gerar_footprints_csv(caminho_package, arquivo_saida)
        
        print("\n✨ Processo concluído!")