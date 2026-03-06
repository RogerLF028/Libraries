#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de comandos SQLite para conectores Phoenix SPT (Push-in Technology)
Arquivo: Gerar_Insert/gerar_insert_spt.py
"""

import csv
import re
from pathlib import Path
from datetime import datetime

class PhoenixSPTGenerator:
    def __init__(self, symbol_file, footprint_file, output_file):
        self.symbol_file = symbol_file
        self.footprint_file = footprint_file
        self.output_file = output_file
        self.footprints = []
        self.phoenix_footprints = []
        self.counter = 530000  # Começar depois dos MSTB (520000)
        
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
        print("\n🔍 Filtrando footprints Phoenix SPT...")
        keywords = [
            'PhoenixContact_SPT_',
            'PhoenixContact_SPT-THR_'  # Versão THR (reflow)
        ]
        
        for fp in self.footprints:
            for kw in keywords:
                if kw in fp:
                    self.phoenix_footprints.append({
                        'full_name': fp,
                        'type': 'SPT'
                    })
                    break
        
        print(f"   ✅ {len(self.phoenix_footprints)} footprints Phoenix SPT encontrados")
        return True
    
    def parse_footprint(self, name):
        """Parse footprints da família SPT (Push-in Technology)"""
        data = {
            'footprint': name,
            'has_flange': 0,
            'orientation': 'Horizontal',
            'pitch': 3.5,
            'positions': 2,
            'series': 'SPT',
            'wire_size': '1.5',  # Padrão 1.5mm², pode ser 2.5 ou 5.0
            'is_thr': 0  # Versão THR para reflow soldering
        }
        
        # Identificar versão THR
        if 'SPT-THR_' in name:
            data['series'] = 'SPT-THR'
            data['is_thr'] = 1
        
        # Determinar orientação
        if 'Horizontal' in name:
            data['orientation'] = 'Horizontal'
        elif 'Vertical' in name:
            data['orientation'] = 'Vertical'
        
        # Extrair número de posições (formato: _10-H ou _10-V)
        pos_match = re.search(r'_(\d+)-[HV]', name)
        if pos_match:
            data['positions'] = int(pos_match.group(1))
        
        # Extrair pitch e determinar seção do fio
        if 'P3.5mm' in name:
            data['pitch'] = 3.5
            data['wire_size'] = '1.5'
        elif 'P5.0mm' in name:
            data['pitch'] = 5.0
            data['wire_size'] = '2.5'
        elif 'P7.5mm' in name:
            data['pitch'] = 7.5
            data['wire_size'] = '5.0' if 'SPT_5' in name else '2.5'
        
        # Extrair seção do fio do nome (SPT_1,5 / SPT_2,5 / SPT_5)
        wire_match = re.search(r'SPT(?:_THR)?_([\d,]+)', name)
        if wire_match:
            data['wire_size'] = wire_match.group(1).replace(',', '.')
        
        return data
    
    def get_current_rating(self, wire_size, positions):
        """
        Corrente nominal baseada na seção do fio e número de posições
        Valores típicos para tecnologia push-in
        """
        wire = float(wire_size)
        
        # Fator de derating por número de posições
        if positions <= 4:
            factor = 1.0
        elif positions <= 8:
            factor = 0.9
        elif positions <= 12:
            factor = 0.85
        else:
            factor = 0.8
        
        if wire >= 5.0:
            base_current = 32.0
        elif wire >= 2.5:
            base_current = 24.0
        elif wire >= 1.5:
            base_current = 17.5
        else:
            base_current = 13.5
            
        return round(base_current * factor, 1)
    
    def get_voltage_rating(self, pitch):
        """
        Tensão nominal baseada no pitch
        """
        if pitch >= 7.5:
            return 630
        elif pitch >= 5.0:
            return 400
        else:
            return 250
    
    def get_symbol(self, positions, has_flange, is_thr):
        """
        Símbolo apropriado - SPT usa os mesmos genéricos
        """
        pos_str = f"{positions:02d}"
        # SPT raramente tem flange, mas mantemos a lógica
        if has_flange:
            return f"Connector_Generic_MountingPin:Conn_01x{pos_str}_MountingPin"
        else:
            return f"Connector_Generic:Conn_01x{pos_str}"
    
    def get_manuf_pn(self, footprint):
        """Extrai o número de peça do fabricante do nome do footprint"""
        name_part = footprint.split(':')[-1].split('_1x')[0]
        return name_part
    
    def generate_name(self, data):
        """Gera nome no formato CON_BLOCK_PHOENIX_SPT_..."""
        series = data['series']
        pos = data['positions']
        pitch = data['pitch']
        orient = data['orientation'][0]
        wire = data['wire_size'].replace('.', '_')
        
        return f"CON_BLOCK_PHOENIX_{series}_{wire}_{pos}_{pitch:.2f}_{orient}"
    
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
    
    def get_wire_awg(self, wire_size_mm2):
        """
        Converte mm² para AWG aproximado
        """
        wire = float(wire_size_mm2)
        if wire >= 5.0:
            return 10
        elif wire >= 2.5:
            return 12
        elif wire >= 1.5:
            return 14
        else:
            return 16
    
    def generate_values_line(self, data):
        """Gera uma linha de VALUES para um componente"""
        positions = data['positions']
        pitch = data['pitch']
        orientation = data['orientation']
        wire_size = data['wire_size']
        is_thr = data['is_thr']
        
        current = self.get_current_rating(wire_size, positions)
        voltage = self.get_voltage_rating(pitch)
        my_pn = self.generate_my_pn()
        name = self.generate_name(data)
        
        # Calcular valores condicionais
        terminal_angle = '90°' if orientation == 'Vertical' else '0°'
        mounting_style = 'Through Hole'
        if is_thr:
            mounting_style = 'THR'  # Through Hole Reflow
        
        # Valores de fio
        wire_mm2 = float(wire_size)
        wire_awg = self.get_wire_awg(wire_mm2)
        wire_awg_min = wire_awg + 4  # AWG menor = fio mais grosso
        strip_length = 10.0  # SPT geralmente usa 10mm
        
        # Descrição e notas
        voltage_desc = f"{int(voltage)}V"
        
        if is_thr:
            desc = f"SPT {wire_size}mm² {positions}-position, pitch {pitch:.2f}mm, {orientation}, Push-in connection, THR soldering, {voltage_desc}"
            notes = "'THR version for reflow soldering'"
            tags = f"'phoenix,spt,push-in,thr,terminal block,{wire_size}mm2,{voltage_desc.lower()}'"
        else:
            desc = f"SPT {wire_size}mm² {positions}-position terminal block, pitch {pitch:.2f}mm, {orientation}, Push-in connection, {voltage_desc}"
            notes = 'NULL'
            tags = f"'phoenix,spt,push-in,terminal block,{wire_size}mm2,{voltage_desc.lower()}'"
        
        # Termination Style específico para push-in
        termination = 'Push-In'
        
        # Montar a linha de valores
        values = f"""    ('{my_pn}', {self.format_value(name)}, {self.format_value(desc)}, {self.format_value(self.get_symbol(positions, False, is_thr))}, {self.format_value(data['footprint'])}, {self.format_value(f'*PhoenixContact*SPT*{wire_size.replace(".",",")}*{positions}*Pitch{pitch:.2f}mm*{orientation}*')}, '{"THT" if not is_thr else "THR"}', 'Phoenix Contact', {self.format_value(self.get_manuf_pn(data['footprint']))}, 'SPT {wire_size}', 'Terminal Block', 'PCB Mount', 'Header', {positions}, 1, {pitch:.2f}, {wire_awg_min}, {wire_awg}, {wire_mm2*0.5:.2f}, {wire_mm2}, {strip_length}, '{termination}', '{terminal_angle}', 'None', {current}, {voltage}, 'PCB', '{mounting_style}', {self.format_value(orientation)}, 'Green', 'Polyamide (PA)', -40, 105, 'UL94V-0', 1, 1, 1, 'IEC 60947-7-4', 1, 1, {notes}, {tags}, datetime('now'), 0, 0)"""
        
        return values
    
    def generate_all_inserts(self):
        print("\n📝 Gerando comandos INSERT para SPT (Push-in)...")
        
        inserts = []
        inserts.append("-- Comandos INSERT para conectores Phoenix SPT (Push-in Technology)")
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
        print("🔧 GERADOR DE INSERTS PARA CONECTORES PHOENIX SPT (PUSH-IN)")
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
    generator = PhoenixSPTGenerator(
        symbol_file=str(base_dir / "simbolos_para_database_connectores.csv"),
        footprint_file=str(base_dir / "footprints_para_database_connectors.csv"),
        output_file=str(base_dir / "sqlite_commands_spt.txt")
    )
    generator.run()


if __name__ == "__main__":
    main()