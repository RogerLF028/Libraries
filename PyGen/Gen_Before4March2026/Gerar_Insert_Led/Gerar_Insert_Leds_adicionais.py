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

def generate_insert(output_path=None, start_id=950001):
    # Dados extraídos dos PDFs

    # 1. ASMT-YTD7-0AA02 (Broadcom RGB PLCC-6)
    asm_data = {
        'part_number': 'ASMT-YTD7-0AA02',
        'manufacturer': 'Broadcom',
        'package': 'PLCC6',
        'viewing_angle': 110,
        'if_test': 20,  # mA
        'colors': [
            {'color': 'Red', 'material': 'AllnGaP', 'wl_min': 617, 'wl_typ': 622, 'wl_max': 627,
             'lumi_min': 285, 'lumi_typ': None, 'lumi_max': 2850,  # faixa geral
             'vf_min': 1.8, 'vf_typ': 2.1, 'vf_max': 2.4},
            {'color': 'Green', 'material': 'InGaN', 'wl_min': 525, 'wl_typ': 530, 'wl_max': 537,
             'lumi_min': 285, 'lumi_typ': None, 'lumi_max': 2850,
             'vf_min': 2.8, 'vf_typ': 3.1, 'vf_max': 3.4},
            {'color': 'Blue', 'material': 'InGaN', 'wl_min': 465, 'wl_typ': 470, 'wl_max': 475,
             'lumi_min': 285, 'lumi_typ': None, 'lumi_max': 2850,
             'vf_min': 2.8, 'vf_typ': 3.2, 'vf_max': 3.5},
        ],
        'notes': 'Intensity bins: T1(285-355), T2(355-450), U1(450-560), U2(560-715), V1(715-900), V2(900-1125), W1(1125-1400), W2(1400-1800), X1(1800-2240), X2(2240-2850)'
    }

    # 2. HLMP-HB75 series (Broadcom/Avago Oval LEDs)
    hlmp_hb_data = [
        # (part_number, color, lumi_min, lumi_typ, lumi_max, wl_typ, vf_typ, if_test, standoff)
        ('HLMP-HG74-XYODD', 'Red', 1660, None, 2400, 626, 2.0, 20, 'No'),
        ('HLMP-HG75-XYODD', 'Red', 1660, None, 2400, 626, 2.0, 20, 'Yes'),
        ('HLMP-HM74-34BDD', 'Green', 4200, None, 6050, 530, 3.2, 20, 'No'),
        ('HLMP-HM75-34BDD', 'Green', 4200, None, 6050, 530, 3.2, 20, 'Yes'),
        ('HLMP-HM74-34CDD', 'Green', 4200, None, 6050, 530, 3.2, 20, 'No'),
        ('HLMP-HM75-34CDD', 'Green', 4200, None, 6050, 530, 3.2, 20, 'Yes'),
        ('HLMP-HB74-UVBDD', 'Blue', 960, None, 1380, 470, 3.2, 20, 'No'),
        ('HLMP-HB75-UVBDD', 'Blue', 960, None, 1380, 470, 3.2, 20, 'Yes'),
        ('HLMP-HB74-UVCDD', 'Blue', 960, None, 1380, 470, 3.2, 20, 'No'),
        ('HLMP-HB75-UVCDD', 'Blue', 960, None, 1380, 470, 3.2, 20, 'Yes'),
    ]

    # 3. HLMP-Y901 series (T-1 3mm LEDs)
    hlmp_y_data = [
        # (part_number, color, lumi_min, lumi_typ, lumi_max, wl_typ, vf_typ, if_test, viewing_angle)
        ('HLMP-Y651-G00xx', 'Deep Red', 140, 300, None, 638, 2.0, 20, 45),
        ('HLMP-Y601-J00xx', 'Red', 240, 680, None, 627, 2.0, 20, 45),
        ('HLMP-Y951-K00xx', 'Red-Orange', 310, 680, None, 615, 2.0, 20, 45),
        ('HLMP-Y901-J00xx', 'Yellow-Orange', 240, 680, None, 605, 2.0, 20, 45),
        ('HLMP-Y902-J00xx', 'Yellow-Orange', 240, 680, None, 605, 2.0, 20, 25),  # tinted, viewing angle diferente
        ('HLMP-Y701-G00xx', 'Amber', 140, 400, None, 592, 2.0, 20, 45),
        ('HLMP-Y802-F00xx', 'Green', 110, 240, None, 572, 2.2, 20, 45),  # tinted
    ]

    # 4. KAAF-5050RGBS-13 (Kingbright RGB 5050)
    kaaf_data = {
        'part_number': 'KAAF-5050RGBS-13',
        'manufacturer': 'Kingbright',
        'package': '5050',
        'viewing_angle': 120,
        'if_test_red': 50,  # mA
        'if_test_gb': 30,    # mA
        'colors': [
            {'color': 'Hyper Red', 'material': 'AlGaInP', 'wl_peak': 640, 'wl_dom': 625,
             'lumi_min': 1000, 'lumi_typ': 1400, 'lumi_max': None,
             'vf_min': 2.5, 'vf_typ': None, 'vf_max': 3.2},
            {'color': 'Green', 'material': 'InGaN', 'wl_peak': 520, 'wl_dom': 525,
             'lumi_min': 1300, 'lumi_typ': 2000, 'lumi_max': None,
             'vf_min': 3.3, 'vf_typ': None, 'vf_max': 4.1},
            {'color': 'Blue', 'material': 'InGaN', 'wl_peak': 465, 'wl_dom': 470,
             'lumi_min': 300, 'lumi_typ': 420, 'lumi_max': None,
             'vf_min': 3.5, 'vf_typ': None, 'vf_max': 4.5},
        ],
        'notes': 'Hyper Red tested at 50mA, Green/Blue at 30mA'
    }

    # Mapeamento de footprints
    footprint_map = {
        'PLCC6': 'MyLib_LED_SMD:LED_RGB_PLCC-6',
        'Oval': 'MyLib_LED_THT:LED_Oval_W5.2mm_H3.8mm',
        'T1': 'MyLib_LED_THT:LED_D3.0mm',
        '5050': 'MyLib_LED_SMD:LED_RGB_5050-6',
    }

    # Símbolos
    symbol_single = 'MyLib_LED:LED'
    symbol_rgb = 'MyLib_LED:LED_RGB'

    # Valores comuns
    rohs = 'Yes'
    reverse_voltage = 5  # V (padrão)

    insert_data = []
    mypn_counter = start_id

    # Processar ASMT-YTD7 (RGB)
    pn = asm_data['part_number']
    name = f"LED_PLCC6_RGB"
    description = f"SMD RGB LED, PLCC-6 package, 110° viewing angle"
    value = pn
    info1 = 'RGB'
    info2 = None
    luminous_intensity = "285-2850 mcd (varies by bin)"
    wavelength = "Red:617-627nm, Green:525-537nm, Blue:465-475nm"
    vf_typical = "Red 2.1V, Green 3.1V, Blue 3.2V"
    forward_voltage = "Red 1.8-2.4V, Green 2.8-3.4V, Blue 2.8-3.5V"
    if_current = "20 mA"
    notes = asm_data['notes']
    # Potência e corrente máximas não fornecidas, deixar NULL
    data_dict = {
        'MyPN': f"EL-LED-{mypn_counter:06d}",
        'Name': name,
        'Description': description,
        'Value': value,
        'Info1': info1,
        'Info2': info2,
        'Symbol': symbol_rgb,
        'Footprint': footprint_map['PLCC6'],
        'Footprint_Filter': None,
        'Datasheet': None,
        'Notes': notes,
        'Notes_to_Buyer': None,
        'Manufacturer': asm_data['manufacturer'],
        'Manufacturer_PN': pn,
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
        'Family_Series': 'ASMT-YTD7',
        'Package': 'PLCC-6',
        'Mount': 'SMD',
        'Dimensions': None,
        'Temperature_Range': None,
        'REACH_Compliant': None,
        'RoHS_Compliant': rohs,
        'Unit': None,
        'Tolerance': None,
        'Voltage_Rating': None,
        'Current_Rating': None,
        'Power_Rating': None,
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
        'Technology_Material': 'Mixed',
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
        'Power_Dissipation': None,
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
        'Viewing_Angle_LED': asm_data['viewing_angle'],
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

    # Processar HLMP-HB75 (Oval)
    package = 'Oval'
    for pn, color, lumi_min, lumi_typ, lumi_max, wl_typ, vf_typ, if_test, standoff in hlmp_hb_data:
        color_clean = format_color_name(color)
        name = f"LED_{package}_{color_clean}"
        if standoff == 'Yes':
            name += "_Standoff"
        description = f"Oval LED, {color}, {wl_typ}nm typ, {vf_typ}V typ"
        value = pn
        info1 = color_clean
        info2 = f"Standoff: {standoff}"
        luminous_intensity = f"{lumi_min}-{lumi_max} mcd"
        wavelength = f"{wl_typ} nm"
        vf_typical = f"{vf_typ} V"
        forward_voltage = f"{vf_typ-0.2}~{vf_typ+0.2} V"  # aproximação
        if_current = f"{if_test} mA"
        # Potência máxima: Red 120mW, Green/Blue 114mW
        if 'Red' in color:
            power_dissipation = "120 mW"
            current_rating = "50 mA"
        else:
            power_dissipation = "114 mW"
            current_rating = "30 mA"
        notes = f"Viewing angle: 40° x 100°"

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
            'Manufacturer': 'Broadcom',
            'Manufacturer_PN': pn,
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
            'Subcategory': 'Oval LED',
            'Family_Series': 'HLMP-HB75',
            'Package': 'Oval',
            'Mount': 'Through Hole',
            'Dimensions': None,
            'Temperature_Range': '-40 to +100°C',
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
            'Pitch': '2.54mm',  # provavelmente
            'Orientation': None,
            'Locking_Mechanism': None,
            'Current_Rating_Per_Pin': None,
            'IP_Rating': None,
            'Wire_Gauge': None,
            'Termination_Style': 'Through Hole',
            'Resistance': None,
            'Technology_Material': 'AlInGaP' if 'Red' in color else 'InGaN',
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
            'Junction_Temperature': '130°C' if 'Red' in color else '110°C',
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
            'Viewing_Angle_LED': None,  # já nas notas
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

    # Processar HLMP-Y901 (T-1)
    package = 'T1'
    for pn, color, lumi_min, lumi_typ, lumi_max, wl_typ, vf_typ, if_test, viewing_angle in hlmp_y_data:
        color_clean = format_color_name(color)
        name = f"LED_{package}_{color_clean}"
        description = f"T-1 (3mm) LED, {color}, {wl_typ}nm typ, {vf_typ}V typ"
        value = pn
        info1 = color_clean
        info2 = None
        luminous_intensity = f"{lumi_min}/{lumi_typ} mcd" if lumi_typ else f"{lumi_min} mcd min"
        wavelength = f"{wl_typ} nm"
        vf_typical = f"{vf_typ} V"
        forward_voltage = f"{vf_typ-0.2}~{vf_typ+0.2} V"
        if_current = f"{if_test} mA"
        power_dissipation = "48 mW"
        current_rating = "20 mA"
        notes = f"Viewing angle: {viewing_angle}°"

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
            'Manufacturer': 'Broadcom',
            'Manufacturer_PN': pn,
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
            'Subcategory': 'T-1 LED',
            'Family_Series': 'HLMP-Y901',
            'Package': 'T-1 3mm',
            'Mount': 'Through Hole',
            'Dimensions': None,
            'Temperature_Range': '-40 to +100°C',
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
            'Pitch': '2.54mm',
            'Orientation': None,
            'Locking_Mechanism': None,
            'Current_Rating_Per_Pin': None,
            'IP_Rating': None,
            'Wire_Gauge': None,
            'Termination_Style': 'Through Hole',
            'Resistance': None,
            'Technology_Material': 'AlInGaP',
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
            'Junction_Temperature': '110°C',
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
            'Viewing_Angle_LED': viewing_angle,
            'Lens_Type': 'Untinted' if 'xx' in pn and not '802' in pn else 'Tinted',
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

    # Processar KAAF-5050RGBS (RGB 5050)
    pn = kaaf_data['part_number']
    name = f"LED_5050_RGB"
    description = f"SMD RGB LED, 5050 package, {kaaf_data['viewing_angle']}° viewing angle"
    value = pn
    info1 = 'RGB'
    info2 = None
    luminous_intensity = "Red:1000-1400, Green:1300-2000, Blue:300-420 mcd"
    wavelength = "Red:625nm dom, Green:525nm dom, Blue:470nm dom"
    vf_typical = "Red 2.9V, Green 3.7V, Blue 4.0V"
    forward_voltage = "Red 2.5-3.2V, Green 3.3-4.1V, Blue 3.5-4.5V"
    if_current = "Red 50mA, Green/Blue 30mA"
    notes = kaaf_data['notes']
    # Potência máxima: 350mW total (nota de rodapé)
    power_dissipation = "350 mW total"
    current_rating = "Red 50mA, Green/Blue 30mA"
    data_dict = {
        'MyPN': f"EL-LED-{mypn_counter:06d}",
        'Name': name,
        'Description': description,
        'Value': value,
        'Info1': info1,
        'Info2': info2,
        'Symbol': symbol_rgb,
        'Footprint': footprint_map['5050'],
        'Footprint_Filter': None,
        'Datasheet': None,
        'Notes': notes,
        'Notes_to_Buyer': None,
        'Manufacturer': kaaf_data['manufacturer'],
        'Manufacturer_PN': pn,
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
        'Family_Series': 'KAAF-5050',
        'Package': '5050',
        'Mount': 'SMD',
        'Dimensions': None,
        'Temperature_Range': '-40 to +85°C',
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
        'Technology_Material': 'Mixed',
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
        'Junction_Temperature': '115°C',
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
        'Viewing_Angle_LED': kaaf_data['viewing_angle'],
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
    output_file = os.path.join(SCRIPT_DIR, 'inserts_led_adicionais.sql')
    generate_insert(output_file, start_id=50)

if __name__ == '__main__':
    main()