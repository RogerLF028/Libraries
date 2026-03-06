#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de comandos SQLite para conectores Phoenix GMSTB
Arquivo: Gerar_Insert/gerar_insert_gmstb.py
"""

import csv
import re
from pathlib import Path
from datetime import datetime

class PhoenixGMSTBGenerator:
    def __init__(self, symbol_file, footprint_file, output_file):
        self.symbol_file = symbol_file
        self.footprint_file = footprint_file
        self.output_file = output_file
        self.footprints = []
        self.phoenix_footprints = []
        self.counter = 510000  # Começar depois dos MC (500000)
        
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
        print("\n🔍 Filtrando footprints Phoenix GMSTB...")
        keywords = [
            'PhoenixContact_GMSTBA_',
            'PhoenixContact_GMSTBVA_',
            'PhoenixContact_GMSTBV_',
            'PhoenixContact_GMSTB_'
        ]
        
        for fp in self.footprints:
            for kw in keywords:
                if kw in fp:
                    self.phoenix_footprints.append({
                        'full_name': fp,
                        'type': 'GMSTB'
                    })
                    break
        
        print(f"   ✅ {len(self.phoenix_footprints)} footprints Phoenix GMSTB encontrados")
        return True
    
    def parse_footprint(self, name):
        """Parse footprints da família GMSTB"""
        # Determinar a variação (BA, BVA, BV, B)
        data = {
            'footprint': name,
            'has_flange': 0,
            'orientation': 'Horizontal',
            'pitch': 7.5,
            'positions': 2,
            'series': 'GMSTBA',  # padrão
            'voltage_series': 'standard'  # standard ou high_voltage
        }
        
        # Identificar o tipo
        if 'GMSTBA_' in name:
            data['series'] = 'GMSTBA'
            data['orientation'] = 'Horizontal'
        elif 'GMSTBVA_' in name:
            data['series'] = 'GMSTBVA'
            data['orientation'] = 'Vertical'
        elif 'GMSTBV_' in name:
            data['series'] = 'GMSTBV'
            data['orientation'] = 'Vertical'
            if 'GF' in name or 'ThreadedFlange' in name:
                data['has_flange'] = 1
        elif 'GMSTB_' in name:
            data['series'] = 'GMSTB'
            data['orientation'] = 'Horizontal'
            if 'GF' in name or 'ThreadedFlange' in name:
                data['has_flange'] = 1
        
        # Extrair número de posições (formato: _10-G ou _10-GF)
        pos_match = re.search(r'_(\d+)-G', name)
        if pos_match:
            data['positions'] = int(pos_match.group(1))
        
        # Extrair pitch e determinar série de tensão
        if 'P7.50mm' in name:
            data['pitch'] = 7.5
            data['voltage_series'] = 'standard'
        elif 'P7.62mm' in name:
            data['pitch'] = 7.62
            data['voltage_series'] = 'high_voltage'
        
        return data
    
    def get_current_rating(self, positions):
        """
        Corrente nominal para GMSTB 2,5mm²
        Valores típicos da série
        """
        if positions <= 4:
            return 16.0
        elif positions <= 8:
            return 14.0
        else:
            return 12.0
    
    def get_voltage_rating(self, voltage_series):
        """
        Tensão nominal baseada na série
        """
        return 400 if voltage_series == 'high_voltage' else 250
    
    def get_symbol(self, positions, has_flange):
        pos_str = f"{positions:02d}"
        if has_flange:
            return f"Connector_Generic_MountingPin:Conn_01x{pos_str}_MountingPin"
        else:
            return f"Connector_Generic:Conn_01x{pos_str}"
    
    def get_manuf_pn(self, footprint):
        """Extrai o número de peça do fabricante do nome do footprint"""
        # Ex: PhoenixContact_GMSTBA_2,5_10-G-7,62
        name_part = footprint.split(':')[-1].split('_1x')[0]
        return name_part
    
    def generate_name(self, data):
        """Gera nome no formato CON_BLOCK_PHOENIX_GMSTB_..."""
        series = data['series']
        pos = data['positions']
        pitch = data['pitch']
        orient = data['orientation'][0]
        flange = '_FLANGE' if data['has_flange'] else ''
        hv = '_HV' if data['voltage_series'] == 'high_voltage' else ''
        
        return f"CON_BLOCK_PHOENIX_{series}_{pos}_{pitch:.2f}_{orient}{flange}{hv}"
    
    def generate_my_pn(self):
        """Gera MyPN sequencial"""
        self.counter += 1
        return f"EL-CON_{self.counter:06d}"
    
    def format_value(self, value):
        """Formata valores para SQL"""
        if value is None:
            return 'NULL'
        if isinstance(value, str):
            return f"'{value}'"
        if isinstance(value, bool):
            return '1' if value else '0'
        return str(value)
    
    def generate_values_line(self, data):
        """Gera uma linha de VALUES para um componente"""
        positions = data['positions']
        pitch = data['pitch']
        has_flange = data['has_flange']
        orientation = data['orientation']
        voltage_series = data['voltage_series']
        
        current = self.get_current_rating(positions)
        voltage = self.get_voltage_rating(voltage_series)
        my_pn = self.generate_my_pn()
        name = self.generate_name(data)
        
        # Calcular valores condicionais
        terminal_angle = '90°' if orientation == 'Vertical' else '0°'
        mounting_style = 'Through Hole - Flange Mount' if has_flange else 'Through Hole'
        
        # Descrição e notas
        voltage_desc = "400V" if voltage_series == 'high_voltage' else "250V"
        if has_flange:
            desc = f"{data['series']} {positions}-position, pitch {pitch:.2f}mm, {orientation}, with threaded flange, {voltage_desc}"
            notes = "'With threaded flange for panel mounting'"
            tags = f"'phoenix,gmstb,terminal block,flange,{voltage_desc.lower()}'"
        else:
            desc = f"{data['series']} {positions}-position terminal block, pitch {pitch:.2f}mm, {orientation}, {voltage_desc}"
            notes = 'NULL'
            tags = f"'phoenix,gmstb,terminal block,{voltage_desc.lower()}'"
        
        # Valores específicos GMSTB (2,5mm²)
        wire_awg_max = 12  # 2,5mm² ≈ 12 AWG
        wire_mm2_max = 2.5
        strip_length = 8.0
        temp_max = 105
        
        # Montar a linha de valores
        values = f"    ('{my_pn}', {self.format_value(name)}, {self.format_value(desc)}, {self.format_value(self.get_symbol(positions, has_flange))}, {self.format_value(data['footprint'])}, {self.format_value(f'*PhoenixContact*{data["series"]}*{positions}*Pitch{pitch:.2f}mm*{orientation}*')}, 'THT', 'Phoenix Contact', {self.format_value(self.get_manuf_pn(data['footprint']))}, 'GMSTB 2,5', 'Terminal Block', 'PCB Mount', 'Header', {positions}, 1, {pitch:.2f}, 18, {wire_awg_max}, 0.75, {wire_mm2_max}, {strip_length}, 'Screw', '{terminal_angle}', 'Slotted', {current}, {voltage}, 'PCB', '{mounting_style}', {self.format_value(orientation)}, 'Green', 'Polyamide (PA)', -40, {temp_max}, 'UL94V-0', 1, 1, 1, 'IEC 60947-7-4', 1, 1, {notes}, {tags}, datetime('now'), 0, 0)"
        
        return values
    
    def generate_all_inserts(self):
        print("\n📝 Gerando comandos INSERT para GMSTB...")
        
        inserts = []
        inserts.append("-- Comandos INSERT para conectores Phoenix GMSTB")
        inserts.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        inserts.append(f"-- Total de footprints: {len(self.phoenix_footprints)}")
        inserts.append("")
        
        # Cabeçalho do INSERT
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
        
        for i, fp in enumerate(self.phoenix_footprints, 1):
            try:
                data = self.parse_footprint(fp['full_name'])
                values_line = self.generate_values_line(data)
                values_lines.append(values_line)
                
                if i % 20 == 0:
                    print(f"   ⏳ Processados {i}/{len(self.phoenix_footprints)} footprints...")
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar {fp['full_name']}: {e}")
        
        # Adicionar todas as linhas de VALUES
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
        print("🔧 GERADOR DE INSERTS PARA CONECTORES PHOENIX GMSTB")
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
    generator = PhoenixGMSTBGenerator(
        symbol_file=str(base_dir / "simbolos_para_database_connectores.csv"),
        footprint_file=str(base_dir / "footprints_para_database_connectors.csv"),
        output_file=str(base_dir / "sqlite_commands_gmstb.txt")
    )
    generator.run()


if __name__ == "__main__":
    main()