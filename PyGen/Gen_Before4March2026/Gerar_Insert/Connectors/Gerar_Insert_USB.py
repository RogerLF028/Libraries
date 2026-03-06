#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de comandos SQLite para conectores USB
Arquivo: Gerar_Insert/gerar_insert_usb.py
"""

import csv
import re
from pathlib import Path
from datetime import datetime

class USBConnectorGenerator:
    def __init__(self, symbol_file, footprint_file, output_file):
        self.symbol_file = symbol_file
        self.footprint_file = footprint_file
        self.output_file = output_file
        self.footprints = []
        self.symbols_dict = {}
        self.usb_footprints = []
        self.counter = 820000
        
        # Lista completa de colunas na ordem correta (118 colunas)
        self.columns = [
            'Keyld', 'MyPN', 'Name', 'Description', 'Value', 'Value 2', 'Symbol', 
            'Footprint', 'Footprint_Filter', 'Package', 'Manufacturer', 'Manufacturer_PN', 
            'Series', 'Category', 'Subcategory', 'Connector_Type', 'Family', 'Standard', 
            'Mounting_Type', 'Mounting_Style', 'Orientation', 'Gender', 'Shielded', 
            'Shield_Material', 'Shield_Plating', 'Pins_Total', 'Pins_Configuration', 'Rows', 
            'Contact_Type', 'Contact_Arrangement', 'Pitch_mm', 'Row_Spacing_mm', 'Length_mm', 
            'Width_mm', 'Height_mm', 'Mating_Height_mm', 'PCB_Mounting_Dimensions', 
            'Current_Rating_A', 'Current_Rating_Total_A', 'Voltage_Rating_V', 
            'Contact_Resistance_mOhm', 'Insulation_Resistance_MOhm', 
            'Dielectric_Withstanding_Voltage_V', 'Impedance_Ohm', 'Frequency_Max_Hz', 
            'Contact_Material', 'Contact_Plating', 'Plating_Thickness_um', 'Contact_Finish', 
            'Housing_Material', 'Housing_Color', 'Insulator_Material', 'Insulator_Color', 
            'Locking_Mechanism', 'Polarization', 'Mating_Cycles', 'Insertion_Force_N', 
            'Withdrawal_Force_N', 'Operating_Temp_Min_C', 'Operating_Temp_Max_C', 
            'Storage_Temp_Min_C', 'Storage_Temp_Max_C', 'IP_Rating', 
            'Moisture_Sensitivity_Level', 'RoHS_Compliant', 'REACH_Compliant', 'UL_Certified', 
            'UL_File_Number', 'CSA_Certified', 'TUV_Certified', 'Flammability_Rating', 
            'Solder_Type', 'Solder_Temperature_C', 'Solder_Process', 'Cleaning_Process', 
            'PCB_Retention', 'Pick_and_Place', 'Tape_and_Reel', 'Cable_Type', 
            'Cable_Diameter_Max_mm', 'Wire_Gauge_AWG', 'Wire_Strip_Length_mm', 'LCSC_PN', 
            'LCSC_URL', 'Mouser_PN', 'Mouser_URL', 'Digikey_PN', 'Digikey_URL', 'Farnell_PN', 
            'Farnell_URL', 'Newark_PN', 'Newark_URL', 'RS_PN', 'RS_URL', 'StockQty', 
            'Min_Stock', 'Max_Stock', 'StockPlace', 'Price', 'Currency', 'MOQ', 'Packaging', 
            'Datasheet', 'Drawing_2D', 'Drawing_3D', 'PCB_Layout_Suggestion', 
            'Application_Note', 'Assembly_Instructions', 'Active', 'Notes', 'Tags', 
            'CreatedBy', 'CreatedAt', 'ModifiedBy', 'ModifiedAt', 'Version', 
            'Exclude_from_BOM', 'Exclude_from_Board'
        ]
        
    def read_csv_files(self):
        print("📖 Lendo arquivos CSV...")
        
        try:
            with open(self.symbol_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    symbol_name = row['Database_Symbol']
                    self.symbols_dict[symbol_name] = row
            print(f"   ✅ {len(self.symbols_dict)} símbolos carregados")
        except Exception as e:
            print(f"   ⚠️ Erro ao ler símbolos: {e}")
        
        try:
            with open(self.footprint_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.footprints = [row['Footprint'] for row in reader]
            print(f"   ✅ {len(self.footprints)} footprints carregados")
            return True
        except Exception as e:
            print(f"   ❌ Erro ao ler footprints: {e}")
            return False
    
    def filter_usb_footprints(self):
        print("\n🔍 Filtrando footprints USB...")
        
        for fp in self.footprints:
            if fp.startswith('Connector_USB:'):
                self.usb_footprints.append(fp)
            elif 'USB' in fp and 'Audio' not in fp and 'Jack' not in fp:
                self.usb_footprints.append(fp)
        
        print(f"   ✅ {len(self.usb_footprints)} footprints USB encontrados")
        return True
    
    def parse_footprint(self, name):
        data = {
            'footprint': name,
            'usb_type': 'USB-A',
            'usb_version': '2.0',
            'pins': 4,
            'gender': 'Receptacle',
            'orientation': 'Horizontal',
            'mounting_style': 'Through Hole',
            'shielded': True,
            'stacked': False,
            'manufacturer': None,
            'series': None,
            'spec': 'USB 2.0'
        }
        
        if ':' in name:
            path_parts = name.split(':')
            fp_parts = path_parts[1].split('_')
            if len(fp_parts) >= 2:
                data['manufacturer'] = fp_parts[0]
        
        if 'USB-A' in name or 'USB_A' in name:
            data['usb_type'] = 'USB-A'
            data['pins'] = 4
        elif 'USB-B' in name or 'USB_B' in name:
            data['usb_type'] = 'USB-B'
            data['pins'] = 4
        elif 'USB-C' in name or 'USB_C' in name or 'Type-C' in name:
            data['usb_type'] = 'USB-C'
            data['pins'] = 24
        elif 'Micro-B' in name or 'Micro_B' in name:
            data['usb_type'] = 'USB-Micro-B'
            data['pins'] = 5
        elif 'Mini-B' in name or 'Mini_B' in name:
            data['usb_type'] = 'USB-Mini-B'
            data['pins'] = 5
        
        if '3.2' in name or 'USB3' in name:
            data['usb_version'] = '3.2'
            data['spec'] = 'USB 3.2'
            if data['usb_type'] == 'USB-C':
                data['pins'] = 24
            elif data['usb_type'] in ['USB-A', 'USB-B']:
                data['pins'] = 9
            elif data['usb_type'] == 'USB-Micro-B':
                data['pins'] = 10
        elif 'USB4' in name:
            data['usb_version'] = '4'
            data['spec'] = 'USB4'
            data['pins'] = 24
        elif '3.1' in name:
            data['usb_version'] = '3.1'
            data['spec'] = 'USB 3.1'
        elif '3.0' in name:
            data['usb_version'] = '3.0'
            data['spec'] = 'USB 3.0'
            if data['usb_type'] == 'USB-C':
                data['pins'] = 24
            elif data['usb_type'] in ['USB-A', 'USB-B']:
                data['pins'] = 9
        
        if 'Plug' in name:
            data['gender'] = 'Plug'
        elif 'Receptacle' in name or 'Socket' in name:
            data['gender'] = 'Receptacle'
        
        if 'Vertical' in name:
            data['orientation'] = 'Vertical'
        elif 'Horizontal' in name or 'Right Angle' in name or 'RA' in name:
            data['orientation'] = 'Right Angle'
        
        if 'SMD' in name or 'SMT' in name:
            data['mounting_style'] = 'SMT'
        
        if 'Stacked' in name or '2x' in name:
            data['stacked'] = True
        
        if 'Unshielded' in name:
            data['shielded'] = False
        
        if data['usb_type'] == 'USB-C':
            if '14P' in name:
                data['pins'] = 14
                data['spec'] = 'USB 2.0'
            elif '16P' in name:
                data['pins'] = 16
                data['spec'] = 'USB 2.0'
            elif '6P' in name:
                data['pins'] = 6
                data['spec'] = 'Power Only'
        
        return data
    
    def get_symbol(self, data):
        usb_type = data['usb_type']
        pins = data['pins']
        gender = data['gender'].lower()
        
        if usb_type == 'USB-A':
            if pins == 9 and self.symbols_dict.get('Connector:USB3_A'):
                return 'Connector:USB3_A'
            if data['stacked'] and self.symbols_dict.get('Connector:USB_A_Stacked'):
                return 'Connector:USB_A_Stacked'
            if self.symbols_dict.get('Connector:USB_A'):
                return 'Connector:USB_A'
            return 'Connector:USB_A'
        
        elif usb_type == 'USB-B':
            if pins == 9 and self.symbols_dict.get('Connector:USB3_B'):
                return 'Connector:USB3_B'
            if self.symbols_dict.get('Connector:USB_B'):
                return 'Connector:USB_B'
            return 'Connector:USB_B'
        
        elif usb_type == 'USB-Micro-B':
            if pins == 10 and self.symbols_dict.get('Connector:USB3_B_Micro'):
                return 'Connector:USB3_B_Micro'
            if self.symbols_dict.get('Connector:USB_B_Micro'):
                return 'Connector:USB_B_Micro'
            return 'Connector:USB_B_Micro'
        
        elif usb_type == 'USB-Mini-B':
            if self.symbols_dict.get('Connector:USB_B_Mini'):
                return 'Connector:USB_B_Mini'
            return 'Connector:USB_B_Mini'
        
        elif usb_type == 'USB-C':
            if pins == 6 and 'PowerOnly' in data['footprint']:
                return 'Connector:USB_C_Receptacle_PowerOnly_6P'
            elif pins == 14:
                return 'Connector:USB_C_Receptacle_USB2.0_14P'
            elif pins == 16:
                return 'Connector:USB_C_Receptacle_USB2.0_16P'
            elif gender == 'plug':
                return 'Connector:USB_C_Plug'
            else:
                return 'Connector:USB_C_Receptacle'
        
        return None
    
    def get_electrical_params(self, data):
        params = {
            'current': 0.5,
            'voltage': 5,
            'contact_resistance': 30,
            'insulation_resistance': 1000,
            'withstanding_voltage': 500
        }
        
        if data['usb_version'] in ['3.0', '3.1', '3.2']:
            params['current'] = 0.9
        
        if data['usb_type'] == 'USB-C':
            params['current'] = 3.0
            if 'PD' in data['footprint']:
                params['voltage'] = 20
            elif data['usb_version'] == '4':
                params['voltage'] = 48
        
        return params
    
    def generate_my_pn(self):
        self.counter += 1
        return f"EL-CON_{self.counter:06d}"
    
    def generate_name(self, data):
        type_map = {
            'USB-A': 'A',
            'USB-B': 'B',
            'USB-C': 'C',
            'USB-Micro-B': 'MICRO_B',
            'USB-Mini-B': 'MINI_B'
        }
        usb_code = type_map.get(data['usb_type'], 'A')
        version = data['usb_version'].replace('.', '')
        orient = 'V' if data['orientation'] == 'Vertical' else 'RA'
        gender = 'P' if data['gender'] == 'Plug' else 'R'
        
        parts = [f"CON_USB{usb_code}"]
        if data['stacked']:
            parts.append('STACKED')
        parts.extend([version, orient, gender])
        if data['mounting_style'] == 'SMT':
            parts.append('SMT')
        
        return "_".join(parts)
    
    def get_manuf_pn(self, footprint):
        parts = footprint.split(':')[-1].split('_')
        if len(parts) >= 3:
            return '_'.join(parts[1:])
        elif len(parts) >= 2:
            return parts[1]
        return None
    
    def format_value(self, value):
        if value is None:
            return 'NULL'
        if isinstance(value, str):
            return f"'{value}'"
        if isinstance(value, bool):
            return '1' if value else '0'
        return str(value)
    
    def generate_values_line(self, data, keyld):
        """Gera uma linha de VALUES com EXATAMENTE 118 valores"""
        
        my_pn = self.generate_my_pn()
        name = self.generate_name(data)
        symbol = self.get_symbol(data)
        manufacturer = data['manufacturer'] or 'Various'
        manuf_pn = self.get_manuf_pn(data['footprint'])
        electrical = self.get_electrical_params(data)
        
        # Valores calculados
        shielded_value = 1 if data['shielded'] else 0
        rows_value = 1 if data['pins'] <= 5 else 2
        impedance_value = 90 if data['usb_version'] in ['3.0', '3.1', '3.2', '4'] else 'NULL'
        temp_min = -40 if ('Industrial' in data['footprint'] or 'Automotive' in data['footprint']) else 0
        temp_max = 85 if ('Industrial' in data['footprint'] or 'Automotive' in data['footprint']) else 70
        
        # Tags
        tags = f"usb,{data['usb_type'].lower().replace('-', '_')},usb{data['usb_version'].replace('.', '')}"
        if data['stacked']:
            tags += ",stacked"
        tags += ",plug" if data['gender'] == 'Plug' else ",receptacle"
        
        # Descrição
        desc = f"{data['usb_type']} {data['spec']} {data['gender'].lower()}"
        if data['stacked']:
            desc = f"Stacked dual-port {desc}"
        desc += f", {data['pins']} contacts, {data['orientation'].lower()} orientation, {data['mounting_style']}"
        if data['shielded']:
            desc += ", shielded"
        desc += f", {electrical['current']}A, {electrical['voltage']}V"
        
        # Construir lista de 118 valores na ordem exata das colunas
        values = [
            str(keyld),                                    # Keyld
            f"'{my_pn}'",                                  # MyPN
            f"'{name}'",                                   # Name
            f"'{desc}'",                                   # Description
            'NULL',                                        # Value
            'NULL',                                        # Value 2
            self.format_value(symbol),                     # Symbol
            f"'{data['footprint']}'",                      # Footprint
            "'*USB*'",                                     # Footprint_Filter
            f"'{data['mounting_style']}'",                 # Package
            f"'{manufacturer}'",                           # Manufacturer
            self.format_value(manuf_pn),                   # Manufacturer_PN
            "'USB Series'",                                # Series
            "'USB Connector'",                             # Category
            f"'{data['usb_type']}'",                       # Subcategory
            f"'{data['usb_type']}'",                       # Connector_Type
            f"'{data['usb_type']}'",                       # Family
            f"'{data['spec']}'",                           # Standard
            "'PCB'",                                       # Mounting_Type
            f"'{data['mounting_style']}'",                 # Mounting_Style
            f"'{data['orientation']}'",                    # Orientation
            f"'{data['gender']}'",                         # Gender
            str(shielded_value),                           # Shielded
            "'Copper Alloy'",                              # Shield_Material
            "'Nickel'",                                    # Shield_Plating
            str(data['pins']),                             # Pins_Total
            f"'{data['pins']}P'",                          # Pins_Configuration
            str(rows_value),                               # Rows
            "'Spring'",                                    # Contact_Type
            'NULL',                                        # Contact_Arrangement
            '2.54',                                        # Pitch_mm
            'NULL',                                        # Row_Spacing_mm
            'NULL',                                        # Length_mm
            'NULL',                                        # Width_mm
            'NULL',                                        # Height_mm
            'NULL',                                        # Mating_Height_mm
            'NULL',                                        # PCB_Mounting_Dimensions
            str(electrical['current']),                    # Current_Rating_A
            'NULL',                                        # Current_Rating_Total_A
            str(electrical['voltage']),                    # Voltage_Rating_V
            str(electrical['contact_resistance']),         # Contact_Resistance_mOhm
            str(electrical['insulation_resistance']),      # Insulation_Resistance_MOhm
            str(electrical['withstanding_voltage']),       # Dielectric_Withstanding_Voltage_V
            str(impedance_value),                          # Impedance_Ohm
            'NULL',                                        # Frequency_Max_Hz
            "'Phosphor Bronze'",                           # Contact_Material
            "'Gold'",                                      # Contact_Plating
            '0.76',                                        # Plating_Thickness_um
            'NULL',                                        # Contact_Finish
            "'Thermoplastic'",                             # Housing_Material
            "'Black'",                                     # Housing_Color
            "'Polyamide (PA)'",                            # Insulator_Material
            "'Black'",                                     # Insulator_Color
            "'Friction'",                                  # Locking_Mechanism
            "'Keyed'",                                     # Polarization
            '1500',                                        # Mating_Cycles
            'NULL',                                        # Insertion_Force_N
            'NULL',                                        # Withdrawal_Force_N
            str(temp_min),                                 # Operating_Temp_Min_C
            str(temp_max),                                 # Operating_Temp_Max_C
            'NULL',                                        # Storage_Temp_Min_C
            'NULL',                                        # Storage_Temp_Max_C
            "'IP20'",                                      # IP_Rating
            'NULL',                                        # Moisture_Sensitivity_Level
            '1',                                           # RoHS_Compliant
            '1',                                           # REACH_Compliant
            '1',                                           # UL_Certified
            'NULL',                                        # UL_File_Number
            '1',                                           # CSA_Certified
            '0',                                           # TUV_Certified
            "'UL94 V-0'",                                  # Flammability_Rating
            'NULL',                                        # Solder_Type
            'NULL',                                        # Solder_Temperature_C
            "'Wave'",                                      # Solder_Process
            'NULL',                                        # Cleaning_Process
            "'Board Lock'",                                # PCB_Retention
            '0',                                           # Pick_and_Place
            '1',                                           # Tape_and_Reel
            'NULL',                                        # Cable_Type
            'NULL',                                        # Cable_Diameter_Max_mm
            'NULL',                                        # Wire_Gauge_AWG
            'NULL',                                        # Wire_Strip_Length_mm
            'NULL',                                        # LCSC_PN
            'NULL',                                        # LCSC_URL
            'NULL',                                        # Mouser_PN
            'NULL',                                        # Mouser_URL
            'NULL',                                        # Digikey_PN
            'NULL',                                        # Digikey_URL
            'NULL',                                        # Farnell_PN
            'NULL',                                        # Farnell_URL
            'NULL',                                        # Newark_PN
            'NULL',                                        # Newark_URL
            'NULL',                                        # RS_PN
            'NULL',                                        # RS_URL
            'NULL',                                        # StockQty
            'NULL',                                        # Min_Stock
            'NULL',                                        # Max_Stock
            'NULL',                                        # StockPlace
            'NULL',                                        # Price
            'NULL',                                        # Currency
            'NULL',                                        # MOQ
            'NULL',                                        # Packaging
            'NULL',                                        # Datasheet
            'NULL',                                        # Drawing_2D
            'NULL',                                        # Drawing_3D
            'NULL',                                        # PCB_Layout_Suggestion
            'NULL',                                        # Application_Note
            'NULL',                                        # Assembly_Instructions
            '1',                                           # Active
            'NULL',                                        # Notes
            f"'{tags}'",                                   # Tags
            "'script'",                                    # CreatedBy
            "datetime('now')",                             # CreatedAt
            'NULL',                                        # ModifiedBy
            'NULL',                                        # ModifiedAt
            "'1.0'",                                       # Version
            '0',                                           # Exclude_from_BOM
            '0'                                            # Exclude_from_Board
        ]
        
        # Verificação de segurança: deve ter 118 valores
        if len(values) != 118:
            print(f"❌ ERRO: Gerados {len(values)} valores, deveriam ser 118")
            print(f"   Para o componente: {my_pn}")
        
        return "(" + ", ".join(values) + ")"
    
    def generate_all_inserts(self):
        print("\n📝 Gerando comandos INSERT para conectores USB...")
        
        inserts = []
        inserts.append("-- Comandos INSERT para conectores USB")
        inserts.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        inserts.append(f"-- Total de footprints: {len(self.usb_footprints)}")
        inserts.append("")
        
        # Cabeçalho do INSERT
        inserts.append("INSERT INTO Connector_General (" + ", ".join([f'"{col}"' for col in self.columns]) + ") VALUES")
        
        values_lines = []
        keyld = 1
        
        for i, fp in enumerate(self.usb_footprints, 1):
            try:
                data = self.parse_footprint(fp)
                values_line = self.generate_values_line(data, keyld)
                values_lines.append(values_line)
                keyld += 1
                
                if i % 10 == 0:
                    print(f"   ⏳ Processados {i}/{len(self.usb_footprints)} footprints...")
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar {fp}: {e}")
        
        inserts.append(",\n".join(values_lines))
        inserts.append(";")
        inserts.append("")
        inserts.append(f"-- Resumo: {len(values_lines)} inserts gerados")
        
        return inserts
    
    def save_to_file(self, inserts):
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(inserts))
            print(f"\n💾 Comandos salvos em: {self.output_file}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return False
    
    def run(self):
        print("=" * 60)
        print("🔧 GERADOR DE INSERTS PARA CONECTORES USB")
        print("=" * 60)
        
        if not self.read_csv_files():
            return False
        
        if not self.filter_usb_footprints():
            return False
        
        inserts = self.generate_all_inserts()
        
        if self.save_to_file(inserts):
            print(f"\n✅ Processo concluído com sucesso!")
            print(f"   📁 Verifique o arquivo: {self.output_file}")
            return True
        return False


def main():
    base_dir = Path(__file__).parent
    generator = USBConnectorGenerator(
        symbol_file=str(base_dir / "simbolos_para_database_connectores.csv"),
        footprint_file=str(base_dir / "footprints_para_database_connectors.csv"),
        output_file=str(base_dir / "sqlite_commands_usb.txt")
    )
    generator.run()


if __name__ == "__main__":
    main()