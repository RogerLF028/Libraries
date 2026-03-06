import os
import sys

# Diretório onde o script está localizado
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Lista ordenada de todas as colunas da tabela LED (baseada na mesma estrutura genérica)
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

def format_color_name(color):
    """Formata o nome da cor para uso em Name."""
    return color.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

def generate_insert(output_path=None, start_id=940001):
    # Dados para LEDs 0603 (extraídos da tabela do PDF)
    data_0603 = [
        # (prefix, color, material, lumi_min, lumi_typ, lumi_max, wl_min, wl_typ, wl_max, vf_min, vf_typ, vf_max, if_test)
        ('598-8010', 'Red', 'AllnGaP', 30, 60, 90, 625, 633, 640, 1.8, 2.1, 2.4, 20),
        ('598-8020', 'Red-Orange', 'AllnGaP', 120, 225, 330, 620, 625, 630, 1.8, 2.1, 2.4, 20),
        ('598-8030', 'Orange', 'AllnGaP', 70, 120, 200, 600, 605, 610, 1.8, 2.1, 2.4, 20),
        ('598-8040', 'Yellow (AllnGaP)', 'AllnGaP', 120, 160, 200, 590, 592, 595, 1.8, 2.1, 2.4, 20),
        ('598-8050', 'Yellow', 'AllnGaP', 90, 105, 120, 585, 587, 590, 1.8, 2.1, 2.4, 20),
        ('598-8060', 'Yellow-Green', 'AllnGaP', 4, 36, 280, 570, 572, 575, 1.8, 2.1, 2.4, 20),
        ('598-8070', 'Green', 'AllnGaP', 1, 22, 84, 562, 566, 570, 1.8, 2.1, 2.4, 20),
        ('598-8081', 'Green (InGaN)', 'InGaN', 260, 580, 900, 517, 525, 530, 2.8, 3.1, 3.4, 20),
        ('598-8091', 'Blue', 'InGaN', 90, 145, 200, 465, 470, 475, 2.8, 3.2, 3.5, 20),
    ]

    # Dados para LEDs 1206
    data_1206 = [
        ('598-8210', 'Red', 'AllnGaP', 20, 55, 90, 625, 633, 640, 1.8, 2.1, 2.4, 20),
        ('598-8220', 'Red-Orange', 'AllnGaP', 70, 120, 200, 620, 625, 630, 1.8, 2.1, 2.4, 20),
        ('598-8230', 'Orange', 'AllnGaP', 90, 175, 260, 600, 605, 610, 1.8, 2.1, 2.4, 20),
        ('598-8240', 'Yellow', 'AllnGaP', 150, 205, 260, 590, 592, 595, 1.8, 2.1, 2.4, 20),
        ('598-8250', 'Yellow', 'AllnGaP', 90, 120, 150, 585, 587, 590, 1.8, 2.1, 2.4, 20),
        ('598-8260', 'Yellow-Green', 'AllnGaP', 43, 70, 100, 570, 572, 575, 1.8, 2.1, 2.4, 20),
        ('598-8270', 'Green', 'AllnGaP', 18, 30, 43, 562, 566, 570, 1.8, 2.1, 2.4, 20),
        ('598-8281', 'Green (InGaN)', 'InGaN', 260, 580, 900, 517, 525, 530, 2.8, 3.2, 3.5, 20),
        ('598-8291', 'Blue', 'InGaN', 90, 175, 260, 465, 470, 475, 2.8, 3.2, 3.5, 20),
    ]

    # Dados para LEDs RGB 1210
    # Cada tupla: (prefix, cores com seus dados: lista de (cor, material, lumi_min, lumi_typ, lumi_max, wl_min, wl_typ, wl_max, vf_min, vf_typ, vf_max))
    data_1210 = [
        ('598-8610', [
            ('Red', 'AllnGaP', 40, 65, 90, 630, 635, 640, 1.8, 2.1, 2.4),
            ('Green', 'InGaN', 260, 580, 900, 515, 520, 525, 2.8, 3.1, 3.4),
            ('Blue', 'InGaN', 60, 160, 260, 465, 470, 475, 2.8, 3.1, 3.4),
        ]),
        ('598-8920', [
            ('Red-Orange', 'AllnGaP', 90, 120, 150, 620, 625, 630, 1.8, 2.1, 2.4),
            ('Green', 'InGaN', 260, 580, 900, 515, 520, 525, 2.8, 3.1, 3.4),
            ('Blue', 'InGaN', 90, 175, 260, 465, 470, 475, 2.8, 3.1, 3.4),
        ]),
        ('598-8940', [
            ('Yellow', 'AllnGaP', 90, 175, 260, 585, 590, 595, 1.8, 2.1, 2.4),
            ('Green', 'InGaN', 260, 580, 900, 515, 520, 525, 2.8, 3.1, 3.4),
            ('Blue', 'InGaN', 60, 160, 260, 465, 470, 475, 2.8, 3.1, 3.4),
        ]),
    ]

    # Suffixos de embalagem: 102F (20-piece tape) e 107F (7" reel)
    packaging_suffixes = [('102F', '20pc tape'), ('107F', '7" reel')]

    # Valores comuns
    manufacturer = "Dialight"
    series = "598 Series MicroLED"
    operating_temp = "-40 to +100 °C"
    rohs = "Yes"
    reverse_voltage = 5  # V
    # Potência e corrente máximas por material
    max_power = {'AllnGaP': 72, 'InGaN': 105}  # mW
    max_current = {'AllnGaP': 30, 'InGaN': 20}  # mA

    # Mapeamento de footprints por pacote
    footprint_map = {
        '0603': 'MyLib_LED_SMD:LED_0603_1608Metric',
        '1206': 'MyLib_LED_SMD:LED_1206_3216Metric',
        '1210': 'MyLib_LED_SMD:LED_RGB_1210',  # para RGB
    }

    # Símbolos: single color usar LED, RGB usar LED_RGB (6 pinos) - ajustável
    symbol_single = 'MyLib_LED:LED'
    symbol_rgb = 'MyLib_LED:LED_RGB'

    insert_data = []
    mypn_counter = start_id

    # Processar 0603
    package = '0603'
    for prefix, color, material, lumi_min, lumi_typ, lumi_max, wl_min, wl_typ, wl_max, vf_min, vf_typ, vf_max, if_test in data_0603:
        for suffix, pack_desc in packaging_suffixes:
            part_number = f"{prefix}-{suffix}"
            color_clean = format_color_name(color)
            name = f"LED_{package}_{color_clean}"
            description = f"SMD LED, {color}, {package} package, {lumi_typ} mcd typ, {wl_typ} nm typ, {vf_typ} V typ"
            value = part_number
            info1 = color_clean
            info2 = pack_desc

            luminous_intensity = f"{lumi_min}/{lumi_typ}/{lumi_max} mcd"
            wavelength = f"{wl_min}/{wl_typ}/{wl_max} nm"
            vf_typical = f"{vf_typ} V"
            forward_voltage = f"{vf_min}~{vf_max} V"
            power_dissipation = f"{max_power[material]} mW"
            current_rating = f"{max_current[material]} mA"
            if_current = f"{if_test} mA"
            notes = f"Material: {material}; Reverse Voltage: {reverse_voltage}V"

            data_dict = {
                'MyPN': f"EL-LED-{mypn_counter:06d}",
                'Name': name,
                'Description': description,
                'Value': value,
                'Info1': info1,
                'Info2': info2,
                'Symbol': symbol_single,
                'Footprint': footprint_map[package],
                'Footprint_Filter': None,
                'Datasheet': None,
                'Notes': notes,
                'Notes_to_Buyer': None,
                'Manufacturer': manufacturer,
                'Manufacturer_PN': part_number,
                'Manufacturer_URL': None,
                'Alternative_PN': None,
                'Alternative_URL': None,
                'Digikey_PN': None,
                'Digikey_URL': None,
                'Mouser_PN': None,
                'Mouser_URL': None,
                'LCSC_PN': None,
                'LCSC_URL': None,
                'Stock_Qty': None,
                'Stock_Location': None,
                'Stock_Unit': None,
                'Price': None,
                'Currency': 'USD',
                'Min_Stock': None,
                'Max_Stock': None,
                'Last_Purchase_Date': None,
                'Last_Purchase_Price': None,
                'Active': 1,
                'Version': 1,
                'Created_At': None,
                'Created_By': None,
                'Modified_At': None,
                'Modified_By': None,
                'Exclude_from_BOM': 0,
                'Exclude_from_Board': 0,
                'Category': 'LED',
                'Subcategory': 'SMD LED',
                'Family_Series': series,
                'Package': package,
                'Mount': 'SMD',
                'Dimensions': None,
                'Temperature_Range': operating_temp,
                'REACH_Compliant': None,
                'RoHS_Compliant': rohs,
                'Unit': None,
                'Tolerance': None,
                'Voltage_Rating': None,
                'Current_Rating': current_rating,
                'Power_Rating': power_dissipation,
                'Temperature_Coefficient': None,
                'Pin_Configuration': None,
                'Gender': None,
                'Pin_Type': None,
                'Pitch': None,
                'Orientation': None,
                'Locking_Mechanism': None,
                'Current_Rating_Per_Pin': None,
                'IP_Rating': None,
                'Wire_Gauge': None,
                'Termination_Style': 'SMD',
                'Resistance': None,
                'Technology_Material': material,
                'Capacitance': None,
                'Dielectric_Type': None,
                'ESR': None,
                'Ripple_Current': None,
                'Leakage_Current': None,
                'Inductance': None,
                'DC_Resistance': None,
                'Self_Resonant_Frequency': None,
                'Quality_Factor_Q': None,
                'Saturation_Current': None,
                'Hold_Current': None,
                'Trip_Current': None,
                'Interrupting_Rating': None,
                'Response_Time': None,
                'Forward_Voltage': forward_voltage,
                'Reverse_Leakage': None,
                'Junction_Capacitance': None,
                'Reverse_Recovery_Time': None,
                'Zener_Voltage': None,
                'Zener_Impedance': None,
                'Reverse_Standoff_Voltage': None,
                'Breakdown_Voltage': None,
                'Clamping_Voltage': None,
                'Peak_Pulse_Current': None,
                'Q_Type': None,
                'Polarity_Channel_Type': None,
                'Power_Dissipation': power_dissipation,
                'Junction_Temperature': None,
                'VDS_Max': None,
                'VGS_Max': None,
                'VGS_Threshold': None,
                'RDS_On': None,
                'ID_Continuous': None,
                'ID_Pulse': None,
                'Input_Capacitance': None,
                'Output_Capacitance': None,
                'Reverse_Transfer_Capacitance': None,
                'Gate_Charge': None,
                'Rise_Time': None,
                'Fall_Time': None,
                'IDSS': None,
                'VGS_Off': None,
                'Gain': None,
                'Gate_Reverse_Current': None,
                'VCEO': None,
                'Current_Collector': None,
                'DC_Gain_HFE': None,
                'Saturation_Voltage': None,
                'Transition_Frequency': None,
                'VCE_Sat': None,
                'IC_Continuous': None,
                'IC_Pulse': None,
                'VGE_Threshold': None,
                'Short_Circuit_Withstanding': None,
                'Diode_Forward_Voltage': None,
                'Frequency': None,
                'Oscillator_Type': None,
                'Load_Capacitance': None,
                'Supply_Voltage': None,
                'Coil_Voltage': None,
                'Coil_Resistance': None,
                'Contact_Configuration': None,
                'Contact_Current_Rating': None,
                'Contact_Voltage_Rating': None,
                'Relay_Type': None,
                'Operating_Time': None,
                'Transformer_Type': None,
                'Turns_Ratio': None,
                'Isolation_Voltage': None,
                'Power_Rating_VA': None,
                'Frequency_Rating': None,
                'Battery_Chemistry': None,
                'Battery_Voltage_Nominal': None,
                'Battery_Capacity': None,
                'Battery_Size': None,
                'Rechargeable': None,
                'Number_of_Cells': None,
                'Display_Type': None,
                'Display_Size': None,
                'Resolution': None,
                'Interface': None,
                'Backlight': None,
                'Controller': None,
                'Color': None,
                'Sensor_Type': None,
                'Sensor_Interface': None,
                'Supply_Voltage_Min': None,
                'Supply_Voltage_Max': None,
                'Accuracy': None,
                'Output_Type': None,
                'LED_Color': color,
                'Luminous_Intensity': luminous_intensity,
                'Wavelength': wavelength,
                'Viewing_Angle_LED': None,
                'Lens_Type': 'Water Clear',  # assumindo
                'If_Current': if_current,
                'VF_Typical': vf_typical,
                'Optocoupler_Type': None,
                'CTR': None,
                'Tube_Type': None,
                'Heater_Voltage': None,
                'Heater_Current': None,
                'Plate_Voltage_Max': None,
            }
            insert_data.append(data_dict)
            mypn_counter += 1

    # Processar 1206
    package = '1206'
    for prefix, color, material, lumi_min, lumi_typ, lumi_max, wl_min, wl_typ, wl_max, vf_min, vf_typ, vf_max, if_test in data_1206:
        for suffix, pack_desc in packaging_suffixes:
            part_number = f"{prefix}-{suffix}"
            color_clean = format_color_name(color)
            name = f"LED_{package}_{color_clean}"
            description = f"SMD LED, {color}, {package} package, {lumi_typ} mcd typ, {wl_typ} nm typ, {vf_typ} V typ"
            value = part_number
            info1 = color_clean
            info2 = pack_desc

            luminous_intensity = f"{lumi_min}/{lumi_typ}/{lumi_max} mcd"
            wavelength = f"{wl_min}/{wl_typ}/{wl_max} nm"
            vf_typical = f"{vf_typ} V"
            forward_voltage = f"{vf_min}~{vf_max} V"
            power_dissipation = f"{max_power[material]} mW"
            current_rating = f"{max_current[material]} mA"
            if_current = f"{if_test} mA"
            notes = f"Material: {material}; Reverse Voltage: {reverse_voltage}V"

            data_dict = {
                'MyPN': f"EL-LED-{mypn_counter:06d}",
                'Name': name,
                'Description': description,
                'Value': value,
                'Info1': info1,
                'Info2': info2,
                'Symbol': symbol_single,
                'Footprint': footprint_map[package],
                'Footprint_Filter': None,
                'Datasheet': None,
                'Notes': notes,
                'Notes_to_Buyer': None,
                'Manufacturer': manufacturer,
                'Manufacturer_PN': part_number,
                'Manufacturer_URL': None,
                'Alternative_PN': None,
                'Alternative_URL': None,
                'Digikey_PN': None,
                'Digikey_URL': None,
                'Mouser_PN': None,
                'Mouser_URL': None,
                'LCSC_PN': None,
                'LCSC_URL': None,
                'Stock_Qty': None,
                'Stock_Location': None,
                'Stock_Unit': None,
                'Price': None,
                'Currency': 'USD',
                'Min_Stock': None,
                'Max_Stock': None,
                'Last_Purchase_Date': None,
                'Last_Purchase_Price': None,
                'Active': 1,
                'Version': 1,
                'Created_At': None,
                'Created_By': None,
                'Modified_At': None,
                'Modified_By': None,
                'Exclude_from_BOM': 0,
                'Exclude_from_Board': 0,
                'Category': 'LED',
                'Subcategory': 'SMD LED',
                'Family_Series': series,
                'Package': package,
                'Mount': 'SMD',
                'Dimensions': None,
                'Temperature_Range': operating_temp,
                'REACH_Compliant': None,
                'RoHS_Compliant': rohs,
                'Unit': None,
                'Tolerance': None,
                'Voltage_Rating': None,
                'Current_Rating': current_rating,
                'Power_Rating': power_dissipation,
                'Temperature_Coefficient': None,
                'Pin_Configuration': None,
                'Gender': None,
                'Pin_Type': None,
                'Pitch': None,
                'Orientation': None,
                'Locking_Mechanism': None,
                'Current_Rating_Per_Pin': None,
                'IP_Rating': None,
                'Wire_Gauge': None,
                'Termination_Style': 'SMD',
                'Resistance': None,
                'Technology_Material': material,
                'Capacitance': None,
                'Dielectric_Type': None,
                'ESR': None,
                'Ripple_Current': None,
                'Leakage_Current': None,
                'Inductance': None,
                'DC_Resistance': None,
                'Self_Resonant_Frequency': None,
                'Quality_Factor_Q': None,
                'Saturation_Current': None,
                'Hold_Current': None,
                'Trip_Current': None,
                'Interrupting_Rating': None,
                'Response_Time': None,
                'Forward_Voltage': forward_voltage,
                'Reverse_Leakage': None,
                'Junction_Capacitance': None,
                'Reverse_Recovery_Time': None,
                'Zener_Voltage': None,
                'Zener_Impedance': None,
                'Reverse_Standoff_Voltage': None,
                'Breakdown_Voltage': None,
                'Clamping_Voltage': None,
                'Peak_Pulse_Current': None,
                'Q_Type': None,
                'Polarity_Channel_Type': None,
                'Power_Dissipation': power_dissipation,
                'Junction_Temperature': None,
                'VDS_Max': None,
                'VGS_Max': None,
                'VGS_Threshold': None,
                'RDS_On': None,
                'ID_Continuous': None,
                'ID_Pulse': None,
                'Input_Capacitance': None,
                'Output_Capacitance': None,
                'Reverse_Transfer_Capacitance': None,
                'Gate_Charge': None,
                'Rise_Time': None,
                'Fall_Time': None,
                'IDSS': None,
                'VGS_Off': None,
                'Gain': None,
                'Gate_Reverse_Current': None,
                'VCEO': None,
                'Current_Collector': None,
                'DC_Gain_HFE': None,
                'Saturation_Voltage': None,
                'Transition_Frequency': None,
                'VCE_Sat': None,
                'IC_Continuous': None,
                'IC_Pulse': None,
                'VGE_Threshold': None,
                'Short_Circuit_Withstanding': None,
                'Diode_Forward_Voltage': None,
                'Frequency': None,
                'Oscillator_Type': None,
                'Load_Capacitance': None,
                'Supply_Voltage': None,
                'Coil_Voltage': None,
                'Coil_Resistance': None,
                'Contact_Configuration': None,
                'Contact_Current_Rating': None,
                'Contact_Voltage_Rating': None,
                'Relay_Type': None,
                'Operating_Time': None,
                'Transformer_Type': None,
                'Turns_Ratio': None,
                'Isolation_Voltage': None,
                'Power_Rating_VA': None,
                'Frequency_Rating': None,
                'Battery_Chemistry': None,
                'Battery_Voltage_Nominal': None,
                'Battery_Capacity': None,
                'Battery_Size': None,
                'Rechargeable': None,
                'Number_of_Cells': None,
                'Display_Type': None,
                'Display_Size': None,
                'Resolution': None,
                'Interface': None,
                'Backlight': None,
                'Controller': None,
                'Color': None,
                'Sensor_Type': None,
                'Sensor_Interface': None,
                'Supply_Voltage_Min': None,
                'Supply_Voltage_Max': None,
                'Accuracy': None,
                'Output_Type': None,
                'LED_Color': color,
                'Luminous_Intensity': luminous_intensity,
                'Wavelength': wavelength,
                'Viewing_Angle_LED': None,
                'Lens_Type': 'Water Clear',
                'If_Current': if_current,
                'VF_Typical': vf_typical,
                'Optocoupler_Type': None,
                'CTR': None,
                'Tube_Type': None,
                'Heater_Voltage': None,
                'Heater_Current': None,
                'Plate_Voltage_Max': None,
            }
            insert_data.append(data_dict)
            mypn_counter += 1

    # Processar 1210 RGB
    package = '1210'
    for prefix, colors in data_1210:
        for suffix, pack_desc in packaging_suffixes:
            part_number = f"{prefix}-{suffix}"
            name = f"LED_{package}_RGB"
            description = f"SMD RGB LED, {package} package"
            value = part_number
            info1 = "RGB"
            info2 = pack_desc

            # Montar notas com as especificações de cada cor
            notes_lines = []
            for color, material, lumi_min, lumi_typ, lumi_max, wl_min, wl_typ, wl_max, vf_min, vf_typ, vf_max in colors:
                line = f"{color}: {lumi_typ} mcd typ, {wl_typ} nm typ, {vf_typ} V typ"
                notes_lines.append(line)
            notes = "; ".join(notes_lines) + f"; Reverse Voltage: {reverse_voltage}V"

            # Usaremos valores típicos para os campos de LED (pode ser da primeira cor ou média)
            # Vamos preencher com a primeira cor (Red) como referência, mas não é ideal. O usuário pode ajustar.
            first = colors[0]
            luminous_intensity = f"{first[2]}/{first[3]}/{first[4]} mcd"  # lumi_min/typ/max
            wavelength = f"{first[5]}/{first[6]}/{first[7]} nm"
            vf_typical = f"{first[9]} V"
            forward_voltage = f"{first[8]}~{first[10]} V"
            # Material varia por cor, então não colocamos
            power_dissipation = None  # pode ser a soma? melhor deixar NULL
            current_rating = None
            if_current = "20 mA"  # padrão

            data_dict = {
                'MyPN': f"EL-LED-{mypn_counter:06d}",
                'Name': name,
                'Description': description,
                'Value': value,
                'Info1': info1,
                'Info2': info2,
                'Symbol': symbol_rgb,
                'Footprint': footprint_map[package],
                'Footprint_Filter': None,
                'Datasheet': None,
                'Notes': notes,
                'Notes_to_Buyer': None,
                'Manufacturer': manufacturer,
                'Manufacturer_PN': part_number,
                'Manufacturer_URL': None,
                'Alternative_PN': None,
                'Alternative_URL': None,
                'Digikey_PN': None,
                'Digikey_URL': None,
                'Mouser_PN': None,
                'Mouser_URL': None,
                'LCSC_PN': None,
                'LCSC_URL': None,
                'Stock_Qty': None,
                'Stock_Location': None,
                'Stock_Unit': None,
                'Price': None,
                'Currency': 'USD',
                'Min_Stock': None,
                'Max_Stock': None,
                'Last_Purchase_Date': None,
                'Last_Purchase_Price': None,
                'Active': 1,
                'Version': 1,
                'Created_At': None,
                'Created_By': None,
                'Modified_At': None,
                'Modified_By': None,
                'Exclude_from_BOM': 0,
                'Exclude_from_Board': 0,
                'Category': 'LED',
                'Subcategory': 'SMD RGB LED',
                'Family_Series': series,
                'Package': package,
                'Mount': 'SMD',
                'Dimensions': None,
                'Temperature_Range': operating_temp,
                'REACH_Compliant': None,
                'RoHS_Compliant': rohs,
                'Unit': None,
                'Tolerance': None,
                'Voltage_Rating': None,
                'Current_Rating': current_rating,
                'Power_Rating': power_dissipation,
                'Temperature_Coefficient': None,
                'Pin_Configuration': None,
                'Gender': None,
                'Pin_Type': None,
                'Pitch': None,
                'Orientation': None,
                'Locking_Mechanism': None,
                'Current_Rating_Per_Pin': None,
                'IP_Rating': None,
                'Wire_Gauge': None,
                'Termination_Style': 'SMD',
                'Resistance': None,
                'Technology_Material': None,
                'Capacitance': None,
                'Dielectric_Type': None,
                'ESR': None,
                'Ripple_Current': None,
                'Leakage_Current': None,
                'Inductance': None,
                'DC_Resistance': None,
                'Self_Resonant_Frequency': None,
                'Quality_Factor_Q': None,
                'Saturation_Current': None,
                'Hold_Current': None,
                'Trip_Current': None,
                'Interrupting_Rating': None,
                'Response_Time': None,
                'Forward_Voltage': forward_voltage,
                'Reverse_Leakage': None,
                'Junction_Capacitance': None,
                'Reverse_Recovery_Time': None,
                'Zener_Voltage': None,
                'Zener_Impedance': None,
                'Reverse_Standoff_Voltage': None,
                'Breakdown_Voltage': None,
                'Clamping_Voltage': None,
                'Peak_Pulse_Current': None,
                'Q_Type': None,
                'Polarity_Channel_Type': None,
                'Power_Dissipation': power_dissipation,
                'Junction_Temperature': None,
                'VDS_Max': None,
                'VGS_Max': None,
                'VGS_Threshold': None,
                'RDS_On': None,
                'ID_Continuous': None,
                'ID_Pulse': None,
                'Input_Capacitance': None,
                'Output_Capacitance': None,
                'Reverse_Transfer_Capacitance': None,
                'Gate_Charge': None,
                'Rise_Time': None,
                'Fall_Time': None,
                'IDSS': None,
                'VGS_Off': None,
                'Gain': None,
                'Gate_Reverse_Current': None,
                'VCEO': None,
                'Current_Collector': None,
                'DC_Gain_HFE': None,
                'Saturation_Voltage': None,
                'Transition_Frequency': None,
                'VCE_Sat': None,
                'IC_Continuous': None,
                'IC_Pulse': None,
                'VGE_Threshold': None,
                'Short_Circuit_Withstanding': None,
                'Diode_Forward_Voltage': None,
                'Frequency': None,
                'Oscillator_Type': None,
                'Load_Capacitance': None,
                'Supply_Voltage': None,
                'Coil_Voltage': None,
                'Coil_Resistance': None,
                'Contact_Configuration': None,
                'Contact_Current_Rating': None,
                'Contact_Voltage_Rating': None,
                'Relay_Type': None,
                'Operating_Time': None,
                'Transformer_Type': None,
                'Turns_Ratio': None,
                'Isolation_Voltage': None,
                'Power_Rating_VA': None,
                'Frequency_Rating': None,
                'Battery_Chemistry': None,
                'Battery_Voltage_Nominal': None,
                'Battery_Capacity': None,
                'Battery_Size': None,
                'Rechargeable': None,
                'Number_of_Cells': None,
                'Display_Type': None,
                'Display_Size': None,
                'Resolution': None,
                'Interface': None,
                'Backlight': None,
                'Controller': None,
                'Color': None,
                'Sensor_Type': None,
                'Sensor_Interface': None,
                'Supply_Voltage_Min': None,
                'Supply_Voltage_Max': None,
                'Accuracy': None,
                'Output_Type': None,
                'LED_Color': 'RGB',
                'Luminous_Intensity': luminous_intensity,
                'Wavelength': wavelength,
                'Viewing_Angle_LED': None,
                'Lens_Type': 'Water Clear',
                'If_Current': if_current,
                'VF_Typical': vf_typical,
                'Optocoupler_Type': None,
                'CTR': None,
                'Tube_Type': None,
                'Heater_Voltage': None,
                'Heater_Current': None,
                'Plate_Voltage_Max': None,
            }
            insert_data.append(data_dict)
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
    sql = f"INSERT INTO LED ({columns_str}) VALUES\n{values_str};\n"
    out.write(sql)

    if output_path:
        out.close()
        print(f"Arquivo SQL gerado: {output_path}")

def main():
    output_file = os.path.join(SCRIPT_DIR, 'inserts_led.sql')
    generate_insert(output_file, start_id=1)

if __name__ == '__main__':
    main()