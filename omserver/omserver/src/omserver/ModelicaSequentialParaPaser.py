from pathlib import Path
from flask import current_app
import re 

class ModelicaSequentialParamParser:
 
    
    def __init__(self, modelName, bsfc_list, fuelConsumptionTable, gen_is_on_list=None):
        
        self.modelName = modelName
        self.bsfc_list = bsfc_list
        self.fuelConsumptionTable = fuelConsumptionTable
        self.gen_is_on_list = gen_is_on_list if gen_is_on_list else []
    def initilize_generator_switch(self) -> bool:
        """
        Set all parameter Boolean gen{N}_is_on = (true|false) to false in the .mo file.
        """
        try:
            path_to_mo = Path(current_app.instance_path) / f"{self.modelName}.mo"
            content = self._read_mo_file(str(path_to_mo))
            if not content:
                print("[initilize_generator_switch] Reading Content Error")
                return False

            modified_content, count = self._set_all_generators_off(content)

            if count == 0:
                print("[initilize_generator_switch] No gen*_is_on parameters found.")
            else:
                print(f"[initilize_generator_switch] Set {count} generator switch(es) to false.")

            return self._write_to_mo_file(path_to_mo, modified_content)

        except Exception as e:
            print(f"[initilize_generator_switch] ERROR: {e}")
            return False

    def update_modelica_txt_formate(self):
         
        try:
            # Extract the path 
            path_to_mo = Path(current_app.instance_path) / f"{self.modelName}.mo"
            
            # Extract the content of mo file
            content = self._read_mo_file(str(path_to_mo))
          
            
            if content == "":
                print("Reading Content Error")
                return False
            
            # Modify the content
            # print("Start Modifying .mo File")  # Disabled
            modified_content = self._modify_txt_file(content)
            # print("Modifying .mo File Done")  # Disabled
            
            # Save the modified content to the modelica model 
            print("Start Saving to .mo File")  
            self._write_to_mo_file(path_to_mo, modified_content) 
            print("Saving to .mo file done")  
            
            return True
            
        except Exception as e:
            print(f"[update_modelica_txt_formate] ERROR: {e}")
            return False

    def _read_mo_file(self, path: str) -> str:
        
        try:
            with open(path, 'r', encoding="utf-8") as file:
                content = file.read()
                return content
        except Exception as e:
            print(f"[_read_mo_file] ERROR: {e}")
            return ""
    
    def _modify_txt_file(self, content: str) -> str:
        
        text = content
        
        # Replace BSFC curves dynamically (BSFC_Curve_1, BSFC_Curve_2, etc.)
        # print(f"Replacing {len(self.bsfc_list)} BSFC curves...")  # Disabled
        for idx, bsfc_value in enumerate(self.bsfc_list, start=1):
            if bsfc_value:  # Only replace if value exists
                text = self._replace_bsfc_curve(text, idx, bsfc_value)
        
        # Replace fuel consumption tables dynamically (Engine_Fuel_Consumption_Look_Up_Table_Diesle_1, etc.)
        # print(f"Replacing {len(self.fuelConsumptionTable)} fuel consumption tables...")  # Disabled
        for idx, fcc_value in enumerate(self.fuelConsumptionTable, start=1):
            if fcc_value:  # Only replace if value exists
                text = self._replace_fuel_consumption_table(text, idx, fcc_value)
        
        # Update gen_is_on parameters (gen1_is_on, gen2_is_on, gen3_is_on, etc.)
        if self.gen_is_on_list:
            for idx, is_on in enumerate(self.gen_is_on_list, start=1):
                if is_on is not None:  # Only update if explicitly set
                    text = self._replace_gen_is_on(text, idx, is_on)
        
        return text
    
    def _replace_bsfc_curve(self, content: str, engine_number: int, new_bsfc: str) -> str:
        
        # Strip brackets from input if they exist (handle both "[...]" and "..." formats)
        bsfc_value = new_bsfc.strip()
        if bsfc_value.startswith('[') and bsfc_value.endswith(']'):
            bsfc_value = bsfc_value[1:-1]
        
        # Pattern to match: parameter Real BSFC_Curve_1[:, 2] = [old_values];
        pattern = rf'(parameter\s+Real\s+BSFC_Curve_{engine_number}\s*\[\s*:\s*,\s*2\s*\]\s*=\s*)\[([^\]]*)\]'
        
        # Replace the array content while keeping the parameter declaration
        replacement = rf'\1[{bsfc_value}]'
        
        modified_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
        
        # if count > 0:
        #     print(f"  ✓ Replaced BSFC_Curve_{engine_number}")  # Disabled
        # else:
        #     print(f"  ⚠ BSFC_Curve_{engine_number} not found in file")  # Disabled
        
        return modified_content
    
    def _replace_fuel_consumption_table(self, content: str, engine_number: int, new_fcc: str) -> str:
        
        # Strip brackets from input if they exist (handle both "[...]" and "..." formats)
        fcc_value = new_fcc.strip()
        if fcc_value.startswith('[') and fcc_value.endswith(']'):
            fcc_value = fcc_value[1:-1]
        
        # Pattern to match: parameter Real Engine_Fuel_Consumption_Look_Up_Table_Diesle_1[:, 2] = [old_values];
        pattern = rf'(parameter\s+Real\s+Engine_Fuel_Consumption_Look_Up_Table_Diesle_{engine_number}\s*\[\s*:\s*,\s*2\s*\]\s*=\s*)\[([^\]]*)\]'
        
        # Replace the array content while keeping the parameter declaration
        replacement = rf'\1[{fcc_value}]'
        
        modified_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
        
        # if count > 0:
        #     print(f"  ✓ Replaced Engine_Fuel_Consumption_Look_Up_Table_Diesle_{engine_number}")  # Disabled
        # else:
        #     print(f"  ⚠ Engine_Fuel_Consumption_Look_Up_Table_Diesle_{engine_number} not found in file")  # Disabled
        
        return modified_content
    
    def _replace_gen_is_on(self, content: str, engine_number: int, is_on: bool) -> str:
        """Update gen{N}_is_on parameter in the Modelica file."""
        
        # Convert boolean to modelica format (lowercase)
        value_str = "true" if is_on else "false"
        
        # Pattern to match: parameter Boolean gen3_is_on = true;
        # or: parameter Boolean gen3_is_on = false;
        pattern = rf'(parameter\s+Boolean\s+gen{engine_number}_is_on\s*=\s*)(true|false)'
        
        # Replace with new value
        replacement = rf'\1{value_str}'
        
        modified_content, count = re.subn(pattern, replacement, content)
        
        if count > 0:
            print(f"  ✓ Updated gen{engine_number}_is_on = {value_str}")
        else:
            print(f"  ⚠ gen{engine_number}_is_on not found in file")
        
        return modified_content
    
    def _write_to_mo_file(self, path: Path, updated_content: str) -> bool:
        """Write the updated content back to the Modelica file."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            return True
        except Exception as e:
            print(f"[_write_to_mo_file] ERROR: {e}")
            return False  
    def _set_all_generators_off(self, content: str):
        """
        Replace any:
        parameter Boolean gen<number>_is_on = true|false;
        with:
        parameter Boolean gen<number>_is_on = false;
        """
        pattern = r'(\bparameter\s+Boolean\s+gen\d+_is_on\s*=\s*)(true|false)(\s*;)'
        replacement = r'\1false\3'
        modified, count = re.subn(pattern, replacement, content)
        return modified, count
