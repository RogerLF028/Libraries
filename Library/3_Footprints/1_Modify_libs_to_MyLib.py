import os
import sys

PREFIX_TO_BE_ADD = 'MyLib_'

def rename_pretty_folders(root_dir=None):
    """
    Percorre recursivamente todas as pastas a partir de root_dir
    e renomeia diretórios com extensão .pretty adicionando prefixo 'MyLib_'.
    Se root_dir for None, usa o diretório onde este script está localizado.
    """
    if root_dir is None:
        root_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"Procurando pastas .pretty em: {root_dir} (e subpastas)")

    renamed_count = 0

    for current_dir, subdirs, files in os.walk(root_dir):
        # Itera sobre uma cópia da lista de subdiretórios para poder modificar a original
        for subdir in list(subdirs):
            full_path = os.path.join(current_dir, subdir)
            if subdir.endswith('.pretty'):
                if not subdir.startswith(PREFIX_TO_BE_ADD):
                    new_name = PREFIX_TO_BE_ADD + subdir
                    new_path = os.path.join(current_dir, new_name)
                    try:
                        os.rename(full_path, new_path)
                        print(f'Renomeado: "{os.path.join(current_dir, subdir)}" -> "{new_path}"')
                        renamed_count += 1
                        # Atualiza a lista de subdiretórios para continuar a varredura corretamente
                        subdirs.remove(subdir)
                        subdirs.append(new_name)
                    except OSError as e:
                        print(f'Erro ao renomear "{full_path}": {e}')
                else:
                    print(f'Ignorado (já tem prefixo): "{full_path}"')

    print(f"\nConcluído. {renamed_count} pasta(s) renomeada(s).")

if __name__ == "__main__":
    # Se um argumento for passado, usa como diretório raiz; caso contrário, usa o diretório do script
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = None
    rename_pretty_folders(target)