#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de comandos SQLite para conectores Molex
Arquivo: Gerar_Insert/gerar_insert_molex.py
"""

import csv
import re
from pathlib import Path
from datetime import datetime

class MolexConnectorGenerator:
    def __init__(self, symbol_file, footprint_file, output_file):
        self.symbol_file = symbol_file
        self.footprint_file = footprint_file
        self.output_file = output_file
        self.footprints = []
        self.symbols_dict = {}
        self.molex_footprints = []
        self.counter = 840000
        
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
    
    def filter_molex_footprints(self):
        print("\n🔍 Filtrando footprints Molex...")
        
        for fp in self.footprints:
            if fp.startswith('Connector_Molex:'):
                self.molex_footprints.append(fp)
        
        print(f"   ✅ {len(self.molex_footprints)} footprints Molex encontrados")
        return True
    
    def parse_footprint(self, name):
        """
        Parse footprints de conectores Molex com extração precisa de pinos
        """
        data = {
            'footprint': name,
            'series': 'KK',
            'pitch': 2.54,
            'pins': 0,  # Inicializar como 0 para forçar extração
            'rows': 1,
            'gender': 'Male',
            'orientation': 'Vertical',
            'mounting_style': 'Through Hole',
            'shielded': False,
            'manufacturer': 'Molex',
            'locking': 'Friction',
            'current': 2.5,
            'voltage': 250,
            'wire_size': None,
            'part_number': None
        }
        
        # Extrair número de peça Molex (formato típico: 43045-0200)
        part_match = re.search(r'(\d{5,6}-\d{4})', name)
        if part_match:
            data['part_number'] = part_match.group(1)
        
        # Identificar série e características baseado no número de peça
        if '43045' in name or '43045' in str(data['part_number']):
            data['series'] = 'Micro-Fit 3.0'
            data['pitch'] = 3.0
            data['current'] = 5.0
            data['rows'] = 2
            # Extrair pinos do código (ex: 43045-0200 = 2 pinos)
            if data['part_number'] and '-' in data['part_number']:
                code = data['part_number'].split('-')[1]
                if len(code) >= 2:
                    data['pins'] = int(code[:2])
        
        elif '43650' in name or '43650' in str(data['part_number']):
            data['series'] = 'Micro-Fit 3.0'
            data['pitch'] = 3.0
            data['current'] = 5.0
            data['rows'] = 1
            if data['part_number'] and '-' in data['part_number']:
                code = data['part_number'].split('-')[1]
                if len(code) >= 2:
                    data['pins'] = int(code[:2])
        
        elif '5566' in name or '5569' in name:
            data['series'] = 'Mini-Fit Jr.'
            data['pitch'] = 4.2
            data['current'] = 9.0
            data['rows'] = 2
            if data['part_number'] and '-' in data['part_number']:
                code = data['part_number'].split('-')[1]
                if len(code) >= 2:
                    data['pins'] = int(code[:2]) * 2
        
        elif '53047' in name or '53048' in name:
            data['series'] = 'PicoBlade'
            data['pitch'] = 1.25
            data['current'] = 1.0
            data['rows'] = 1
            if data['part_number'] and '-' in data['part_number']:
                code = data['part_number'].split('-')[1]
                if len(code) >= 2:
                    data['pins'] = int(code[:2])
        
        elif '53261' in name or '53398' in name:
            data['series'] = 'PicoBlade'
            data['pitch'] = 1.25
            data['current'] = 1.0
            data['rows'] = 1
            if data['part_number'] and '-' in data['part_number']:
                code = data['part_number'].split('-')[1]
                if len(code) >= 2:
                    data['pins'] = int(code[:2])
        
        elif '5273' in name or '41791' in name:
            data['series'] = 'KK 396'
            data['pitch'] = 3.96
            data['current'] = 5.0
            data['rows'] = 1
            # KK geralmente tem o número de pinos no nome: _02A_, _03A_, etc
            pin_match = re.search(r'_(\d+)A_', name)
            if pin_match:
                data['pins'] = int(pin_match.group(1))
        
        elif '6410' in name:
            data['series'] = 'KK 254'
            data['pitch'] = 2.54
            data['current'] = 2.5
            data['rows'] = 1
            pin_match = re.search(r'_(\d+)A_', name)
            if pin_match:
                data['pins'] = int(pin_match.group(1))
        
        elif '502352' in name:
            data['series'] = 'DuraClik'
            data['pitch'] = 2.0
            data['current'] = 3.0
            data['rows'] = 1
            if data['part_number'] and '-' in data['part_number']:
                code = data['part_number'].split('-')[1]
                if len(code) >= 2:
                    data['pins'] = int(code[:2])
        
        elif '105309' in name or '105310' in name:
            data['series'] = 'Nano-Fit'
            data['pitch'] = 2.5
            data['current'] = 6.5
            data['rows'] = 2
            if data['part_number'] and '-' in data['part_number']:
                code = data['part_number'].split('-')[1]
                if len(code) >= 2:
                    data['pins'] = int(code[:2]) * 2
        
        elif '76825' in name or '76829' in name:
            data['series'] = 'Mega-Fit'
            data['pitch'] = 5.7
            data['current'] = 23.0
            data['rows'] = 2
            if data['part_number'] and '-' in data['part_number']:
                code = data['part_number'].split('-')[1]
                if len(code) >= 2:
                    data['pins'] = int(code[:2]) * 2
        
        # Se ainda não conseguiu extrair pinos, tentar padrões no nome
        if data['pins'] == 0:
            # Padrão: 1x02, 2x05, etc
            config_match = re.search(r'(\d+)x(\d+)', name)
            if config_match:
                data['rows'] = int(config_match.group(1))
                pins_per_row = int(config_match.group(2))
                data['pins'] = data['rows'] * pins_per_row
            
            # Padrão: 1x02_P2.54mm
            if not config_match:
                pin_match = re.search(r'1x(\d+)_P', name)
                if pin_match:
                    data['pins'] = int(pin_match.group(1))
                    data['rows'] = 1
        
        # Identificar gender
        if 'SOCKET' in name.upper() or 'RECEPTACLE' in name.upper() or 'FEMALE' in name.upper():
            data['gender'] = 'Female'
        elif 'HEADER' in name.upper() or 'PIN' in name.upper() or 'MALE' in name.upper():
            data['gender'] = 'Male'
        
        # Identificar orientação
        if 'VERTICAL' in name.upper():
            data['orientation'] = 'Vertical'
        elif 'HORIZONTAL' in name.upper() or 'RIGHT ANGLE' in name.upper() or 'RA' in name.upper():
            data['orientation'] = 'Right Angle'
        
        # Identificar montagem
        if 'SMD' in name.upper() or 'SMT' in name.upper():
            data['mounting_style'] = 'SMT'
        
        # Identificar locking
        if 'LATCH' in name.upper():
            data['locking'] = 'Latch'
        elif 'LOCK' in name.upper():
            data['locking'] = 'Locking'
        
        return data
    
    def get_symbol(self, data):
        """
        Encontra o símbolo apropriado baseado no número real de pinos
        """
        pins = data['pins']
        rows = data['rows']
        
        # Garantir que pins seja pelo menos 1
        if pins < 1:
            pins = 2
            print(f"   ⚠️ Pinos não detectados, usando {pins}")
        
        # Construir nome do símbolo baseado em pinos reais
        if rows == 1:
            # Para 1 fileira
            if pins <= 40:
                symbol_name = f"Connector_Generic:Conn_01x{pins:02d}"
            else:
                symbol_name = f"Connector_Generic:Conn_01x{pins:02d}"
        else:
            # Para 2 fileiras
            pins_per_row = pins // rows
            # Tentar diferentes variantes
            if self.symbols_dict.get(f"Connector_Generic:Conn_{rows:02d}x{pins_per_row:02d}_Odd_Even"):
                symbol_name = f"Connector_Generic:Conn_{rows:02d}x{pins_per_row:02d}_Odd_Even"
            elif self.symbols_dict.get(f"Connector_Generic:Conn_{rows:02d}x{pins_per_row:02d}_Top_Bottom"):
                symbol_name = f"Connector_Generic:Conn_{rows:02d}x{pins_per_row:02d}_Top_Bottom"
            else:
                symbol_name = f"Connector_Generic:Conn_{rows:02d}x{pins_per_row:02d}"
        
        return symbol_name
    
    def generate_my_pn(self):
        self.counter += 1
        return f"EL-CON_{self.counter:06d}"
    
    def generate_name(self, data):
        """Gera nome único baseado em características reais"""
        
        series_clean = data['series'].replace(' ', '_').replace('.', '')
        gender = 'M' if data['gender'] == 'Male' else 'F'
        orient = 'V' if data['orientation'] == 'Vertical' else 'RA'
        mount = 'SMT' if data['mounting_style'] == 'SMT' else 'THT'
        
        # Incluir número de pinos no nome para garantir unicidade
        parts = [
            'CON_MOLEX',
            series_clean,
            f"{data['pins']:02d}P",
            f"{data['rows']}R",
            gender,
            orient,
            mount
        ]
        
        # Adicionar código do produto se disponível para maior unicidade
        if data.get('part_number'):
            parts.append(data['part_number'])
        
        return "_".join(parts)
    
    def get_manuf_pn(self, footprint):
        """Extrai o número de peça do fabricante"""
        parts = footprint.split(':')[-1].split('_')
        if len(parts) >= 3:
            return '_'.join(parts[1:])
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
        manufacturer = 'Molex'
        manuf_pn = self.get_manuf_pn(data['footprint'])
        
        # Garantir que pins seja um número válido
        pins = max(1, data['pins'])
        rows = max(1, data['rows'])
        
        # Valores calculados
        temp_min = -40 if ('AUTOMOTIVE' in data['footprint'].upper()) else -25
        temp_max = 105 if ('AUTOMOTIVE' in data['footprint'].upper()) else 85
        
        # Tags com informação real de pinos
        tags = f"molex,{data['series'].lower().replace(' ', '_').replace('.', '')},{pins}pin"
        tags += ",header" if data['gender'] == 'Male' else ",receptacle"
        tags += f",{data['pitch']}mm"
        
        # Descrição com número real de pinos
        desc = f"Molex {data['series']} {pins}-position {data['gender']} connector"
        desc += f", {rows} row(s), {data['pitch']}mm pitch"
        desc += f", {data['orientation']} orientation, {data['mounting_style']}"
        desc += f", {data['current']}A, {data['voltage']}V"
        if data.get('part_number'):
            desc += f", PN: {data['part_number']}"
        
        # Lista de 118 valores
        values = [
            str(keyld),                                    # Keyld
            f"'{my_pn}'",                                  # MyPN
            f"'{name}'",                                   # Name
            f"'{desc}'",                                   # Description
            'NULL',                                        # Value
            'NULL',                                        # Value 2
            self.format_value(symbol),                     # Symbol
            f"'{data['footprint']}'",                      # Footprint
            f"'*Molex*{data['series']}*{pins}*'",          # Footprint_Filter
            f"'{data['mounting_style']}'",                 # Package
            f"'{manufacturer}'",                           # Manufacturer
            self.format_value(manuf_pn),                   # Manufacturer_PN
            f"'{data['series']}'",                         # Series
            "'Header Connector'",                          # Category
            f"'Molex {data['series']}'",                   # Subcategory
            "'Board-to-Board'",                            # Connector_Type
            f"'{data['series']}'",                         # Family
            "'Molex Specification'",                       # Standard
            "'PCB'",                                       # Mounting_Type
            f"'{data['mounting_style']}'",                 # Mounting_Style
            f"'{data['orientation']}'",                    # Orientation
            f"'{data['gender']}'",                         # Gender
            '0',                                           # Shielded
            'NULL',                                        # Shield_Material
            'NULL',                                        # Shield_Plating
            str(pins),                                     # Pins_Total
            f"'{pins}P'",                                    # Pins_Configuration
            str(rows),                                     # Rows
            "'Pin'",                                       # Contact_Type
            'NULL',                                        # Contact_Arrangement
            str(data['pitch']),                            # Pitch_mm
            'NULL',                                        # Row_Spacing_mm
            'NULL',                                        # Length_mm
            'NULL',                                        # Width_mm
            'NULL',                                        # Height_mm
            'NULL',                                        # Mating_Height_mm
            'NULL',                                        # PCB_Mounting_Dimensions
            str(data['current']),                          # Current_Rating_A
            'NULL',                                        # Current_Rating_Total_A
            str(data['voltage']),                          # Voltage_Rating_V
            '20',                                          # Contact_Resistance_mOhm
            '1000',                                        # Insulation_Resistance_MOhm
            '500',                                         # Dielectric_Withstanding_Voltage_V
            'NULL',                                        # Impedance_Ohm
            'NULL',                                        # Frequency_Max_Hz
            "'Phosphor Bronze'",                           # Contact_Material
            "'Tin'",                                       # Contact_Plating
            '2.0',                                         # Plating_Thickness_um
            'NULL',                                        # Contact_Finish
            "'Nylon'",                                     # Housing_Material
            "'Black'",                                     # Housing_Color
            "'Nylon'",                                     # Insulator_Material
            "'Black'",                                     # Insulator_Color
            f"'{data['locking']}'",                        # Locking_Mechanism
            "'Keyed'",                                     # Polarization
            '30',                                          # Mating_Cycles
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
            "'Friction Lock'",                             # PCB_Retention
            '0',                                           # Pick_and_Place
            '1',                                           # Tape_and_Reel
            'NULL',                                        # Cable_Type
            'NULL',                                        # Cable_Diameter_Max_mm
            self.format_value(data.get('wire_size')),      # Wire_Gauge_AWG
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
        
        # Verificação de segurança
        if len(values) != 118:
            print(f"❌ ERRO: Gerados {len(values)} valores, deveriam ser 118")
            print(f"   Para o componente: {my_pn}")
        
        return "(" + ", ".join(values) + ")"
    
    def generate_all_inserts(self):
        print("\n📝 Gerando comandos INSERT para conectores Molex...")
        
        inserts = []
        inserts.append("-- Comandos INSERT para conectores Molex")
        inserts.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        inserts.append(f"-- Total de footprints: {len(self.molex_footprints)}")
        inserts.append("")
        
        inserts.append("INSERT INTO Connector_General (" + ", ".join([f'"{col}"' for col in self.columns]) + ") VALUES")
        
        values_lines = []
        keyld = 1
        used_names = set()  # Para evitar nomes duplicados
        
        for i, fp in enumerate(self.molex_footprints, 1):
            try:
                data = self.parse_footprint(fp)
                values_line = self.generate_values_line(data, keyld)
                
                # Verificar nome único
                name = self.generate_name(data)
                if name in used_names:
                    # Adicionar sufixo para tornar único
                    data['part_number'] = data.get('part_number') or str(keyld)
                    values_line = self.generate_values_line(data, keyld)
                
                used_names.add(self.generate_name(data))
                values_lines.append(values_line)
                keyld += 1
                
                if i % 10 == 0:
                    print(f"   ⏳ Processados {i}/{len(self.molex_footprints)} footprints...")
                    
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
        print("🔧 GERADOR DE INSERTS PARA CONECTORES MOLEX")
        print("=" * 60)
        
        if not self.read_csv_files():
            return False
        
        if not self.filter_molex_footprints():
            return False
        
        inserts = self.generate_all_inserts()
        
        if self.save_to_file(inserts):
            print(f"\n✅ Processo concluído com sucesso!")
            print(f"   📁 Verifique o arquivo: {self.output_file}")
            return True
        return False


def main():
    base_dir = Path(__file__).parent
    generator = MolexConnectorGenerator(
        symbol_file=str(base_dir / "simbolos_para_database_connectores.csv"),
        footprint_file=str(base_dir / "footprints_para_database_connectors.csv"),
        output_file=str(base_dir / "sqlite_commands_molex.txt")
    )
    generator.run()


if __name__ == "__main__":
    main()