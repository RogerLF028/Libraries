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

def format_current(val):
    """Formata o valor da corrente para o nome, sem zeros desnecessários."""
    try:
        f = float(val)
        if f.is_integer():
            return f"{int(f)}A"
        else:
            # Remove zeros à direita
            s = f"{f:.3f}".rstrip('0').rstrip('.')
            return f"{s}A"
    except:
        return f"{val}A"

def generate_insert(output_path=None, start_id=920001):
    # Dados extraídos dos PDFs
    # Formato: (part_number, package, ihold, itrip, vmax, imax, pd, time_sec, time_current, rmin, rmax)
    # Obs: para alguns, o tempo de disparo é dado em segundos para uma corrente específica.
    # Vamos incluir todos os part numbers listados nas tabelas.

    data = [
        # Série SMD0603
        ("SMD0603B004TF", "0603", 0.04, 0.12, 20, 40, 0.5, 1.0, 0.20, 4.00, 40.0),
        ("SMD0603B010TF", "0603", 0.10, 0.30, 15, 40, 0.5, 1.0, 0.50, 0.90, 6.0),
        ("SMD0603B020TF", "0603", 0.20, 0.50, 9, 40, 0.5, 0.6, 1.00, 0.55, 3.5),
        ("SMD0603B025TF", "0603", 0.25, 0.55, 9, 40, 0.5, 0.088, 8.00, 0.50, 3.0),
        ("SMD0603B035TF", "0603", 0.35, 0.75, 6, 40, 0.5, 0.10, 8.00, 0.20, 1.0),
        ("SMD0603B050TF", "0603", 0.50, 1.00, 6, 40, 0.5, 0.10, 8.00, 0.10, 0.68),

        # Série SMD0805
        ("SMD0805B005TF", "0805", 0.05, 0.15, 30, 40, 0.5, 1.5, 0.25, 3.60, 20.0),
        ("SMD0805B010TF", "0805", 0.10, 0.30, 15, 100, 0.5, 1.5, 0.50, 1.00, 6.00),
        ("SMD0805B010TF/24", "0805", 0.10, 0.30, 24, 100, 0.5, 1.5, 0.50, 1.50, 6.00),
        ("SMD0805B020TF", "0805", 0.20, 0.50, 9, 100, 0.5, 0.028, 8.00, 0.65, 3.50),
        ("SMD0805B035TF", "0805", 0.35, 0.75, 6, 100, 0.5, 0.10, 8.00, 0.25, 1.20),
        ("SMD0805B050TF", "0805", 0.50, 1.00, 6, 100, 0.5, 0.10, 8.00, 0.15, 0.85),
        ("SMD0805B075TF", "0805", 0.75, 1.50, 6, 40, 0.6, 0.20, 8.00, 0.09, 0.35),
        ("SMD0805B100TF", "0805", 1.00, 1.95, 6, 40, 0.6, 0.30, 8.00, 0.04, 0.23),
        ("SMD0805B110TF", "0805", 1.10, 2.00, 6, 100, 0.8, 0.30, 8.00, 0.03, 0.21),

        # Série SMD1206
        ("SMD1206B005TF", "1206", 0.05, 0.15, 30, 100, 0.6, 0.25, 1.50, 3.60, 50.0),
        ("SMD1206B010TF", "1206", 0.10, 0.27, 30, 100, 0.6, 0.20, 1.50, 1.50, 15.00),
        ("SMD1206B012TF", "1206", 0.12, 0.29, 30, 100, 0.6, 0.20, 1.00, 1.50, 6.00),
        ("SMD1206B012TF/48", "1206", 0.125, 0.29, 48, 100, 0.6, 0.20, 1.00, 1.50, 6.0),
        ("SMD1206B016TF", "1206", 0.16, 0.37, 30, 100, 0.6, 0.30, 1.00, 1.20, 4.50),
        ("SMD1206B020TF/24", "1206", 0.20, 0.42, 24, 100, 0.6, 0.10, 8.00, 0.65, 2.60),
        ("SMD1206B020TF/30", "1206", 0.20, 0.42, 30, 100, 0.6, 0.10, 8.00, 0.65, 2.60),
        ("SMD1206B025TF", "1206", 0.25, 0.50, 16, 100, 0.6, 0.088, 8.00, 0.55, 2.30),
        ("SMD1206B025TF/24", "1206", 0.25, 0.55, 24, 100, 0.6, 0.088, 8.00, 0.55, 2.30),
        ("SMD1206B035TF/16", "1206", 0.35, 0.75, 16, 100, 0.6, 0.10, 8.00, 0.30, 1.20),
        ("SMD1206B035TF/30", "1206", 0.35, 0.75, 30, 100, 0.6, 0.10, 8.00, 0.30, 1.20),
        ("SMD1206B050TF", "1206", 0.50, 1.00, 6, 100, 0.6, 0.10, 8.00, 0.15, 0.70),
        ("SMD1206B050TF/15", "1206", 0.50, 1.00, 15, 100, 0.6, 0.10, 8.00, 0.15, 0.75),
        ("SMD1206B050TF/24", "1206", 0.50, 1.00, 24, 100, 0.6, 0.10, 8.00, 0.15, 0.75),
        ("SMD1206B075TF", "1206", 0.75, 1.50, 8, 100, 0.6, 0.20, 8.00, 0.09, 0.35),
        ("SMD1206B075TF/13.2", "1206", 0.75, 1.50, 13.2, 100, 0.6, 0.20, 8.00, 0.09, 0.35),
        ("SMD1206B075TF/16", "1206", 0.75, 1.50, 16, 100, 0.6, 0.20, 8.00, 0.09, 0.35),
        ("SMD1206B110TF", "1206", 1.10, 2.20, 8, 100, 0.8, 0.10, 8.00, 0.04, 0.21),
        ("SMD1206B110TF/16", "1206", 1.10, 2.20, 16, 100, 0.8, 0.10, 8.00, 0.06, 0.21),
        ("SMD1206B150TF", "1206", 1.50, 3.00, 8, 100, 0.8, 0.30, 8.00, 0.03, 0.12),
        ("SMD1206B175TF", "1206", 1.75, 3.50, 6, 100, 0.8, 0.50, 8.00, 0.02, 0.09),
        ("SMD1206B200TF", "1206", 2.00, 3.50, 6, 100, 0.8, 1.50, 8.00, 0.018, 0.08),

        # Série SMD1210
        ("SMD1210B005TF", "1210", 0.05, 0.15, 30, 100, 0.6, 1.5, 0.25, 3.60, 50.0),
        ("SMD1210B010TF", "1210", 0.10, 0.30, 30, 100, 0.6, 1.5, 0.50, 1.60, 15.0),
        ("SMD1210B010TF/60", "1210", 0.10, 0.25, 60, 100, 0.6, 1.5, 0.50, 1.50, 15.0),
        ("SMD1210B020TF", "1210", 0.20, 0.40, 30, 100, 0.6, 0.028, 8.00, 0.80, 5.00),
        ("SMD1210B035TF", "1210", 0.35, 0.70, 60, 100, 0.6, 0.20, 8.00, 0.32, 1.30),
        ("SMD1210B035TF/30", "1210", 0.35, 0.70, 30, 40, 0.6, 0.20, 8.00, 0.32, 1.30),
        ("SMD1210B050TF", "1210", 0.50, 1.00, 13.2, 100, 0.6, 0.058, 8.00, 0.25, 0.90),
        ("SMD1210B050TF/30", "1210", 0.50, 1.00, 30, 40, 0.6, 0.15, 8.00, 0.22, 0.90),
        ("SMD1210B075TF", "1210", 0.75, 1.50, 6, 100, 0.6, 0.10, 8.00, 0.07, 0.40),
        ("SMD1210B075TF/24", "1210", 0.75, 1.50, 24, 100, 0.6, 0.10, 8.00, 0.07, 0.40),
        ("SMD1210B110TF", "1210", 1.10, 2.20, 8, 100, 0.6, 0.30, 8.00, 0.05, 0.21),
        ("SMD1210B110TF/12", "1210", 1.10, 2.20, 12, 100, 0.6, 0.30, 8.00, 0.05, 0.21),
        ("SMD1210B110TF/16", "1210", 1.10, 2.20, 16, 100, 0.6, 0.30, 8.00, 0.05, 0.21),
        ("SMD1210B150TF", "1210", 1.50, 3.00, 6, 100, 0.8, 0.30, 8.00, 0.03, 0.12),
        ("SMD1210B150TF/12", "1210", 1.50, 3.00, 12, 100, 0.8, 0.30, 8.00, 0.03, 0.12),
        ("SMD1210B150TF/16", "1210", 1.50, 3.00, 16, 100, 0.8, 0.30, 8.00, 0.03, 0.12),
        ("SMD1210B175TF", "1210", 1.75, 3.50, 6, 100, 0.8, 1.00, 8.00, 0.02, 0.08),
        ("SMD1210B200TF", "1210", 2.00, 4.00, 6, 100, 0.8, 1.00, 8.00, 0.015, 0.075),

        # Série SMD1812
        ("SMD1812B010TF", "1812", 0.10, 0.30, 30, 100, 0.8, 1.5, 0.50, 1.60, 15.0),
        ("SMD1812B010TF/60", "1812", 0.10, 0.30, 60, 100, 0.8, 1.5, 0.50, 1.60, 15.0),
        ("SMD1812B014TF", "1812", 0.14, 0.34, 60, 100, 0.8, 0.15, 1.50, 1.50, 6.0),
        ("SMD1812B020TF", "1812", 0.20, 0.40, 30, 100, 0.8, 0.028, 8.00, 0.80, 5.0),
        ("SMD1812B020TF-J", "1812", 0.20, 0.40, 60, 40, 0.8, 2.00, 1.00, 0.70, 5.0),
        ("SMD1812B030TF/60", "1812", 0.30, 0.60, 60, 100, 0.8, 0.10, 8.00, 0.25, 3.0),
        ("SMD1812B035TF/30", "1812", 0.35, 0.75, 30, 40, 0.8, 0.15, 8.00, 0.40, 1.7),
        ("SMD1812B035TF/60", "1812", 0.35, 0.75, 60, 40, 1.0, 0.15, 8.00, 0.40, 1.7),
        ("SMD1812B050TF", "1812", 0.50, 1.00, 15, 100, 0.8, 0.15, 8.00, 0.15, 1.0),
        ("SMD1812B050TF/30", "1812", 0.50, 1.00, 30, 100, 0.8, 0.15, 8.00, 0.15, 1.0),
        ("SMD1812B050TF/60", "1812", 0.50, 1.00, 60, 10, 1.5, 0.15, 8.00, 0.15, 1.0),
        ("SMD1812B075TF", "1812", 0.75, 1.50, 13.2, 100, 0.8, 0.20, 8.00, 0.10, 0.45),
        ("SMD1812B075TF/24", "1812", 0.75, 1.50, 24, 100, 0.8, 0.20, 8.00, 0.10, 0.29),
        ("SMD1812B075TF/33", "1812", 0.75, 1.50, 33, 20, 0.8, 0.20, 8.00, 0.10, 0.40),
        ("SMD1812B110TF", "1812", 1.10, 2.20, 8, 100, 0.8, 0.30, 8.00, 0.04, 0.21),
        ("SMD1812B110TF/16", "1812", 1.10, 1.95, 16, 100, 0.8, 0.30, 8.00, 0.06, 0.18),
        ("SMD1812B110TF/24", "1812", 1.10, 1.95, 24, 20, 0.8, 0.50, 8.00, 0.06, 0.20),
        ("SMD1812B110TF/33", "1812", 1.10, 1.95, 33, 20, 0.8, 0.50, 8.00, 0.06, 0.20),
        ("SMD1812B125TF/16", "1812", 1.25, 2.50, 16, 100, 0.8, 0.40, 8.00, 0.05, 0.14),
        ("SMD1812B125TF/6,4L", "1812", 1.25, 2.50, 6, 100, 0.8, 0.40, 8.00, 0.05, 0.14),
        ("SMD1812B150TF/8", "1812", 1.50, 3.00, 8, 100, 0.8, 0.30, 8.00, 0.04, 0.12),
        ("SMD1812B150TF/12", "1812", 1.50, 3.00, 12, 100, 0.8, 0.50, 8.00, 0.040, 0.120),
        ("SMD1812B150TF/16", "1812", 1.50, 2.80, 16, 100, 0.8, 0.50, 8.00, 0.040, 0.120),
        ("SMD1812B150TF/24", "1812", 1.50, 3.00, 24, 20, 0.8, 1.50, 8.00, 0.040, 0.120),
        ("SMD1812B160TF/8(4L)", "1812", 1.60, 2.80, 8, 100, 0.8, 0.30, 8.00, 0.030, 0.100),
        ("SMD1812B160TF/16", "1812", 1.60, 2.80, 16, 100, 0.8, 0.80, 8.00, 0.030, 0.100),
        ("SMD1812B200TFT", "1812", 2.00, 3.50, 8, 100, 0.8, 2.00, 8.00, 0.020, 0.070),
        ("SMD1812B200TF/12", "1812", 2.00, 3.50, 12, 100, 1.0, 2.00, 8.00, 0.020, 0.075),
        ("SMD1812B200TF/16", "1812", 2.00, 3.50, 16, 100, 1.0, 2.00, 8.00, 0.020, 0.075),
        ("SMD1812B260TFT", "1812", 2.60, 5.00, 8, 100, 0.8, 2.50, 8.00, 0.015, 0.047),
        ("SMD1812B260TF/12", "1812", 2.60, 5.00, 12, 100, 0.8, 5.00, 8.00, 0.015, 0.055),
        ("SMD1812B260TF/16", "1812", 2.60, 5.00, 16, 100, 1.2, 5.00, 8.00, 0.015, 0.050),
        ("SMD1812B300TFT", "1812", 3.00, 5.00, 6, 100, 0.8, 4.00, 8.00, 0.012, 0.040),

        # Série SMD2920
        ("SMD2920B030TF", "2920", 0.30, 0.60, 60, 10, 1.5, 3.0, 1.50, 0.600, 4.800),
        ("SMD2920B050TF", "2920", 0.50, 1.00, 60, 10, 1.5, 4.0, 2.50, 0.180, 1.400),
        ("SMD2920B075TF", "2920", 0.75, 1.50, 30, 40, 1.5, 0.3, 8.00, 0.100, 1.000),
        ("SMD2920B075TF/60", "2920", 0.75, 1.50, 60, 10, 1.5, 0.3, 8.00, 0.100, 0.950),
        ("SMD2920B100TF", "2920", 1.10, 2.20, 33, 40, 1.5, 0.5, 8.00, 0.065, 0.410),
        ("SMD2920B110TF/60", "2920", 1.10, 2.20, 60, 20, 2.0, 0.5, 8.00, 0.120, 0.410),
        ("SMD2920B125TF", "2920", 1.25, 2.50, 15, 40, 1.5, 2.0, 8.00, 0.050, 0.250),
        ("SMD2920B150TF", "2920", 1.50, 3.00, 33, 40, 1.5, 2.0, 8.00, 0.035, 0.230),
        ("SMD2920B185TF", "2920", 1.85, 3.70, 33, 40, 1.5, 2.5, 8.00, 0.030, 0.150),
        ("SMD2920B200TF/24", "2920", 2.00, 4.00, 24, 40, 1.5, 5.0, 8.00, 0.020, 0.125),
        ("SMD2920B250TF", "2920", 2.50, 5.00, 15, 40, 1.5, 5.0, 8.00, 0.020, 0.085),
        ("SMD2920B260TF", "2920", 2.60, 5.00, 6, 40, 1.5, 10.0, 8.00, 0.014, 0.075),
        ("SMD2920B260TF/24", "2920", 2.60, 5.00, 24, 40, 1.5, 5.0, 8.00, 0.014, 0.075),
        ("SMD2920B300TF/15", "2920", 3.00, 5.00, 15, 40, 1.5, 20.0, 8.00, 0.012, 0.048),
        ("SMD2920B300TF/30", "2920", 3.00, 5.00, 30, 40, 1.5, 20.0, 8.00, 0.012, 0.048),
        ("SMD2920B330TF", "2920", 3.30, 5.50, 24, 40, 2.0, 5.0, 8.00, 0.015, 0.055),
        ("SMD2920B400TF", "2920", 4.00, 8.00, 15, 40, 1.5, 4.0, 20.00, 0.008, 0.040),
        ("SMD2920B500TF", "2920", 5.00, 10.00, 12, 40, 1.5, 5.0, 20.00, 0.005, 0.031),
        ("SMD2920B500TF/16", "2920", 5.00, 10.00, 16, 40, 2.0, 5.0, 20.00, 0.005, 0.031),
        ("SMD2920B600TF/12", "2920", 6.00, 12.00, 12, 50, 2.0, 2.0, 30.00, 0.004, 0.020),
        ("SMD2920B700TF/12", "2920", 7.00, 14.00, 12, 50, 2.0, 2.0, 35.00, 0.0035, 0.0180),
    ]

    # Mapeamento de footprints por package
    footprint_map = {
        "0603": "MyLib_Fuse:Fuse_0603_1608Metric",
        "0805": "MyLib_Fuse:Fuse_0805_2012Metric",
        "1206": "MyLib_Fuse:Fuse_1206_3216Metric",
        "1210": "MyLib_Fuse:Fuse_1210_3225Metric",
        "1812": "MyLib_Fuse:Fuse_1812_4532Metric",
        "2920": "MyLib_Fuse:Fuse_2920_7451Metric",
    }

    symbol = "MyLib_Fuse:Polyfuse"
    manufacturer = "Bourns"

    insert_data = []
    mypn_counter = start_id

    for row in data:
        part_number, package, ihold, itrip, vmax, imax, pd, time_sec, time_current, rmin, rmax = row

        # Gerar Name
        current_str = format_current(ihold)
        name = f"FUSE_{package}_{current_str}"

        # Description
        description = f"PTC Resettable Fuse, {package} package, {ihold}A hold, {vmax}V"

        # Info1 = corrente
        info1 = f"{ihold}A"

        # Value = part number
        value = part_number

        # Footprint
        footprint = footprint_map.get(package, None)
        if not footprint:
            print(f"Aviso: Pacote {package} não mapeado para footprint. Usando NULL.")
            footprint = None

        # Resistência formatada
        resistance = f"{rmin} ~ {rmax} Ohm"

        # Tempo de resposta
        response_time = f"{time_sec} s at {time_current} A"

        # Notas (incluir Itrip e outros)
        notes = f"Trip current: {itrip}A; Time to trip: {time_sec}s at {time_current}A; Power dissipation: {pd}W"

        # Montar dicionário
        data_dict = {
            'MyPN': f"EL-FUSE-{mypn_counter:06d}",
            'Name': name,
            'Description': description,
            'Value': value,
            'Info1': info1,
            'Info2': None,
            'Symbol': symbol,
            'Footprint': footprint,
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
            'Category': 'PTC Resettable Fuse',
            'Subcategory': 'Surface Mount',
            'Family_Series': f"SMD{package}",
            'Package': package,
            'Mount': 'SMD',
            'Dimensions': None,
            'Temperature_Range': '-40°C to +85°C',
            'REACH_Compliant': None,
            'RoHS_Compliant': 'Yes',
            'Unit': None,
            'Tolerance': None,
            'Voltage_Rating': f"{vmax} V",
            'Current_Rating': f"{ihold} A",
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
            'Resistance': resistance,
            'Technology_Material': 'Polymeric PTC',
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
            'Hold_Current': f"{ihold} A",
            'Trip_Current': f"{itrip} A",
            'Interrupting_Rating': f"{imax} A",
            'Response_Time': response_time,
            'Forward_Voltage': None,
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
            'Power_Dissipation': f"{pd} W",
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
            'LED_Color': None,
            'Luminous_Intensity': None,
            'Wavelength': None,
            'Viewing_Angle_LED': None,
            'Lens_Type': None,
            'If_Current': None,
            'VF_Typical': None,
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
    sql = f"INSERT INTO Fuse ({columns_str}) VALUES\n{values_str};\n"
    out.write(sql)

    if output_path:
        out.close()
        print(f"Arquivo SQL gerado: {output_path}")

def main():
    output_file = os.path.join(SCRIPT_DIR, 'inserts_fuse_yageo.sql')
    generate_insert(output_file, start_id=200)

if __name__ == '__main__':
    main()