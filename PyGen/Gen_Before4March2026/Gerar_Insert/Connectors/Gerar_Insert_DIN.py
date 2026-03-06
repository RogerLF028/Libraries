#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de comandos SQLite para conectores DIN 41612
Arquivo: Gerar_Insert/gerar_insert_din.py
"""

import csv
import re
from pathlib import Path
from datetime import datetime

class DINGenerator:
    def __init__(self, symbol_file, footprint_file, output_file):
        self.symbol_file = symbol_file
        self.footprint_file = footprint_file
        self.output_file = output_file
        self.footprints = []
        self.symbols_dict = {}
        self.din_footprints = []
        self.counter = 700000
        
    def read_csv_files(self):
        print("📖 Lendo arquivos CSV...")
        
        # Ler símbolos
        try:
            with open(self.symbol_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    symbol_name = row['Database_Symbol']
                    self.symbols_dict[symbol_name] = row
            print(f"   ✅ {len(self.symbols_dict)} símbolos carregados")
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
    
    def filter_din_footprints(self):
        print("\n🔍 Filtrando footprints DIN 41612...")
        
        for fp in self.footprints:
            if 'DIN41612' in fp:
                self.din_footprints.append(fp)
        
        print(f"   ✅ {len(self.din_footprints)} footprints DIN 41612 encontrados")
        return True
    
    def get_symbol_name(self, rows, columns):
        """
        Retorna o nome do símbolo baseado nas regras da imagem:
        - DIN41612_01x32, DIN41612_02x05, DIN41612_02x08, etc.
        Todos na biblioteca myLib_Connector
        """
        rows_str = str(rows)
        cols_str = str(columns)
        
        # Formata o nome do símbolo conforme a lista da imagem
        # Formato: DIN41612_0XxYY (com zero à esquerda para rows)
        return f"myLib_Connector:DIN41612_{rows_str.zfill(2)}x{cols_str}"
    
    def parse_footprint(self, name):
        """Parse footprints de conectores DIN 41612"""
        data = {
            'footprint': name,  # Valor direto do CSV
            'standard': 'DIN 41612',
            'gender': 'Female',
            'orientation': 'Vertical',
            'rows': 2,
            'columns': 16,
            'total_pins': 32,
            'shell_style': 'Straight',
            'mounting_type': 'PCB',
            'mounting_style': 'Through Hole',
            'coding': None
        }
        
        # Extrair série (B, C, R, Q, etc) - pode ser útil para nome, mas não para símbolo
        series_match = re.search(r'DIN41612_([A-Z]+)[-_]', name)
        if series_match:
            data['series'] = series_match.group(1)
        
        # Extrair configuração (2x16, 3x32, etc)
        config_match = re.search(r'(\d+)x(\d+)', name)
        if config_match:
            data['rows'] = int(config_match.group(1))
            data['columns'] = int(config_match.group(2))
            data['total_pins'] = data['rows'] * data['columns']
        
        # Configurações especiais tipo "3x14+6"
        special_match = re.search(r'(\d+)x(\d+)\+(\d+)', name)
        if special_match:
            data['rows'] = int(special_match.group(1))
            data['columns'] = int(special_match.group(2))
            data['extra_pins'] = int(special_match.group(3))
            data['total_pins'] = (data['rows'] * data['columns']) + data['extra_pins']
            data['pin_configuration'] = f"{data['rows']}x{data['columns']}+{data['extra_pins']}"
        
        # Gender
        if 'Female' in name:
            data['gender'] = 'Female'
        elif 'Male' in name:
            data['gender'] = 'Male'
        
        # Orientação
        if 'Vertical' in name:
            data['orientation'] = 'Vertical'
        elif 'Horizontal' in name:
            data['orientation'] = 'Horizontal'
        
        # Shell style
        if 'flat' in name.lower():
            data['shell_style'] = 'Flat'
        elif 'invers' in name.lower():
            data['shell_style'] = 'Inverse'
        
        # Determinar símbolo baseado nas regras
        data['symbol'] = self.get_symbol_name(data['rows'], data['columns'])
        
        return data
    
    def generate_my_pn(self):
        self.counter += 1
        return f"EL-CON_{self.counter:06d}"
    
    def generate_name(self, data):
        """Gera nome no formato CON_DIN41612_{config}_{gender}_{orientation}_{style}"""
        
        # Configuração (2x16, 3x32, ou 3x14+6, etc)
        if 'pin_configuration' in data:
            config = data['pin_configuration']  # já vem como "3x14+6"
        else:
            config = f"{data['rows']}x{data['columns']}"
        
        # Gênero: F ou M
        gender = 'F' if data['gender'] == 'Female' else 'M'
        
        # Orientação: V ou H
        orient = 'V' if data['orientation'] == 'Vertical' else 'H'
        
        # Estilo do shell (se não for Straight)
        style = ''
        if data['shell_style'] != 'Straight':
            style = f"_{data['shell_style'].lower()}"
        
        return f"CON_DIN41612_{config}_{gender}_{orient}{style}"

    def format_value(self, value):
        if value is None:
            return 'NULL'
        if isinstance(value, str):
            return f"'{value}'"
        return str(value)
    
    def generate_values_line(self, data):
        """Gera uma linha de VALUES para Connector_DIN"""
        
        my_pn = self.generate_my_pn()
        name = self.generate_name(data)
        
        if 'pin_configuration' in data:
            description = f"DIN 41612 {data.get('series', 'C')} Series, {data['gender']} connector, {data['pin_configuration']} configuration, {data['total_pins']} pins, {data['orientation']}"
        else:
            description = f"DIN 41612 {data.get('series', 'C')} Series, {data['gender']} connector, {data['rows']} rows x {data['columns']} columns, {data['total_pins']} pins, {data['orientation']}"
        
        # Usar símbolo determinado pelas regras
        symbol = data.get('symbol')
        
        # Footprint é o valor direto do CSV
        footprint = data['footprint']
        
        footprint_filter = f"*DIN41612*{data.get('series', 'C')}*{data['rows']}x{data['columns']}*{data['gender']}*{data['orientation']}*"
        
        # Valores básicos
        package = 'THT'
        manufacturer = 'Various'
        manufacturer_pn = None
        series = f"DIN 41612 {data.get('series', 'C')}"
        category = 'DIN 41612 Connector'
        subcategory = f"Series {data.get('series', 'C')}"
        
        # Campos que NÃO podemos extrair - todos NULL
        standard = 'DIN 41612'
        shell_style = data['shell_style']
        shell_size = f"{data['rows']}x{data['columns']}"
        shell_design = None
        coupling = None
        number_of_pins = data['total_pins']
        pin_configuration = data.get('pin_configuration', f"{data['rows']}x{data['columns']}")
        contact_gender = data['gender']
        contact_arrangement = None
        insert_arrangement = None
        mounting_type = data['mounting_type']
        mounting_style = data['mounting_style']
        orientation = data['orientation']
        polarization = None
        coding = None
        anti_rotation = 0
        shell_material = None
        shell_plating = None
        shell_finish = None
        shell_color = None
        backshell_type = None
        backshell_material = None
        grommet_material = None
        contact_type = None
        contact_material = None
        contact_plating = None
        plating_thickness_um = None
        contact_size = None
        contact_finish = None
        current_rating_a = None
        current_rating_power_a = None
        current_rating_signal_a = None
        voltage_rating_v = None
        voltage_rating_power_v = None
        voltage_rating_signal_v = None
        contact_resistance_mohm = None
        insulation_resistance_mohm = None
        dielectric_withstanding_voltage_v = None
        impedance_ohm = None
        frequency_max_hz = None
        ip_rating = None
        ingress_protection_mated = None
        ingress_protection_unmated = None
        operating_temp_min_c = None
        operating_temp_max_c = None
        storage_temp_min_c = None
        storage_temp_max_c = None
        corrosion_resistance = None
        shock_rating = None
        vibration_rating = None
        length_mm = None
        width_mm = None
        height_mm = None
        diameter_mm = None
        panel_cutout_mm = None
        mounting_hole_pattern = None
        thread_size = None
        mating_thread_size = None
        cable_entry_size = None
        cable_diameter_min_mm = None
        cable_diameter_max_mm = None
        cable_type = None
        cable_length_m = None
        cable_gauge_awg = None
        cable_color = None
        shielded_cable = 0
        cable_flexing_cycles = None
        bending_radius_mm = None
        mating_cycles = None
        insertion_force_n = None
        withdrawal_force_n = None
        locking_force_n = None
        unlocking_force_n = None
        insulator_material = None
        insulator_color = None
        flammability_rating = None
        rohs_compliant = None
        reach_compliant = None
        ul_certified = None
        ul_file_number = None
        csa_certified = None
        vde_certified = None
        ce_compliant = None
        dnv_gl_certified = None
        atex_certified = None
        iecex_certified = None
        mating_connector_pn = None
        dust_cap_available = 0
        dust_cap_pn = None
        sealing_cap_available = 0
        sealing_cap_pn = None
        gasket_included = 0
        gasket_pn = None
        mounting_nut_included = 0
        mounting_nut_pn = None
        o_ring_included = 0
        o_ring_size = None
        termination_tool = None
        termination_tool_pn = None
        assembly_instructions = None
        crimp_specifications = None
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
        supplier = None
        datasheet = None
        drawing_2d = None
        drawing_3d = None
        panel_cutout_drawing = None
        certification_documents = None
        application_note = None
        active = 1
        notes = None
        tags = f"din41612,connector,{data.get('series', 'C')} series,{data['rows']}row,{data['columns']}col"
        created_by = 'script'
        created_at = "datetime('now')"
        modified_by = None
        modified_at = None
        version = '1.0'
        exclude_from_bom = 0
        exclude_from_board = 0
        
        # Montar VALUES
        values = f"""    ({self.format_value(my_pn)}, {self.format_value(name)}, {self.format_value(description)}, {self.format_value(symbol)}, {self.format_value(footprint)}, {self.format_value(footprint_filter)}, {self.format_value(package)}, {self.format_value(manufacturer)}, {self.format_value(manufacturer_pn)}, {self.format_value(series)}, {self.format_value(category)}, {self.format_value(subcategory)}, {self.format_value(standard)}, {self.format_value(shell_style)}, {self.format_value(shell_size)}, {self.format_value(shell_design)}, {self.format_value(coupling)}, {number_of_pins}, {self.format_value(pin_configuration)}, {self.format_value(contact_gender)}, {self.format_value(contact_arrangement)}, {self.format_value(insert_arrangement)}, {self.format_value(mounting_type)}, {self.format_value(mounting_style)}, {self.format_value(orientation)}, {self.format_value(polarization)}, {self.format_value(coding)}, {anti_rotation}, {self.format_value(shell_material)}, {self.format_value(shell_plating)}, {self.format_value(shell_finish)}, {self.format_value(shell_color)}, {self.format_value(backshell_type)}, {self.format_value(backshell_material)}, {self.format_value(grommet_material)}, {self.format_value(contact_type)}, {self.format_value(contact_material)}, {self.format_value(contact_plating)}, {self.format_value(plating_thickness_um)}, {self.format_value(contact_size)}, {self.format_value(contact_finish)}, {self.format_value(current_rating_a)}, {self.format_value(current_rating_power_a)}, {self.format_value(current_rating_signal_a)}, {self.format_value(voltage_rating_v)}, {self.format_value(voltage_rating_power_v)}, {self.format_value(voltage_rating_signal_v)}, {self.format_value(contact_resistance_mohm)}, {self.format_value(insulation_resistance_mohm)}, {self.format_value(dielectric_withstanding_voltage_v)}, {self.format_value(impedance_ohm)}, {self.format_value(frequency_max_hz)}, {self.format_value(ip_rating)}, {self.format_value(ingress_protection_mated)}, {self.format_value(ingress_protection_unmated)}, {self.format_value(operating_temp_min_c)}, {self.format_value(operating_temp_max_c)}, {self.format_value(storage_temp_min_c)}, {self.format_value(storage_temp_max_c)}, {self.format_value(corrosion_resistance)}, {self.format_value(shock_rating)}, {self.format_value(vibration_rating)}, {self.format_value(length_mm)}, {self.format_value(width_mm)}, {self.format_value(height_mm)}, {self.format_value(diameter_mm)}, {self.format_value(panel_cutout_mm)}, {self.format_value(mounting_hole_pattern)}, {self.format_value(thread_size)}, {self.format_value(mating_thread_size)}, {self.format_value(cable_entry_size)}, {self.format_value(cable_diameter_min_mm)}, {self.format_value(cable_diameter_max_mm)}, {self.format_value(cable_type)}, {self.format_value(cable_length_m)}, {self.format_value(cable_gauge_awg)}, {self.format_value(cable_color)}, {shielded_cable}, {self.format_value(cable_flexing_cycles)}, {self.format_value(bending_radius_mm)}, {self.format_value(mating_cycles)}, {self.format_value(insertion_force_n)}, {self.format_value(withdrawal_force_n)}, {self.format_value(locking_force_n)}, {self.format_value(unlocking_force_n)}, {self.format_value(insulator_material)}, {self.format_value(insulator_color)}, {self.format_value(flammability_rating)}, {self.format_value(rohs_compliant)}, {self.format_value(reach_compliant)}, {self.format_value(ul_certified)}, {self.format_value(ul_file_number)}, {self.format_value(csa_certified)}, {self.format_value(vde_certified)}, {self.format_value(ce_compliant)}, {self.format_value(dnv_gl_certified)}, {self.format_value(atex_certified)}, {self.format_value(iecex_certified)}, {self.format_value(mating_connector_pn)}, {dust_cap_available}, {self.format_value(dust_cap_pn)}, {sealing_cap_available}, {self.format_value(sealing_cap_pn)}, {gasket_included}, {self.format_value(gasket_pn)}, {mounting_nut_included}, {self.format_value(mounting_nut_pn)}, {o_ring_included}, {self.format_value(o_ring_size)}, {self.format_value(termination_tool)}, {self.format_value(termination_tool_pn)}, {self.format_value(assembly_instructions)}, {self.format_value(crimp_specifications)}, {self.format_value(lcsc_pn)}, {self.format_value(lcsc_url)}, {self.format_value(mouser_pn)}, {self.format_value(mouser_url)}, {self.format_value(digikey_pn)}, {self.format_value(digikey_url)}, {self.format_value(farnell_pn)}, {self.format_value(farnell_url)}, {self.format_value(newark_pn)}, {self.format_value(newark_url)}, {self.format_value(rs_pn)}, {self.format_value(rs_url)}, {self.format_value(stock_qty)}, {self.format_value(min_stock)}, {self.format_value(max_stock)}, {self.format_value(stock_place)}, {self.format_value(price)}, {self.format_value(currency)}, {self.format_value(moq)}, {self.format_value(packaging)}, {self.format_value(supplier)}, {self.format_value(datasheet)}, {self.format_value(drawing_2d)}, {self.format_value(drawing_3d)}, {self.format_value(panel_cutout_drawing)}, {self.format_value(certification_documents)}, {self.format_value(application_note)}, {active}, {self.format_value(notes)}, {self.format_value(tags)}, {self.format_value(created_by)}, {created_at}, {self.format_value(modified_by)}, {self.format_value(modified_at)}, {self.format_value(version)}, {exclude_from_bom}, {exclude_from_board})"""
        
        return values
    
    def generate_all_inserts(self):
        print("\n📝 Gerando comandos INSERT para DIN 41612...")
        
        inserts = []
        inserts.append("-- Comandos INSERT para conectores DIN 41612")
        inserts.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        inserts.append(f"-- Total de footprints: {len(self.din_footprints)}")
        inserts.append("")
        inserts.append("-- Regras de símbolos:")
        inserts.append("--   - 3x32 → Connector:DIN41612_03x32_C_Split")
        inserts.append("--   - Demais → Connector:DIN41612_XXxYY_AB")
        inserts.append("")
        
        inserts.append("INSERT INTO Connector_DIN (")
        inserts.append("    MyPN, Name, Description, Symbol, Footprint, Footprint_Filter, Package,")
        inserts.append("    Manufacturer, Manufacturer_PN, Series, Category, Subcategory,")
        inserts.append("    Standard, Shell_Style, Shell_Size, Shell_Design, Coupling,")
        inserts.append("    Number_of_Pins, Pin_Configuration, Contact_Gender, Contact_Arrangement, Insert_Arrangement,")
        inserts.append("    Mounting_Type, Mounting_Style, Orientation, Polarization, Coding, Anti_Rotation,")
        inserts.append("    Shell_Material, Shell_Plating, Shell_Finish, Shell_Color,")
        inserts.append("    Backshell_Type, Backshell_Material, Grommet_Material,")
        inserts.append("    Contact_Type, Contact_Material, Contact_Plating, Plating_Thickness_um, Contact_Size, Contact_Finish,")
        inserts.append("    Current_Rating_A, Current_Rating_Power_A, Current_Rating_Signal_A,")
        inserts.append("    Voltage_Rating_V, Voltage_Rating_Power_V, Voltage_Rating_Signal_V,")
        inserts.append("    Contact_Resistance_mOhm, Insulation_Resistance_MOhm, Dielectric_Withstanding_Voltage_V,")
        inserts.append("    Impedance_Ohm, Frequency_Max_Hz,")
        inserts.append("    IP_Rating, Ingress_Protection_Mated, Ingress_Protection_Unmated,")
        inserts.append("    Operating_Temp_Min_C, Operating_Temp_Max_C, Storage_Temp_Min_C, Storage_Temp_Max_C,")
        inserts.append("    Corrosion_Resistance, Shock_Rating, Vibration_Rating,")
        inserts.append("    Length_mm, Width_mm, Height_mm, Diameter_mm, Panel_Cutout_mm, Mounting_Hole_Pattern,")
        inserts.append("    Thread_Size, Mating_Thread_Size, Cable_Entry_Size, Cable_Diameter_Min_mm, Cable_Diameter_Max_mm,")
        inserts.append("    Cable_Type, Cable_Length_m, Cable_Gauge_AWG, Cable_Color, Shielded_Cable, Cable_Flexing_Cycles, Bending_Radius_mm,")
        inserts.append("    Mating_Cycles, Insertion_Force_N, Withdrawal_Force_N, Locking_Force_N, Unlocking_Force_N,")
        inserts.append("    Insulator_Material, Insulator_Color, Flammability_Rating,")
        inserts.append("    RoHS_Compliant, REACH_Compliant, UL_Certified, UL_File_Number, CSA_Certified, VDE_Certified, CE_Compliant,")
        inserts.append("    DNV_GL_Certified, ATEX_Certified, IECEx_Certified,")
        inserts.append("    Mating_Connector_PN, Dust_Cap_Available, Dust_Cap_PN, Sealing_Cap_Available, Sealing_Cap_PN,")
        inserts.append("    Gasket_Included, Gasket_PN, Mounting_Nut_Included, Mounting_Nut_PN, O_Ring_Included, O_Ring_Size,")
        inserts.append("    Termination_Tool, Termination_Tool_PN, Assembly_Instructions, Crimp_Specifications,")
        inserts.append("    LCSC_PN, LCSC_URL, Mouser_PN, Mouser_URL, Digikey_PN, Digikey_URL,")
        inserts.append("    Farnell_PN, Farnell_URL, Newark_PN, Newark_URL, RS_PN, RS_URL,")
        inserts.append("    StockQty, Min_Stock, Max_Stock, StockPlace, Price, Currency, MOQ, Packaging, Supplier,")
        inserts.append("    Datasheet, Drawing_2D, Drawing_3D, Panel_Cutout_Drawing, Certification_Documents, Application_Note,")
        inserts.append("    Active, Notes, Tags, CreatedBy, CreatedAt, ModifiedBy, ModifiedAt, Version,")
        inserts.append("    Exclude_from_BOM, Exclude_from_Board")
        inserts.append(") VALUES")
        
        values_lines = []
        
        for i, fp in enumerate(self.din_footprints, 1):
            try:
                data = self.parse_footprint(fp)
                values_line = self.generate_values_line(data)
                values_lines.append(values_line)
                
                if i % 10 == 0:
                    print(f"   ⏳ Processados {i}/{len(self.din_footprints)} footprints...")
                    
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
        print("🔧 GERADOR DE INSERTS PARA CONECTORES DIN 41612")
        print("=" * 60)
        
        if not self.read_csv_files():
            return False
        if not self.filter_din_footprints():
            return False
        
        inserts = self.generate_all_inserts()
        
        if self.save_to_file(inserts):
            print(f"\n✅ Processo concluído com sucesso!")
            print(f"   📁 Verifique o arquivo: {self.output_file}")
            return True
        return False


def main():
    base_dir = Path(__file__).parent
    generator = DINGenerator(
        symbol_file=str(base_dir / "simbolos_para_database_connectores.csv"),
        footprint_file=str(base_dir / "footprints_para_database_connectors.csv"),
        output_file=str(base_dir / "sqlite_commands_din.txt")
    )
    generator.run()


if __name__ == "__main__":
    main()