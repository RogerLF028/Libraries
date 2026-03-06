#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de comandos SQLite para conectores Phoenix MC
Arquivo: Gerar_Insert/gerar_insert.py
"""

import csv
import re
from pathlib import Path
from datetime import datetime

class PhoenixMCGenerator:
    def __init__(self, symbol_file, footprint_file, output_file):
        self.symbol_file = symbol_file
        self.footprint_file = footprint_file
        self.output_file = output_file
        self.footprints = []
        self.phoenix_footprints = []
        self.base_counter = 500000
        self.hv_counter = 600000
        
    def read_csv_files(self):
        print("📖 Lendo arquivos CSV...")
        try:
            with open(self.footprint_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.footprints = [row['Footprint'] for row in reader]
            print(f"   ✅ {len(self.footprints)} footprints carregados")
            return True
        except Exception as e:
            print(f"   ❌ Erro ao ler footprints: {e}")
            return False
    
    def filter_phoenix_footprints(self):
        print("\n🔍 Filtrando footprints Phoenix MC...")
        keywords = ['PhoenixContact_MC_', 'PhoenixContact_MCV_', 'PhoenixContact_MC_HighVoltage']
        
        for fp in self.footprints:
            for kw in keywords:
                if kw in fp:
                    self.phoenix_footprints.append({
                        'full_name': fp,
                        'type': 'HV' if 'HighVoltage' in fp else 'standard'
                    })
                    break
        
        print(f"   ✅ {len(self.phoenix_footprints)} footprints Phoenix MC encontrados")
        return True

    def parse_standard(self, name):
        """Parse footprints padrão MC/MCV"""
        # Verificar se o nome já começa com o prefixo da biblioteca
        if name.startswith('Connector_Phoenix_MC:'):
            footprint = name  # Já tem o prefixo
        else:
            footprint = f'Connector_Phoenix_MC:{name}'
        
        data = {
            'footprint': footprint,
            'has_flange': 0,
            'orientation': 'Horizontal',
            'pitch': 3.5,
            'positions': 2,
            'series': 'MC'
        }
        
        # Resto do código continua igual...
        if 'PhoenixContact_MCV_' in name:
            data['series'] = 'MCV'
            data['orientation'] = 'Vertical'
        elif 'PhoenixContact_MC_' in name:
            data['series'] = 'MC'
            data['orientation'] = 'Vertical' if 'Vertical' in name else 'Horizontal'
        
        if 'GF' in name or 'ThreadedFlange' in name:
            data['has_flange'] = 1
        
        pos_match = re.search(r'_(\d+)-G', name)
        if pos_match:
            data['positions'] = int(pos_match.group(1))
        
        if 'P3.50mm' in name:
            data['pitch'] = 3.5
        elif 'P3.81mm' in name:
            data['pitch'] = 3.81
        elif 'P5.00mm' in name:
            data['pitch'] = 5.0
        elif 'P5.08mm' in name:
            data['pitch'] = 5.08
            
        return data

    def parse_hv(self, name):
        """Parse footprints HighVoltage"""
        # Verificar se o nome já começa com o prefixo da biblioteca
        if name.startswith('Connector_Phoenix_MC_HighVoltage:'):
            footprint = name  # Já tem o prefixo
        else:
            footprint = f'Connector_Phoenix_MC_HighVoltage:{name}'
        
        data = {
            'footprint': footprint,
            'has_flange': 0,
            'orientation': 'Horizontal',
            'pitch': 5.08,
            'positions': 2,
            'series': 'MC_HV'
        }
        
        # Resto do código continua igual...
        pos_match = re.search(r'_(\d+)-G', name)
        if pos_match:
            data['positions'] = int(pos_match.group(1))
        
        if 'P5.00mm' in name:
            data['pitch'] = 5.0
        elif 'P5.08mm' in name:
            data['pitch'] = 5.08
        
        if 'GF' in name or 'ThreadedFlange' in name:
            data['has_flange'] = 1
        
        if 'Vertical' in name:
            data['orientation'] = 'Vertical'
            
        return data


    def get_current_rating(self, positions, pitch, is_hv=False):
        if is_hv:
            return 24.0
        if pitch >= 5.0:
            return 24.0
        elif pitch == 3.81:
            return 16.0 if positions <= 4 else (14.0 if positions <= 8 else 12.0)
        else:  # 3.5mm
            return 13.5 if positions <= 4 else (12.0 if positions <= 8 else 10.0)
    
    def get_voltage_rating(self, pitch, is_hv=False):
        return 400 if is_hv or pitch >= 5.0 else 250
    
    def get_symbol(self, positions, has_flange):
        pos_str = f"{positions:02d}"
        if has_flange:
            return f"Connector_Generic_MountingPin:Conn_01x{pos_str}_MountingPin"
        else:
            return f"Connector_Generic:Conn_01x{pos_str}"
    
    def get_manuf_pn(self, footprint):
        return footprint.split(':')[1].split('_1x')[0]
    
    def generate_name(self, data):
        series = data['series']
        pos = data['positions']
        pitch = data['pitch']
        orient = data['orientation'][0]
        flange = '_FLANGE' if data['has_flange'] else ''
        return f"CON_BLOCK_PHOENIX_{series}_{pos}_{pitch:.2f}_{orient}{flange}"
    
    def generate_my_pn(self, is_hv=False):
        if is_hv:
            self.hv_counter += 1
            return f"EL-CON_{self.hv_counter:06d}"
        else:
            self.base_counter += 1
            return f"EL-CON_{self.base_counter:06d}"
    
    def format_value(self, value):
        """Formata valores para SQL, tratando strings e números"""
        if value is None:
            return 'NULL'
        if isinstance(value, str):
            return f"'{value}'"
        if isinstance(value, bool):
            return '1' if value else '0'
        return str(value)
    
    """Gera uma linha de VALUES para um componente"""
    def generate_values_line(self, data):
        
        is_hv = (data['series'] == 'MC_HV')
        positions = data['positions']
        pitch = data['pitch']
        has_flange = data['has_flange']
        orientation = data['orientation']
        
        current = self.get_current_rating(positions, pitch, is_hv)
        voltage = self.get_voltage_rating(pitch, is_hv)
        my_pn = self.generate_my_pn(is_hv)
        name = self.generate_name(data)
        
        # Calcular valores condicionais ANTES de montar a string
        terminal_angle = '90°' if orientation == 'Vertical' else '0°'
        mounting_style = 'Through Hole - Flange Mount' if has_flange else 'Through Hole'
        
        if has_flange:
            desc = f"{data['series']} {positions}-position, pitch {pitch:.2f}mm, {orientation}, with threaded flange"
            notes = "'With threaded flange for panel mounting'"
            tags = f"'phoenix,mc,terminal block,flange{',high voltage' if is_hv else ''}'"
        else:
            desc = f"{data['series']} {positions}-position terminal block, pitch {pitch:.2f}mm, {orientation}"
            notes = 'NULL'
            tags = f"'phoenix,mc,terminal block{',high voltage' if is_hv else ''}'"
        
        # Valores específicos para HV vs Standard
        if is_hv:
            wire_awg_max = 12
            wire_mm2_max = 2.5
            strip_length = 8.0
            temp_max = 120
        else:
            wire_awg_max = 16
            wire_mm2_max = 1.5
            strip_length = 7.0
            temp_max = 105
        
        # Montar a linha de valores (usando as variáveis já calculadas)
        values = f"    ('{my_pn}', {self.format_value(name)}, {self.format_value(desc)}, {self.format_value(self.get_symbol(positions, has_flange))}, {self.format_value(data['footprint'])}, {self.format_value(f'*PhoenixContact*{data["series"]}*{positions}*Pitch{pitch:.2f}mm*{orientation}*')}, 'THT', 'Phoenix Contact', {self.format_value(self.get_manuf_pn(data['footprint']))}, 'MC 1,5', 'Terminal Block', 'PCB Mount', 'Header', {positions}, 1, {pitch:.2f}, 26, {wire_awg_max}, 0.14, {wire_mm2_max}, {strip_length}, 'Screw', '{terminal_angle}', 'Slotted', {current}, {voltage}, 'PCB', '{mounting_style}', {self.format_value(orientation)}, 'Green', 'Polyamide (PA)', -40, {temp_max}, 'UL94V-0', 1, 1, 1, 'IEC 60947-7-4', 1, 1, {notes}, {tags}, datetime('now'), 0, 0)"
        
        return values
    
        is_hv = (data['series'] == 'MC_HV')
        positions = data['positions']
        pitch = data['pitch']
        has_flange = data['has_flange']
        orientation = data['orientation']
        
        current = self.get_current_rating(positions, pitch, is_hv)
        voltage = self.get_voltage_rating(pitch, is_hv)
        my_pn = self.generate_my_pn(is_hv)
        name = self.generate_name(data)
        
        if has_flange:
            desc = f"{data['series']} {positions}-position, pitch {pitch:.2f}mm, {orientation}, with threaded flange"
            notes = "'With threaded flange for panel mounting'"
            tags = f"'phoenix,mc,terminal block{',flange' if has_flange else ''}{',high voltage' if is_hv else ''}'"
        else:
            desc = f"{data['series']} {positions}-position terminal block, pitch {pitch:.2f}mm, {orientation}"
            notes = 'NULL'
            tags = f"'phoenix,mc,terminal block{',high voltage' if is_hv else ''}'"
        
        # Valores específicos para HV vs Standard
        if is_hv:
            wire_awg_max = 12
            wire_mm2_max = 2.5
            strip_length = 8.0
            temp_max = 120
        else:
            wire_awg_max = 16
            wire_mm2_max = 1.5
            strip_length = 7.0
            temp_max = 105
        
        # Montar a linha de valores (TUDO EM UMA LINHA)
        values = f"    ({my_pn}, {self.format_value(name)}, {self.format_value(desc)}, {self.format_value(self.get_symbol(positions, has_flange))}, {self.format_value(data['footprint'])}, {self.format_value(f'*PhoenixContact*{data["series"]}*{positions}*Pitch{pitch:.2f}mm*{orientation}*')}, 'THT', 'Phoenix Contact', {self.format_value(self.get_manuf_pn(data['footprint']))}, 'MC 1,5', 'Terminal Block', 'PCB Mount', 'Header', {positions}, 1, {pitch:.2f}, 26, {wire_awg_max}, 0.14, {wire_mm2_max}, {strip_length}, 'Screw', '90°' if orientation == 'Vertical' else '0°', 'Slotted', {current}, {voltage}, 'PCB', 'Through Hole - Flange Mount' if has_flange else 'Through Hole', {self.format_value(orientation)}, 'Green', 'Polyamide (PA)', -40, {temp_max}, 'UL94V-0', 1, 1, 1, 'IEC 60947-7-4', 1, 1, {notes}, {tags}, " + "datetime('now'), 0, 0)"
        
        return values
    
    def generate_all_inserts(self):
        print("\n📝 Gerando comandos INSERT...")
        
        inserts = []
        inserts.append("-- Comandos INSERT para conectores Phoenix MC")
        inserts.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        inserts.append(f"-- Total de footprints: {len(self.phoenix_footprints)}")
        inserts.append("")
        
        # Cabeçalho do INSERT (uma única vez)
        inserts.append("INSERT INTO Connector_Block (")
        inserts.append("    MyPN, Name, Description, Symbol, Footprint, Footprint_Filter, Package,")
        inserts.append("    Manufacturer, Manufacturer_PN, Series, Category, Subcategory,")
        inserts.append("    Block_Type, Number_of_Positions, Number_of_Levels, Pitch_mm,")
        inserts.append("    Wire_Gauge_AWG_MIN, Wire_Gauge_AWG_MAX, Wire_Gauge_mm2_MIN, Wire_Gauge_mm2_MAX,")
        inserts.append("    Wire_Strip_Length_mm, Termination_Style, Terminal_Angle, Screw_Head_Type,")
        inserts.append("    Current_Rating_A, Voltage_Rating_V, Mounting_Type, Mounting_Style, Orientation,")
        inserts.append("    Color, Housing_Material, Operating_Temp_Min_C, Operating_Temp_Max_C,")
        inserts.append("    Flammability_Rating, RoHS_Compliant, UL_Certified, VDE_Certified,")
        inserts.append("    IEC_Standard, CE_Compliant, Active, Notes, Tags, CreatedAt,")
        inserts.append("    Exclude_from_BOM, Exclude_from_Board")
        inserts.append(") VALUES")
        
        values_lines = []
        hv_count = 0
        std_count = 0
        
        for i, fp in enumerate(self.phoenix_footprints, 1):
            try:
                if fp['type'] == 'HV':
                    data = self.parse_hv(fp['full_name'])
                    hv_count += 1
                else:
                    data = self.parse_standard(fp['full_name'])
                    std_count += 1
                
                values_line = self.generate_values_line(data)
                values_lines.append(values_line)
                
                if i % 20 == 0:
                    print(f"   ⏳ Processados {i}/{len(self.phoenix_footprints)} footprints...")
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar {fp['full_name']}: {e}")
        
        # Adicionar todas as linhas de VALUES, separadas por vírgula
        inserts.append(",\n".join(values_lines))
        inserts.append(";")  # Ponto e vírgula final
        
        inserts.append("")
        inserts.append(f"-- Resumo: {std_count} inserts padrão, {hv_count} inserts HighVoltage")
        
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
        print("🔧 GERADOR DE INSERTS PARA CONECTORES PHOENIX MC")
        print("=" * 60)
        
        if not self.read_csv_files():
            return False
        if not self.filter_phoenix_footprints():
            return False
        
        inserts = self.generate_all_inserts()
        
        if self.save_to_file(inserts):
            print(f"\n✅ Processo concluído com sucesso!")
            print(f"   📁 Verifique o arquivo: {self.output_file}")
            return True
        return False


def main():
    base_dir = Path(__file__).parent
    generator = PhoenixMCGenerator(
        symbol_file=str(base_dir / "simbolos_para_database_connectores.csv"),
        footprint_file=str(base_dir / "footprints_para_database_connectors.csv"),
        output_file=str(base_dir / "sqlite_commands_MC.txt")
    )
    generator.run()


if __name__ == "__main__":
    main()