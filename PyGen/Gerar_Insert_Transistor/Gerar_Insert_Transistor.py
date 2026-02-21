import os
import csv
import re

# =============================================================================
# CONFIGURAÇÕES GLOBAIS
# =============================================================================
CSV_FILES = {
    "BJT": "Transistor_BJT.csv",
    "FET": "Transistor_FET.csv",
    "OTHER": "Transistor_Other.csv",
}

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
CREATED_BY = "Rogerio Fontanario"
MYPN_PREFIX = "EL-TRA-"
MYPN_DIGITS = 6

BASE_COUNTER = {
    "BJT": 1,
    "FET": 100001,
    "IGBT": 200001,
    "General": 300001
}

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================
def safe_int(value, default=0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def add_prefix_to_footprint(footprint):
    if not footprint or footprint == "~":
        return None
    if footprint.startswith("MyLib_"):
        return footprint
    if ":" in footprint:
        parts = footprint.split(":", 1)
        return f"MyLib_{parts[0]}:{parts[1]}"
    return f"MyLib_{footprint}"

def ensure_unit(value, unit):
    if value is None or value == "":
        return None
    s = str(value).strip()
    if s and not s[-1].isalpha():
        return f"{s}{unit}"
    return s

def combine_min_max(min_val, max_val, unit=""):
    if min_val is None and max_val is None:
        return None
    min_str = str(min_val) if min_val is not None else ""
    max_str = str(max_val) if max_val is not None else ""
    if min_str and max_str:
        return f"{min_str}{unit} ~ {max_str}{unit}"
    elif min_str:
        return f"{min_str}{unit}"
    elif max_str:
        return f"{max_str}{unit}"
    return None

def combine_range_with_unit(min_val, max_val, unit):
    min_str = str(min_val) if min_val is not None else ""
    max_str = str(max_val) if max_val is not None else ""
    if min_str and max_str:
        return f"{min_str} ~ {max_str}"
    elif min_str:
        return min_str
    elif max_str:
        return max_str
    return None

# =============================================================================
# FUNÇÃO PARA CONSTRUIR NAME, INFO1, INFO2
# =============================================================================
def build_name_and_info(row, tipo):
    pn = row.get("Name", "").strip()
    if not pn:
        pn = "UNKNOWN"

    if tipo == "BJT":
        polarity = row.get("Type", "").strip()
        vceo = ensure_unit(row.get("VCEO"), "V") or ""
        ic = ensure_unit(row.get("IC_Continuous"), "A") or ""
        parts = [pn]
        if polarity:
            parts.append(polarity)
        if vceo:
            parts.append(vceo)
        if ic:
            parts.append(ic)
        name = "_".join(parts)
        info1 = f"BJT-{polarity}" if polarity else "BJT"
        info2 = f"{vceo}-{ic}".strip("-")
        q_type = "BJT"
        polarity_channel = polarity
        return name, info1, info2, q_type, polarity_channel

    elif tipo == "FET":
        fet_type = row.get("FET_Type", "MOSFET").strip()
        channel = row.get("Channel", "").strip()
        vds = ensure_unit(row.get("VDS"), "V") or ""
        id_cont = ensure_unit(row.get("ID_Continuous"), "A") or ""
        rds = ensure_unit(row.get("RDS_On"), "Ω") or ""
        parts = [pn]
        type_channel = fet_type
        if channel:
            type_channel += f"-{channel}"
        parts.append(type_channel)
        if vds:
            parts.append(vds)
        if id_cont:
            parts.append(id_cont)
        if rds:
            parts.append(rds)
        name = "_".join(parts)
        info1 = type_channel
        info2 = f"{vds}-{id_cont}-{rds}".strip("-")
        q_type = fet_type
        polarity_channel = channel
        return name, info1, info2, q_type, polarity_channel

    elif tipo == "IGBT":
        vce = ensure_unit(row.get("VCE"), "V") or ""
        ic = ensure_unit(row.get("IC_Continuous"), "A") or ""
        vcesat = ensure_unit(row.get("VCE_Sat"), "V") or ""
        parts = [pn, "IGBT-N"]
        if vce:
            parts.append(vce)
        if ic:
            parts.append(ic)
        if vcesat:
            parts.append(vcesat)
        name = "_".join(parts)
        info1 = "IGBT-N"
        info2 = f"{vce}-{ic}-{vcesat}".strip("-")
        q_type = "IGBT"
        polarity_channel = "N"
        return name, info1, info2, q_type, polarity_channel

    else:  # General
        dev_type = row.get("Device_Type", "").strip()
        polarity = row.get("Subtype", "").strip()
        vce = ensure_unit(row.get("VCE"), "V") or ""
        ic = ensure_unit(row.get("IC_Continuous"), "A") or ""
        parts = [pn]
        if dev_type:
            parts.append(dev_type)
        if polarity:
            parts.append(polarity)
        if vce:
            parts.append(vce)
        if ic:
            parts.append(ic)
        name = "_".join(parts)
        info1 = f"{dev_type}-{polarity}" if polarity else dev_type
        info2 = f"{vce}-{ic}".strip("-")
        q_type = dev_type
        polarity_channel = polarity
        return name, info1, info2, q_type, polarity_channel

# =============================================================================
# COLUNAS COMUNS A TODOS OS TRANSISTORES (EXISTENTES NA TABELA)
# =============================================================================
BASE_COLUMNS = [
    "MyPN", "Name", "Description", "Value", "Info1", "Info2",
    "Symbol", "Footprint", "Footprint_Filter", "Datasheet",
    "Manufacturer", "Manufacturer_PN", "Package", "Mount",
    "Temperature_Range", "REACH_Compliant", "RoHS_Compliant",
    "Stock_Qty", "Stock_Location", "Price", "Currency",
    "Min_Stock", "Max_Stock", "Active", "Version",
    "Created_At", "Created_By", "Exclude_from_BOM", "Exclude_from_Board",
    "LCSC_PN", "LCSC_URL", "Mouser_PN", "Mouser_URL",
    "Digikey_PN", "Digikey_URL", "Alternative_PN", "Alternative_URL",
    "Category", "Subcategory", "Family_Series", "Q_Type", "Polarity_Channel_Type",
]

# =============================================================================
# COLUNAS ESPECÍFICAS PARA CADA TIPO (APENAS AS QUE EXISTEM NA TABELA)
# =============================================================================
BJT_EXTRA = [
    "VCEO", "Current_Collector", "DC_Gain_HFE", "VCE_Sat",
    "Transition_Frequency", "IC_Pulse", "Power_Dissipation", "Junction_Temperature"
]

FET_EXTRA = [
    "VDS_Max", "VGS_Max", "VGS_Threshold", "RDS_On", "ID_Continuous", "ID_Pulse",
    "Input_Capacitance", "Output_Capacitance", "Reverse_Transfer_Capacitance",
    "Gate_Charge", "Rise_Time", "Fall_Time", "Diode_Forward_Voltage",
    "IDSS", "Gate_Reverse_Current", "Power_Dissipation", "Junction_Temperature",
    # Opcionais para JFET:
    "VGS_Off", "Gain"
]

IGBT_EXTRA = [
    "VCEO", "VGE_Threshold", "IC_Continuous", "IC_Pulse", "VCE_Sat",
    "Power_Dissipation", "Junction_Temperature"
]

GENERAL_EXTRA = [
    "VCEO", "IC_Continuous", "DC_Gain_HFE", "Power_Dissipation", "Junction_Temperature"
]

# =============================================================================
# FUNÇÃO PARA CRIAR UM DICIONÁRIO COM AS COLUNAS DESEJADAS
# =============================================================================
def create_row(columns):
    return {col: None for col in columns}

# =============================================================================
# FUNÇÃO PARA PROCESSAR UM CSV E GERAR INSERTS
# =============================================================================
def process_csv(csv_path, table_name, tipo, base_counter, extra_columns):
    if not os.path.isfile(csv_path):
        print(f"Arquivo não encontrado: {csv_path}")
        return [], base_counter

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return [], base_counter

    all_columns = BASE_COLUMNS + extra_columns
    values_lines = []
    mypn_counter = base_counter

    for row in rows:
        if tipo == "OTHER" and row.get("Device_Type", "").upper() == "IGBT":
            continue

        name, info1, info2, q_type, polarity_channel = build_name_and_info(row, tipo)

        mypn = f"{MYPN_PREFIX}{mypn_counter:06d}"
        mypn_counter += 1

        values = create_row(all_columns)

        # Campos básicos
        values["MyPN"] = mypn
        values["Name"] = name
        values["Description"] = row.get("Description")
        values["Value"] = row.get("Value")
        values["Info1"] = info1
        values["Info2"] = info2
        values["Symbol"] = row.get("Symbol")
        values["Footprint"] = add_prefix_to_footprint(row.get("Footprint"))
        values["Footprint_Filter"] = row.get("Footprint_Filter")
        values["Datasheet"] = row.get("Datasheet")
        values["Manufacturer"] = row.get("Manufacturer")
        values["Manufacturer_PN"] = row.get("Manufacturer_PN") or row.get("Name")
        values["Package"] = row.get("Package")
        values["Mount"] = row.get("Mount").replace("Through Hole", "THT") if row.get("Mount") else None
        values["Temperature_Range"] = combine_range_with_unit(row.get("MinTemp"), row.get("MaxTemp"), "°C")
        values["REACH_Compliant"] = row.get("REACH_Compliant")
        values["RoHS_Compliant"] = row.get("RoHS_Compliant")
        values["Stock_Qty"] = safe_int(row.get("StockQty"))
        values["Stock_Location"] = row.get("StockPlace")
        values["Price"] = row.get("Price")
        values["Currency"] = row.get("Currency", "USD")
        values["Min_Stock"] = safe_int(row.get("Min_Stock"))
        values["Max_Stock"] = safe_int(row.get("Max_Stock"))
        values["Active"] = 1
        values["Version"] = 1
        values["Created_At"] = "datetime('now')"
        values["Created_By"] = CREATED_BY
        values["Exclude_from_BOM"] = 0
        values["Exclude_from_Board"] = 0

        # Fornecedores
        values["LCSC_PN"] = row.get("LCSC_PN")
        values["LCSC_URL"] = row.get("LCSC_URL")
        values["Mouser_PN"] = row.get("Mouser_PN")
        values["Mouser_URL"] = row.get("Mouser_URL")
        values["Digikey_PN"] = row.get("Digikey_PN")
        values["Digikey_URL"] = row.get("Digikey_URL")
        values["Alternative_PN"] = row.get("Alternative_PN")
        values["Alternative_URL"] = row.get("Alternative_URL")

        # Categoria e subcategoria
        values["Category"] = "Transistor"
        if tipo == "BJT":
            values["Subcategory"] = "BJT"
        elif tipo == "FET":
            values["Subcategory"] = "FET"
        elif tipo == "IGBT":
            values["Subcategory"] = "IGBT"
        else:
            values["Subcategory"] = row.get("Device_Type")

        values["Family_Series"] = row.get("Series")
        values["Q_Type"] = q_type
        values["Polarity_Channel_Type"] = polarity_channel

        # Campos específicos
        if tipo == "BJT":
            values["VCEO"] = ensure_unit(row.get("VCEO"), "V")
            values["Current_Collector"] = ensure_unit(row.get("IC_Continuous"), "A")
            values["DC_Gain_HFE"] = combine_min_max(row.get("HFE_Min"), row.get("HFE_Max"))
            values["VCE_Sat"] = ensure_unit(row.get("VCE_Sat_Max"), "V")
            values["Transition_Frequency"] = ensure_unit(row.get("FT"), "MHz")
            values["IC_Pulse"] = ensure_unit(row.get("IC_Peak"), "A")
            values["Power_Dissipation"] = ensure_unit(row.get("Power_Total"), "W")
            values["Junction_Temperature"] = row.get("Operating_Temp")

        elif tipo == "FET":
            values["VDS_Max"] = ensure_unit(row.get("VDS"), "V")
            values["VGS_Max"] = ensure_unit(row.get("VGS"), "V")
            values["VGS_Threshold"] = ensure_unit(row.get("VGS_Threshold"), "V")
            values["RDS_On"] = ensure_unit(row.get("RDS_On"), "Ω")
            values["ID_Continuous"] = ensure_unit(row.get("ID_Continuous"), "A")
            values["ID_Pulse"] = ensure_unit(row.get("ID_Pulse"), "A")
            values["Input_Capacitance"] = ensure_unit(row.get("Input_Capacitance"), "pF")
            values["Output_Capacitance"] = ensure_unit(row.get("Output_Capacitance"), "pF")
            values["Reverse_Transfer_Capacitance"] = ensure_unit(row.get("Reverse_Capacitance"), "pF")
            values["Gate_Charge"] = ensure_unit(row.get("Gate_Charge_Total"), "nC")
            values["Rise_Time"] = ensure_unit(row.get("Rise_Time"), "ns")
            values["Fall_Time"] = ensure_unit(row.get("Fall_Time"), "ns")
            values["Diode_Forward_Voltage"] = ensure_unit(row.get("Diode_Forward_Voltage"), "V")
            values["IDSS"] = ensure_unit(row.get("IDSS"), "A")
            values["Gate_Reverse_Current"] = ensure_unit(row.get("IGSS"), "A")  # IGSS -> Gate_Reverse_Current
            values["Power_Dissipation"] = ensure_unit(row.get("Power_Total"), "W")
            values["Junction_Temperature"] = row.get("Operating_Temp")
            # Opcionais JFET
            values["VGS_Off"] = ensure_unit(row.get("VGS_Off"), "V")
            values["Gain"] = ensure_unit(row.get("Gain"), "")

        elif tipo == "IGBT":
            values["VCEO"] = ensure_unit(row.get("VCE"), "V")
            values["VGE_Threshold"] = ensure_unit(row.get("VGE"), "V")
            values["IC_Continuous"] = ensure_unit(row.get("IC_Continuous"), "A")
            values["IC_Pulse"] = ensure_unit(row.get("IC_Pulse"), "A")
            values["VCE_Sat"] = ensure_unit(row.get("VCE_Sat"), "V")
            values["Power_Dissipation"] = ensure_unit(row.get("Power_Total"), "W")
            values["Junction_Temperature"] = row.get("Operating_Temp")

        elif tipo == "OTHER":  # General
            values["VCEO"] = ensure_unit(row.get("VCE"), "V")
            values["IC_Continuous"] = ensure_unit(row.get("IC_Continuous"), "A")
            values["DC_Gain_HFE"] = ensure_unit(row.get("HFE"), "")
            values["Power_Dissipation"] = ensure_unit(row.get("Power_Total"), "W")
            values["Junction_Temperature"] = row.get("Operating_Temp")

        values_lines.append(values)

    return values_lines, mypn_counter

# =============================================================================
# FUNÇÃO PARA ESCREVER ARQUIVO SQL
# =============================================================================
def write_sql(table_name, values_list, output_dir, extra_columns):
    if not values_list:
        return

    columns = BASE_COLUMNS + extra_columns

    values_lines = []
    for v in values_list:
        formatted = []
        for col in columns:
            val = v.get(col)
            if val is None:
                formatted.append("NULL")
            elif isinstance(val, int):
                formatted.append(str(val))
            elif val == "datetime('now')":
                formatted.append(val)
            else:
                val_escaped = str(val).replace("'", "''")
                formatted.append(f"'{val_escaped}'")
        values_lines.append("(" + ", ".join(formatted) + ")")

    output_file = os.path.join(output_dir, f"insert_{table_name}.sql")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"-- Script de inserção para {table_name}\n")
        f.write(f"-- Gerado a partir de CSVs\n\n")
        f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES\n")
        f.write(",\n".join(values_lines) + ";\n")
    print(f"Arquivo gerado: {output_file} com {len(values_list)} inserts")

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # BJT
    bjt_path = os.path.join(script_dir, CSV_FILES["BJT"])
    bjt_values, _ = process_csv(bjt_path, "Transistor_BJT", "BJT", BASE_COUNTER["BJT"], BJT_EXTRA)
    write_sql("Transistor_BJT", bjt_values, script_dir, BJT_EXTRA)

    # FET
    fet_path = os.path.join(script_dir, CSV_FILES["FET"])
    fet_values, _ = process_csv(fet_path, "Transistor_FET", "FET", BASE_COUNTER["FET"], FET_EXTRA)
    write_sql("Transistor_FET", fet_values, script_dir, FET_EXTRA)

    # IGBT e General do OTHER
    other_path = os.path.join(script_dir, CSV_FILES["OTHER"])
    igbt_values = []
    general_values = []
    if os.path.isfile(other_path):
        with open(other_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dev_type = row.get("Device_Type", "").upper()
                if dev_type == "IGBT":
                    # IGBT
                    name, info1, info2, q_type, polarity = build_name_and_info(row, "IGBT")
                    mypn = f"{MYPN_PREFIX}{BASE_COUNTER['IGBT'] + len(igbt_values):06d}"
                    values = create_row(BASE_COLUMNS + IGBT_EXTRA)
                    # Preencher campos (código de preenchimento - pode ser simplificado com função)
                    values["MyPN"] = mypn
                    values["Name"] = name
                    values["Description"] = row.get("Description")
                    values["Value"] = row.get("Value")
                    values["Info1"] = info1
                    values["Info2"] = info2
                    values["Symbol"] = row.get("Symbol")
                    values["Footprint"] = add_prefix_to_footprint(row.get("Footprint"))
                    values["Footprint_Filter"] = row.get("Footprint_Filter")
                    values["Datasheet"] = row.get("Datasheet")
                    values["Manufacturer"] = row.get("Manufacturer")
                    values["Manufacturer_PN"] = row.get("Manufacturer_PN") or row.get("Name")
                    values["Package"] = row.get("Package")
                    values["Mount"] = row.get("Mount").replace("Through Hole", "THT") if row.get("Mount") else None
                    values["Temperature_Range"] = combine_range_with_unit(row.get("MinTemp"), row.get("MaxTemp"), "°C")
                    values["REACH_Compliant"] = row.get("REACH_Compliant")
                    values["RoHS_Compliant"] = row.get("RoHS_Compliant")
                    values["Stock_Qty"] = safe_int(row.get("StockQty"))
                    values["Stock_Location"] = row.get("StockPlace")
                    values["Price"] = row.get("Price")
                    values["Currency"] = row.get("Currency", "USD")
                    values["Min_Stock"] = safe_int(row.get("Min_Stock"))
                    values["Max_Stock"] = safe_int(row.get("Max_Stock"))
                    values["Active"] = 1
                    values["Version"] = 1
                    values["Created_At"] = "datetime('now')"
                    values["Created_By"] = CREATED_BY
                    values["Exclude_from_BOM"] = 0
                    values["Exclude_from_Board"] = 0
                    values["LCSC_PN"] = row.get("LCSC_PN")
                    values["LCSC_URL"] = row.get("LCSC_URL")
                    values["Mouser_PN"] = row.get("Mouser_PN")
                    values["Mouser_URL"] = row.get("Mouser_URL")
                    values["Digikey_PN"] = row.get("Digikey_PN")
                    values["Digikey_URL"] = row.get("Digikey_URL")
                    values["Alternative_PN"] = row.get("Alternative_PN")
                    values["Alternative_URL"] = row.get("Alternative_URL")
                    values["Category"] = "Transistor"
                    values["Subcategory"] = "IGBT"
                    values["Family_Series"] = row.get("Series")
                    values["Q_Type"] = q_type
                    values["Polarity_Channel_Type"] = polarity
                    # IGBT extras
                    values["VCEO"] = ensure_unit(row.get("VCE"), "V")
                    values["VGE_Threshold"] = ensure_unit(row.get("VGE"), "V")
                    values["IC_Continuous"] = ensure_unit(row.get("IC_Continuous"), "A")
                    values["IC_Pulse"] = ensure_unit(row.get("IC_Pulse"), "A")
                    values["VCE_Sat"] = ensure_unit(row.get("VCE_Sat"), "V")
                    values["Power_Dissipation"] = ensure_unit(row.get("Power_Total"), "W")
                    values["Junction_Temperature"] = row.get("Operating_Temp")
                    igbt_values.append(values)
                else:
                    # General
                    name, info1, info2, q_type, polarity = build_name_and_info(row, "General")
                    mypn = f"{MYPN_PREFIX}{BASE_COUNTER['General'] + len(general_values):06d}"
                    values = create_row(BASE_COLUMNS + GENERAL_EXTRA)
                    # Preencher campos (idêntico ao IGBT, mas com GENERAL_EXTRA)
                    values["MyPN"] = mypn
                    values["Name"] = name
                    values["Description"] = row.get("Description")
                    values["Value"] = row.get("Value")
                    values["Info1"] = info1
                    values["Info2"] = info2
                    values["Symbol"] = row.get("Symbol")
                    values["Footprint"] = add_prefix_to_footprint(row.get("Footprint"))
                    values["Footprint_Filter"] = row.get("Footprint_Filter")
                    values["Datasheet"] = row.get("Datasheet")
                    values["Manufacturer"] = row.get("Manufacturer")
                    values["Manufacturer_PN"] = row.get("Manufacturer_PN") or row.get("Name")
                    values["Package"] = row.get("Package")
                    values["Mount"] = row.get("Mount").replace("Through Hole", "THT") if row.get("Mount") else None
                    values["Temperature_Range"] = combine_range_with_unit(row.get("MinTemp"), row.get("MaxTemp"), "°C")
                    values["REACH_Compliant"] = row.get("REACH_Compliant")
                    values["RoHS_Compliant"] = row.get("RoHS_Compliant")
                    values["Stock_Qty"] = safe_int(row.get("StockQty"))
                    values["Stock_Location"] = row.get("StockPlace")
                    values["Price"] = row.get("Price")
                    values["Currency"] = row.get("Currency", "USD")
                    values["Min_Stock"] = safe_int(row.get("Min_Stock"))
                    values["Max_Stock"] = safe_int(row.get("Max_Stock"))
                    values["Active"] = 1
                    values["Version"] = 1
                    values["Created_At"] = "datetime('now')"
                    values["Created_By"] = CREATED_BY
                    values["Exclude_from_BOM"] = 0
                    values["Exclude_from_Board"] = 0
                    values["LCSC_PN"] = row.get("LCSC_PN")
                    values["LCSC_URL"] = row.get("LCSC_URL")
                    values["Mouser_PN"] = row.get("Mouser_PN")
                    values["Mouser_URL"] = row.get("Mouser_URL")
                    values["Digikey_PN"] = row.get("Digikey_PN")
                    values["Digikey_URL"] = row.get("Digikey_URL")
                    values["Alternative_PN"] = row.get("Alternative_PN")
                    values["Alternative_URL"] = row.get("Alternative_URL")
                    values["Category"] = "Transistor"
                    values["Subcategory"] = row.get("Device_Type")
                    values["Family_Series"] = row.get("Series")
                    values["Q_Type"] = q_type
                    values["Polarity_Channel_Type"] = polarity
                    # General extras
                    values["VCEO"] = ensure_unit(row.get("VCE"), "V")
                    values["IC_Continuous"] = ensure_unit(row.get("IC_Continuous"), "A")
                    values["DC_Gain_HFE"] = ensure_unit(row.get("HFE"), "")
                    values["Power_Dissipation"] = ensure_unit(row.get("Power_Total"), "W")
                    values["Junction_Temperature"] = row.get("Operating_Temp")
                    general_values.append(values)

        write_sql("Transistor_IGBT", igbt_values, script_dir, IGBT_EXTRA)
        write_sql("Transistor_General", general_values, script_dir, GENERAL_EXTRA)

    print("Processamento concluído.")

if __name__ == "__main__":
    main()