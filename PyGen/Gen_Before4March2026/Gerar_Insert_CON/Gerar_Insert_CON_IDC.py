import csv
import os
import re
import sys

# Diretório onde o script está localizado
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Lista ordenada de todas as colunas da tabela Connector_IDC (baseada na CREATE TABLE Relay, exceto ID_AUX)
TABLE_COLUMNS_ORDER = [
    'MyPN', 'Name', 'Description', 'Value', 'Info1', 'Info2',
    'Symbol', 'Footprint', 'Footprint_Filter', 'Datasheet', 'Notes', 'Notes_to_Buyer',
    'Manufacturer', 'Manufacturer_PN', 'Manufacturer_URL', 'Alternative_PN', 'Alternative_URL',
    'Digikey_PN', 'Digikey_URL', 'Mouser_PN', 'Mouser_URL', 'LCSC_PN', 'LCSC_URL',
    'Stock_Qty', 'Stock_Location', 'Stock_Unit', 'Price', 'Currency', 'Min_Stock', 'Max_Stock',
    'Last_Purchase_Date', 'Last_Purchase_Price', 'Active', 'Version', 'Created_At', 'Created_By',
    'Modified_At', 'Modified_By', 'Exclude_from_BOM', 'Exclude_from_Board',
    'Category', 'Subcategory', 'Family_Series', 'Package', 'Mount', 'Dimensions',
    'Temperature_Range', 'REACH_Compliant', 'RoHS_Compliant', 'Unit', 'Tolerance',
    'Voltage_Rating', 'Current_Rating', 'Power_Rating', 'Temperature_Coefficient',
    'Pin_Configuration', 'Gender', 'Pin_Type', 'Pitch', 'Orientation', 'Locking_Mechanism',
    'Current_Rating_Per_Pin', 'IP_Rating', 'Wire_Gauge', 'Termination_Style', 'Resistance',
    'Technology_Material', 'Capacitance', 'Dielectric_Type', 'ESR', 'Ripple_Current',
    'Leakage_Current', 'Inductance', 'DC_Resistance', 'Self_Resonant_Frequency',
    'Quality_Factor_Q', 'Saturation_Current', 'Hold_Current', 'Trip_Current',
    'Interrupting_Rating', 'Response_Time', 'Forward_Voltage', 'Reverse_Leakage',
    'Junction_Capacitance', 'Reverse_Recovery_Time', 'Zener_Voltage', 'Zener_Impedance',
    'Reverse_Standoff_Voltage', 'Breakdown_Voltage', 'Clamping_Voltage', 'Peak_Pulse_Current',
    'Q_Type', 'Polarity_Channel_Type', 'Power_Dissipation', 'Junction_Temperature',
    'VDS_Max', 'VGS_Max', 'VGS_Threshold', 'RDS_On', 'ID_Continuous', 'ID_Pulse',
    'Input_Capacitance', 'Output_Capacitance', 'Reverse_Transfer_Capacitance', 'Gate_Charge',
    'Rise_Time', 'Fall_Time', 'IDSS', 'VGS_Off', 'Gain', 'Gate_Reverse_Current', 'VCEO',
    'Current_Collector', 'DC_Gain_HFE', 'Saturation_Voltage', 'Transition_Frequency',
    'VCE_Sat', 'IC_Continuous', 'IC_Pulse', 'VGE_Threshold', 'Short_Circuit_Withstanding',
    'Diode_Forward_Voltage', 'Frequency', 'Oscillator_Type', 'Load_Capacitance',
    'Supply_Voltage', 'Coil_Voltage', 'Coil_Resistance', 'Contact_Configuration',
    'Contact_Current_Rating', 'Contact_Voltage_Rating', 'Relay_Type', 'Operating_Time',
    'Transformer_Type', 'Turns_Ratio', 'Isolation_Voltage', 'Power_Rating_VA',
    'Frequency_Rating', 'Battery_Chemistry', 'Battery_Voltage_Nominal', 'Battery_Capacity',
    'Battery_Size', 'Rechargeable', 'Number_of_Cells', 'Display_Type', 'Display_Size',
    'Resolution', 'Interface', 'Backlight', 'Controller', 'Color', 'Sensor_Type',
    'Sensor_Interface', 'Supply_Voltage_Min', 'Supply_Voltage_Max', 'Accuracy', 'Output_Type',
    'LED_Color', 'Luminous_Intensity', 'Wavelength', 'Viewing_Angle_LED', 'Lens_Type',
    'If_Current', 'VF_Typical', 'Optocoupler_Type', 'CTR', 'Tube_Type', 'Heater_Voltage',
    'Heater_Current', 'Plate_Voltage_Max'
]

def escape_sql_string(s):
    """Escapa aspas simples para uso seguro em SQL."""
    if s is None:
        return 'NULL'
    return "'" + str(s).replace("'", "''") + "'"

def extract_cols_from_footprint(footprint):
    """
    Extrai rows e columns do footprint no formato:
    Connector_IDC:IDC-Header_2x05_P2.54mm_Horizontal
    Retorna (rows, cols) como inteiros.
    """
    match = re.search(r'IDC-Header_(\d+)x(\d+)', footprint)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def generate_insert(csv_path, table_name, output_path=None, start_id=200000):
    csv_path = os.path.abspath(csv_path)
    if not os.path.isfile(csv_path):
        print(f"Erro: Arquivo CSV não encontrado: {csv_path}")
        return

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        rows = list(reader)
        if not rows:
            print("Erro: CSV vazio.")
            return

        # Lista para armazenar os dicionários com os valores a inserir
        insert_data = []
        mypn_counter = start_id

        for row in rows:
            # Extrair informações do footprint
            footprint = row.get('Footprint', '')
            rows_f, cols = extract_cols_from_footprint(footprint)
            if rows_f is None or cols is None:
                print(f"Aviso: Não foi possível extrair rows/cols do footprint: {footprint}")
                continue

            # Dados básicos
            pitch = row.get('Pitch_mm', '').strip()
            orientation = row.get('Orientation', '')
            orientation_letter = 'H' if orientation.upper().startswith('H') else 'V'
            smd = 'SMD' in footprint

            # Gerar MyPN sequencial
            mypn = f"EL_CON-{mypn_counter}"
            mypn_counter += 1

            # Name: CON_IDC_Header_02x05_P2.54mm_H_SMD
            name = f"CON_IDC_Header_{rows_f:02d}x{cols:02d}_P{pitch}mm_{orientation_letter}"
            if smd:
                name += "_SMD"

            # Value: IDC_Header_02x05
            value = f"IDC_Header_{rows_f:02d}x{cols:02d}"

            # Info1: P2.54mm_V
            info1 = f"P{pitch}mm_{orientation_letter}"

            # Info2: SMD se aplicável, senão None (não será incluído)
            info2 = "SMD" if smd else None

            # Pin_Configuration: 2x05 (sem zeros à esquerda nas linhas, mas colunas com dois dígitos)
            pin_config = f"{rows_f}x{cols:02d}"

            # Mount: "SMD" se smd, senão "Through Hole"
            mount = "SMD" if smd else "Through Hole"

            # Mapeamento direto das colunas do CSV para a tabela
            direct_mapping = {
                'Description': row.get('Description', ''),
                'Symbol': row.get('Symbol', ''),
                'Footprint': footprint,
                'Footprint_Filter': row.get('Footprint_Filter', ''),
                'Category': row.get('Category', ''),
                'Subcategory': row.get('Subcategory', ''),
                'Pin_Type': row.get('Connector_Type', ''),  # Connector_Type -> Pin_Type
                'Gender': row.get('Gender', ''),
                'Orientation': row.get('Orientation', ''),
                'Locking_Mechanism': row.get('Locking_Mechanism', ''),
                'Version': row.get('Version', '1'),  # Valor padrão 1 se vazio
                'Exclude_from_BOM': row.get('Exclude_from_BOM', '0'),
                'Exclude_from_Board': row.get('Exclude_from_Board', '0'),
            }

            # Campos calculados adicionais
            computed_fields = {
                'MyPN': mypn,
                'Name': name,
                'Value': value,
                'Info1': info1,
                'Info2': info2,
                'Pin_Configuration': pin_config,
                'Mount': mount,
                'Pitch': pitch,
                'Active': '1',  # Sempre ativo
            }

            # Combinar todos os campos, priorizando os calculados se houver conflito
            row_data = {**direct_mapping, **computed_fields}

            # Remover campos com valor vazio (None) para posterior análise
            insert_data.append(row_data)

        if not insert_data:
            print("Erro: Nenhum dado válido para inserir.")
            return

        # Determinar quais colunas da tabela realmente têm dados em pelo menos uma linha
        # Consideramos campos que não são None e não são string vazia
        all_columns_set = set()
        for data in insert_data:
            for k, v in data.items():
                if v is not None and v != '':
                    all_columns_set.add(k)

        # Ordenar conforme a ordem da tabela (para manter consistência)
        final_columns = [col for col in TABLE_COLUMNS_ORDER if col in all_columns_set]

        if not final_columns:
            print("Erro: Nenhuma coluna válida para inserir.")
            return

        # Prepara saída
        if output_path:
            output_path = os.path.abspath(output_path)
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            out = open(output_path, 'w', encoding='utf-8')
        else:
            out = sys.stdout

        # Gerar os VALUES
        values_lines = []
        for data in insert_data:
            values = []
            for col in final_columns:
                val = data.get(col, None)
                if val is None or val == '':
                    values.append('NULL')
                else:
                    values.append(escape_sql_string(val))
            values_lines.append(f"({', '.join(values)})")

        # Montar o comando INSERT
        columns_str = ', '.join(final_columns)
        values_str = ',\n'.join(values_lines)
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES\n{values_str};\n"
        out.write(sql)

        if output_path:
            out.close()
            print(f"Arquivo SQL gerado: {output_path}")

def main():
    # Caminhos padrão
    csv_file = os.path.join(SCRIPT_DIR, 'Connector_IDC.csv')
    output_file = os.path.join(SCRIPT_DIR, 'inserts_idc.sql')
    table_name = 'Connector_IDC'

    # Aceita argumentos da linha de comando
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2:
        table_name = sys.argv[2]
    if len(sys.argv) > 3:
        output_file = sys.argv[3]

    generate_insert(csv_file, table_name, output_file, start_id=200000)

if __name__ == '__main__':
    main()