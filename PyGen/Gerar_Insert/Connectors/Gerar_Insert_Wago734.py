#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de comandos SQLite para conectores Wago 734 (CAGE CLAMP®)
Arquivo: Gerar_Insert/gerar_insert_wago.py
"""

import csv
import re
from pathlib import Path
from datetime import datetime

class Wago734Generator:
    def __init__(self, symbol_file, footprint_file, output_file):
        self.symbol_file = symbol_file
        self.footprint_file = footprint_file
        self.output_file = output_file
        self.footprints = []
        self.wago_footprints = []
        self.counter = 540000  # Começar depois dos SPT (530000)
        
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
    
    def filter_wago_footprints(self):
        print("\n🔍 Filtrando footprints Wago 734...")
        
        for fp in self.footprints:
            if 'Wago_734-' in fp:
                self.wago_footprints.append({
                    'full_name': fp,
                    'type': '734'
                })
        
        print(f"   ✅ {len(self.wago_footprints)} footprints Wago 734 encontrados")
        return True
    
    def parse_footprint(self, name):
        """Parse footprints da família Wago 734"""
        data = {
            'footprint': name,
            'orientation': 'Vertical',
            'pitch': 3.5,
            'positions': 2,
            'series': '734',
            'voltage_rating': 160  # padrão
        }
        
        # Extrair número do modelo (ex: 734-132)
        model_match = re.search(r'Wago_734-(\d+)', name)
        if model_match:
            model_num = int(model_match.group(1))
            data['model'] = model_num
            
            # Determinar orientação baseado no modelo
            # 132-154: vertical, 162-184: horizontal
            if 132 <= model_num <= 154:
                data['orientation'] = 'Vertical'
            elif 162 <= model_num <= 184:
                data['orientation'] = 'Horizontal'
        
        # Extrair número de posições do nome (1x02, 1x03, etc)
        pos_match = re.search(r'1x(\d+)', name)
        if pos_match:
            data['positions'] = int(pos_match.group(1))
        
        # Determinar tensão baseado no modelo (alguns são 300V)
        if data.get('model', 0) in [146, 148, 150, 154, 166, 168, 170, 174, 176, 178, 180, 184]:
            data['voltage_rating'] = 300
        
        return data
    
    def get_current_rating(self, positions):
        """
        Corrente nominal para Wago 734 (CAGE CLAMP®)
        Valores típicos: 6A para muitas posições, até 10A para poucas
        """
        if positions <= 4:
            return 10.0
        elif positions <= 8:
            return 9.0
        elif positions <= 12:
            return 8.0
        else:
            return 6.0
    
    def get_voltage_rating(self, voltage_rating):
        """
        Tensão nominal (160V ou 300V)
        """
        return voltage_rating
    
    def get_symbol(self, positions):
        """
        Símbolo genérico (Wago usa os mesmos símbolos)
        """
        pos_str = f"{positions:02d}"
        return f"Connector_Generic:Conn_01x{pos_str}"
    
    def get_manuf_pn(self, footprint):
        """Extrai o número de peça do fabricante"""
        # Ex: Wago_734-132
        name_part = footprint.split(':')[-1].split('_1x')[0]
        return name_part
    
    def generate_name(self, data):
        """Gera nome no formato CON_BLOCK_WAGO_734_..."""
        pos = data['positions']
        orient = data['orientation'][0]
        voltage = "300V" if data['voltage_rating'] == 300 else "160V"
        
        return f"CON_BLOCK_WAGO_734_{pos}_{orient}_{voltage}"
    
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
        orientation = data['orientation']
        voltage = data['voltage_rating']
        
        current = self.get_current_rating(positions)
        my_pn = self.generate_my_pn()
        name = self.generate_name(data)
        
        # Calcular valores condicionais
        terminal_angle = '90°' if orientation == 'Vertical' else '0°'
        
        # Descrição e notas
        voltage_desc = f"{voltage}V"
        desc = f"Wago 734 Series {positions}-position CAGE CLAMP® terminal block, pitch 3.50mm, {orientation}, {voltage_desc}"
        
        tags = f"'wago,734,cage clamp,terminal block,{voltage_desc.lower()}'"
        
        # Valores específicos Wago 734
        wire_awg_min = 28
        wire_awg_max = 16
        wire_mm2_min = 0.08
        wire_mm2_max = 1.5
        strip_length = 6.0  # 5-6mm típico para Wago
        
        # Termination Style específico para CAGE CLAMP®
        termination = 'CAGE CLAMP®'
        
        # Montar a linha de valores
        values = f"""    ('{my_pn}', {self.format_value(name)}, {self.format_value(desc)}, {self.format_value(self.get_symbol(positions))}, {self.format_value(data['footprint'])}, {self.format_value(f'*Wago*734*{positions}*P3.50mm*{orientation}*')}, 'THT', 'Wago', {self.format_value(self.get_manuf_pn(data['footprint']))}, '734 Series', 'Terminal Block', 'PCB Mount', 'Header', {positions}, 1, 3.50, {wire_awg_min}, {wire_awg_max}, {wire_mm2_min}, {wire_mm2_max}, {strip_length}, '{termination}', '{terminal_angle}', 'None', {current}, {voltage}, 'PCB', 'Through Hole', {self.format_value(orientation)}, 'Green', 'Polyamide (PA)', -40, 105, 'UL94V-0', 1, 1, 1, 'IEC 60947-7-1', 1, 1, NULL, {tags}, datetime('now'), 0, 0)"""
        
        return values
    
    def generate_all_inserts(self):
        print("\n📝 Gerando comandos INSERT para Wago 734...")
        
        inserts = []
        inserts.append("-- Comandos INSERT para conectores Wago 734 (CAGE CLAMP®)")
        inserts.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        inserts.append(f"-- Total de footprints: {len(self.wago_footprints)}")
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
        
        for i, fp in enumerate(self.wago_footprints, 1):
            try:
                data = self.parse_footprint(fp['full_name'])
                values_line = self.generate_values_line(data)
                values_lines.append(values_line)
                
                if i % 20 == 0:
                    print(f"   ⏳ Processados {i}/{len(self.wago_footprints)} footprints...")
                    
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
        print("🔧 GERADOR DE INSERTS PARA CONECTORES WAGO 734")
        print("=" * 60)
        
        if not self.read_csv_files():
            return False
        if not self.filter_wago_footprints():
            return False
        
        inserts = self.generate_all_inserts()
        
        if self.save_to_file(inserts):
            print(f"\n✅ Processo concluído com sucesso!")
            print(f"   📁 Verifique o arquivo: {self.output_file}")
            return True
        return False


def main():
    base_dir = Path(__file__).parent
    generator = Wago734Generator(
        symbol_file=str(base_dir / "simbolos_para_database_connectores.csv"),
        footprint_file=str(base_dir / "footprints_para_database_connectors.csv"),
        output_file=str(base_dir / "sqlite_commands_wago.txt")
    )
    generator.run()


if __name__ == "__main__":
    main()