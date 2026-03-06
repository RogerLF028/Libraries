#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de comandos SQLite para conectores IDC
Arquivo: Gerar_Insert/gerar_insert_idc.py
"""

import csv
import re
from pathlib import Path
from datetime import datetime

class IDCGenerator:
    def __init__(self, symbol_file, footprint_file, output_file):
        self.symbol_file = symbol_file
        self.footprint_file = footprint_file
        self.output_file = output_file
        self.footprints = []
        self.symbols = []
        self.symbols_dict = {}
        self.idc_footprints = []
        self.counter = 600000
        
    def read_csv_files(self):
        print("📖 Lendo arquivos CSV...")
        
        # Ler símbolos
        try:
            with open(self.symbol_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.symbols = list(reader)
                # Criar um dicionário para busca rápida
                for row in self.symbols:
                    self.symbols_dict[row['Database_Symbol']] = row
            print(f"   ✅ {len(self.symbols)} símbolos carregados")
        except Exception as e:
            print(f"   ❌ Erro ao ler símbolos: {e}")
            return False
        
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
    
    def filter_idc_footprints(self):
        print("\n🔍 Filtrando footprints IDC...")
        
        for fp in self.footprints:
            if 'IDC-Header' in fp or 'IDC_Socket' in fp:
                self.idc_footprints.append(fp)
        
        print(f"   ✅ {len(self.idc_footprints)} footprints IDC encontrados")
        return True
    
    def get_symbol_name(self, pins_per_row, has_mounting_pin):
        """
        Retorna o nome do símbolo baseado nas regras:
        - Com MP: Connector_Generic_MountingPin:Conn_02xXX_Odd_Even_MountingPin
        - Sem MP: Connector_Generic:Conn_02xXX_Odd_Even
        """
        pos_str = f"{pins_per_row:02d}"
        
        if has_mounting_pin:
            return f"Connector_Generic_MountingPin:Conn_02x{pos_str}_Odd_Even_MountingPin"
        else:
            return f"Connector_Generic:Conn_02x{pos_str}_Odd_Even"
    
    def parse_footprint(self, name):
        """Parse footprints de conectores IDC"""
        data = {
            'footprint': name,  # Valor direto do CSV
            'gender': 'Male' if 'IDC-Header' in name else 'Female',
            'pitch': 2.54 if 'P2.54mm' in name else 1.27,
            'rows': 2,  # IDC sempre 2 linhas
            'orientation': 'Vertical' if 'Vertical' in name else 'Horizontal',
            'mounting_style': 'Through Hole' if 'THT' in name or 'Vertical' in name or 'Horizontal' in name else 'SMT',
            'connector_type': 'IDC Header' if 'IDC-Header' in name else 'IDC Socket',
            'subcategory': 'Header' if 'IDC-Header' in name else 'Socket'
        }
        
        # Extrair número de contatos
        contacts_match = re.search(r'2x(\d+)', name)
        if contacts_match:
            pins_per_row = int(contacts_match.group(1))
            data['contacts'] = pins_per_row * 2
            data['pins_per_row'] = pins_per_row
        else:
            data['contacts'] = 0
            data['pins_per_row'] = 0
        
        # Verificar se tem mounting pin (MP)
        data['has_mounting_pin'] = 1 if '-1MP_' in name else 0
        
        # Verificar se tem latch (não afeta o símbolo, mas preenchemos o campo)
        data['locking'] = 'Latch' if 'Latch' in name else None
        data['ejectors'] = 1 if 'Latch' in name else 0
        
        if 'Latch6.5mm' in name:
            data['ejector_type'] = 'Short'
        elif 'Latch9.5mm' in name:
            data['ejector_type'] = 'Long'
        elif 'Latch12.0mm' in name:
            data['ejector_type'] = 'Long'
        elif 'Latch' in name:
            data['ejector_type'] = 'Standard'
        else:
            data['ejector_type'] = None
        
        # Determinar símbolo baseado nas regras
        if data['pins_per_row'] > 0:
            data['symbol'] = self.get_symbol_name(data['pins_per_row'], data['has_mounting_pin'])
        else:
            data['symbol'] = None
            print(f"   ⚠️  Aviso: Não foi possível determinar número de pinos para {name}")
        
        return data
    
    def generate_my_pn(self):
        self.counter += 1
        return f"EL-CON_{self.counter:06d}"
    
    def generate_name(self, data):
        """Gera nome no formato CON_IDC_..."""
        gender = 'M' if data['gender'] == 'Male' else 'F'
        contacts = data.get('contacts', 0)
        pitch = data['pitch']
        orient = data['orientation'][0]
        mount = 'SMD' if data['mounting_style'] == 'SMT' else 'THT'
        latch = '_LATCH' if data['ejectors'] else ''
        mp = '_MP' if data.get('has_mounting_pin', 0) else ''
        
        return f"CON_IDC_{gender}_{contacts}_{pitch:.2f}_{orient}{mount}{latch}{mp}"
    
    def format_value(self, value):
        if value is None:
            return 'NULL'
        if isinstance(value, str):
            return f"'{value}'"
        if isinstance(value, bool):
            return '1' if value else '0'
        return str(value)
    
    def generate_values_line(self, data):
        """Gera uma linha de VALUES"""
        
        my_pn = self.generate_my_pn()
        name = self.generate_name(data)
        description = f"{data['connector_type']}, {data.get('contacts', 0)} pins, {data['pitch']:.2f}mm pitch, {data['orientation']}"
        
        if data.get('ejectors'):
            description += f", with {data.get('ejector_type', '')} ejectors"
        if data.get('has_mounting_pin'):
            description += ", with mounting pins"
        
        # Usar símbolo determinado
        symbol = data.get('symbol')
        
        # Footprint é o valor direto do CSV
        footprint = data['footprint']
        
        # Gerar footprint filter básico
        footprint_filter = f"*IDC*{data.get('contacts', 0)}*P{data['pitch']:.2f}mm*{data['orientation']}*"
        
        # Package
        package = 'THT' if data['mounting_style'] == 'Through Hole' else 'SMD'
        
        # Valores que podemos extrair
        manufacturer = None
        manufacturer_pn = None
        series = 'IDC'
        category = 'IDC Connector'
        subcategory = data['subcategory']
        
        # Campos que NÃO podemos extrair - deixar NULL
        cable_type = None
        cable_compatibility = None
        cable_width_max_mm = None
        cable_thickness_max_mm = None
        wire_gauge_awg = None
        conductor_size_mm = None
        insulation_diameter_max_mm = None
        strain_relief = 0
        strain_relief_type = None
        mounting_type = 'PCB'
        mounting_style = data['mounting_style']
        orientation = data['orientation']
        locking_mechanism = data.get('locking')
        polarization = None
        center_polarization = 0
        ejectors = data.get('ejectors', 0)
        ejector_type = data.get('ejector_type')
        current_rating_a = None
        voltage_rating_v = None
        contact_resistance_mohm = None
        insulation_resistance_mohm = None
        dielectric_withstanding_voltage_v = None
        capacitance_pf = None
        contact_material = None
        contact_plating = None
        plating_thickness_um = None
        contact_finish = None
        contact_design = None
        housing_material = None
        housing_color = None
        insulator_material = None
        insulator_color = None
        flammability_rating = None
        length_mm = None
        width_mm = None
        height_mm = None
        height_above_pcb_mm = None
        mating_height_mm = None
        pcb_mounting_dimensions = None
        operating_temp_min_c = None
        operating_temp_max_c = None
        storage_temp_min_c = None
        storage_temp_max_c = None
        mating_cycles = None
        insertion_force_n = None
        withdrawal_force_n = None
        rohs_compliant = None
        reach_compliant = None
        ul_certified = None
        ul_file_number = None
        csa_certified = None
        termination = 'IDC'
        termination_process = None
        tooling_required = None
        tooling_pn = None
        lcsc_pn = None
        lcsc_url = None
        mouser_pn = None
        mouser_url = None
        digikey_pn = None
        digikey_url = None
        farnell_pn = None
        farnell_url = None
        newark_pn = None
        newark_url = None
        rs_pn = None
        rs_url = None
        stock_qty = None
        min_stock = None
        max_stock = None
        stock_place = None
        price = None
        currency = None
        moq = None
        packaging = None
        datasheet = None
        drawing_2d = None
        drawing_3d = None
        cable_assembly_drawing = None
        tooling_documentation = None
        application_note = None
        active = 1
        notes = None
        tags = f"idc,connector,{data['gender'].lower()},{data.get('contacts', 0)}pin"
        created_by = 'script'
        created_at = "datetime('now')"
        modified_by = None
        modified_at = None
        version = '1.0'
        exclude_from_bom = 0
        exclude_from_board = 0
        
        # Montar VALUES
        values = f"""    ({self.format_value(my_pn)}, {self.format_value(name)}, {self.format_value(description)}, {self.format_value(symbol)}, {self.format_value(footprint)}, {self.format_value(footprint_filter)}, {self.format_value(package)}, {self.format_value(manufacturer)}, {self.format_value(manufacturer_pn)}, {self.format_value(series)}, {self.format_value(category)}, {self.format_value(subcategory)}, {self.format_value(data['connector_type'])}, {data.get('contacts', 'NULL')}, {data['pitch']}, {data['rows']}, {self.format_value(data['gender'])}, {self.format_value(cable_type)}, {self.format_value(cable_compatibility)}, {self.format_value(cable_width_max_mm)}, {self.format_value(cable_thickness_max_mm)}, {self.format_value(wire_gauge_awg)}, {self.format_value(conductor_size_mm)}, {self.format_value(insulation_diameter_max_mm)}, {strain_relief}, {self.format_value(strain_relief_type)}, {self.format_value(mounting_type)}, {self.format_value(mounting_style)}, {self.format_value(orientation)}, {self.format_value(locking_mechanism)}, {self.format_value(polarization)}, {center_polarization}, {ejectors}, {self.format_value(ejector_type)}, {self.format_value(current_rating_a)}, {self.format_value(voltage_rating_v)}, {self.format_value(contact_resistance_mohm)}, {self.format_value(insulation_resistance_mohm)}, {self.format_value(dielectric_withstanding_voltage_v)}, {self.format_value(capacitance_pf)}, {self.format_value(contact_material)}, {self.format_value(contact_plating)}, {self.format_value(plating_thickness_um)}, {self.format_value(contact_finish)}, {self.format_value(contact_design)}, {self.format_value(housing_material)}, {self.format_value(housing_color)}, {self.format_value(insulator_material)}, {self.format_value(insulator_color)}, {self.format_value(flammability_rating)}, {self.format_value(length_mm)}, {self.format_value(width_mm)}, {self.format_value(height_mm)}, {self.format_value(height_above_pcb_mm)}, {self.format_value(mating_height_mm)}, {self.format_value(pcb_mounting_dimensions)}, {self.format_value(operating_temp_min_c)}, {self.format_value(operating_temp_max_c)}, {self.format_value(storage_temp_min_c)}, {self.format_value(storage_temp_max_c)}, {self.format_value(mating_cycles)}, {self.format_value(insertion_force_n)}, {self.format_value(withdrawal_force_n)}, {self.format_value(rohs_compliant)}, {self.format_value(reach_compliant)}, {self.format_value(ul_certified)}, {self.format_value(ul_file_number)}, {self.format_value(csa_certified)}, {self.format_value(termination)}, {self.format_value(termination_process)}, {self.format_value(tooling_required)}, {self.format_value(tooling_pn)}, {self.format_value(lcsc_pn)}, {self.format_value(lcsc_url)}, {self.format_value(mouser_pn)}, {self.format_value(mouser_url)}, {self.format_value(digikey_pn)}, {self.format_value(digikey_url)}, {self.format_value(farnell_pn)}, {self.format_value(farnell_url)}, {self.format_value(newark_pn)}, {self.format_value(newark_url)}, {self.format_value(rs_pn)}, {self.format_value(rs_url)}, {self.format_value(stock_qty)}, {self.format_value(min_stock)}, {self.format_value(max_stock)}, {self.format_value(stock_place)}, {self.format_value(price)}, {self.format_value(currency)}, {self.format_value(moq)}, {self.format_value(packaging)}, {self.format_value(datasheet)}, {self.format_value(drawing_2d)}, {self.format_value(drawing_3d)}, {self.format_value(cable_assembly_drawing)}, {self.format_value(tooling_documentation)}, {self.format_value(application_note)}, {active}, {self.format_value(notes)}, {self.format_value(tags)}, {self.format_value(created_by)}, {created_at}, {self.format_value(modified_by)}, {self.format_value(modified_at)}, {self.format_value(version)}, {exclude_from_bom}, {exclude_from_board})"""
        
        return values
    
    def generate_all_inserts(self):
        print("\n📝 Gerando comandos INSERT para IDC...")
        
        inserts = []
        inserts.append("-- Comandos INSERT para conectores IDC")
        inserts.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        inserts.append(f"-- Total de footprints: {len(self.idc_footprints)}")
        inserts.append("")
        inserts.append("-- Regras de símbolos:")
        inserts.append("--   - Sem MP: Connector_Generic:Conn_02xXX_Odd_Even")
        inserts.append("--   - Com MP: Connector_Generic_MountingPin:Conn_02xXX_Odd_Even_MountingPin")
        inserts.append("")
        
        inserts.append("INSERT INTO Connector_IDC (")
        inserts.append("    MyPN, Name, Description, Symbol, Footprint, Footprint_Filter, Package,")
        inserts.append("    Manufacturer, Manufacturer_PN, Series, Category, Subcategory,")
        inserts.append("    Connector_Type, Number_of_Contacts, Pitch_mm, Rows, Gender,")
        inserts.append("    Cable_Type, Cable_Compatibility, Cable_Width_Max_mm, Cable_Thickness_Max_mm,")
        inserts.append("    Wire_Gauge_AWG, Conductor_Size_mm, Insulation_Diameter_Max_mm, Strain_Relief, Strain_Relief_Type,")
        inserts.append("    Mounting_Type, Mounting_Style, Orientation, Locking_Mechanism, Polarization,")
        inserts.append("    Center_Polarization, Ejectors, Ejector_Type,")
        inserts.append("    Current_Rating_A, Voltage_Rating_V, Contact_Resistance_mOhm, Insulation_Resistance_MOhm,")
        inserts.append("    Dielectric_Withstanding_Voltage_V, Capacitance_pF,")
        inserts.append("    Contact_Material, Contact_Plating, Plating_Thickness_um, Contact_Finish, Contact_Design,")
        inserts.append("    Housing_Material, Housing_Color, Insulator_Material, Insulator_Color, Flammability_Rating,")
        inserts.append("    Length_mm, Width_mm, Height_mm, Height_above_PCB_mm, Mating_Height_mm, PCB_Mounting_Dimensions,")
        inserts.append("    Operating_Temp_Min_C, Operating_Temp_Max_C, Storage_Temp_Min_C, Storage_Temp_Max_C,")
        inserts.append("    Mating_Cycles, Insertion_Force_N, Withdrawal_Force_N,")
        inserts.append("    RoHS_Compliant, REACH_Compliant, UL_Certified, UL_File_Number, CSA_Certified,")
        inserts.append("    Termination, Termination_Process, Tooling_Required, Tooling_PN,")
        inserts.append("    LCSC_PN, LCSC_URL, Mouser_PN, Mouser_URL, Digikey_PN, Digikey_URL,")
        inserts.append("    Farnell_PN, Farnell_URL, Newark_PN, Newark_URL, RS_PN, RS_URL,")
        inserts.append("    StockQty, Min_Stock, Max_Stock, StockPlace, Price, Currency, MOQ, Packaging,")
        inserts.append("    Datasheet, Drawing_2D, Drawing_3D, Cable_Assembly_Drawing, Tooling_Documentation, Application_Note,")
        inserts.append("    Active, Notes, Tags, CreatedBy, CreatedAt, ModifiedBy, ModifiedAt, Version,")
        inserts.append("    Exclude_from_BOM, Exclude_from_Board")
        inserts.append(") VALUES")
        
        values_lines = []
        
        for i, fp in enumerate(self.idc_footprints, 1):
            try:
                data = self.parse_footprint(fp)
                values_line = self.generate_values_line(data)
                values_lines.append(values_line)
                
                if i % 20 == 0:
                    print(f"   ⏳ Processados {i}/{len(self.idc_footprints)} footprints...")
                    
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
        print("🔧 GERADOR DE INSERTS PARA CONECTORES IDC")
        print("=" * 60)
        
        if not self.read_csv_files():
            return False
        if not self.filter_idc_footprints():
            return False
        
        inserts = self.generate_all_inserts()
        
        if self.save_to_file(inserts):
            print(f"\n✅ Processo concluído com sucesso!")
            print(f"   📁 Verifique o arquivo: {self.output_file}")
            return True
        return False


def main():
    base_dir = Path(__file__).parent
    generator = IDCGenerator(
        symbol_file=str(base_dir / "simbolos_para_database_connectores.csv"),
        footprint_file=str(base_dir / "footprints_para_database_connectors.csv"),
        output_file=str(base_dir / "sqlite_commands_idc.txt")
    )
    generator.run()


if __name__ == "__main__":
    main()