#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de comandos SQLite para conectores D-SUB
Arquivo: Gerar_Insert/gerar_insert_dsub.py
"""

import csv
import re
from pathlib import Path
from datetime import datetime

class DSUBConnectorGenerator:
    def __init__(self, symbol_file, footprint_file, output_file):
        self.symbol_file = symbol_file
        self.footprint_file = footprint_file
        self.output_file = output_file
        self.footprints = []
        self.symbols_dict = {}
        self.dsub_footprints = []
        self.counter = 830000  # Faixa para D-SUB
        
        # Lista completa de colunas (118 colunas)
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
    
    def filter_dsub_footprints(self):
        print("\n🔍 Filtrando footprints D-SUB...")
        
        for fp in self.footprints:
            if fp.startswith('Connector_Dsub:'):
                self.dsub_footprints.append(fp)
            elif 'DSUB' in fp or 'D-SUB' in fp or 'D SUB' in fp:
                self.dsub_footprints.append(fp)
        
        print(f"   ✅ {len(self.dsub_footprints)} footprints D-SUB encontrados")
        return True
    
    def parse_footprint(self, name):
        """
        Parse footprints de conectores D-SUB
        Formato típico: DSUB-9_Pins_Horizontal_P2.77x2.84mm
        """
        data = {
            'footprint': name,
            'shell_size': 'DE9',  # DE9, DA15, DB25, DC37, DD50
            'pins': 9,
            'gender': 'Male',  # Male (Pins) ou Female (Socket)
            'density': 'Standard',  # Standard ou High Density
            'orientation': 'Horizontal',
            'mounting_style': 'Through Hole',
            'shielded': True,
            'manufacturer': None,
            'series': None,
            'contact_arrangement': None,  # Para HD: 3W3, 5W5, etc
            'rows': 2,
            'pitch': 2.77,
            'row_spacing': 2.84
        }
        
        if ':' in name:
            path_parts = name.split(':')
            fp_parts = path_parts[1].split('_')
            if len(fp_parts) >= 2:
                data['manufacturer'] = fp_parts[0]
        
        # Identificar tamanho do shell e número de pinos
        shell_patterns = [
            (r'DE9', 9), (r'DA15', 15), (r'DB25', 25), 
            (r'DC37', 37), (r'DD50', 50), (r'DD62', 62),
            (r'DE15.*HighDensity', 15, 'High Density'),
            (r'DA15.*HighDensity', 15, 'High Density'),
            (r'DB26.*HighDensity', 26, 'High Density'),
            (r'DC37.*HighDensity', 37, 'High Density'),
            (r'DD44.*HighDensity', 44, 'High Density'),
            (r'DD62.*HighDensity', 62, 'High Density'),
            (r'DD78.*HighDensity', 78, 'High Density'),
            (r'DD104.*HighDensity', 104, 'High Density')
        ]
        
        for pattern in shell_patterns:
            if len(pattern) == 3:  # High Density
                if re.search(pattern[0], name):
                    data['shell_size'] = pattern[0][:2]  # DE, DA, etc
                    data['pins'] = pattern[1]
                    data['density'] = pattern[2]
                    if data['density'] == 'High Density':
                        data['rows'] = 3
                        data['pitch'] = 2.29
                        data['row_spacing'] = 1.98
                    break
            else:  # Standard Density
                if re.search(pattern[0], name):
                    data['shell_size'] = pattern[0]
                    data['pins'] = pattern[1]
                    data['rows'] = 2
                    data['pitch'] = 2.77
                    data['row_spacing'] = 2.84
                    break
        
        # Identificar gender
        if 'Socket' in name or 'Female' in name:
            data['gender'] = 'Female'
        elif 'Pins' in name or 'Male' in name:
            data['gender'] = 'Male'
        
        # Identificar orientação
        if 'Vertical' in name:
            data['orientation'] = 'Vertical'
        elif 'Horizontal' in name or 'Right Angle' in name:
            data['orientation'] = 'Right Angle'
        
        # Identificar montagem
        if 'SMD' in name or 'SMT' in name:
            data['mounting_style'] = 'SMT'
        
        # Identificar se tem mounting holes
        if 'MountingHoles' in name:
            data['has_mounting_holes'] = True
        
        # Identificar mixed layout (ex: 3W3, 5W5, etc)
        mixed_match = re.search(r'(\d)W(\d)', name)
        if mixed_match:
            data['contact_arrangement'] = mixed_match.group(0)
            data['pins'] = int(mixed_match.group(1)) + int(mixed_match.group(2))
        
        return data
    
    def get_symbol(self, data):
        """
        Encontra o símbolo apropriado no dicionário de símbolos
        """
        shell = data['shell_size']
        pins = data['pins']
        gender = 'Pins' if data['gender'] == 'Male' else 'Socket'
        density = 'HighDensity' if data['density'] == 'High Density' else ''
        holes = 'MountingHoles' if data.get('has_mounting_holes', False) else ''
        
        # Construir nome base
        if density:
            symbol_name = f"Connector:{shell}_{pins}_Pins_{density}_{holes}"
        else:
            symbol_name = f"Connector:{shell}_{pins}_{gender}_{holes}"
        
        # Remover underscores extras
        symbol_name = symbol_name.replace('__', '_').strip('_')
        
        # Verificar se existe no dicionário
        if self.symbols_dict.get(symbol_name):
            return symbol_name
        
        # Fallbacks
        if density:
            if gender == 'Pins':
                return f"Connector:{shell}_{pins}_Pins_{density}"
            else:
                return f"Connector:{shell}_{pins}_Socket_{density}"
        else:
            if gender == 'Pins':
                return f"Connector:{shell}_{pins}_Pins"
            else:
                return f"Connector:{shell}_{pins}_Socket"
    
    def get_electrical_params(self, data):
        """
        Parâmetros elétricos padrão para D-SUB
        Baseado em especificações comuns
        """
        params = {
            'current': 5.0,  # 5A para contatos de potência, 3A para sinal
            'voltage': 250,   # 250V AC/DC
            'contact_resistance': 10,
            'insulation_resistance': 5000,
            'withstanding_voltage': 1000
        }
        
        # D-SUB high density tem corrente menor
        if data['density'] == 'High Density':
            params['current'] = 3.0
        
        # Mixed layout tem contatos de potência
        if data.get('contact_arrangement'):
            params['current'] = 10.0  # Contatos de potência podem ter mais corrente
        
        return params
    
    def generate_my_pn(self):
        self.counter += 1
        return f"EL-CON_{self.counter:06d}"
    
    def generate_name(self, data):
        """Gera nome no formato CON_DSUB_{size}_{pins}_{gender}_{orientation}"""
        
        size_map = {
            'DE9': 'DE9', 'DA15': 'DA15', 'DB25': 'DB25',
            'DC37': 'DC37', 'DD50': 'DD50', 'DD62': 'DD62'
        }
        
        size = size_map.get(data['shell_size'], data['shell_size'])
        gender = 'M' if data['gender'] == 'Male' else 'F'
        orient = 'V' if data['orientation'] == 'Vertical' else 'RA'
        density = 'HD' if data['density'] == 'High Density' else 'SD'
        
        parts = [f"CON_DSUB_{size}", f"{data['pins']}P", density, gender, orient]
        
        if data.get('contact_arrangement'):
            parts.insert(1, data['contact_arrangement'])
        
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
        temp_min = -40 if ('Industrial' in data['footprint'] or 'Automotive' in data['footprint']) else -25
        temp_max = 105 if ('Industrial' in data['footprint'] or 'Automotive' in data['footprint']) else 85
        
        # Tags
        tags = f"dsub,d-{data['shell_size'].lower()},{data['pins']}pins"
        if data['density'] == 'High Density':
            tags += ",high density"
        tags += ",male" if data['gender'] == 'Male' else ",female"
        if data.get('contact_arrangement'):
            tags += f",{data['contact_arrangement'].lower()}"
        
        # Descrição
        desc = f"D-SUB {data['shell_size']} {data['pins']}-pin {data['density']} {data['gender']} connector"
        if data['contact_arrangement']:
            desc += f" with {data['contact_arrangement']} arrangement"
        desc += f", {data['orientation'].lower()} orientation, {data['mounting_style']}"
        if data.get('has_mounting_holes'):
            desc += ", with mounting holes"
        desc += f", {electrical['current']}A, {electrical['voltage']}V"
        
        # Lista de 118 valores na ordem exata
        values = [
            str(keyld),                                    # Keyld
            f"'{my_pn}'",                                  # MyPN
            f"'{name}'",                                   # Name
            f"'{desc}'",                                   # Description
            'NULL',                                        # Value
            'NULL',                                        # Value 2
            self.format_value(symbol),                     # Symbol
            f"'{data['footprint']}'",                      # Footprint
            f"'*DSUB*{data['pins']}*'",                    # Footprint_Filter
            f"'{data['mounting_style']}'",                 # Package
            f"'{manufacturer}'",                           # Manufacturer
            self.format_value(manuf_pn),                   # Manufacturer_PN
            "'D-SUB Series'",                              # Series
            "'D-SUB Connector'",                           # Category
            f"'D-SUB {data['shell_size']}'",               # Subcategory
            "'D-SUB'",                                     # Connector_Type
            f"'{data['shell_size']}'",                     # Family
            "'MIL-DTL-24308'",                             # Standard
            "'PCB'",                                       # Mounting_Type
            f"'{data['mounting_style']}'",                 # Mounting_Style
            f"'{data['orientation']}'",                    # Orientation
            f"'{data['gender']}'",                         # Gender
            str(shielded_value),                           # Shielded
            "'Steel'",                                     # Shield_Material
            "'Tin'",                                       # Shield_Plating
            str(data['pins']),                             # Pins_Total
            f"'{data['pins']}P'",                          # Pins_Configuration
            str(data['rows']),                             # Rows
            "'Machined'",                                  # Contact_Type
            self.format_value(data.get('contact_arrangement')), # Contact_Arrangement
            str(data['pitch']),                            # Pitch_mm
            str(data['row_spacing']),                      # Row_Spacing_mm
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
            'NULL',                                        # Impedance_Ohm
            'NULL',                                        # Frequency_Max_Hz
            "'Copper Alloy'",                              # Contact_Material
            "'Gold'",                                      # Contact_Plating
            '0.76',                                        # Plating_Thickness_um
            'NULL',                                        # Contact_Finish
            "'Steel'",                                     # Housing_Material
            "'Tin'",                                       # Housing_Color
            "'PBT'",                                       # Insulator_Material
            "'Black'",                                     # Insulator_Color
            "'Friction'",                                  # Locking_Mechanism
            "'Keyed'",                                     # Polarization
            '500',                                         # Mating_Cycles
            'NULL',                                        # Insertion_Force_N
            'NULL',                                        # Withdrawal_Force_N
            str(temp_min),                                 # Operating_Temp_Min_C
            str(temp_max),                                 # Operating_Temp_Max_C
            'NULL',                                        # Storage_Temp_Min_C
            'NULL',                                        # Storage_Temp_Max_C
            'NULL',                                        # IP_Rating
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
        print("\n📝 Gerando comandos INSERT para conectores D-SUB...")
        
        inserts = []
        inserts.append("-- Comandos INSERT para conectores D-SUB")
        inserts.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        inserts.append(f"-- Total de footprints: {len(self.dsub_footprints)}")
        inserts.append("")
        
        # Cabeçalho do INSERT
        inserts.append("INSERT INTO Connector_General (" + ", ".join([f'"{col}"' for col in self.columns]) + ") VALUES")
        
        values_lines = []
        keyld = 1
        
        for i, fp in enumerate(self.dsub_footprints, 1):
            try:
                data = self.parse_footprint(fp)
                values_line = self.generate_values_line(data, keyld)
                values_lines.append(values_line)
                keyld += 1
                
                if i % 10 == 0:
                    print(f"   ⏳ Processados {i}/{len(self.dsub_footprints)} footprints...")
                    
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
        print("🔧 GERADOR DE INSERTS PARA CONECTORES D-SUB")
        print("=" * 60)
        
        if not self.read_csv_files():
            return False
        
        if not self.filter_dsub_footprints():
            return False
        
        inserts = self.generate_all_inserts()
        
        if self.save_to_file(inserts):
            print(f"\n✅ Processo concluído com sucesso!")
            print(f"   📁 Verifique o arquivo: {self.output_file}")
            return True
        return False


def main():
    base_dir = Path(__file__).parent
    generator = DSUBConnectorGenerator(
        symbol_file=str(base_dir / "simbolos_para_database_connectores.csv"),
        footprint_file=str(base_dir / "footprints_para_database_connectors.csv"),
        output_file=str(base_dir / "sqlite_commands_dsub.txt")
    )
    generator.run()


if __name__ == "__main__":
    main()