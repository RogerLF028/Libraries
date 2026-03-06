#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gera três BOMs customizadas (Buyer, Assembly, Engineer) a partir da netlist XML do KiCad.
Os arquivos são salvos em subpastas dentro do diretório do projeto:
  - Buyer   → Outputs/Fabrication/
  - Engineer → Outputs/Documentation/
  - Assembly → Outputs/Assemble/
As pastas são criadas automaticamente se não existirem.
"""

import sys
import os
import datetime
import csv
import xml.etree.ElementTree as ET

# =============================================================================
# LISTA DE TODAS AS COLUNAS DISPONÍVEIS (baseada na tabela fornecida)
# =============================================================================
ALL_POSSIBLE_FIELDS = [
    "MyPN", "Name", "Description", "Value", "Info1", "Info2", "Symbol",
    "Footprint", "Footprint_Filter", "Datasheet", "Notes", "Notes_to_Buyer",
    "Manufacturer", "Manufacturer_PN", "Manufacturer_URL", "Alternative_PN",
    "Alternative_URL", "Digikey_PN", "Digikey_URL", "Mouser_PN", "Mouser_URL",
    "LCSC_PN", "LCSC_URL", "Stock_Qty", "Stock_Location", "Stock_Unit",
    "Price", "Currency", "Min_Stock", "Max_Stock", "Last_Purchase_Date",
    "Last_Purchase_Price", "Active", "Version", "Created_At", "Created_By",
    "Modified_At", "Modified_By", "Exclude_from_BOM", "Exclude_from_Board",
    "Category", "Subcategory", "Family_Series", "Package", "Mount",
    "Dimensions", "Temperature_Range", "REACH_Compliant", "RoHS_Compliant",
    "Unit", "Tolerance", "Voltage_Rating", "Current_Rating", "Power_Rating",
    "Temperature_Coefficient", "Pin_Configuration", "Gender", "Pin_Type",
    "Pitch", "Orientation", "Locking_Mechanism", "Current_Rating_Per_Pin",
    "IP_Rating", "Wire_Gauge", "Termination_Style", "Resistance",
    "Technology_Material", "Capacitance", "Dielectric_Type", "ESR",
    "Ripple_Current", "Leakage_Current", "Inductance", "DC_Resistance",
    "Self_Resonant_Frequency", "Quality_Factor_Q", "Saturation_Current",
    "Hold_Current", "Trip_Current", "Interrupting_Rating", "Response_Time",
    "Forward_Voltage", "Reverse_Leakage", "Junction_Capacitance",
    "Reverse_Recovery_Time", "Zener_Voltage", "Zener_Impedance",
    "Reverse_Standoff_Voltage", "Breakdown_Voltage", "Clamping_Voltage",
    "Peak_Pulse_Current", "Q_Type", "Polarity_Channel_Type", "Power_Dissipation",
    "Junction_Temperature", "VDS_Max", "VGS_Max", "VGS_Threshold", "RDS_On",
    "ID_Continuous", "ID_Pulse", "Input_Capacitance", "Output_Capacitance",
    "Reverse_Transfer_Capacitance", "Gate_Charge", "Rise_Time", "Fall_Time",
    "IDSS", "VGS_Off", "Gain", "Gate_Reverse_Current", "VCEO",
    "Current_Collector", "DC_Gain_HFE", "Saturation_Voltage", "Transition_Frequency",
    "VCE_Sat", "IC_Continuous", "IC_Pulse", "VGE_Threshold",
    "Short_Circuit_Withstanding", "Diode_Forward_Voltage", "Frequency",
    "Oscillator_Type", "Load_Capacitance", "Supply_Voltage", "Coil_Voltage",
    "Coil_Resistance", "Contact_Configuration", "Contact_Current_Rating",
    "Contact_Voltage_Rating", "Relay_Type", "Operating_Time", "Transformer_Type",
    "Turns_Ratio", "Isolation_Voltage", "Power_Rating_VA", "Frequency_Rating",
    "Battery_Chemistry", "Battery_Voltage_Nominal", "Battery_Capacity",
    "Battery_Size", "Rechargeable", "Number_of_Cells", "Display_Type",
    "Display_Size", "Resolution", "Interface", "Backlight", "Controller",
    "Color", "Sensor_Type", "Sensor_Interface", "Supply_Voltage_Min",
    "Supply_Voltage_Max", "Accuracy", "Output_Type", "LED_Color",
    "Luminous_Intensity", "Wavelength", "Viewing_Angle_LED", "Lens_Type",
    "If_Current", "VF_Typical", "Optocoupler_Type", "CTR", "Tube_Type",
    "Heater_Voltage", "Heater_Current", "Plate_Voltage_Max",
]

# =============================================================================
# CONFIGURAÇÃO DAS BOMs (ative/desative colunas comentando linhas)
# =============================================================================

# BOM para Buyer (Comprador)
BUYER_COLUMNS = [
    "MyPN", 
    "Name", 
    "Description", 
    "Value", 
    "Info1", 
    "Info2", 
    #"Symbol",
    "Footprint",
    "Package", 
    #"Mount",
    #"Footprint_Filter", 
    "Datasheet",
    "Notes", 
    "Notes_to_Buyer",
    "Manufacturer", 
    "Manufacturer_PN", 
    "Manufacturer_URL", 
    "Alternative_PN",
    "Alternative_URL", 
    "Digikey_PN", 
    "Digikey_URL", 
    "Mouser_PN", 
    "Mouser_URL",
    "LCSC_PN", 
    "LCSC_URL", 
    "Stock_Qty", 
    "Stock_Location", 
    "Stock_Unit",
    "Price", 
    "Currency", 
    "Min_Stock", 
    "Max_Stock", 
    "Last_Purchase_Date",
    "Last_Purchase_Price", 
    "Active", 
    #"Version", 
    #"Created_At", 
    #"Created_By",
    #"Modified_At", 
    #"Modified_By",
    #"Category", 
    #"Subcategory", 
    #"Family_Series", 
    #"Package", 
    #"Mount",
    #"Dimensions", 
    #"Temperature_Range", 
    #"REACH_Compliant", 
    #"RoHS_Compliant",
]

# BOM para Assembly (Montador)
ASSEMBLY_COLUMNS = [
    "MyPN", 
    "Name", 
    "Description", 
    "Value", 
    "Info1", 
    "Info2", 
    #"Symbol",
    "Footprint",
    "Package", 
    "Mount",
    #"Footprint_Filter", 
    "Datasheet", 
    #"Notes", 
    #"Notes_to_Buyer",
    "Manufacturer", 
    "Manufacturer_PN", 
    #"Manufacturer_URL", 
    #"Alternative_PN",
    #"Alternative_URL", 
    #"Digikey_PN", 
    #"Digikey_URL", 
    #"Mouser_PN", 
    #"Mouser_URL",
    #"LCSC_PN", 
    #"LCSC_URL", 
    "Stock_Qty", 
    "Stock_Location", 
    "Stock_Unit",
    #"Price", 
    #"Currency", 
    "Min_Stock", 
    "Max_Stock", 
    "Last_Purchase_Date",
    "Last_Purchase_Price", 
    "Active", 
    "Version", 
    #"Created_At", 
    #"Created_By",
    #"Modified_At", 
    #"Modified_By",
]

# BOM para Engineer (Engenharia)
ENGINEERING_COLUMNS = [
    "MyPN", 
    "Name", 
    "Description", 
    "Value", 
    "Info1", 
    "Info2", 
    "Symbol",
    "Footprint", 
    "Footprint_Filter", 
    "Datasheet", 
    "Notes", 
    "Notes_to_Buyer",

    "Category", 
    "Subcategory", 
    "Family_Series", 
    "Package", 
    "Mount",
    "Dimensions", 
    "Temperature_Range", 
    "REACH_Compliant", 
    "RoHS_Compliant",

    "Manufacturer", 
    "Manufacturer_PN", 
    "Manufacturer_URL", 
    "Alternative_PN",
    "Alternative_URL", 
    #"Digikey_PN", 
    #"Digikey_URL", 
    #"Mouser_PN", 
    #"Mouser_URL",
    #"LCSC_PN", 
    #"LCSC_URL", 
    "Stock_Qty", 
    "Stock_Location", 
    "Stock_Unit",
    "Price", 
    "Currency", 
    "Min_Stock", 
    "Max_Stock", 
    "Last_Purchase_Date",
    "Last_Purchase_Price", 
    "Active", 
    "Version", 
    "Created_At", 
    "Created_By",
    "Modified_At", 
    "Modified_By",
    "Category", 
    "Subcategory", 
    "Family_Series", 
    "Package", 
    "Mount",
    "Dimensions", 
    "Temperature_Range", 
    "REACH_Compliant", 
    "RoHS_Compliant",
]

# =============================================================================
# CONFIGURAÇÃO DE AGRUPAMENTO
# =============================================================================
GROUP_BY_FIELDS = [
    "Value",
    "Footprint",
    "Manufacturer",
    "Manufacturer_PN",
]

# =============================================================================
# FUNÇÕES DE LEITURA DO XML
# =============================================================================

def parse_netlist(xml_file):
    """
    Lê o arquivo XML de netlist do KiCad e retorna uma lista de dicionários,
    cada dicionário representando um componente com todos os campos (incluindo
    os personalizados).
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    components = []

    # O elemento <components> contém todos os componentes
    for comp in root.findall(".//comp"):
        ref = comp.get("ref")  # referência (R1, C2, etc.)

        # Valor (value)
        value_elem = comp.find("value")
        value = value_elem.text if value_elem is not None else ""

        # Footprint
        footprint_elem = comp.find("footprint")
        footprint = footprint_elem.text if footprint_elem is not None else ""

        # Datasheet
        datasheet_elem = comp.find("datasheet")
        datasheet = datasheet_elem.text if datasheet_elem is not None else ""

        # Campos de libsource (símbolo, lib) – podem ser úteis
        libsource = comp.find("libsource")
        lib = libsource.get("lib") if libsource is not None else ""
        part = libsource.get("part") if libsource is not None else ""

        # Campos personalizados (fields)
        fields = {
            "Ref": ref,
            "Value": value,
            "Footprint": footprint,
            "Datasheet": datasheet,
            "Symbol": part,          # nome do símbolo
            "Library": lib,
        }

        for field in comp.findall(".//field"):
            name = field.get("name")
            text = field.text if field.text is not None else ""
            fields[name] = text

        components.append(fields)

    return components

# =============================================================================
# FUNÇÕES DE AGRUPAMENTO
# =============================================================================

def group_components(components, group_fields):
    """
    Agrupa os componentes com base nos campos especificados.
    Retorna um dicionário: chave = tupla dos valores dos campos de agrupamento,
    valor = lista de componentes (dicionários) que compartilham a chave.
    """
    groups = {}
    for comp in components:
        # Extrai os valores dos campos de agrupamento (se o campo não existir, usa string vazia)
        key = tuple(comp.get(field, "") for field in group_fields)
        if key not in groups:
            groups[key] = []
        groups[key].append(comp)
    return groups

# =============================================================================
# FUNÇÃO PARA ESCREVER CSV
# =============================================================================

def write_csv(filepath, columns, groups):
    """
    Escreve um arquivo CSV com as colunas especificadas, a partir dos grupos.
    columns: lista de nomes de colunas (sem "Ref" e "Qty", que são sempre adicionadas)
    filepath: caminho completo do arquivo a ser criado.
    """
    all_columns = ["Ref", "Qty"] + columns
    # Garante que o diretório de destino existe
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(all_columns)
        for group_comps in groups.values():
            # Usa o primeiro componente como representante
            rep = group_comps[0]
            row = []
            # Referências concatenadas
            refs = ','.join([c.get("Ref", "") for c in group_comps])
            row.append(refs)
            # Quantidade
            row.append(str(len(group_comps)))
            # Demais campos
            for field in columns:
                row.append(rep.get(field, ""))
            writer.writerow(row)

# =============================================================================
# PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python bom_customizado.py <arquivo_entrada.xml> <arquivo_saida_base>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_base = sys.argv[2]
    output_base = os.path.splitext(output_base)[0]  # remove eventual extensão

    # O diretório do projeto é o diretório onde o output_base está
    project_dir = os.path.dirname(output_base)
    # Nome base do projeto (sem caminho e sem extensão)
    project_name = os.path.basename(output_base)

    # Carrega os componentes do XML
    try:
        components = parse_netlist(input_file)
        print(f"Componentes encontrados: {len(components)}")
    except Exception as e:
        print(f"Erro ao ler o arquivo XML: {e}")
        sys.exit(1)

    # (Opcional) Filtrar componentes com Exclude_from_BOM = 1
    # filtered = []
    # for comp in components:
    #     if comp.get("Exclude_from_BOM", "").lower() not in ["1", "true", "yes"]:
    #         filtered.append(comp)
    # components = filtered

    # Agrupa
    groups = group_components(components, GROUP_BY_FIELDS)

    # Data para o nome do arquivo
    date_str = datetime.datetime.now().strftime("%Y%m%d")

    # Define os caminhos de saída conforme a estrutura solicitada
    # Estrutura: project_dir/Outputs/{Fabrication, Documentation, Assemble}/project_name_{tipo}_{data}.csv
    base_output_dir = os.path.join(project_dir, "Outputs")

    # Buyer (Fabrication)
    buyer_dir = os.path.join(base_output_dir, "Fabrication")
    buyer_file = os.path.join(buyer_dir, f"BOM_{project_name}_Buyer_{date_str}.csv")
    write_csv(buyer_file, BUYER_COLUMNS, groups)

    # Engineer (Documentation)
    engineer_dir = os.path.join(base_output_dir, "Documentation")
    engineer_file = os.path.join(engineer_dir, f"BOM_{project_name}_Engineer_{date_str}.csv")
    write_csv(engineer_file, ENGINEERING_COLUMNS, groups)

    # Assembly (Assemble)
    assembly_dir = os.path.join(base_output_dir, "Assembly")
    assembly_file = os.path.join(assembly_dir, f"BOM_{project_name}_Assembly_{date_str}.csv")
    write_csv(assembly_file, ASSEMBLY_COLUMNS, groups)

    print("BOMs geradas com sucesso:")
    print(f"  Buyer    : {buyer_file}")
    print(f"  Engineer : {engineer_file}")
    print(f"  Assembly : {assembly_file}")