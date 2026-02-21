import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tables_file = os.path.join(script_dir, "Tables_names.txt")

    if not os.path.isfile(tables_file):
        print(f"Erro: Arquivo {tables_file} não encontrado.")
        return

    table_names = []
    with open(tables_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                table_names.append(line)

    if not table_names:
        print("Nenhum nome de tabela encontrado.")
        return

    # Definição das colunas (igual à versão anterior, sem comentários)
    columns = [
        "ID_Aux INTEGER PRIMARY KEY ",
        "MyPN TEXT NOT NULL UNIQUE",
        "Name TEXT NOT NULL",
        "Description TEXT",
        "Value TEXT",
        "Info1 TEXT",
        "Info2 TEXT",
        "Symbol TEXT",
        "Footprint TEXT",
        "Footprint_Filter TEXT",
        "Datasheet TEXT",
        "Notes TEXT",
        "Notes_to_Buyer TEXT",
        "Manufacturer TEXT",
        "Manufacturer_PN TEXT",
        "Manufacturer_URL TEXT",
        "Alternative_PN TEXT",
        "Alternative_URL TEXT",
        "Digikey_PN TEXT",
        "Digikey_URL TEXT",
        "Mouser_PN TEXT",
        "Mouser_URL TEXT",
        "LCSC_PN TEXT",
        "LCSC_URL TEXT",
        "Stock_Qty INTEGER DEFAULT 0",
        "Stock_Location TEXT",
        "Stock_Unit TEXT",
        "Price TEXT",
        "Currency TEXT DEFAULT 'USD'",
        "Min_Stock INTEGER DEFAULT 0",
        "Max_Stock INTEGER DEFAULT 0",
        "Last_Purchase_Date TEXT",
        "Last_Purchase_Price TEXT",
        "Active INTEGER DEFAULT 1",
        "Version INTEGER DEFAULT 1",
        "Created_At TEXT",
        "Created_By TEXT",
        "Modified_At TEXT",
        "Modified_By TEXT",
        "Exclude_from_BOM INTEGER DEFAULT 0",
        "Exclude_from_Board INTEGER DEFAULT 0",
        "Category TEXT",
        "Subcategory TEXT",
        "Family_Series TEXT",
        "Package TEXT",
        "Mount TEXT",
        "Dimensions TEXT",
        "Temperature_Range TEXT",
        "REACH_Compliant TEXT",
        "RoHS_Compliant TEXT",
        "Unit TEXT",
        "Tolerance TEXT",
        "Voltage_Rating TEXT",
        "Current_Rating TEXT",
        "Power_Rating TEXT",
        "Temperature_Coefficient TEXT",
        "Pin_Configuration TEXT",
        "Gender TEXT",
        "Pin_Type TEXT",
        "Pitch TEXT",
        "Orientation TEXT",
        "Locking_Mechanism TEXT",
        "Current_Rating_Per_Pin TEXT",
        "IP_Rating TEXT",
        "Wire_Gauge TEXT",
        "Termination_Style TEXT",
        "Resistance TEXT",
        "Technology_Material TEXT",
        "Capacitance TEXT",
        "Dielectric_Type TEXT",
        "ESR TEXT",
        "Ripple_Current TEXT",
        "Leakage_Current TEXT",
        "Inductance TEXT",
        "DC_Resistance TEXT",
        "Self_Resonant_Frequency TEXT",
        "Quality_Factor_Q TEXT",
        "Saturation_Current TEXT",
        "Hold_Current TEXT",
        "Trip_Current TEXT",
        "Interrupting_Rating TEXT",
        "Response_Time TEXT",
        "Forward_Voltage TEXT",
        "Reverse_Leakage TEXT",
        "Junction_Capacitance TEXT",
        "Reverse_Recovery_Time TEXT",
        "Zener_Voltage TEXT",
        "Zener_Impedance TEXT",
        "Reverse_Standoff_Voltage TEXT",
        "Breakdown_Voltage TEXT",
        "Clamping_Voltage TEXT",
        "Peak_Pulse_Current TEXT",
        "Q_Type TEXT",
        "Polarity_Channel_Type TEXT",
        "Power_Dissipation TEXT",
        "Junction_Temperature TEXT",
        "VDS_Max TEXT",
        "VGS_Max TEXT",
        "VGS_Threshold TEXT",
        "RDS_On TEXT",
        "ID_Continuous TEXT",
        "ID_Pulse TEXT",
        "Input_Capacitance TEXT",
        "Output_Capacitance TEXT",
        "Reverse_Transfer_Capacitance TEXT",
        "Gate_Charge TEXT",
        "Rise_Time TEXT",
        "Fall_Time TEXT",
        "IDSS TEXT",
        "VGS_Off TEXT",
        "Gain TEXT",
        "Gate_Reverse_Current TEXT",
        "VCEO TEXT",
        "Current_Collector TEXT",
        "DC_Gain_HFE TEXT",
        "Saturation_Voltage TEXT",
        "Transition_Frequency TEXT",
        "VCE_Sat TEXT",
        "IC_Continuous TEXT",
        "IC_Pulse TEXT",
        "VGE_Threshold TEXT",
        "Short_Circuit_Withstanding TEXT",
        "Diode_Forward_Voltage TEXT",
        "Frequency TEXT",
        "Oscillator_Type TEXT",
        "Load_Capacitance TEXT",
        "Supply_Voltage TEXT",
        "Coil_Voltage TEXT",
        "Coil_Resistance TEXT",
        "Contact_Configuration TEXT",
        "Contact_Current_Rating TEXT",
        "Contact_Voltage_Rating TEXT",
        "Relay_Type TEXT",
        "Operating_Time TEXT",
        "Transformer_Type TEXT",
        "Turns_Ratio TEXT",
        "Isolation_Voltage TEXT",
        "Power_Rating_VA TEXT",
        "Frequency_Rating TEXT",
        "Battery_Chemistry TEXT",
        "Battery_Voltage_Nominal TEXT",
        "Battery_Capacity TEXT",
        "Battery_Size TEXT",
        "Rechargeable INTEGER",
        "Number_of_Cells INTEGER",
        "Display_Type TEXT",
        "Display_Size TEXT",
        "Resolution TEXT",
        "Interface TEXT",
        "Backlight INTEGER",
        "Controller TEXT",
        "Color TEXT",
        "Sensor_Type TEXT",
        "Sensor_Interface TEXT",
        "Supply_Voltage_Min TEXT",
        "Supply_Voltage_Max TEXT",
        "Accuracy TEXT",
        "Output_Type TEXT",
        "LED_Color TEXT",
        "Luminous_Intensity TEXT",
        "Wavelength TEXT",
        "Viewing_Angle_LED TEXT",
        "Lens_Type TEXT",
        "If_Current TEXT",
        "VF_Typical TEXT",
        "Optocoupler_Type TEXT",
        "CTR TEXT",
        "Tube_Type TEXT",
        "Heater_Voltage TEXT",
        "Heater_Current TEXT",
        "Plate_Voltage_Max TEXT"
    ]

    # Índices base (sem o nome da tabela)
    base_indexes = [
        ("idx_my_pn", "MyPN"),
        ("idx_name", "Name"),
    ]

    output_file = os.path.join(script_dir, "create_tables.sqlite")

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("-- Script de criação de tabelas para SQLite\n")
        out.write("-- Gerado automaticamente a partir da lista de tabelas\n\n")

        for table in table_names:
            # Cria a tabela
            out.write(f"CREATE TABLE {table} (\n")
            for i, col in enumerate(columns):
                comma = "," if i < len(columns) - 1 else ""
                out.write(f"    {col}{comma}\n")
            out.write(");\n\n")

            # Cria os índices com nomes únicos (incluindo o nome da tabela)
            for base_name, col in base_indexes:
                index_name = f"{base_name}_{table}"
                out.write(f"CREATE INDEX {index_name} ON {table} ({col});\n")
            out.write("\n")

    print(f"Arquivo gerado com sucesso: {output_file}")

if __name__ == "__main__":
    main()