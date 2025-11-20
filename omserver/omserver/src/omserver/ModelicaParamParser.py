from pathlib import Path
from flask import current_app
import re 
class ModelicaParamParser:

    def __init__(self, modelName, dieselBSFC, methBSFC, dieselFuelConsumptionTable, methanolConsumptionCurve):
        self.modelName = modelName  # model name is to dynamically access the thing 
        self.dieselBSFC = dieselBSFC
        self.methBSFC = methBSFC
        self.dieselFuelConsumptionTable = dieselFuelConsumptionTable
        self.methanolConsumptionTable = methanolConsumptionCurve
    
    def update_modelica_txt_formate(self):
   
        # Access the Modelica Model.
        try :
            # Extract the path 
            path_to_mo = Path(current_app.instance_path) / f"{self.modelName}.mo"
            # Extract the content of mo file
            content  = self._read_mo_file(str(path_to_mo))
            print("Reading Modelica File Done")
            if (content == ""):
                print("Reading Content Error")
                return False
            # Modify the content
            print("Start Modifying .mo File")
            modifled_content = self._modify_txt_file(content)
            print("Modifying .mo File")
            print("Start Saving to .mo File")
            # Save the modified content to the modelica model 
            self._write_to_mo_file(path_to_mo, modifled_content) 
            print("Saving to .mo file done")
            return True
        except Exception as e:
            print(e)
            return False


    ## IO Functions   
    def _read_mo_file(self, path : str) -> str:
        # Extract the content of the file in string formate
        try :
            with open(path, 'r', encoding="utf-8") as file:
                content = file.read()
                return content
        except Exception as e:
            print(f"[_read_mo_file] ERROR: {e}")
            return ""
    def _write_to_mo_file(self, path : Path , updated_content : str) -> bool:
        
        try:
            with open (path, "w", encoding = "utf-8") as f:
                f.write(updated_content)
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            return True  


    def _modify_txt_file(self, content: str) -> str:
     
        text = content

 
        text = self._replace_param_array(
            text,
            param_name="BSFC_Curve",         
            new_array=self.dieselBSFC
        )

       
        text = self._replace_param_array(
            text,
            param_name="BSFC_Curve_AltFuel",      
            new_array=self.methBSFC
        )

      
        text = self._replace_param_array(
            text,
            param_name="Engine_Fuel_Consumption_Look_Up_Table_Diesle", 
            new_array=self.dieselFuelConsumptionTable
        )

        
        text = self._replace_param_array(
            text,
            param_name="Engine_Fuel_Consumption_Look_Up_Table_AltFuel",    
            new_array=self.methanolConsumptionTable
        )

        return text

    def _replace_param_array(self, content: str, param_name: str, new_array: str = "") -> str:

        pattern = re.compile(
            rf'(parameter\s+Real\s+{re.escape(param_name)}\s*\[\s*:\s*,\s*2\s*\]\s*=\s*)'
            r'(\[[^\]]*\])?'   
            r'\s*(;)',
            flags=re.IGNORECASE | re.DOTALL
        )

        # Replacement: header + new array (or empty) + semicolon
        replacement = r'\1' + (new_array or "") + r'\3'
        new_text, n = pattern.subn(replacement, content, count=1)
        if n == 0:
            print(f"[_replace_param_array] WARN: parameter not found: {param_name}")
        return new_text
    

            
        