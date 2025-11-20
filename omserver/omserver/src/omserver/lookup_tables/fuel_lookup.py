import pandas as pd
import os
from pathlib import Path

class FuelPropertiesLookup:
    """
    Utility class to load and query fuel properties from CSV lookup tables.
    Handles fuel property lookups for emission calculations based on EU regulations.
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.fuel_properties_df = None
        self.load_tables()
    
    def load_tables(self):
        """Load all CSV lookup tables into pandas DataFrames"""
        try:
            # Load fuel properties table
            fuel_properties_path = self.base_path / 'fuel_properties.csv'
            if fuel_properties_path.exists():
                self.fuel_properties_df = pd.read_csv(fuel_properties_path)
                # Set pathway_name as index for faster lookups
                self.fuel_properties_df.set_index('pathway_name', inplace=True)
                print(f"Loaded fuel properties table with {len(self.fuel_properties_df)} fuel types")
            else:
                raise FileNotFoundError(f"Fuel properties CSV not found at {fuel_properties_path}")
                
        except Exception as e:
            print(f"Error loading lookup tables: {e}")
            # Initialize empty DataFrame as fallback
            self.fuel_properties_df = pd.DataFrame()
    
    def get_fuel_properties(self, pathway_name):
        """
        Get all properties for a specific fuel pathway
        
        Args:
            pathway_name (str): Name of the fuel pathway (e.g., "HFO (Grades RME to RMK)")
            
        Returns:
            dict: Dictionary containing all fuel properties, or None if not found
        """
        if self.fuel_properties_df is None or self.fuel_properties_df.empty:
            return None
            
        try:
            if pathway_name in self.fuel_properties_df.index:
                properties = self.fuel_properties_df.loc[pathway_name].to_dict()
                # Convert any NaN values to 0 or appropriate defaults
                for key, value in properties.items():
                    if pd.isna(value):
                        properties[key] = 0.0
                return properties
            else:
                print(f"Fuel pathway '{pathway_name}' not found in lookup table")
                return None
        except Exception as e:
            print(f"Error retrieving fuel properties for '{pathway_name}': {e}")
            return None
    
    def get_available_fuels(self):
        """
        Get list of all available fuel pathway names
        
        Returns:
            list: List of available fuel pathway names
        """
        if self.fuel_properties_df is None or self.fuel_properties_df.empty:
            return []
        return self.fuel_properties_df.index.tolist()
    
    def get_fuel_property(self, pathway_name, property_name):
        """
        Get a specific property value for a fuel pathway
        
        Args:
            pathway_name (str): Name of the fuel pathway
            property_name (str): Name of the property (e.g., 'lcv_mj_per_g')
            
        Returns:
            float: Property value, or None if not found
        """
        properties = self.get_fuel_properties(pathway_name)
        if properties and property_name in properties:
            return properties[property_name]
        return None
    
    def search_fuels(self, search_term):
        """
        Search for fuel pathways containing the search term
        
        Args:
            search_term (str): Term to search for in pathway names
            
        Returns:
            list: List of matching fuel pathway names
        """
        if self.fuel_properties_df is None or self.fuel_properties_df.empty:
            return []
            
        matching_fuels = []
        for fuel_name in self.fuel_properties_df.index:
            if search_term.lower() in fuel_name.lower():
                matching_fuels.append(fuel_name)
        return matching_fuels

# Global instance for easy access
fuel_lookup = FuelPropertiesLookup()

# Convenience functions for direct access
def get_fuel_properties(pathway_name):
    """Get all properties for a fuel pathway"""
    return fuel_lookup.get_fuel_properties(pathway_name)

def get_fuel_property(pathway_name, property_name):
    """Get a specific property for a fuel pathway"""
    return fuel_lookup.get_fuel_property(pathway_name, property_name)

def get_available_fuels():
    """Get list of all available fuel pathways"""
    return fuel_lookup.get_available_fuels()

def search_fuels(search_term):
    """Search for fuel pathways"""
    return fuel_lookup.search_fuels(search_term) 