import csv
import os
import sys
import re

# Diretório onde o script está localizado
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Lista ordenada de todas as colunas da tabela Connector_General (baseada na CREATE TABLE Relay, exceto ID_AUX)
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

def safe_int(val):
    """Converte para int se possível, senão retorna None."""
    try:
        return int(val) if val else None
    except:
        return None

def safe_float(val):
    """Converte para float se possível, senão retorna None."""
    try:
        return float(val) if val else None
    except:
        return None

def clean_series(series):
    """Substitui espaços por hífen e remove caracteres especiais."""
    if not series:
        return ''
    # Remove espaços extras e substitui espaços por hífen
    series = re.sub(r'\s+', '-', series.strip())
    # Remove pontos ou vírgulas? Vamos manter apenas alfanuméricos e hífen
    series = re.sub(r'[^a-zA-Z0-9\-]', '', series)
    return series

def generate_molex_name(row):
    """Gera o nome padronizado para conectores Molex."""
    pins = safe_int(row.get('Pins_Total', '0'))
    if not pins:
        pins = 0
    pitch = row.get('Pitch_mm', '').strip()
    gender = row.get('Gender', '').strip().lower()
    orientation = row.get('Orientation', '').strip().lower()
    mount = row.get('Mounting_Type', '').strip().lower()

    # Determinar gênero (M/F)
    if 'male' in gender:
        gender_letter = 'M'
    elif 'female' in gender:
        gender_letter = 'F'
    else:
        gender_letter = ''

    # Determinar orientação
    if 'vertical' in orientation:
        orient_letter = 'V'
    elif 'right angle' in orientation or 'horizontal' in orientation:
        orient_letter = 'RA'  # Right Angle
    else:
        orient_letter = ''

    # Determinar montagem
    if 'through hole' in mount:
        mount_code = 'THT'
    elif 'smt' in mount or 'surface mount' in mount:
        mount_code = 'SMT'
    else:
        mount_code = ''

    # Extrair série do campo Series
    series_raw = row.get('Series', '').strip()
    series_clean = clean_series(series_raw)

    # Formatar número de posições com dois dígitos
    pins_str = f"{pins:02d}" if pins else ''

    # Construir nome
    name_parts = ['CON', 'MOLEX']
    if series_clean:
        name_parts.append(series_clean)
    if pins_str:
        name_parts.append(pins_str)
    if pitch:
        name_parts.append(f"P{pitch}mm")
    if gender_letter:
        name_parts.append(gender_letter)
    if orient_letter:
        name_parts.append(orient_letter)
    if mount_code:
        name_parts.append(mount_code)

    return '_'.join(name_parts)

def generate_insert(csv_path, table_name, output_path=None, start_id=1):
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
        mypn_counter = start_id

        for row in rows:
            # Gerar MyPN sequencial
            mypn = f"EL-CON_{mypn_counter:06d}"
            mypn_counter += 1

            # Dados básicos
            manufacturer = row.get('Manufacturer', '').strip()
            manufacturer_pn = row.get('Manufacturer_PN', '').strip()
            description = row.get('Description', '').strip()
            value = manufacturer_pn if manufacturer_pn else None

            # Determinar Name e Info2
            if 'molex' in manufacturer.lower():
                # Para Molex, gerar nome padronizado e colocar PN em Info2
                name = generate_molex_name(row)
                info2 = manufacturer_pn
            else:
                # Para outros, manter o nome original e Info2 vazio
                name = row.get('Name', '').strip()
                info2 = None

            # Construir Notes com informações adicionais
            notes_parts = []
            if row.get('Shielded', ''):
                notes_parts.append(f"Shielded: {row['Shielded']}")
            if row.get('Contact_Resistance_mOhm', ''):
                notes_parts.append(f"Contact Resistance: {row['Contact_Resistance_mOhm']} mOhm")
            if row.get('Insulation_Resistance_MOhm', ''):
                notes_parts.append(f"Insulation Resistance: {row['Insulation_Resistance_MOhm']} MOhm")
            if row.get('Dielectric_Withstanding_Voltage_V', ''):
                notes_parts.append(f"Dielectric Withstanding: {row['Dielectric_Withstanding_Voltage_V']} V")
            if row.get('Impedance_Ohm', ''):
                notes_parts.append(f"Impedance: {row['Impedance_Ohm']} Ohm")
            if row.get('Contact_Material', ''):
                notes_parts.append(f"Contact Material: {row['Contact_Material']}")
            if row.get('Contact_Plating', ''):
                notes_parts.append(f"Contact Plating: {row['Contact_Plating']}")
            if row.get('Plating_Thickness_um', ''):
                notes_parts.append(f"Plating Thickness: {row['Plating_Thickness_um']} µm")
            if row.get('Contact_Finish', ''):
                notes_parts.append(f"Contact Finish: {row['Contact_Finish']}")
            if row.get('Housing_Material', ''):
                notes_parts.append(f"Housing Material: {row['Housing_Material']}")
            if row.get('Insulator_Material', ''):
                notes_parts.append(f"Insulator Material: {row['Insulator_Material']}")
            if row.get('Polarization', ''):
                notes_parts.append(f"Polarization: {row['Polarization']}")
            if row.get('Insertion_Force_N', ''):
                notes_parts.append(f"Insertion Force: {row['Insertion_Force_N']} N")
            if row.get('Withdrawal_Force_N', ''):
                notes_parts.append(f"Withdrawal Force: {row['Withdrawal_Force_N']} N")
            if row.get('Storage_Temp_Min_C', '') and row.get('Storage_Temp_Max_C', ''):
                notes_parts.append(f"Storage Temp: {row['Storage_Temp_Min_C']} to {row['Storage_Temp_Max_C']} °C")
            if row.get('Moisture_Sensitivity_Level', ''):
                notes_parts.append(f"MSL: {row['Moisture_Sensitivity_Level']}")
            if row.get('UL_Certified', ''):
                notes_parts.append(f"UL Certified: {row['UL_Certified']}")
            if row.get('CSA_Certified', ''):
                notes_parts.append(f"CSA Certified: {row['CSA_Certified']}")
            if row.get('TUV_Certified', ''):
                notes_parts.append(f"TUV Certified: {row['TUV_Certified']}")
            if row.get('Solder_Type', ''):
                notes_parts.append(f"Solder Type: {row['Solder_Type']}")
            if row.get('Solder_Temperature_C', ''):
                notes_parts.append(f"Solder Temp: {row['Solder_Temperature_C']} °C")
            if row.get('Solder_Process', ''):
                notes_parts.append(f"Solder Process: {row['Solder_Process']}")
            if row.get('Cleaning_Process', ''):
                notes_parts.append(f"Cleaning: {row['Cleaning_Process']}")
            if row.get('PCB_Retention', ''):
                notes_parts.append(f"PCB Retention: {row['PCB_Retention']}")
            if row.get('Pick_and_Place', ''):
                notes_parts.append(f"Pick & Place: {row['Pick_and_Place']}")
            if row.get('Tape_and_Reel', ''):
                notes_parts.append(f"Tape & Reel: {row['Tape_and_Reel']}")
            if row.get('Cable_Type', ''):
                notes_parts.append(f"Cable Type: {row['Cable_Type']}")
            if row.get('Cable_Diameter_Max_mm', ''):
                notes_parts.append(f"Cable Dia Max: {row['Cable_Diameter_Max_mm']} mm")
            if row.get('Wire_Gauge_AWG', ''):
                notes_parts.append(f"Wire Gauge: {row['Wire_Gauge_AWG']} AWG")
            if row.get('Wire_Strip_Length_mm', ''):
                notes_parts.append(f"Strip Length: {row['Wire_Strip_Length_mm']} mm")
            # Adicionar Tags se existir
            if row.get('Tags', ''):
                notes_parts.append(f"Tags: {row['Tags']}")

            notes = '; '.join(notes_parts) if notes_parts else None

            # Dimensões
            dims = []
            if row.get('Length_mm', ''):
                dims.append(f"L={row['Length_mm']}mm")
            if row.get('Width_mm', ''):
                dims.append(f"W={row['Width_mm']}mm")
            if row.get('Height_mm', ''):
                dims.append(f"H={row['Height_mm']}mm")
            if row.get('Mating_Height_mm', ''):
                dims.append(f"Mating H={row['Mating_Height_mm']}mm")
            if row.get('PCB_Mounting_Dimensions', ''):
                dims.append(f"PCB Mount: {row['PCB_Mounting_Dimensions']}")
            dimensions = ', '.join(dims) if dims else None

            # Temperatura de operação
            t_min = row.get('Operating_Temp_Min_C', '')
            t_max = row.get('Operating_Temp_Max_C', '')
            temp_range = None
            if t_min and t_max:
                temp_range = f"{t_min} to {t_max} °C"
            elif t_min:
                temp_range = f"min {t_min} °C"
            elif t_max:
                temp_range = f"max {t_max} °C"

            # Resistência de contato (colocar em Resistance)
            resistance = None
            if row.get('Contact_Resistance_mOhm', ''):
                resistance = f"{row['Contact_Resistance_mOhm']} mOhm"

            # Frequência
            frequency = None
            if row.get('Frequency_Max_Hz', ''):
                freq_val = row['Frequency_Max_Hz']
                # Converter para string com unidade
                if 'MHz' in freq_val:
                    frequency = freq_val
                else:
                    try:
                        f = float(freq_val)
                        if f >= 1e9:
                            frequency = f"{f/1e9} GHz"
                        elif f >= 1e6:
                            frequency = f"{f/1e6} MHz"
                        elif f >= 1e3:
                            frequency = f"{f/1e3} kHz"
                        else:
                            frequency = f"{f} Hz"
                    except:
                        frequency = freq_val

            # Corrente nominal
            current_rating = None
            if row.get('Current_Rating_A', ''):
                current_rating = f"{row['Current_Rating_A']} A"

            # Tensão nominal
            voltage_rating = None
            if row.get('Voltage_Rating_V', ''):
                voltage_rating = f"{row['Voltage_Rating_V']} V"

            # Pitch
            pitch = None
            if row.get('Pitch_mm', ''):
                pitch = f"{row['Pitch_mm']} mm"

            # Mapeamento direto
            data = {
                'MyPN': mypn,
                'Name': name,
                'Description': description,
                'Value': value,
                'Info1': None,
                'Info2': info2,
                'Symbol': row.get('Symbol', ''),
                'Footprint': row.get('Footprint', ''),
                'Footprint_Filter': row.get('Footprint_Filter', ''),
                'Datasheet': row.get('Datasheet', ''),
                'Notes': notes,
                'Manufacturer': manufacturer,
                'Manufacturer_PN': manufacturer_pn,
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
                'Stock_Qty': safe_int(row.get('StockQty', '0')),
                'Stock_Location': row.get('StockPlace', ''),
                'Price': row.get('Price', ''),
                'Currency': row.get('Currency', 'USD'),
                'Min_Stock': safe_int(row.get('Min_Stock', '0')),
                'Max_Stock': safe_int(row.get('Max_Stock', '0')),
                'Active': 1,
                'Version': 1,
                'Created_At': row.get('CreatedAt', ''),
                'Created_By': row.get('CreatedBy', ''),
                'Modified_At': row.get('ModifiedAt', ''),
                'Modified_By': row.get('ModifiedBy', ''),
                'Exclude_from_BOM': safe_int(row.get('Exclude_from_BOM', '0')),
                'Exclude_from_Board': safe_int(row.get('Exclude_from_Board', '0')),
                'Category': row.get('Category', ''),
                'Subcategory': row.get('Subcategory', ''),
                'Family_Series': row.get('Series', ''),
                'Package': row.get('Package', ''),
                'Mount': row.get('Mounting_Type', ''),
                'Dimensions': dimensions,
                'Temperature_Range': temp_range,
                'RoHS_Compliant': safe_int(row.get('RoHS_Compliant', '0')),
                'REACH_Compliant': safe_int(row.get('REACH_Compliant', '0')),
                'Voltage_Rating': voltage_rating,
                'Current_Rating': current_rating,
                'Pin_Configuration': row.get('Pins_Configuration', ''),
                'Gender': row.get('Gender', ''),
                'Pin_Type': row.get('Contact_Type', ''),
                'Pitch': pitch,
                'Orientation': row.get('Orientation', ''),
                'Locking_Mechanism': row.get('Locking_Mechanism', ''),
                'IP_Rating': row.get('IP_Rating', ''),
                'Wire_Gauge': row.get('Wire_Gauge_AWG', ''),
                'Termination_Style': row.get('Solder_Type', ''),  # aproximação
                'Resistance': resistance,
                'Frequency': frequency,
                'Color': row.get('Housing_Color', '') or row.get('Insulator_Color', ''),
                'Mating_Cycles': safe_int(row.get('Mating_Cycles', '')),
                'Flammability_Rating': row.get('Flammability_Rating', ''),
            }

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
    csv_file = os.path.join(SCRIPT_DIR, 'Connector_General.csv')
    output_file = os.path.join(SCRIPT_DIR, 'inserts_general.sql')
    table_name = 'Connector_General'

    # Aceita argumentos da linha de comando
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2:
        table_name = sys.argv[2]
    if len(sys.argv) > 3:
        output_file = sys.argv[3]

    generate_insert(csv_file, table_name, output_file, start_id=1)

if __name__ == '__main__':
    main()