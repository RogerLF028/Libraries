#!/usr/bin/env python3
"""
Setup_Database_Generator.py
Generates .kicad_dbl files by reading all tables from MyKiCadDatabase.sqlite
"""

import json
import sqlite3
import os
import sys
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class KiCadDBLGeneratorFromDB:
    """Generator for KiCad database library (.kicad_dbl) files from SQLite database"""
    
    # Default field configuration for all fields
    DEFAULT_FIELD_CONFIG = {
        "visible_on_add": False,
        "visible_in_chooser": False,
        "show_name": False,
        "inherit_properties": False
    }
    
    # Tables to exclude from the library (system tables)
    EXCLUDE_TABLES = ['sqlite_sequence', 'sqlite_master', 'sqlite_temp_master']
    
    def __init__(self, db_path: str, library_name: str = "My KiCad Database", 
                 description: str = "A database of electronic components for KiCAD"):
        """
        Initialize the generator
        
        Args:
            db_path: Full path to the SQLite database file
            library_name: Name of the library
            description: Description of the library
        """
        self.db_path = os.path.abspath(db_path)
        self.library_name = library_name
        self.description = description
        self.connection_string = f"Driver={{SQLite3 ODBC Driver}};Database={self.db_path}"
        
        # Verify database exists
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
    
    def get_all_tables(self) -> List[Tuple[str, List[str]]]:
        """
        Get all tables from the SQLite database
        
        Returns:
            List of tuples (table_name, list_of_columns)
        """
        tables = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all table names
            placeholders = ','.join(['?'] * len(self.EXCLUDE_TABLES))
            cursor.execute(f"""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT IN ({placeholders})
                ORDER BY name
            """, self.EXCLUDE_TABLES)
            
            table_names = [row[0] for row in cursor.fetchall()]
            
            # Get columns for each table
            for table_name in table_names:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]  # column name is at index 1
                tables.append((table_name, columns))
            
            conn.close()
            
        except sqlite3.Error as e:
            raise Exception(f"Error reading database: {e}")
        
        return tables
    
    def get_table_preview(self, table_name: str, limit: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get a preview row from a table to help determine field types
        
        Args:
            table_name: Name of the table
            limit: Number of rows to fetch
            
        Returns:
            First row of data or None if table is empty
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except sqlite3.Error:
            return None
    
    def format_library_name(self, table_name: str) -> str:
        """
        Format table name to be used as library name
        Keeps the original name with underscores
        
        Args:
            table_name: Original table name
            
        Returns:
            Library name (same as table name)
        """
        # Just remove quotes if present, keep everything else
        return table_name.strip('"')
    
    def generate_field_configs(self, table_name: str, columns: List[str]) -> List[Dict[str, Any]]:
        """
        Generate field configurations for all columns
        
        Args:
            table_name: Name of the table
            columns: List of column names
            
        Returns:
            List of field configuration dictionaries
        """
        fields = []
        
        # Get preview data (optional, not used for inherit_properties anymore)
        preview_data = self.get_table_preview(table_name)
        
        for column in columns:
            # Start with default configuration (all False)
            field_config = {
                "column": column,
                "name": column,
                **self.DEFAULT_FIELD_CONFIG
            }
            
            # Special handling for Value, Info1, Info2
            if column in ["Value", "Info1", "Info2"]:
                field_config["visible_on_add"] = True
                field_config["visible_in_chooser"] = True
                field_config["show_name"] = False
                # inherit_properties remains False (default)
            if column in ["Package"]:
                field_config["visible_on_add"] = False
                field_config["visible_in_chooser"] = False
                field_config["show_name"] = False
                field_config["inherit_properties"]= True
            
            # For all other columns, keep default (inherit_properties = False)
            
            fields.append(field_config)
        
        return fields
    
    def generate_properties_mapping(self, columns: List[str]) -> Dict[str, str]:
        """Generate properties mapping for KiCad"""
        properties = {}
        
        # Map standard KiCad properties to database columns
        property_mappings = {
            "description": ["Description", "Desc", "description", "DESC"],
            "datasheet": ["Datasheet", "DataSheet", "datasheet", "DS"],
            "footprint_filters": ["Footprint_Filter", "FootprintFilter", "footprint_filter", "Filter"],
            "keywords": ["Tags", "Keywords", "tags", "Tag"],
            "exclude_from_bom": ["Exclude_from_BOM", "ExcludeFromBOM", "exclude_from_bom", "NoBOM"],
            "exclude_from_board": ["Exclude_from_Board", "ExcludeFromBoard", "exclude_from_board", "NoBoard"]
        }
        
        for prop, possible_columns in property_mappings.items():
            for col in possible_columns:
                if col in columns:
                    properties[prop] = col
                    break
        
        return properties
    
    def generate_library_config(self, table_name: str, columns: List[str]) -> Dict[str, Any]:
        """
        Generate library configuration for a single table
        
        Args:
            table_name: Name of the table
            columns: List of column names
            
        Returns:
            Library configuration dictionary
        """
        # Determine key column (prefer MyPN, then ID, then first column)
        key_column = "MyPN" if "MyPN" in columns else \
                    "KeyId" if "KeyId" in columns else \
                    "ID" if "ID" in columns else \
                    columns[0]
        
        # Determine symbol column
        symbol_column = "Symbol" if "Symbol" in columns else \
                       "Symbols" if "Symbols" in columns else \
                       ""
        
        # Determine footprint column
        footprint_column = "Footprint" if "Footprint" in columns else \
                          "Footprints" if "Footprints" in columns else \
                          "Package" if "Package" in columns else \
                          ""
        
        return {
            "name": self.format_library_name(table_name),
            "table": table_name,
            "key": key_column,
            "symbols": symbol_column,
            "footprints": footprint_column,
            "fields": self.generate_field_configs(table_name, columns),
            "properties": self.generate_properties_mapping(columns)
        }
    
    def generate_dbl_file(self, output_file: Optional[str] = None, 
                         include_tables: Optional[List[str]] = None,
                         exclude_tables: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate the complete .kicad_dbl file content from the database
        
        Args:
            output_file: Optional output file path (if None, returns dict only)
            include_tables: Optional list of tables to include (if None, include all)
            exclude_tables: Optional list of tables to exclude
            
        Returns:
            Dictionary with the complete DBL configuration
        """
        # Get all tables
        all_tables = self.get_all_tables()
        
        if not all_tables:
            raise Exception("No tables found in database")
        
        # Filter tables
        libraries = []
        skipped_tables = []
        
        for table_name, columns in all_tables:
            # Apply include filter
            if include_tables and table_name not in include_tables:
                skipped_tables.append(f"{table_name} (excluded by include filter)")
                continue
            
            # Apply exclude filter
            if exclude_tables and table_name in exclude_tables:
                skipped_tables.append(f"{table_name} (explicitly excluded)")
                continue
            
            try:
                library_config = self.generate_library_config(table_name, columns)
                libraries.append(library_config)
                print(f"✓ Added table: {table_name} -> Library: {library_config['name']}")
            except Exception as e:
                print(f"✗ Error processing table {table_name}: {e}")
                skipped_tables.append(f"{table_name} (error: {e})")
        
        if skipped_tables:
            print(f"\nSkipped tables:")
            for skipped in skipped_tables:
                print(f"  - {skipped}")
        
        if not libraries:
            raise Exception("No valid tables found to include in library")
        
        print(f"\nTotal libraries generated: {len(libraries)}")
        
        dbl_config = {
            "meta": {
                "version": 0
            },
            "name": self.library_name,
            "description": self.description,
            "source": {
                "type": "odbc",
                "dsn": "",
                "username": "",
                "password": "",
                "timeout_seconds": 2,
                "connection_string": self.connection_string
            },
            "libraries": libraries
        }
        
        if output_file:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_file)) or '.', exist_ok=True)
            
            # Write to file with pretty formatting
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dbl_config, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Generated {output_file} successfully!")
            print(f"   Database: {self.db_path}")
            print(f"   Tables included: {len(libraries)}")
        
        return dbl_config
    
    def list_tables(self) -> None:
        """List all tables in the database with their column counts"""
        tables = self.get_all_tables()
        
        print(f"\nTables in database: {self.db_path}")
        print("-" * 50)
        for table_name, columns in tables:
            print(f"  {table_name}: {len(columns)} columns")
            # Show first few columns as preview
            col_preview = ', '.join(columns[:5])
            if len(columns) > 5:
                col_preview += f" ... (+{len(columns)-5})"
            print(f"    Columns: {col_preview}")
        print("-" * 50)
        print(f"Total tables: {len(tables)}")


def get_project_paths():
    """
    Get all relevant paths based on the script location
    Returns a dictionary with all paths
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate up to the PyGen folder
    # script_dir = .../Libraries/PyGen/Setup_Database_Generator/
    pygen_dir = os.path.dirname(script_dir)  # .../Libraries/PyGen/
    libraries_dir = os.path.dirname(pygen_dir)  # .../Libraries/
    
    # Define all paths
    paths = {
        'script_dir': script_dir,
        'pygen_dir': pygen_dir,
        'libraries_dir': libraries_dir,
        'database_setup_dir': os.path.join(libraries_dir, 'Database_Setup'),
        'database_file': os.path.join(libraries_dir, 'Library', '1_Database_Library', 'MyKiCadLibDatabase.sqlite')
    }
    
    return paths


def generate_output_filename(base_name="MyKiCadDatabaseSetup"):
    """
    Generate a unique output filename with timestamp to avoid overwriting
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.kicad_dbl"


def main():
    """Main entry point"""
    # Get all project paths
    paths = get_project_paths()
    
    print("=" * 60)
    print("Setup_Database_Generator.py")
    print("=" * 60)
    print(f"Script location: {paths['script_dir']}")
    print(f"Libraries directory: {paths['libraries_dir']}")
    print(f"Database file: {paths['database_file']}")
    print(f"Output directory: {paths['database_setup_dir']}")
    print("-" * 60)
    
    # Check if database exists
    if not os.path.exists(paths['database_file']):
        print(f"❌ ERROR: Database file not found at:")
        print(f"   {paths['database_file']}")
        print("\nPlease ensure the file exists at the expected location.")
        return 1
    
    # Ensure output directory exists
    os.makedirs(paths['database_setup_dir'], exist_ok=True)
    
    # Generate output filename with timestamp
    output_filename = generate_output_filename()
    output_path = os.path.join(paths['database_setup_dir'], output_filename)
    
    print(f"\n📁 Output file: {output_path}")
    print("-" * 60)
    
    try:
        # Create generator
        generator = KiCadDBLGeneratorFromDB(
            db_path=paths['database_file'],
            library_name="My KiCad Database Library",
            description="Database library for electronic components"
        )
        
        # First, list all tables found
        print("\n📊 Reading database tables...")
        tables = generator.get_all_tables()
        print(f"Found {len(tables)} tables:")
        for table_name, columns in tables[:10]:  # Show first 10
            print(f"  - {table_name} ({len(columns)} columns)")
        if len(tables) > 10:
            print(f"  ... and {len(tables) - 10} more")
        
        # Generate DBL file
        print("\n⚙️ Generating KiCad DBL file...")
        generator.generate_dbl_file(
            output_file=output_path
        )
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"\nGenerated file: {output_path}")
        print("\nNext steps:")
        print("1. In KiCad, go to Preferences → Configure Paths")
        print("2. Add a path variable pointing to your Libraries folder")
        print("3. In Schematic Editor, go to Preferences → Manage Symbol Libraries")
        print("4. Add the generated .kicad_dbl file as a new library")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())