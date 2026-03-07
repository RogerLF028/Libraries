import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tables_file = os.path.join(script_dir, "Tables_names_V2.txt")

    if not os.path.isfile(tables_file):
        print(f"Erro: Arquivo {tables_file} não encontrado.")
        return

    table_names = []
    with open(tables_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                table_names.append(line)

    if not table_names:
        print("Nenhum nome de tabela encontrado.")
        return

    # Definição das colunas (igual à versão anterior, sem comentários)
    columns = [
        "ID_Aux INTEGER PRIMARY KEY ",
        "MyPN TEXT NOT NULL UNIQUE",
        "Name TEXT NOT NULL",
        "Description TEXT",
        "Value TEXT",
        "Info1 TEXT",
        "Info2 TEXT",
        "Symbol TEXT",
        "Footprint TEXT",
        "Footprint_Filter TEXT",
        "Datasheet TEXT",
        "Category TEXT",
        "Subcategory TEXT",
        "Family_Series TEXT",
        "Package TEXT",
        "Mount TEXT",
        "Dimensions TEXT",
        "Temperature_Range TEXT",
        "REACH_Compliant TEXT",
        "RoHS_Compliant TEXT",
        "Notes TEXT",
        "Notes_to_Buyer TEXT",
        "Manufacturer TEXT",
        "Manufacturer_PN TEXT",
        "Manufacturer_URL TEXT",
        "Alternative_PN TEXT",
        "Alternative_URL TEXT",
        "Digikey_PN TEXT",
        "Digikey_URL TEXT",
        "Mouser_PN TEXT",
        "Mouser_URL TEXT",
        "LCSC_PN TEXT",
        "LCSC_URL TEXT",
        "Stock_Qty INTEGER DEFAULT 0",
        "Stock_Location TEXT",
        "Stock_Unit TEXT",
        "Price TEXT",
        "Currency TEXT DEFAULT 'USD'",
        "Min_Stock INTEGER ",
        "Max_Stock INTEGER ",
        "Last_Purchase_Date TEXT",
        "Last_Purchase_Price TEXT",
        "Active INTEGER DEFAULT 1",
        "Version TEXT DEFAULT '1.0'",
        "Created_At TEXT DEFAULT CURRENT_TIMESTAMP",
        "Created_By TEXT DEFAULT 'Rogerio Fontanario'",
        "Modified_At TEXT",
        "Modified_By TEXT",
        "Exclude_from_BOM INTEGER DEFAULT 0",
        "Exclude_from_Board INTEGER DEFAULT 0"
    ]

    # Índices base (sem o nome da tabela)
    base_indexes = [
        ("idx_my_pn", "MyPN"),
        ("idx_name", "Name"),
    ]

    output_file = os.path.join(script_dir, "create_tables_v2.sqlite")

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("-- Script de criação de tabelas para SQLite\n")
        out.write("-- Gerado automaticamente a partir da lista de tabelas\n\n")

        for table in table_names:
            # Cria a tabela
            out.write(f"CREATE TABLE {table} (\n")
            for i, col in enumerate(columns):
                comma = "," if i < len(columns) - 1 else ""
                out.write(f"    {col}{comma}\n")
            out.write(");\n\n")

            # Cria os índices com nomes únicos (incluindo o nome da tabela)
            for base_name, col in base_indexes:
                index_name = f"{base_name}_{table}"
                out.write(f"CREATE INDEX {index_name} ON {table} ({col});\n")
            out.write("\n")

    print(f"Arquivo gerado com sucesso: {output_file}")

if __name__ == "__main__":
    main()