import os
import sys

# Diretório onde o script está localizado
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Lista ordenada de todas as colunas da tabela Fuse (baseada no CREATE TABLE, exceto ID_Aux)
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

def safe_float(val):
    try:
        return float(val) if val else None
    except:
        return None

def format_current(val):
    """Formata o valor da corrente para o nome, removendo .0 se inteiro."""
    try:
        f = float(val)
        if f.is_integer():
            return f"{int(f)}A"
        else:
            s = f"{f:.3f}".rstrip('0').rstrip('.')
            return f"{s}A"
    except:
        return f"{val}A"

def generate_insert(output_path=None, start_id=910001):
    # Dados da série 154 Fast-Acting (fusíveis 451/453) extraídos da primeira imagem
    fuse_154_data = [
        {'current': 0.062, 'voltage': 125, 'interrupt': '', 'resistance': 5.5000, 'i2t': 0.00019},
        {'current': 0.080, 'voltage': 125, 'interrupt': '', 'resistance': 4.0500, 'i2t': 0.00033},
        {'current': 0.100, 'voltage': 125, 'interrupt': '', 'resistance': 3.1000, 'i2t': 0.00138},
        {'current': 0.125, 'voltage': 125, 'interrupt': '', 'resistance': 1.7000, 'i2t': 0.00286},
        {'current': 0.160, 'voltage': 125, 'interrupt': '', 'resistance': 1.2157, 'i2t': 0.0048},
        {'current': 0.200, 'voltage': 125, 'interrupt': '', 'resistance': 0.8372, 'i2t': 0.0089},
        {'current': 0.250, 'voltage': 125, 'interrupt': '', 'resistance': 0.5765, 'i2t': 0.0158},
        {'current': 0.315, 'voltage': 125, 'interrupt': '50A @ 125VAC/VDC; 300A @ 32VDC; PSE: 100A @ 100VAC', 'resistance': 0.3918, 'i2t': 0.0311},
        {'current': 0.375, 'voltage': 125, 'interrupt': '', 'resistance': 0.4541, 'i2t': 0.0442},
        {'current': 0.400, 'voltage': 125, 'interrupt': '', 'resistance': 0.4233, 'i2t': 0.0551},
        {'current': 0.500, 'voltage': 125, 'interrupt': '', 'resistance': 0.3046, 'i2t': 0.0824},
        {'current': 0.630, 'voltage': 125, 'interrupt': '', 'resistance': 0.2022, 'i2t': 0.1381},
        {'current': 0.750, 'voltage': 125, 'interrupt': '', 'resistance': 0.1444, 'i2t': 0.2143},
        {'current': 0.800, 'voltage': 125, 'interrupt': '', 'resistance': 0.1355, 'i2t': 0.2654},
        {'current': 1.00, 'voltage': 125, 'interrupt': '', 'resistance': 0.0780, 'i2t': 0.6029},
        {'current': 1.25, 'voltage': 125, 'interrupt': '', 'resistance': 0.0780, 'i2t': 0.6624},
        {'current': 1.50, 'voltage': 125, 'interrupt': '', 'resistance': 0.0630, 'i2t': 0.853},
        {'current': 1.60, 'voltage': 125, 'interrupt': '', 'resistance': 0.0580, 'i2t': 1.060},
        {'current': 2.00, 'voltage': 125, 'interrupt': '50A @ 125VAC/VDC; 10,000A @ 75VDC; PSE: 100A @ 100VAC', 'resistance': 0.0367, 'i2t': 0.530},
        {'current': 2.50, 'voltage': 125, 'interrupt': '', 'resistance': 0.0286, 'i2t': 1.029},
        {'current': 3.00, 'voltage': 125, 'interrupt': '', 'resistance': 0.0227, 'i2t': 1.650},
        {'current': 3.15, 'voltage': 125, 'interrupt': '', 'resistance': 0.0215, 'i2t': 1.920},
        {'current': 3.50, 'voltage': 125, 'interrupt': '', 'resistance': 0.0200, 'i2t': 2.469},
        {'current': 4.00, 'voltage': 125, 'interrupt': '', 'resistance': 0.0160, 'i2t': 3.152},
        {'current': 5.00, 'voltage': 125, 'interrupt': '', 'resistance': 0.0125, 'i2t': 5.566},
        {'current': 6.30, 'voltage': 125, 'interrupt': '', 'resistance': 0.0096, 'i2t': 9.170},
        {'current': 7.00, 'voltage': 125, 'interrupt': '', 'resistance': 0.0090, 'i2t': 10.32},
        {'current': 8.00, 'voltage': 125, 'interrupt': '', 'resistance': 0.0077, 'i2t': 20.23},
        {'current': 10.0, 'voltage': 125, 'interrupt': '35A @ 125VAC / 50A @ 125VDC; PSE: 100A @ 100VAC', 'resistance': 0.0056, 'i2t': 26.46},
        {'current': 12.0, 'voltage': 65, 'interrupt': '150A @ 65VDC; 100A @ 65VAC; 400A @ 32VDC', 'resistance': 0.0049, 'i2t': 47.97},
        {'current': 15.0, 'voltage': 65, 'interrupt': '', 'resistance': 0.0037, 'i2t': 97.82},
        {'current': 20.0, 'voltage': 65, 'interrupt': '', 'resistance': 0.00244, 'i2t': 154},
    ]

    # Dados do MINI® Shunt (segunda imagem)
    mini_shunt_data = [
        {'pn': '0297002', 'current': 2, 'voltage': 32, 'interrupt': '1000A @ 32VDC', 'resistance_mohm': 55.60, 'i2t': 9, 'voltage_drop': 171},
        {'pn': '0297003', 'current': 3, 'voltage': 32, 'interrupt': '1000A @ 32VDC', 'resistance_mohm': 33.75, 'i2t': 20, 'voltage_drop': 153},
        {'pn': '0297004', 'current': 4, 'voltage': 32, 'interrupt': '1000A @ 32VDC', 'resistance_mohm': 23.48, 'i2t': 31, 'voltage_drop': 121},
        {'pn': '0297005', 'current': 5, 'voltage': 32, 'interrupt': '1000A @ 32VDC', 'resistance_mohm': 17.75, 'i2t': 37, 'voltage_drop': 129},
        {'pn': '029707.5', 'current': 7.5, 'voltage': 32, 'interrupt': '1000A @ 32VDC', 'resistance_mohm': 10.85, 'i2t': 82, 'voltage_drop': 135},
        {'pn': '0297010', 'current': 10, 'voltage': 32, 'interrupt': '1000A @ 32VDC', 'resistance_mohm': 7.42, 'i2t': 122, 'voltage_drop': 108},
        {'pn': '0297015', 'current': 15, 'voltage': 32, 'interrupt': '1000A @ 32VDC', 'resistance_mohm': 4.58, 'i2t': 308, 'voltage_drop': 98},
        {'pn': '0297020', 'current': 20, 'voltage': 32, 'interrupt': '1000A @ 32VDC', 'resistance_mohm': 3.21, 'i2t': 442, 'voltage_drop': 96},
        {'pn': '0297025', 'current': 25, 'voltage': 32, 'interrupt': '1000A @ 32VDC', 'resistance_mohm': 2.36, 'i2t': 622, 'voltage_drop': 86},
        {'pn': '0297030', 'current': 30, 'voltage': 32, 'interrupt': '1000A @ 32VDC', 'resistance_mohm': 1.85, 'i2t': 1230, 'voltage_drop': 87},
        # SHUNT (sem corrente) - podemos ignorar ou tratar como item especial
        # {'pn': '0297900', 'current': None, 'voltage': 32, 'interrupt': '', 'resistance_mohm': None, 'i2t': None, 'voltage_drop': None},
    ]

    # Símbolo fixo para fusíveis
    symbol = "MyLib_Fuse:Fuse"

    insert_data = []
    mypn_counter = start_id

    # Processar série 154
    for item in fuse_154_data:
        current = item['current']
        voltage = item['voltage']
        resistance = item['resistance']
        i2t = item['i2t']
        interrupt = item['interrupt']

        # Gerar Manufacturer_PN para fast-acting 451/453 (formato 0451.xxx)
        # O código da corrente: para 0.062, é .062; para 1.00, é .001 (conforme tabela)
        # Vamos usar o valor da corrente com três casas decimais, removendo ponto.
        # Ex: 0.062 -> "0451.062"
        if current < 1.0:
            code = f"{current:.3f}".lstrip('0')  # ".062"
        else:
            # Para 1.0, 1.25, etc., usar o valor sem zeros desnecessários
            if current == 1.0:
                code = ".001"
            elif current == 1.25:
                code = "1.25"
            elif current == 1.5:
                code = "1.50"
            elif current == 1.6:
                code = "1.60"
            elif current == 2.0:
                code = ".002"
            elif current == 2.5:
                code = "2.50"
            elif current == 3.0:
                code = "3.00"
            elif current == 3.15:
                code = "3.15"
            elif current == 3.5:
                code = "3.50"
            elif current == 4.0:
                code = "4.00"
            elif current == 5.0:
                code = "5.00"
            elif current == 6.3:
                code = "6.30"
            elif current == 7.0:
                code = "7.00"
            elif current == 8.0:
                code = "8.00"
            elif current == 10.0:
                code = "10.0"
            elif current == 12.0:
                code = "12.0"
            elif current == 15.0:
                code = "15.0"
            elif current == 20.0:
                code = "20.0"
            else:
                code = str(current).replace('.', '')

        manufacturer_pn = f"0451.{code}"
        name = f"FUSE_154_{format_current(current)}"
        description = f"Fast-Acting Fuse, {current}A, {voltage}V, Nano2 SMF, 451/453 Series"
        voltage_rating = f"{voltage} V"
        current_rating = f"{current} A"
        resistance_str = f"{resistance} Ohm" if resistance else None
        i2t_str = f"{i2t} A²s" if i2t else None
        interrupting = interrupt if interrupt else None

        # Notas
        notes_parts = []
        if i2t_str:
            notes_parts.append(f"I²t: {i2t_str}")
        if interrupt:
            notes_parts.append(f"Interrupting: {interrupt}")
        notes = '; '.join(notes_parts) if notes_parts else None

        data = {
            'MyPN': f"EL-FUSE-{mypn_counter:06d}",
            'Name': name,
            'Description': description,
            'Value': manufacturer_pn,
            'Symbol': symbol,
            'Footprint': "MyLib_Fuse:Fuseholder_Littelfuse_Nano2_154x",  # conjunto holder + fusível
            'Manufacturer': "Littelfuse",
            'Manufacturer_PN': manufacturer_pn,
            'Family_Series': "154",
            'Voltage_Rating': voltage_rating,
            'Current_Rating': current_rating,
            'Resistance': resistance_str,
            'Interrupting_Rating': interrupting,
            'Notes': notes,
            'Active': 1,
            'Version': 1,
            'Exclude_from_BOM': 0,
            'Exclude_from_Board': 0,
        }
        insert_data.append(data)
        mypn_counter += 1

    # Processar MINI Shunt
    for item in mini_shunt_data:
        current = item['current']
        pn = item['pn']
        voltage = item['voltage']
        interrupt = item['interrupt']
        resistance_mohm = item['resistance_mohm']
        i2t = item['i2t']
        # voltage_drop opcional

        name = f"FUSE_MINI_{format_current(current)}"
        description = f"MINI® 32V Automotive Blade Fuse, {current}A, {voltage}V"
        manufacturer_pn = pn  # usar o part number exato
        voltage_rating = f"{voltage} V"
        current_rating = f"{current} A"
        resistance_str = f"{resistance_mohm / 1000:.4f} Ohm" if resistance_mohm else None  # converter mOhm para Ohm
        i2t_str = f"{i2t} A²s" if i2t else None
        interrupting = interrupt

        notes_parts = []
        if i2t_str:
            notes_parts.append(f"I²t: {i2t_str}")
        if item.get('voltage_drop'):
            notes_parts.append(f"Voltage Drop: {item['voltage_drop']} mV")
        notes = '; '.join(notes_parts) if notes_parts else None

        data = {
            'MyPN': f"EL-FUSE-{mypn_counter:06d}",
            'Name': name,
            'Description': description,
            'Value': manufacturer_pn,
            'Symbol': symbol,
            'Footprint': "MyLib_Fuse:Fuse_Blade_Mini_directSolder",
            'Manufacturer': "Littelfuse",
            'Manufacturer_PN': manufacturer_pn,
            'Family_Series': "MINI",
            'Voltage_Rating': voltage_rating,
            'Current_Rating': current_rating,
            'Resistance': resistance_str,
            'Interrupting_Rating': interrupting,
            'Notes': notes,
            'Active': 1,
            'Version': 1,
            'Exclude_from_BOM': 0,
            'Exclude_from_Board': 0,
        }
        insert_data.append(data)
        mypn_counter += 1

    if not insert_data:
        print("Erro: Nenhum dado para inserir.")
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
    sql = f"INSERT INTO Fuse ({columns_str}) VALUES\n{values_str};\n"
    out.write(sql)

    if output_path:
        out.close()
        print(f"Arquivo SQL gerado: {output_path}")

def main():
    output_file = os.path.join(SCRIPT_DIR, 'inserts_fuse_littelfuse.sql')
    generate_insert(output_file, start_id=100)

if __name__ == '__main__':
    main()