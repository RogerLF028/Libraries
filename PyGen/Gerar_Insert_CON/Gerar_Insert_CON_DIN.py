import csv
import os
import sys
from collections import defaultdict

# Diretório do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Lista ordenada de todas as colunas da tabela Connector_DIN (baseada no CREATE TABLE, exceto ID_AUX)
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

# Mapeamento de colunas do CSV para colunas da tabela (quando os nomes diferem)
CSV_TO_TABLE_MAP = {
    'MyPN': 'MyPN',
    'Name': 'Name',
    'Description': 'Description',
    'Symbol': 'Symbol',
    'Footprint': 'Footprint',
    'Footprint_Filter': 'Footprint_Filter',
    'Package': 'Package',
    'Manufacturer': 'Manufacturer',
    'Manufacturer_PN': 'Manufacturer_PN',
    'Series': 'Family_Series',
    'Category': 'Category',
    'Subcategory': 'Subcategory',
    'Number_of_Pins': None,  # ignorado (já temos Pin_Configuration)
    'Pin_Configuration': 'Pin_Configuration',
    'Contact_Gender': 'Gender',
    'Mounting_Type': 'Mount',
    'Mounting_Style': None,  # ignorado
    'Orientation': 'Orientation',
    'Active': 'Active',
    'Notes': 'Notes',
    'Tags': 'Notes',          # Tags vão para Notes
    'CreatedBy': 'Created_By',
    'CreatedAt': 'Created_At',
    'ModifiedBy': 'Modified_By',
    'ModifiedAt': 'Modified_At',
    'Version': 'Version',
    'Exclude_from_BOM': 'Exclude_from_BOM',
    'Exclude_from_Board': 'Exclude_from_Board',
    'RoHS_Compliant': 'RoHS_Compliant',
    'REACH_Compliant': 'REACH_Compliant',
    'StockQty': 'Stock_Qty',
    'Min_Stock': 'Min_Stock',
    'Max_Stock': 'Max_Stock',
    'StockPlace': 'Stock_Location',
    'Price': 'Price',
    'Currency': 'Currency',
    'Datasheet': 'Datasheet',
    # Outras colunas podem ser adicionadas se necessário, mas serão ignoradas se não houver dados
}

def escape_sql_string(s):
    """Escapa aspas simples para uso seguro em SQL e retorna a string entre aspas."""
    if s is None:
        return 'NULL'
    # Converte para string e escapa aspas simples
    s_str = str(s)
    return "'" + s_str.replace("'", "''") + "'"

def get_non_empty_columns(rows, all_columns):
    """Retorna lista de colunas do CSV que possuem pelo menos um valor não vazio (diferente de '') em alguma linha."""
    non_empty = []
    for col in all_columns:
        for row in rows:
            if row.get(col, '') != '':
                non_empty.append(col)
                break
    return non_empty

def generate_insert(csv_path, table_name, output_path=None):
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

        # Colunas disponíveis no CSV (exceto Keyld)
        all_csv_columns = [col for col in reader.fieldnames if col != 'Keyld']

        # Identifica quais colunas do CSV têm dados não vazios
        csv_columns_with_data = get_non_empty_columns(rows, all_csv_columns)

        # Mapeia para colunas da tabela
        table_columns_set = set()
        for csv_col in csv_columns_with_data:
            if csv_col in CSV_TO_TABLE_MAP:
                table_col = CSV_TO_TABLE_MAP[csv_col]
                if table_col:  # se não for None
                    table_columns_set.add(table_col)
            else:
                # Se não houver mapeamento, assume mesmo nome (caso exista na tabela)
                if csv_col in TABLE_COLUMNS_ORDER:
                    table_columns_set.add(csv_col)

        # Adiciona a coluna gerada "Value"
        table_columns_set.add('Value')

        # Ordena as colunas da tabela conforme a ordem original
        final_columns = [col for col in TABLE_COLUMNS_ORDER if col in table_columns_set]

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

        # Gera os VALUES para cada linha
        values_lines = []
        for row in rows:
            values = []
            for col in final_columns:
                if col == 'Value':
                    # Gera Value a partir dos dados da linha
                    pin_conf = row.get('Pin_Configuration', '')
                    gender = row.get('Contact_Gender', '')
                    orient = row.get('Orientation', '')
                    # Pega primeira letra da orientação (V ou H)
                    orient_letter = orient[0] if orient else ''
                    value_str = f"DIN41612_{pin_conf}_{gender}_{orient_letter}"
                    values.append(escape_sql_string(value_str))
                else:
                    # Encontra a coluna correspondente no CSV (pode ter vindo de mapeamento)
                    # Primeiro, procura no mapeamento reverso (da tabela para csv)
                    csv_col = None
                    for k, v in CSV_TO_TABLE_MAP.items():
                        if v == col:
                            csv_col = k
                            break
                    if csv_col is None:
                        # Se não achou no mapeamento, assume mesmo nome
                        csv_col = col
                    val = row.get(csv_col, '')
                    if val == '':
                        values.append('NULL')
                    else:
                        values.append(escape_sql_string(val))
            values_lines.append(f"({', '.join(values)})")

        # Monta o INSERT
        columns_str = ', '.join(final_columns)
        values_str = ',\n'.join(values_lines)
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES\n{values_str};\n"
        out.write(sql)

        if output_path:
            out.close()
            print(f"Arquivo SQL gerado: {output_path}")

def main():
    # Caminhos padrão
    csv_file = os.path.join(SCRIPT_DIR, 'Connector_DIN.csv')
    output_file = os.path.join(SCRIPT_DIR, 'inserts.sql')
    table_name = 'Connector_DIN'

    # Aceita argumentos da linha de comando
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2:
        table_name = sys.argv[2]
    if len(sys.argv) > 3:
        output_file = sys.argv[3]

    generate_insert(csv_file, table_name, output_file)

if __name__ == '__main__':
    main()