import csv
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
            # Remove zeros desnecessários
            s = f"{f:.1f}".rstrip('0').rstrip('.') if '.' in f"{f:.1f}" else f"{f:.1f}"
            return f"{s}A"
    except:
        return f"{val}A"

def generate_insert(output_path=None, start_id=900001):
    # Série MF-RG (dados extraídos da primeira imagem)
    rg_series = [
        {'model': 'MF-RG300', 'vmax': 16, 'imax': 100, 'ihold': 3.0, 'itrip': 5.1,
         'r_min': 0.0380, 'r1_max': 0.0650, 'time_trip_amps': 15, 'time_trip_sec': 1.0,
         'power_diss': 2.3},
        {'model': 'MF-RG400', 'vmax': 16, 'imax': 100, 'ihold': 4.0, 'itrip': 6.8,
         'r_min': 0.0210, 'r1_max': 0.0385, 'time_trip_amps': 20, 'time_trip_sec': 1.7,
         'power_diss': 2.4},
        {'model': 'MF-RG500', 'vmax': 16, 'imax': 100, 'ihold': 5.0, 'itrip': 8.5,
         'r_min': 0.0150, 'r1_max': 0.0230, 'time_trip_amps': 25, 'time_trip_sec': 2.0,
         'power_diss': 2.6},
        {'model': 'MF-RG600', 'vmax': 16, 'imax': 100, 'ihold': 6.0, 'itrip': 10.2,
         'r_min': 0.0100, 'r1_max': 0.0185, 'time_trip_amps': 30, 'time_trip_sec': 3.3,
         'power_diss': 2.8},
        {'model': 'MF-RG650', 'vmax': 16, 'imax': 100, 'ihold': 6.5, 'itrip': 11.1,
         'r_min': 0.0088, 'r1_max': 0.0158, 'time_trip_amps': 33, 'time_trip_sec': 3.5,
         'power_diss': 3.0},
        {'model': 'MF-RG700', 'vmax': 16, 'imax': 100, 'ihold': 7.0, 'itrip': 11.9,
         'r_min': 0.0077, 'r1_max': 0.0130, 'time_trip_amps': 35, 'time_trip_sec': 3.5,
         'power_diss': 3.0},
        {'model': 'MF-RG800', 'vmax': 16, 'imax': 100, 'ihold': 8.0, 'itrip': 13.6,
         'r_min': 0.0056, 'r1_max': 0.0110, 'time_trip_amps': 40, 'time_trip_sec': 5.0,
         'power_diss': 3.0},
        {'model': 'MF-RG900', 'vmax': 16, 'imax': 100, 'ihold': 9.0, 'itrip': 15.3,
         'r_min': 0.0047, 'r1_max': 0.0092, 'time_trip_amps': 45, 'time_trip_sec': 5.5,
         'power_diss': 3.3},
        {'model': 'MF-RG1000', 'vmax': 16, 'imax': 100, 'ihold': 10.0, 'itrip': 17.0,
         'r_min': 0.0040, 'r1_max': 0.0071, 'time_trip_amps': 50, 'time_trip_sec': 6.0,
         'power_diss': 3.6},
        {'model': 'MF-RG1100', 'vmax': 16, 'imax': 100, 'ihold': 11.0, 'itrip': 18.7,
         'r_min': 0.0037, 'r1_max': 0.0062, 'time_trip_amps': 55, 'time_trip_sec': 7.0,
         'power_diss': 3.7},
    ]

    # Série MF-RHT (dados extraídos da segunda imagem)
    rht_series = [
        {'model': 'MF-RHT050', 'vmax': 30, 'imax': 40, 'ihold': 0.5, 'itrip': 0.92,
         'r_min': 0.48, 'r1_max': 1.10, 'time_trip_amps': 2.5, 'time_trip_sec': 2.5,
         'power_diss': 0.9},
        {'model': 'MF-RHT070', 'vmax': 30, 'imax': 40, 'ihold': 0.7, 'itrip': 1.4,
         'r_min': 0.30, 'r1_max': 0.80, 'time_trip_amps': 3.5, 'time_trip_sec': 4.0,
         'power_diss': 1.4},
        {'model': 'MF-RHT100', 'vmax': 30, 'imax': 40, 'ihold': 1.0, 'itrip': 1.8,
         'r_min': 0.18, 'r1_max': 0.43, 'time_trip_amps': 5.2, 'time_trip_sec': 5.0,
         'power_diss': 1.4},
        {'model': 'MF-RHT200', 'vmax': 16, 'imax': 100, 'ihold': 2.0, 'itrip': 3.8,
         'r_min': 0.045, 'r1_max': 0.110, 'time_trip_amps': 12.5, 'time_trip_sec': 3.0,
         'power_diss': 1.4},
        {'model': 'MF-RHT200/32', 'vmax': 32, 'imax': 50, 'ihold': 2.0, 'itrip': 3.8,
         'r_min': 0.045, 'r1_max': 0.110, 'time_trip_amps': 12.5, 'time_trip_sec': 3.0,
         'power_diss': 1.4},
        {'model': 'MF-RHT300', 'vmax': 16, 'imax': 100, 'ihold': 3.0, 'itrip': 6.0,
         'r_min': 0.033, 'r1_max': 0.079, 'time_trip_amps': 15.0, 'time_trip_sec': 5.0,
         'power_diss': 3.0},
        {'model': 'MF-RHT400', 'vmax': 16, 'imax': 100, 'ihold': 4.0, 'itrip': 7.5,
         'r_min': 0.024, 'r1_max': 0.060, 'time_trip_amps': 20.0, 'time_trip_sec': 5.0,
         'power_diss': 3.3},
        {'model': 'MF-RHT450', 'vmax': 16, 'imax': 100, 'ihold': 4.5, 'itrip': 7.8,
         'r_min': 0.022, 'r1_max': 0.054, 'time_trip_amps': 22.5, 'time_trip_sec': 3.0,
         'power_diss': 3.6},
        {'model': 'MF-RHT500', 'vmax': 16, 'imax': 100, 'ihold': 5.0, 'itrip': 9.0,
         'r_min': 0.0175, 'r1_max': 0.045, 'time_trip_amps': 25.0, 'time_trip_sec': 9.0,
         'power_diss': 3.6},
        {'model': 'MF-RHT550', 'vmax': 16, 'imax': 100, 'ihold': 5.5, 'itrip': 10.0,
         'r_min': 0.0150, 'r1_max': 0.037, 'time_trip_amps': 27.5, 'time_trip_sec': 6.0,
         'power_diss': 3.5},
        {'model': 'MF-RHT600', 'vmax': 16, 'imax': 100, 'ihold': 6.0, 'itrip': 10.8,
         'r_min': 0.0130, 'r1_max': 0.032, 'time_trip_amps': 30.0, 'time_trip_sec': 5.0,
         'power_diss': 4.1},
        {'model': 'MF-RHT650', 'vmax': 16, 'imax': 100, 'ihold': 6.5, 'itrip': 12.0,
         'r_min': 0.0110, 'r1_max': 0.026, 'time_trip_amps': 32.5, 'time_trip_sec': 5.5,
         'power_diss': 4.3},
        {'model': 'MF-RHT700', 'vmax': 16, 'imax': 100, 'ihold': 7.0, 'itrip': 13.0,
         'r_min': 0.0100, 'r1_max': 0.025, 'time_trip_amps': 35.0, 'time_trip_sec': 7.0,
         'power_diss': 4.0},
        {'model': 'MF-RHT750', 'vmax': 16, 'imax': 100, 'ihold': 7.5, 'itrip': 13.1,
         'r_min': 0.0094, 'r1_max': 0.022, 'time_trip_amps': 37.5, 'time_trip_sec': 7.0,
         'power_diss': 4.5},
        {'model': 'MF-RHT800', 'vmax': 16, 'imax': 100, 'ihold': 8.0, 'itrip': 15.0,
         'r_min': 0.0080, 'r1_max': 0.020, 'time_trip_amps': 40.0, 'time_trip_sec': 8.0,
         'power_diss': 4.2},
        {'model': 'MF-RHT900', 'vmax': 16, 'imax': 100, 'ihold': 9.0, 'itrip': 16.5,
         'r_min': 0.0074, 'r1_max': 0.017, 'time_trip_amps': 45.0, 'time_trip_sec': 10.0,
         'power_diss': 5.0},
        {'model': 'MF-RHT1000', 'vmax': 16, 'imax': 100, 'ihold': 10.0, 'itrip': 18.5,
         'r_min': 0.0062, 'r1_max': 0.015, 'time_trip_amps': 50.0, 'time_trip_sec': 9.0,
         'power_diss': 5.3},
        {'model': 'MF-RHT1100', 'vmax': 16, 'imax': 100, 'ihold': 11.0, 'itrip': 20.0,
         'r_min': 0.0055, 'r1_max': 0.013, 'time_trip_amps': 55.0, 'time_trip_sec': 11.0,
         'power_diss': 5.5},
        {'model': 'MF-RHT1300', 'vmax': 16, 'imax': 100, 'ihold': 13.0, 'itrip': 24.0,
         'r_min': 0.0041, 'r1_max': 0.010, 'time_trip_amps': 60.0, 'time_trip_sec': 13.0,
         'power_diss': 6.9},
    ]

    # Série MF-SM (dados extraídos da terceira imagem)
    sm_series = [
        {'model': 'MF-SM030', 'vmax': 60, 'imax': 40, 'ihold': 0.30, 'itrip': 0.60,
         'r_min': 0.90, 'r1_max': 4.80, 'time_trip_amps': 1.5, 'time_trip_sec': 3.0,
         'power_diss': 1.7},
        {'model': 'MF-SM050', 'vmax': 60, 'imax': 40, 'ihold': 0.50, 'itrip': 1.00,
         'r_min': 0.35, 'r1_max': 1.40, 'time_trip_amps': 2.5, 'time_trip_sec': 4.0,
         'power_diss': 1.7},
        {'model': 'MF-SM075', 'vmax': 30, 'imax': 80, 'ihold': 0.75, 'itrip': 1.50,
         'r_min': 0.23, 'r1_max': 1.00, 'time_trip_amps': 8.0, 'time_trip_sec': 0.3,
         'power_diss': 1.7},
        {'model': 'MF-SM075/60', 'vmax': 60, 'imax': 10, 'ihold': 0.75, 'itrip': 1.50,
         'r_min': 0.23, 'r1_max': 1.00, 'time_trip_amps': 8.0, 'time_trip_sec': 0.3,
         'power_diss': 1.7},
        {'model': 'MF-SM100', 'vmax': 30, 'imax': 80, 'ihold': 1.10, 'itrip': 2.20,
         'r_min': 0.12, 'r1_max': 0.48, 'time_trip_amps': 8.0, 'time_trip_sec': 0.5,
         'power_diss': 1.7},
        {'model': 'MF-SM100/33', 'vmax': 33, 'imax': 40, 'ihold': 1.10, 'itrip': 2.20,
         'r_min': 0.12, 'r1_max': 0.41, 'time_trip_amps': 8.0, 'time_trip_sec': 0.5,
         'power_diss': 1.7},
        {'model': 'MF-SM125', 'vmax': 15, 'imax': 100, 'ihold': 1.25, 'itrip': 2.50,
         'r_min': 0.07, 'r1_max': 0.25, 'time_trip_amps': 8.0, 'time_trip_sec': 2.0,
         'power_diss': 1.7},
        {'model': 'MF-SM150', 'vmax': 15, 'imax': 100, 'ihold': 1.50, 'itrip': 3.00,
         'r_min': 0.06, 'r1_max': 0.25, 'time_trip_amps': 8.0, 'time_trip_sec': 5.0,
         'power_diss': 1.9},
        {'model': 'MF-SM150/33', 'vmax': 33, 'imax': 40, 'ihold': 1.50, 'itrip': 3.00,
         'r_min': 0.06, 'r1_max': 0.23, 'time_trip_amps': 8.0, 'time_trip_sec': 5.0,
         'power_diss': 1.9},
        {'model': 'MF-SM185/33', 'vmax': 33, 'imax': 40, 'ihold': 1.80, 'itrip': 3.60,
         'r_min': 0.04, 'r1_max': 0.15, 'time_trip_amps': 8.0, 'time_trip_sec': 5.0,
         'power_diss': 1.9},
        {'model': 'MF-SM200', 'vmax': 15, 'imax': 100, 'ihold': 2.00, 'itrip': 4.00,
         'r_min': 0.045, 'r1_max': 0.125, 'time_trip_amps': 8.0, 'time_trip_sec': 12.0,
         'power_diss': 1.9},
        {'model': 'MF-SM250', 'vmax': 15, 'imax': 100, 'ihold': 2.50, 'itrip': 5.00,
         'r_min': 0.024, 'r1_max': 0.085, 'time_trip_amps': 8.0, 'time_trip_sec': 25.0,
         'power_diss': 1.9},
        {'model': 'MF-SM260', 'vmax': 6, 'imax': 100, 'ihold': 2.60, 'itrip': 5.20,
         'r_min': 0.025, 'r1_max': 0.075, 'time_trip_amps': 8.0, 'time_trip_sec': 20.0,
         'power_diss': 1.7},
        {'model': 'MF-SM300', 'vmax': 6, 'imax': 100, 'ihold': 3.00, 'itrip': 6.00,
         'r_min': 0.015, 'r1_max': 0.048, 'time_trip_amps': 8.0, 'time_trip_sec': 35.0,
         'power_diss': 1.5},
    ]

    all_models = rg_series + rht_series + sm_series

    # Símbolo fixo para PTC
    symbol = "MyLib_Fuse:Polyfuse"

    # Mapeamento para MF-SM: modelos menores usam o footprint 7.98x5.44mm, maiores usam 9.5x6.71mm
    sm_small_models = ['MF-SM030', 'MF-SM050', 'MF-SM075', 'MF-SM075/60', 'MF-SM100', 'MF-SM100/33', 'MF-SM125']
    sm_large_models = ['MF-SM150', 'MF-SM150/33', 'MF-SM185/33', 'MF-SM200', 'MF-SM250', 'MF-SM260', 'MF-SM300']

    insert_data = []
    mypn_counter = start_id

    for model_data in all_models:
        model = model_data['model']
        ihold = model_data['ihold']

        # Determinar família
        if model.startswith('MF-RG'):
            family = 'MF-RG'
            desc = f"PTC Resettable Fuse, {model}, {ihold}A hold, {model_data['vmax']}V"
        elif model.startswith('MF-RHT'):
            family = 'MF-RHT'
            desc = f"PTC Resettable Fuse, {model}, {ihold}A hold, {model_data['vmax']}V"
        elif model.startswith('MF-SM'):
            family = 'MF-SM'
            desc = f"PTC Resettable Fuse, {model}, {ihold}A hold, {model_data['vmax']}V"
        else:
            family = 'Bourns PTC'
            desc = f"PTC Resettable Fuse {model}"

        # Determinar footprint
        if model.startswith('MF-RG') or model.startswith('MF-RHT'):
            # Para RG e RHT, gerar diretamente no padrão
            footprint = f"MyLib_Fuse:Fuse_Bourns_{model}"
        elif model.startswith('MF-SM'):
            if model in sm_small_models:
                footprint = "MyLib_Fuse:Fuse_Bourns_MF-SM_7.98x5.44mm"
            elif model in sm_large_models:
                footprint = "MyLib_Fuse:Fuse_Bourns_MF-SM_9.5x6.71mm"
            else:
                footprint = None
        else:
            footprint = None

        if not footprint:
            print(f"Aviso: Nenhum footprint definido para o modelo {model}. O valor será NULL.")

        # Name no formato "FUSE_<modelo>_<Ihold>A"
        current_str = format_current(ihold)
        name = f"FUSE_{model}_{current_str}"

        # Value = modelo
        value = model

        # Manufacturer
        manufacturer = "Bourns"
        manufacturer_pn = model

        # Campos específicos
        voltage_rating = f"{model_data['vmax']} V"
        current_rating = f"{ihold} A"
        hold_current = f"{ihold} A"
        trip_current = f"{model_data['itrip']} A"
        resistance = f"{model_data['r_min']} ~ {model_data['r1_max']} Ohm"
        power_diss = f"{model_data['power_diss']} W"
        response_time = f"{model_data['time_trip_sec']} s at {model_data['time_trip_amps']} A"
        interrupting_rating = f"{model_data['imax']} A"

        # Notas
        notes = f"Trip current: {model_data['itrip']}A; Time to trip: {model_data['time_trip_sec']}s at {model_data['time_trip_amps']}A; Power dissipation: {model_data['power_diss']}W"

        # Criar dicionário com os campos preenchidos
        data = {
            'MyPN': f"EL-FUSE-{mypn_counter:06d}",
            'Name': name,
            'Description': desc,
            'Value': value,
            'Symbol': symbol,
            'Footprint': footprint,
            'Manufacturer': manufacturer,
            'Manufacturer_PN': manufacturer_pn,
            'Family_Series': family,
            'Voltage_Rating': voltage_rating,
            'Current_Rating': current_rating,
            'Hold_Current': hold_current,
            'Trip_Current': trip_current,
            'Resistance': resistance,
            'Power_Dissipation': power_diss,
            'Response_Time': response_time,
            'Interrupting_Rating': interrupting_rating,
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
    output_file = os.path.join(SCRIPT_DIR, 'inserts_fuse.sql')
    generate_insert(output_file, start_id=1)

if __name__ == '__main__':
    main()