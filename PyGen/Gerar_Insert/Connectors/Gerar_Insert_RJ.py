#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de comandos SQLite para conectores RJ (Ethernet/Telefonia)
Arquivo: Gerar_Insert/gerar_insert_rj.py
"""

import csv
import re
from pathlib import Path
from datetime import datetime

class RJConnectorGenerator:
    def __init__(self, symbol_file, footprint_file, output_file):
        self.symbol_file = symbol_file
        self.footprint_file = footprint_file
        self.output_file = output_file
        self.footprints = []
        self.symbols_dict = {}
        self.rj_footprints = []
        self.counter = 800000
        
    def read_csv_files(self):
        print("📖 Lendo arquivos CSV...")
        
        # Ler símbolos (opcional, só para referência)
        try:
            with open(self.symbol_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    symbol_name = row['Database_Symbol']
                    self.symbols_dict[symbol_name] = row
            print(f"   ✅ {len(self.symbols_dict)} símbolos carregados")
        except Exception as e:
            print(f"   ⚠️ Erro ao ler símbolos: {e}")
        
        # Ler footprints
        try:
            with open(self.footprint_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.footprints = [row['Footprint'] for row in reader]
            print(f"   ✅ {len(self.footprints)} footprints carregados")
            return True
        except Exception as e:
            print(f"   ❌ Erro ao ler footprints: {e}")
            return False
    
    def filter_rj_footprints(self):
        print("\n🔍 Filtrando footprints RJ...")
        
        # Padrões para identificar conectores RJ
        rj_patterns = [
            'RJ', '8P8C', '6P4C', '6P2C', '4P4C', '4P2C',
            'Ethernet', 'MagJack', 'LAN', 'Network'
        ]
        
        for fp in self.footprints:
            # Verifica se está na pasta Connector_RJ ou tem padrões RJ
            if 'Connector_RJ:' in fp:
                self.rj_footprints.append({
                    'full_name': fp,
                    'type': 'RJ'
                })
            else:
                fp_upper = fp.upper()
                if any(pattern.upper() in fp_upper for pattern in rj_patterns):
                    self.rj_footprints.append({
                        'full_name': fp,
                        'type': 'RJ'
                    })
        
        print(f"   ✅ {len(self.rj_footprints)} footprints RJ encontrados")
        return True
    
    def parse_footprint(self, name):
        """Parse footprints de conectores RJ"""
        data = {
            'footprint': name,
            'connector_type': 'RJ45',
            'configuration': '8P8C',
            'pins': 8,
            'shielded': False,
            'has_leds': False,
            'has_magnetics': False,
            'orientation': 'Horizontal',
            'port_count': 1,
            'manufacturer': None,
            'series': None
        }
        
        # Extrair fabricante
        if ':' in name:
            path_parts = name.split(':')
            fp_parts = path_parts[1].split('_')
            if len(fp_parts) >= 2:
                data['manufacturer'] = fp_parts[0]
        
        # Identificar configuração (4P4C, 6P2C, 6P4C, 6P6C, 8P4C, 8P8C)
        config_match = re.search(r'(\d)P(\d)C', name)
        if config_match:
            data['pins'] = int(config_match.group(1))
            data['configuration'] = f"{config_match.group(1)}P{config_match.group(2)}C"
            
            # Mapear para tipo RJ baseado na configuração
            if data['configuration'] == '4P4C':
                data['connector_type'] = 'RJ9/RJ10/RJ22'
            elif data['configuration'] == '6P2C':
                data['connector_type'] = 'RJ11'
            elif data['configuration'] == '6P4C':
                data['connector_type'] = 'RJ13/RJ14'
            elif data['configuration'] == '6P6C':
                data['connector_type'] = 'RJ12/RJ18/RJ25'
            elif data['configuration'] == '8P4C':
                data['connector_type'] = 'RJ38/RJ48'
            elif data['configuration'] == '8P8C':
                data['connector_type'] = 'RJ45'
        
        # Identificar por padrões RJ diretos
        rj_type_match = re.search(r'RJ(10|11|12|13|14|18|22|25|31|32|33|34|35|38|41|45|48|49|61)', name)
        if rj_type_match:
            rj_num = rj_type_match.group(1)
            data['connector_type'] = f'RJ{rj_num}'
        
        # Verificar se tem LEDs
        led_patterns = ['LED', 'MagJack', 'Green', 'Yellow', 'G/Y', 'Y/G']
        for pattern in led_patterns:
            if pattern in name:
                data['has_leds'] = True
                break
        
        # Verificar se é shielded
        shield_patterns = ['SHIELD', 'Shielded', 'Shield']
        for pattern in shield_patterns:
            if pattern in name:
                data['shielded'] = True
                break
        
        # Verificar se tem magnetics
        mag_patterns = ['Mag', 'Magnetics', 'Magnetic']
        for pattern in mag_patterns:
            if pattern in name:
                data['has_magnetics'] = True
                break
        
        # Orientação
        if 'Vertical' in name:
            data['orientation'] = 'Vertical'
        elif 'Horizontal' in name or 'Right Angle' in name or 'RA' in name:
            data['orientation'] = 'Right Angle'
        
        # Port count (stacked connectors)
        if 'Stacked' in name or '2x' in name:
            data['port_count'] = 2
        elif '4x' in name or 'Quad' in name:
            data['port_count'] = 4
        elif '8x' in name:
            data['port_count'] = 8
        
        return data
    
    def get_symbol(self, data):
        """Retorna o símbolo baseado nas características"""
        config = data['configuration']
        shielded = data['shielded']
        has_leds = data['has_leds']
        
        # Construir nome base do símbolo
        if config == '4P4C':
            base = 'Connector:4P4C'
        elif config == '6P2C':
            base = 'Connector:6P2C'
        elif config == '6P4C':
            base = 'Connector:6P4C'
        elif config == '6P6C':
            base = 'Connector:6P6C'
        elif config == '8P4C':
            base = 'Connector:8P4C'
        elif config == '8P8C':
            if has_leds:
                base = 'Connector:8P8C_LED'
            else:
                base = 'Connector:8P8C'
        else:
            base = 'Connector:8P8C'
        
        # Adicionar shielded se aplicável
        if shielded:
            if has_leds and config == '8P8C':
                return 'Connector:8P8C_LED_Shielded'
            elif config == '8P8C':
                return 'Connector:8P8C_Shielded'
            else:
                return f"{base}_Shielded"
        
        return base
    
    def generate_my_pn(self):
        self.counter += 1
        return f"EL-CON_{self.counter:06d}"
    
    def generate_name(self, data):
        """Gera nome no formato CON_RJ{type}_{config}_{features}"""
        
        # Simplificar tipo removendo barras
        conn_type = data['connector_type'].replace('/', '_')
        
        parts = [f"CON_RJ{conn_type}"]
        parts.append(data['configuration'])
        
        if data['shielded']:
            parts.append('SHIELDED')
        
        if data['has_leds']:
            parts.append('LED')
        
        if data['has_magnetics']:
            parts.append('MAG')
        
        if data['port_count'] > 1:
            parts.append(f"{data['port_count']}P")
        
        if data['orientation'] == 'Vertical':
            parts.append('VERT')
        elif data['orientation'] == 'Right Angle':
            parts.append('RA')
        
        return "_".join(parts)
    
    def get_manuf_pn(self, footprint):
        """Extrai o número de peça do fabricante"""
        parts = footprint.split(':')[-1].split('_')
        if len(parts) >= 3:
            return '_'.join(parts[1:])
        return None
    
    def get_current_rating(self, config, has_magnetics):
        """Corrente nominal baseada na configuração"""
        if '1000' in config or 'Gigabit' in config:
            return 1.5
        elif 'PoE' in config:
            return 1.5
        else:
            return 1.5
    
    def get_voltage_rating(self, config, has_magnetics):
        """Tensão nominal baseada na configuração"""
        if 'PoE' in config:
            return 57
        else:
            return 125
    
    def format_value(self, value):
        if value is None:
            return 'NULL'
        if isinstance(value, str):
            return f"'{value}'"
        if isinstance(value, bool):
            return '1' if value else '0'
        return str(value)
    
    def generate_values_line(self, data):
        """Gera uma linha de VALUES para Connector_General - formato igual ao MSTB"""
        
        my_pn = self.generate_my_pn()
        name = self.generate_name(data)
        symbol = self.get_symbol(data)
        manufacturer = data['manufacturer'] or 'Various'
        manuf_pn = self.get_manuf_pn(data['footprint'])
        current = self.get_current_rating(data['footprint'], data['has_magnetics'])
        voltage = self.get_voltage_rating(data['footprint'], data['has_magnetics'])
        
        # Determinar temperatura
        if 'Industrial' in data['footprint']:
            temp_min = -40
            temp_max = 85
        else:
            temp_min = 0
            temp_max = 70
        
        # Construir descrição
        desc = f"{data['connector_type']} {data['configuration']}"
        if data['port_count'] > 1:
            desc = f"{data['port_count']}-port {desc}"
        if data['has_magnetics']:
            desc += " with magnetics"
        if data['shielded']:
            desc += " shielded"
        if data['has_leds']:
            desc += " with LEDs"
        desc += f", {data['orientation'].lower()} orientation"
        
        # Construir tags
        tags = f"rj,{data['connector_type'].lower().replace('/', '_')},{data['configuration'].lower()}"
        if data['shielded']:
            tags += ",shielded"
        if data['has_leds']:
            tags += ",led"
        if data['has_magnetics']:
            tags += ",magnetics"
        
        # Montar VALUES no mesmo formato do MSTB
        values = f"""    ({self.format_value(my_pn)}, {self.format_value(name)}, {self.format_value(desc)}, {self.format_value(symbol)}, {self.format_value(data['footprint'])}, {self.format_value(f'*{data["configuration"]}*')}, {self.format_value('THT')}, {self.format_value(manufacturer)}, {self.format_value(manuf_pn)}, {self.format_value('RJ Series')}, {self.format_value('Modular Connector')}, {self.format_value(data['connector_type'])}, {self.format_value('RJ')}, {self.format_value(data['configuration'])}, {self.format_value('IEEE 802.3')}, {self.format_value('PCB')}, {self.format_value('Through Hole')}, {self.format_value(data['orientation'])}, {self.format_value('Female')}, {1 if data['shielded'] else 0}, {self.format_value('Copper Alloy')}, {self.format_value('Nickel')}, {data['pins']}, {self.format_value(data['configuration'])}, {data['pins'] // 2}, {self.format_value('Spring')}, {self.format_value('NULL')}, {self.format_value('1.27')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {current}, {self.format_value('NULL')}, {voltage}, {self.format_value('20')}, {self.format_value('500')}, {self.format_value('1500')}, {self.format_value('100')}, {self.format_value('100 MHz')}, {self.format_value('Copper Alloy')}, {self.format_value('Gold')}, {self.format_value('0.76')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('Polyamide (PA)')}, {self.format_value('Black')}, {self.format_value('Friction')}, {self.format_value('Keyed')}, {self.format_value('750')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {temp_min}, {temp_max}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, 1, 1, 1, {self.format_value('NULL')}, 1, 0, {self.format_value('UL94 V-0')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('Wave')}, {self.format_value('NULL')}, {self.format_value('Hold-down tabs')}, 1, 1, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('Tray')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('NULL')}, 1, {self.format_value('NULL')}, {self.format_value(tags)}, {self.format_value('script')}, datetime('now'), {self.format_value('NULL')}, {self.format_value('NULL')}, {self.format_value('1.0')}, 0, 0)"""
        
        return values
    
    def generate_all_inserts(self):
        print("\n📝 Gerando comandos INSERT para conectores RJ...")
        
        inserts = []
        inserts.append("-- Comandos INSERT para conectores RJ (Ethernet/Telefonia)")
        inserts.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        inserts.append(f"-- Total de footprints: {len(self.rj_footprints)}")
        inserts.append("")
        
        # Cabeçalho do INSERT - agora com todos os campos na ordem da tabela
        inserts.append("INSERT INTO Connector_General (")
        inserts.append("    MyPN, Name, Description, Symbol, Footprint, Footprint_Filter, Package,")
        inserts.append("    Manufacturer, Manufacturer_PN, Series, Category, Subcategory,")
        inserts.append("    Connector_Type, Family, Standard, Mounting_Type, Mounting_Style, Orientation,")
        inserts.append("    Gender, Shielded, Shield_Material, Shield_Plating, Pins_Total, Pins_Configuration, Rows,")
        inserts.append("    Contact_Type, Contact_Arrangement, Pitch_mm, Row_Spacing_mm, Length_mm, Width_mm, Height_mm,")
        inserts.append("    Mating_Height_mm, PCB_Mounting_Dimensions, Current_Rating_A, Current_Rating_Total_A,")
        inserts.append("    Voltage_Rating_V, Contact_Resistance_mOhm, Insulation_Resistance_MOhm,")
        inserts.append("    Dielectric_Withstanding_Voltage_V, Impedance_Ohm, Frequency_Max_Hz,")
        inserts.append("    Contact_Material, Contact_Plating, Plating_Thickness_um, Contact_Finish,")
        inserts.append("    Housing_Material, Housing_Color, Insulator_Material, Insulator_Color,")
        inserts.append("    Locking_Mechanism, Polarization, Mating_Cycles, Insertion_Force_N, Withdrawal_Force_N,")
        inserts.append("    Operating_Temp_Min_C, Operating_Temp_Max_C, Storage_Temp_Min_C, Storage_Temp_Max_C,")
        inserts.append("    IP_Rating, Moisture_Sensitivity_Level, RoHS_Compliant, REACH_Compliant, UL_Certified,")
        inserts.append("    UL_File_Number, CSA_Certified, TUV_Certified, Flammability_Rating, Solder_Type,")
        inserts.append("    Solder_Temperature_C, Solder_Process, Cleaning_Process, PCB_Retention, Pick_and_Place,")
        inserts.append("    Tape_and_Reel, Cable_Type, Cable_Diameter_Max_mm, Wire_Gauge_AWG, Wire_Strip_Length_mm,")
        inserts.append("    LCSC_PN, LCSC_URL, Mouser_PN, Mouser_URL, Digikey_PN, Digikey_URL, Farnell_PN, Farnell_URL,")
        inserts.append("    Newark_PN, Newark_URL, RS_PN, RS_URL, StockQty, Min_Stock, Max_Stock, StockPlace, Price,")
        inserts.append("    Currency, MOQ, Packaging, Datasheet, Drawing_2D, Drawing_3D, PCB_Layout_Suggestion,")
        inserts.append("    Application_Note, Assembly_Instructions, Active, Notes, Tags, CreatedBy, CreatedAt,")
        inserts.append("    ModifiedBy, ModifiedAt, Version, Exclude_from_BOM, Exclude_from_Board")
        inserts.append(") VALUES")
        
        values_lines = []
        
        for i, fp in enumerate(self.rj_footprints, 1):
            try:
                data = self.parse_footprint(fp['full_name'])
                values_line = self.generate_values_line(data)
                values_lines.append(values_line)
                
                if i % 10 == 0:
                    print(f"   ⏳ Processados {i}/{len(self.rj_footprints)} footprints...")
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar {fp['full_name']}: {e}")
        
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
        print("🔧 GERADOR DE INSERTS PARA CONECTORES RJ")
        print("=" * 60)
        
        if not self.read_csv_files():
            return False
        if not self.filter_rj_footprints():
            return False
        
        inserts = self.generate_all_inserts()
        
        if self.save_to_file(inserts):
            print(f"\n✅ Processo concluído com sucesso!")
            print(f"   📁 Verifique o arquivo: {self.output_file}")
            return True
        return False


def main():
    base_dir = Path(__file__).parent
    generator = RJConnectorGenerator(
        symbol_file=str(base_dir / "simbolos_para_database_connectores.csv"),
        footprint_file=str(base_dir / "footprints_para_database_connectors.csv"),
        output_file=str(base_dir / "sqlite_commands_rj.txt")
    )
    generator.run()


if __name__ == "__main__":
    main()