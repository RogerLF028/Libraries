import csv
import os
import sys

# Diretório onde o script está localizado
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Lista ordenada de todas as colunas da tabela Connector_Block (baseada na CREATE TABLE Relay, exceto ID_AUX)
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

def extract_series_from_manufacturer_pn(manuf_pn):
    """
    Extrai o identificador da série a partir do Manufacturer_PN.
    Para Phoenix Contact: "PhoenixContact_MCV_1,5_..." -> "MCV-1,5"
    Para Wago: "Wago_734-132" -> "734"
    """
    if not manuf_pn:
        return None
    if manuf_pn.startswith("PhoenixContact_"):
        parts = manuf_pn.split('_')
        if len(parts) >= 3:
            # Ex: ["PhoenixContact", "MCV", "1,5", "10-G-3.5"]
            series = f"{parts[1]}-{parts[2]}"
        elif len(parts) == 2:
            series = parts[1]
        else:
            series = parts[1] if len(parts) > 1 else manuf_pn
        return series
    elif manuf_pn.startswith("Wago_"):
        # Ex: "Wago_734-132" -> "734"
        part = manuf_pn.split('_')[1]
        if '-' in part:
            series = part.split('-')[0]
        else:
            series = part
        return series
    else:
        # Fallback: retorna o próprio PN
        return manuf_pn

def has_flange(row):
    """Determina se o componente possui flange."""
    mounting_style = row.get('Mounting_Style', '')
    description = row.get('Description', '')
    footprint = row.get('Footprint', '')
    if 'Flange' in mounting_style or 'flange' in description.lower() or 'ThreadedFlange' in footprint:
        return True
    return False

def has_mounting_pin(row):
    """Determina se o componente possui mounting pin (pinos de fixação)."""
    symbol = row.get('Symbol', '')
    footprint = row.get('Footprint', '')
    if 'MountingPin' in symbol or 'MountingPin' in footprint:
        return True
    return False

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

        insert_data = []

        for row in rows:
            mypn = row.get('MyPN', '').strip()
            if not mypn:
                continue

            # Extrair dados básicos
            num_positions = row.get('Number_of_Positions', '')
            try:
                num_pos = int(num_positions) if num_positions else 0
            except:
                num_pos = 0

            pitch = row.get('Pitch_mm', '').strip()
            orientation = row.get('Orientation', '').strip()
            orient_letter = orientation[0].upper() if orientation else ''

            flange = has_flange(row)
            mp = has_mounting_pin(row)

            # Extrair série limpa
            manuf_pn = row.get('Manufacturer_PN', '')
            series_clean = extract_series_from_manufacturer_pn(manuf_pn)
            if not series_clean:
                # Fallback: usar o campo Series
                series_clean = row.get('Series', '').strip()
                # Limpar: remover espaços e substituir vírgula por hífen?
                series_clean = series_clean.replace(' ', '-').replace(',', '-')

            # Gerar pin_config
            pin_config = f"01x{num_pos:02d}" if num_pos > 0 else ""

            # Construir sufixos
            suffix_parts = [orient_letter]
            if mp:
                suffix_parts.append("MP")
            if flange:
                suffix_parts.append("FLANGE")
            suffix = '_' + '_'.join(suffix_parts) if suffix_parts else ''

            # Construir campos calculados
            name = f"CON_{series_clean}_{pin_config}_P{pitch}mm{suffix}"
            value = f"{series_clean}_{pin_config}"
            info1 = f"P{pitch}mm{suffix}"
            info2 = None  # será NULL

            # Mapeamento direto das colunas do CSV para a tabela
            data = {
                'MyPN': mypn,
                'Name': name,
                'Description': row.get('Description', ''),
                'Value': value,
                'Info1': info1,
                'Info2': info2,
                'Symbol': row.get('Symbol', ''),
                'Footprint': row.get('Footprint', ''),
                'Footprint_Filter': row.get('Footprint_Filter', ''),
                'Datasheet': row.get('Datasheet', ''),
                'Manufacturer': row.get('Manufacturer', ''),
                'Manufacturer_PN': manuf_pn,
                'Series': row.get('Series', ''),  # será mapeado para Family_Series depois
                'Category': row.get('Category', ''),
                'Subcategory': row.get('Subcategory', ''),
                'Package': row.get('Package', ''),
                'Mount': 'Through Hole',  # fixo, pois todos são THT
                'Color': row.get('Color', ''),
                'Locking_Mechanism': row.get('Locking_Mechanism', ''),
                'Mating_Cycles': row.get('Mating_Cycles', ''),
                'IP_Rating': row.get('IP_Rating', ''),
                'Flammability_Rating': row.get('Flammability_Rating', ''),
                'RoHS_Compliant': row.get('RoHS_Compliant', ''),
                'REACH_Compliant': row.get('REACH_Compliant', ''),
                'Active': row.get('Active', '1'),
                'Version': row.get('Version', '1'),
                'Created_By': row.get('CreatedBy', ''),
                'Created_At': row.get('CreatedAt', ''),
                'Modified_By': row.get('ModifiedBy', ''),
                'Modified_At': row.get('ModifiedAt', ''),
                'Exclude_from_BOM': row.get('Exclude_from_BOM', '0'),
                'Exclude_from_Board': row.get('Exclude_from_Board', '0'),
                'Stock_Qty': row.get('StockQty', '0'),
                'Stock_Location': row.get('StockPlace', ''),
                'Price': row.get('Price', ''),
                'Currency': row.get('Currency', 'USD'),
                'Min_Stock': row.get('Min_Stock', '0'),
                'Max_Stock': row.get('Max_Stock', '0'),
                'LCSC_PN': row.get('LCSC_PN', ''),
                'LCSC_URL': row.get('LCSC_URL', ''),
                'Mouser_PN': row.get('Mouser_PN', ''),
                'Mouser_URL': row.get('Mouser_URL', ''),
                'Digikey_PN': row.get('Digikey_PN', ''),
                'Digikey_URL': row.get('Digikey_URL', ''),
                'Farnell_PN': row.get('Farnell_PN', ''),
                'Farnell_URL': row.get('Farnell_URL', ''),
                'Newark_PN': row.get('Newark_PN', ''),
                'Newark_URL': row.get('Newark_URL', ''),
                'RS_PN': row.get('RS_PN', ''),
                'RS_URL': row.get('RS_URL', ''),
                'Notes': row.get('Notes', '') + (' ' + row.get('Tags', '') if row.get('Tags') else ''),
            }

            # Campos específicos
            data['Pin_Configuration'] = pin_config
            data['Pitch'] = pitch
            data['Orientation'] = orientation
            data['Termination_Style'] = row.get('Termination_Style', '')
            data['Current_Rating'] = row.get('Current_Rating_A', '')
            data['Voltage_Rating'] = row.get('Voltage_Rating_V', '')
            t_min = row.get('Operating_Temp_Min_C', '')
            t_max = row.get('Operating_Temp_Max_C', '')
            if t_min and t_max:
                data['Temperature_Range'] = f"{t_min} to {t_max} °C"
            w_min = row.get('Wire_Gauge_AWG_MIN', '')
            w_max = row.get('Wire_Gauge_AWG_MAX', '')
            if w_min and w_max:
                data['Wire_Gauge'] = f"{w_min}-{w_max} AWG"
            data['Family_Series'] = row.get('Series', '')

            insert_data.append(data)

        if not insert_data:
            print("Erro: Nenhum dado válido para inserir.")
            return

        # Determinar quais colunas da tabela realmente têm dados não vazios em pelo menos uma linha
        all_columns_set = set()
        for data in insert_data:
            for k, v in data.items():
                if v is not None and v != '':
                    all_columns_set.add(k)

        # Ordenar conforme a ordem da tabela
        final_columns = [col for col in TABLE_COLUMNS_ORDER if col in all_columns_set]

        if not final_columns:
            print("Erro: Nenhuma coluna válida para inserir.")
            return

        # Preparar saída
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
    csv_file = os.path.join(SCRIPT_DIR, 'Connector_Block.csv')
    output_file = os.path.join(SCRIPT_DIR, 'inserts_block.sql')
    table_name = 'Connector_Block'

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