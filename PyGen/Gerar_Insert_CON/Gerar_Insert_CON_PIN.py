import csv
import os
import re
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, "Connector_PIN.csv")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "insert_connector_pin.sql")

# Lista completa das colunas da tabela na ordem desejada (excluindo ID_Aux)
COLUNAS = [
    'MyPN', 'Name', 'Description', 'Value', 'Info1', 'Info2',
    'Symbol', 'Footprint', 'Footprint_Filter', 'Datasheet', 'Notes',
    'Notes_to_Buyer', 'Manufacturer', 'Manufacturer_PN', 'Manufacturer_URL',
    'Alternative_PN', 'Alternative_URL', 'Digikey_PN', 'Digikey_URL',
    'Mouser_PN', 'Mouser_URL', 'LCSC_PN', 'LCSC_URL',
    'Stock_Qty', 'Stock_Location', 'Stock_Unit', 'Price', 'Currency',
    'Min_Stock', 'Max_Stock', 'Last_Purchase_Date', 'Last_Purchase_Price',
    'Active', 'Version', 'Created_At', 'Created_By', 'Modified_At', 'Modified_By',
    'Exclude_from_BOM', 'Exclude_from_Board', 'Category', 'Subcategory',
    'Family_Series', 'Package', 'Mount', 'Dimensions', 'Temperature_Range',
    'REACH_Compliant', 'RoHS_Compliant', 'Unit', 'Tolerance',
    'Voltage_Rating', 'Current_Rating', 'Power_Rating', 'Temperature_Coefficient',
    'Pin_Configuration', 'Gender', 'Pin_Type', 'Pitch', 'Orientation',
    'Locking_Mechanism', 'Current_Rating_Per_Pin', 'IP_Rating', 'Wire_Gauge',
    'Termination_Style', 'Resistance', 'Technology_Material', 'Capacitance',
    'Dielectric_Type', 'ESR', 'Ripple_Current', 'Leakage_Current', 'Inductance',
    'DC_Resistance', 'Self_Resonant_Frequency', 'Quality_Factor_Q',
    'Saturation_Current', 'Hold_Current', 'Trip_Current', 'Interrupting_Rating',
    'Response_Time', 'Forward_Voltage', 'Reverse_Leakage', 'Junction_Capacitance',
    'Reverse_Recovery_Time', 'Zener_Voltage', 'Zener_Impedance',
    'Reverse_Standoff_Voltage', 'Breakdown_Voltage', 'Clamping_Voltage',
    'Peak_Pulse_Current', 'Q_Type', 'Polarity_Channel_Type', 'Power_Dissipation',
    'Junction_Temperature', 'VDS_Max', 'VGS_Max', 'VGS_Threshold', 'RDS_On',
    'ID_Continuous', 'ID_Pulse', 'Input_Capacitance', 'Output_Capacitance',
    'Reverse_Transfer_Capacitance', 'Gate_Charge', 'Rise_Time', 'Fall_Time',
    'IDSS', 'VGS_Off', 'Gain', 'Gate_Reverse_Current', 'VCEO', 'Current_Collector',
    'DC_Gain_HFE', 'Saturation_Voltage', 'Transition_Frequency', 'VCE_Sat',
    'IC_Continuous', 'IC_Pulse', 'VGE_Threshold', 'Short_Circuit_Withstanding',
    'Diode_Forward_Voltage', 'Frequency', 'Oscillator_Type', 'Load_Capacitance',
    'Supply_Voltage', 'Coil_Voltage', 'Coil_Resistance', 'Contact_Configuration',
    'Contact_Current_Rating', 'Contact_Voltage_Rating', 'Relay_Type', 'Operating_Time',
    'Transformer_Type', 'Turns_Ratio', 'Isolation_Voltage', 'Power_Rating_VA',
    'Frequency_Rating', 'Battery_Chemistry', 'Battery_Voltage_Nominal',
    'Battery_Capacity', 'Battery_Size', 'Rechargeable', 'Number_of_Cells',
    'Display_Type', 'Display_Size', 'Resolution', 'Interface', 'Backlight',
    'Controller', 'Color', 'Sensor_Type', 'Sensor_Interface', 'Supply_Voltage_Min',
    'Supply_Voltage_Max', 'Accuracy', 'Output_Type', 'LED_Color', 'Luminous_Intensity',
    'Wavelength', 'Viewing_Angle_LED', 'Lens_Type', 'If_Current', 'VF_Typical',
    'Optocoupler_Type', 'CTR', 'Tube_Type', 'Heater_Voltage', 'Heater_Current',
    'Plate_Voltage_Max'
]

# ==================== FUNÇÕES AUXILIARES ====================
def get_val(row, key):
    """Retorna o valor da coluna ou None se vazio."""
    val = row.get(key, '').strip()
    return val if val != '' else None

def sql_str(val):
    """Escapa aspas simples e retorna string formatada para SQL."""
    if val is None:
        return 'NULL'
    return "'" + str(val).replace("'", "''") + "'"

def format_pitch(pitch_str):
    """Formata o pitch para duas casas decimais (ex: 1.0 -> 1.00)."""
    try:
        pitch = float(pitch_str)
        return f"{pitch:.2f}"
    except (ValueError, TypeError):
        return pitch_str

def build_footprint(row, suffix):
    """Constrói o footprint conforme as pastas da imagem."""
    connector_type = row.get('Connector_Type', '').strip()
    pitch_raw = row.get('Pitch_mm', '').strip()
    pitch_fmt = format_pitch(pitch_raw)
    if 'Header' in connector_type:
        folder = f"MyLib_Connector_PinHeader_{pitch_fmt}mm.pretty"
    elif 'Socket' in connector_type:
        folder = f"MyLib_Connector_PinSocket_{pitch_fmt}mm.pretty"
    else:
        folder = "MyLib_Connector_PIN"
    return f"{folder}:{suffix}"

# ==================== LEITURA E PROCESSAMENTO ====================
if not os.path.exists(CSV_FILE):
    print(f"ERRO: Arquivo CSV não encontrado: {CSV_FILE}")
    exit(1)

# Lista para armazenar os dados processados de cada linha
dados_linhas = []
# Conjunto para armazenar todas as colunas da tabela que aparecem em pelo menos uma linha
colunas_utilizadas = set()

with open(CSV_FILE, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        valores = {}

        # Mapeamento direto (CSV -> tabela)
        mapeamento_direto = {
            'MyPN': 'MyPN',
            'Name': 'Name',
            'Description': 'Description',
            'Symbol': 'Symbol',
            'Footprint_Filter': 'Footprint_Filter',
            'Datasheet': 'Datasheet',
            'Notes': 'Notes',
            'Manufacturer': 'Manufacturer',
            'Manufacturer_PN': 'Manufacturer_PN',
            'LCSC_PN': 'LCSC_PN',
            'LCSC_URL': 'LCSC_URL',
            'Mouser_PN': 'Mouser_PN',
            'Mouser_URL': 'Mouser_URL',
            'Digikey_PN': 'Digikey_PN',
            'Digikey_URL': 'Digikey_URL',
            'Alternative_PN': 'Alternative_PN',
            'StockQty': 'Stock_Qty',
            'Stock_Unit': 'Stock_Unit',
            'Price': 'Price',
            'Currency': 'Currency',
            'Min_Stock': 'Min_Stock',
            'Max_Stock': 'Max_Stock',
            'Last_Purchase_Date': 'Last_Purchase_Date',
            'Last_Purchase_Price': 'Last_Purchase_Price',
            'Active': 'Active',
            'Version': 'Version',
            'CreatedAt': 'Created_At',
            'CreatedBy': 'Created_By',
            'ModifiedAt': 'Modified_At',
            'ModifiedBy': 'Modified_By',
            'Exclude_from_BOM': 'Exclude_from_BOM',
            'Exclude_from_Board': 'Exclude_from_Board',
            'Category': 'Category',
            'Subcategory': 'Subcategory',
            'Package': 'Package',
            'Dimensions': 'Dimensions',
            'REACH_Compliant': 'REACH_Compliant',
            'RoHS_Compliant': 'RoHS_Compliant',
            'UL_Certified': 'UL_Certified',
            'IP_Rating': 'IP_Rating',
            'Flammability_Rating': 'Flammability_Rating',
            'Solder_Type': 'Termination_Style',
            'Solder_Temperature_C': 'Solder_Temperature_C',
            'Cleaning_Process': 'Cleaning_Process',
            'Series': 'Family_Series',
            'StockPlace': 'Stock_Location',
            'Pins_Configuration': 'Pin_Configuration',
            'Gender': 'Gender',
            'Orientation': 'Orientation',
            'Locking_Mechanism': 'Locking_Mechanism',
            'Current_Rating_A': 'Current_Rating_Per_Pin',
            'Voltage_Rating_V': 'Voltage_Rating',
            'Contact_Resistance_mOhm': 'Contact_Resistance',
            'Insulation_Resistance_MOhm': 'Insulation_Resistance',
            'Dielectric_Withstanding_Voltage_V': 'Dielectric_Withstanding_Voltage',
            'Contact_Type': 'Contact_Type',
            'Contact_Material': 'Contact_Material',
            'Contact_Plating': 'Contact_Plating',
            'Plating_Thickness_um': 'Plating_Thickness',
            'Housing_Material': 'Housing_Material',
            'Housing_Color': 'Housing_Color',
            'Insulator_Material': 'Insulator_Material',
            'Polarization': 'Polarization',
            'Length_mm': 'Length_mm',
            'Width_mm': 'Width_mm',
            'Height_mm': 'Height_mm',
            'PCB_Tolerance': 'PCB_Tolerance',
            'Mating_Cycles': 'Mating_Cycles',
            'Insertion_Force_N': 'Insertion_Force',
            'Withdrawal_Force_N': 'Withdrawal_Force',
            'Mounting_Type': 'Mount',
        }

        for csv_col, tab_col in mapeamento_direto.items():
            v = get_val(row, csv_col)
            if v is not None:
                valores[tab_col] = v

        # --- Campos especiais ---
        pitch_val = get_val(row, 'Pitch_mm')
        if pitch_val:
            valores['Pitch'] = pitch_val + 'mm'

        curr_total = get_val(row, 'Current_Rating_Total_A')
        if curr_total:
            valores['Current_Rating'] = curr_total

        min_temp = get_val(row, 'Operating_Temp_Min_C')
        max_temp = get_val(row, 'Operating_Temp_Max_C')
        if min_temp and max_temp:
            valores['Temperature_Range'] = f"{min_temp}°C to {max_temp}°C"

        # Value
        valor_csv = get_val(row, 'Value')
        if valor_csv:
            valores['Value'] = valor_csv
        else:
            pins_cfg = get_val(row, 'Pins_Configuration')
            conn_type = get_val(row, 'Connector_Type')
            if pins_cfg and conn_type:
                tipo = "Header" if "Header" in conn_type else "Socket" if "Socket" in conn_type else "Pin"
                valores['Value'] = f"Pin_{tipo}_{pins_cfg}"

        # Info1
        pitch_raw = get_val(row, 'Pitch_mm')
        orient = get_val(row, 'Orientation')
        if pitch_raw and orient:
            pitch_fmt = format_pitch(pitch_raw)
            valores['Info1'] = f"{pitch_fmt}mm_{orient}"
        # Info2 não será incluído (permanece sem valor)

        # Footprint (modificado)
        fp_original = get_val(row, 'Footprint')
        if fp_original and ':' in fp_original:
            prefix, suffix = fp_original.split(':', 1)
            new_fp = build_footprint(row, suffix)
            valores['Footprint'] = new_fp

        # Pin_Type
        conn_type = get_val(row, 'Connector_Type')
        if conn_type:
            if 'Header' in conn_type:
                valores['Pin_Type'] = 'Header'
            elif 'Socket' in conn_type:
                valores['Pin_Type'] = 'Socket'

        # Adicionar as colunas presentes ao conjunto
        colunas_utilizadas.update(valores.keys())
        # Guardar a linha processada
        dados_linhas.append(valores)

# ==================== DETERMINAR COLUNAS FINAIS ====================
# Manter apenas as colunas que estão na lista original e foram utilizadas
# Ordenar conforme a ordem original
colunas_finais = [col for col in COLUNAS if col in colunas_utilizadas]

print(f"Colunas a serem inseridas ({len(colunas_finais)}): {colunas_finais}")

# ==================== GERAÇÃO DO INSERT ÚNICO ====================
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(f"-- Inserções para a tabela Connector_PIN\n")
    f.write(f"-- Gerado em {datetime.now()}\n\n")

    # Cabeçalho do INSERT
    f.write(f"INSERT INTO Connector_PIN (\n")
    f.write("    " + ",\n    ".join(colunas_finais) + "\n")
    f.write(") VALUES\n")

    linhas_sql = []
    for valores in dados_linhas:
        # Para cada coluna na lista final, obter o valor ou NULL
        linha_valores = []
        for col in colunas_finais:
            linha_valores.append(sql_str(valores.get(col)))
        linhas_sql.append("(" + ", ".join(linha_valores) + ")")

    f.write(",\n".join(linhas_sql))
    f.write(";\n\n-- Fim dos inserts\n")

print(f"Arquivo SQL gerado: {OUTPUT_FILE}")