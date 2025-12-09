import base64
from itertools import product
import json
import  pandas as pd
from datetime import datetime
import shutil
import os
import numpy as np
from pathlib import Path
from multiprocessing  import Pool, Process
from flask_cors import CORS
from flask import Blueprint, current_app, request, jsonify
from omserver.EUEmissionCalculator import EUMarineEmissionCalculator
from omserver.ModelicaSequentialParaPaser import ModelicaSequentialParamParser
from concurrent.futures import ProcessPoolExecutor, as_completed
from .OMCConnection import OMCConnection
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from omserver.ExcelGenerator import ExcelGenerator
bp = Blueprint("seq_model", __name__, url_prefix="/seq_model")
CORS(bp)
PROGRESS = {
    "running": False,
    "total": 0,
    "done": 0,
    "current": None,     
    "cancelled": False,
    "last_error": None,
}
@bp.route("/upload", methods=["POST"])
def upload():
    try:
        model_path = Path(current_app.instance_path) / f"{request.json['model_name']}.mo"
        # Ensure instance directory exists
        model_path.parent.mkdir(parents=True, exist_ok=True)
        # Write in binary mode to handle Unicode properly
        with open(model_path, "wb") as model_file:
            model_file.write(base64.b64decode(request.json['model_data']))
        print(f"Decoded model to {model_path}")
    except Exception as e:
        print(f"Error writing model file: {e}")
        return json.dumps({
            "name": request.json['model_name'],
            "status": "Error opening writable instance resource"
        })

    return json.dumps({
        "name": request.json['model_name'],
        "status": "Model written"
    })

@bp.route("/simulate_batch", methods=["POST"])
def simulate_batch():
    # Retrive Request
    data = request.get_json(force=True)
    model_name  = data["model_name"]
    start_time  = data["start_time"]
    stop_time   = data["stop_time"]
    combos      = data["list_of_config_combinations"]
    number_of_slots =data["number_of_slots"]
    # Log General Batch Simulation Info
    print(f"[simulate_batch] model={model_name}, combos={len(combos)}, "
          f"start={start_time}, stop={stop_time}")

    # Connect OMC 
    omc = OMCConnection()
    
    
    # Check if the result collection db exist, if not , make one
    # This only Applied to First Time 
    path_to_db = Path(current_app.instance_path) / "res_db.json"
    path_to_db.parent.mkdir(parents=True, exist_ok=True)

    # Form Current Time
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Form the current bastch simulation object
    temp_result_collection = {
        "batch_sim_title" :  f"{current_time}_{model_name}_vessel_name_place_holder",
        "batch_sim_time_stamp" : f"{current_time}",
        "vessel_name" : "fortuna_crane",
        "batch_size" : int(len(combos)),
        "batch_sim_res_collection"  : []
    }

    # Looping Start
    try:
        # Looping Start
        for idx, cfg in enumerate(combos):
            # Update the BSFC &&  FCC for this iteration
            temp_fcc_list = []
            temp_bsfc_list = []
            temp_gen_is_on_list = []
            config = cfg.get("instance", {}).get("config", {})
            for i in range(1, number_of_slots + 1):
                slot = config.get(f"slot {i}")
                if slot is not None and isinstance(slot, dict):
                    temp_fcc_list.append(slot.get("engine_fcc", ""))
                    temp_bsfc_list.append(slot.get("engine_bsfc", ""))
                    temp_gen_is_on_list.append(True)  # Engine exists, should be on
                    # print(f"Slot {i}: {slot.get('engine_name', 'Unknown')} engine loaded")  # Disabled
                else:
                    temp_fcc_list.append("")
                    temp_bsfc_list.append("")
                    temp_gen_is_on_list.append(False)  # No engine, should be off
                    # print(f"Slot {i} has No Engine - skipping")  # Disabled
            print(f"FCC list: {temp_fcc_list}")
            print(f"BSFC list: {temp_bsfc_list}")
            print(f"Generator ON/OFF: {temp_gen_is_on_list}")
            modelicaArrayParser = ModelicaSequentialParamParser(model_name, temp_bsfc_list, temp_fcc_list, temp_gen_is_on_list)
            modelicaArrayParser.update_modelica_txt_formate()
        
            # Log Simulation Detail
            print(f"\n[{idx+1}/{len(combos)}] Starting simulation...")
            #  extract engine names (handle null slots)
            slot1_name = (cfg.get("instance", {}).get("config", {}).get("slot 1") or {}).get("engine_name", "None")
            slot2_name = (cfg.get("instance", {}).get("config", {}).get("slot 2") or {}).get("engine_name", "None")
            slot3_name = (cfg.get("instance", {}).get("config", {}).get("slot 3") or {}).get("engine_name", "None")
            battery_info = cfg.get("instance", {}).get("config", {}).get("battery", {})
            battery_count_log = cfg.get("instance", {}).get("config", {}).get("battery_count", 0)
            battery_name_log = battery_info.get("battery_name", "None")
            
            print(f"  Config: Gen1:[{slot1_name}] Gen2:[{slot2_name}] Gen3:[{slot3_name}] Battery:[{battery_count_log}x{battery_name_log}]")
            
            
            #Form the total cost of the configuration
            #cost  = float(cfg.get("instance").get("Diesel_Engine").get("engine_cost")) * int(cfg.get("instance").get("Diesel_Engine_Count"))+ float(cfg.get("instance").get("Meth_Engine").get("engine_cost")) * int(cfg.get("instance").get("Meth_Count"))+ float(cfg.get("instance").get("Battery").get("battery_cost"))* int(cfg.get("instance").get("Battery_Count"))
            #print(f"Cost of  Setup : {cost}  £  ")

            #Form the max potential power output of the power train
            #max_potential_gen = float(cfg.get("instance").get("Diesel_Engine").get("engine_p_max")) * float(cfg.get("instance").get("Diesel_Engine_Count")) + float(cfg.get("instance").get("Meth_Engine").get("engine_p_max")) * float(cfg.get("instance").get("Meth_Count"))+ float(cfg.get("instance").get("Battery").get("battery_max_charge_power"))* (1/1000)* float(cfg.get("instance").get("Battery_Count"))
            #print(f"Max Possible Power {max_potential_gen} w")
            
            # Unpack the parameter list
            overrides_list = cfg.get("modelica_parameters", [])
            # print(f"Found {len(overrides_list)} override parameters")  
            
            # Build override string 
            if overrides_list:
                override_pairs = []
                for o in overrides_list:
                    param_name = o.get('param') # Handle both key names
                    param_value = o.get('value')
                    if param_name and param_value is not None:
                        override_pairs.append(f"{param_name}={param_value}")
                
                if override_pairs:
                    ov = " -override " + ",".join(override_pairs)
                else:
                    ov = ""
            else:
                ov = ""
            
            # Convert Windows backslashes to forward slashes (OpenModelica accepts this)
            output_path = str(current_app.instance_path).replace('\\', '/')
            simflags = f'-outputPath {output_path}{ov}'
            print(f"Simflags: {simflags}") 
            path_to_mo = Path(current_app.instance_path) / f"{model_name}.mo"
            
            try:
                # Load the model (use forward slashes for cross-platform compatibility)
                model_path = str(Path(current_app.instance_path) / f"{model_name}.mo").replace('\\', '/')
                omc.request(f'loadFile("{model_path}")')
                
            
                # Run simulation (with extended timeout for long simulations)
                # print(f"Running simulation...") 
                omc.request(
                    f'simulate({model_name}, '
                    f'outputFormat="csv", '
                    f'startTime={start_time}, '
                    f'stopTime={stop_time}, '
                    f'numberOfIntervals=32643, '
                    f'tolerance=1e-6, '
                    f'simflags="{simflags}")'  
                )
                # print(f"Simulation result: {sim_result}")  # Disabled verbose output
                
                # Check for simulation errors (only print actual errors)
                sim_errors = omc.request('getErrorString()')
                if sim_errors and "Error" in sim_errors:
                    print(f"⚠ Simulation errors: {sim_errors}")
                
                # Check if CSV was created
                csv_path = Path(current_app.instance_path) / f"{model_name}_res.csv"
                if not csv_path.exists():
                    print(f" ERROR: CSV file was not created at {csv_path}")
                    raise FileNotFoundError(f"Simulation did not produce output CSV: {csv_path}")

                # Log if the simulation has finished 
                print(f"[{idx+1}/{len(combos)}] ✓ Simulation complete")
                # print(f"[simulate_batch] start processing")  # Disabled
                
                # Extract configuration details (safely handle null slots)
                config = cfg.get("instance", {}).get("config", {})
                slot1_engine = (config.get("slot 1") or {}).get("engine_name", "None")
                slot2_engine = (config.get("slot 2") or {}).get("engine_name", "None")
                slot3_engine = (config.get("slot 3") or {}).get("engine_name", "None")
                slot1_engine_db_idx = (config.get("slot 1") or {}).get("engine_db_index", "None")
                slot2_engine_db_idx = (config.get("slot 2") or {}).get("engine_db_index", "None")
                slot3_engine_db_idx = (config.get("slot 3") or {}).get("engine_db_index", "None")

                battery_name = (config.get("battery") or {}).get("battery_name", "None")
                battery_count = config.get("battery_count", 0)
                battery_db_idx = (config.get("battery") or {}).get("battery_db_index", "None")
                battery_abb = (config.get("battery") or {}).get("battery_abbreviation", "None")
                #store all the current opt zone pairs (for  max three gens)
                cur_optZonePairs= [config.get("slot 1_lower") or 0, config.get("slot 1_upper") or 0, config.get("slot 2_lower") or 0, config.get("slot 2_upper") or 0, config.get("slot 3_lower") or 0, config.get("slot 3_upper") or 0]
                # Create descriptive simulation name
                # Make the abberivation for generators 1, 2 ,3 
                #gen1_type_abb = "D" if (config.get("slot 1") or {}).get("engine_fuel_type", "None") == "Diesel" else "M" if (config.get("slot 1") or {}).get("engine_fuel_type", "None") == "Methanol" else "F" if (config.get("slot 1") or {}).get("engine_fuel_type", "None")=="FC" else "None"
                #gen2_type_abb = "D" if (config.get("slot 2") or {}).get("engine_fuel_type", "None") == "Diesel" else "M" if (config.get("slot 2") or {}).get("engine_fuel_type", "None") == "Methanol" else "F" if (config.get("slot 2") or {}).get("engine_fuel_type", "None")=="FC" else "None"
                #gen3_type_abb = "D" if (config.get("slot 3") or {}).get("engine_fuel_type", "None") == "Diesel" else "M" if (config.get("slot 3") or {}).get("engine_fuel_type", "None") == "Methanol" else "F" if (config.get("slot 3") or {}).get("engine_fuel_type", "None")=="FC" else "None"
                battery_power =  f"{"{:.2f}".format((config.get("battery") or {}).get("battery_max_charge_power", 0) * battery_count * (1/1000))}" if config.get("battery_count", 0) >= 1 else 0
                gen1_power_abb = f"{(config.get("slot 1") or {}).get("engine_p_max", 0)}" if (config.get("slot 1") or {}).get("engine_fuel_type", "None") != "None" else 0
                gen2_power_abb = f"{(config.get("slot 2") or {}).get("engine_p_max", 0)}" if (config.get("slot 2") or {}).get("engine_fuel_type", "None") != "None" else 0   
                gen3_power_abb = f"{(config.get("slot 3") or {}).get("engine_p_max", 0)}" if (config.get("slot 3") or {}).get("engine_fuel_type", "None") != "None" else 0
                
                gen1_name_section = f"G1_{slot1_engine_db_idx+"_" + gen1_power_abb if (config.get("slot 1") or {}).get("engine_fuel_type", "None") != "None" else 0}:"
                gen2_name_section = f"G2_{slot2_engine_db_idx+"_" + gen2_power_abb if (config.get("slot 2") or {}).get("engine_fuel_type", "None") != "None" else 0}:"
                gen3_name_section = f"G3_{slot3_engine_db_idx+"_" + gen3_power_abb if (config.get("slot 3") or {}).get("engine_fuel_type", "None") != "None" else 0}:"
                battery_name_section =f"{battery_db_idx+"_"+battery_abb+str(battery_count)+"_"+ str(battery_power)}"
                
                # Create simulation abbreviation
                simName = f"{gen1_name_section + gen2_name_section + gen3_name_section + battery_name_section}" 
                # Create power train sequence description
                sequence_description = f"Gen1:[{slot1_engine}] → Gen2:[{slot2_engine}] → Gen3:[{slot3_engine}] + Batt:[{battery_count}x{battery_name}]"
                
                simResult = process_simmultion_result(
                    int(idx), 
                    simName,
                    sequence_description,
                    "cost_placeholder",
                    "max_potential_gen_placeholder",
                    model_name,
                    cur_optZonePairs,
                    battery_name,
                    battery_count
                )
                temp_result_collection["batch_sim_res_collection"].append(simResult)

            except Exception as e:
                print(f"[simulate_batch] ✗ error at {idx+1}: {e}")
                raise
           
        # Loop ends, Check Status
        status = "cancelled" if PROGRESS["cancelled"] else "completed"
        print(f"[simulate_batch] finished with status={status}, " f"done={PROGRESS['done']}/{PROGRESS['total']}")
        
        # Load Result into the database JSON 
        try:
            append_batch_result(temp_result_collection)
            current_app.logger.info(
                "Saved batch: %s (size=%d)", temp_result_collection["batch_sim_title"], len(temp_result_collection["batch_sim_res_collection"])
            )
        except Exception as e: 
            current_app.logger.exception("[simulate_batch_end] ERROR: %s", e)
    except Exception as e:
        PROGRESS["last_error"] = str(e)
        print(f"[simulate_batch] ERROR: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500
    finally:
        print("Saving finally done")
        
        # Export results to Excel
        try:
            # excel_filename = export_batch_to_excel(temp_result_collection)
            excel_generator = ExcelGenerator(temp_result_collection)
            excel_filename= excel_generator.export_batch_to_excel()
            print(f" Excel file created: {excel_filename}")
        except Exception as e:
            print(f"Excel export failed: {e}")
        
        avalible_batches = []
        return jsonify({
            "avalible_batches" : avalible_batches
        })

def process_simmultion_result(index, simName, sequence_description, total_cost, 
                              max_powertrain_gen ,model_name, optZonePairs, batName, batCount):
    
    processed_simulation_result = {}
    try:
        # Construct the path to the CSV result file
        csv_path = Path(current_app.instance_path) / f"{model_name}_res.csv"
        # print(f"Reading CSV from: {csv_path}")  # Disabled
        
        if not csv_path.exists():
            print(f" ERROR: CSV file not found at {csv_path}")
            raise FileNotFoundError(f"Result CSV not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        processed_simulation_result['sim_name'] = simName
        processed_simulation_result['sequence'] = sequence_description

        processed_simulation_result['iteration_id'] = index
        processed_simulation_result['time (h)'] = [t / 3600 for t in df['time'].tolist()]
        processed_simulation_result['power_demand (KW)'] = [p / 1000 for p in df['gain1.y'].tolist()]
        processed_simulation_result['gen_1_power (KW)'] = [p / 1000 for p in df['generator1.P_out'].tolist()]
        processed_simulation_result['gen_2_power (KW)'] = [p / 1000 for p in df['generator2.P_out'].tolist()]
        processed_simulation_result['gen_3_power (KW)'] = [p / 1000 for p in df['generator3.P_out'].tolist()]
        #processed_simulation_result['gen_1_fuel_volume_flow (m^3/s)'] = df['generator1.V_flow_fuel'].tolist()
        #processed_simulation_result['gen_2_fuel_volume_flow (m^3/s)'] = df['generator2.V_flow_fuel'].tolist()
        #processed_simulation_result['gen_3_fuel_volume_flow (m^3/s)'] = df['generator3.V_flow_fuel'].tolist()
        processed_simulation_result['battery_name'] = batName
        processed_simulation_result['battery_count'] = batCount
        processed_simulation_result['battery_soc (%)'] = df['battery1.SOC'].tolist()
        processed_simulation_result['battery_discharge (KW)'] = [p / 1000 for p in df['battery1.P_discharge_abs'].tolist()]
        processed_simulation_result['battery_charge (KW)'] = [p / 1000 for p in df['battery1.P_charge_abs'].tolist()]
        processed_simulation_result['optimalZone'] = optZonePairs
        processed_simulation_result['Total Energy Deamand (kWh)'] = float(df['realValueTotalDemand.showNumber'].iloc[-1])
        processed_simulation_result['Total Energy Supplied (kWh)'] = float(df['realValueTotalEnergySuppliedIncludingLoss.showNumber'].iloc[-1])
        print(f"[Total Energy Demand] : {float(df['realValueTotalDemand.showNumber'].iloc[-1])}")
        print(f"[Total Energy Supplied] : {float(df['realValueTotalEnergySuppliedIncludingLoss.showNumber'].iloc[-1])}")
        processed_simulation_result['Total Energy Wasted (kWh)'] = float(df['realValueTotalWastedEnergy.showNumber'].iloc[-1])
        print(f"[Total Energy Wasted] : {float(df['realValueTotalWastedEnergy.showNumber'].iloc[-1])}")
        processed_simulation_result['Wasted Power (kW)'] = [p / 1000 for p in df['Surplus1.y'].tolist()]
        #processed_simulation_result['battery_charge_energy (kWh)'] = (df['battery1.P_charge_abs']).tolist() 
        #processed_simulation_result['battery_discharge_energy (kWh)'] = (df['battery1.P_discharge_abs']).tolist()
        processed_simulation_result['battery_measured_power (kW)'] = [p / 1000 for p in df['battery1.P_out'].tolist()]
        # Extract fuel consumption values
        diesel_kg = float(df['realTotalDieselUsage.showNumber'].iloc[-1])
        methanol_kg = float(df['realTotalAltFuelUsage.showNumber'].iloc[-1])
        hydrogen_kg = float(df['realTotalHydroUsage.showNumber'].iloc[-1])
        
        processed_simulation_result['diesel_usage (Ton)'] = diesel_kg / 1000
        processed_simulation_result['meth_usage (Ton)'] = methanol_kg / 1000
        processed_simulation_result['hydrogen_usage (Ton)'] = hydrogen_kg / 1000
        
        # Display fuel consumption (highlighted)
        print(f"  Diesel: {diesel_kg:.2f} kg | Methanol: {methanol_kg:.2f} kg | Hydrogen: {hydrogen_kg:.2f} kg")
        # print(f"Cost : {total_cost} £")  # Disabled
        
        total_emisstion = 444
        penalty = 444
        try: 
            temp_emission_res = calculate_eu_fuel_compliance(diesel_kg, methanol_kg)
            total_emisstion = temp_emission_res.get("emission").get("total_co2")
            penalty = temp_emission_res.get("emission").get("penalty")
            print(f" CO2: {total_emisstion:.2f} tons | Penalty: €{penalty:.2f}")
        except Exception as e:
            print(f"  Emission calculation error: {e}")
        processed_simulation_result['CO2_emission (Ton)'] = total_emisstion
        processed_simulation_result['penalty (EUR)'] = penalty
        processed_simulation_result['capital_cost (£)'] = total_cost
        processed_simulation_result['max_pwr_potential (KW)'] = max_powertrain_gen
        processed_simulation_result['peak_power_demand (KW)'] = (max(df['gain1.y'].tolist())) * (1/1000)
        #processed_simulation_result['node_tracker'] = df['masterControllerSingleBattery.methanolBatteryDieselDebug.nodeTracker'].tolist()
    except Exception as e:
        print(f"[simulate_batch_result_processing] ERROR: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500
    return processed_simulation_result 
def append_batch_result(batch_record: dict):
    db_path = get_db_path()
    data = read_db(db_path)
    data.append(batch_record)
    write_db_atomic(db_path, data) 

def get_db_path() -> Path:
    # instance_path is the right place to write app data
    p = Path(current_app.instance_path) / "res_db.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def read_db(db_path: Path):
    try:
        text = db_path.read_text(encoding="utf-8")
        data = json.loads(text)
        if not isinstance(data, list):
            current_app.logger.warning("res_db.json not a list; reinitializing")
            return []
        return data
    except FileNotFoundError:
        return []
    except Exception as e:
        current_app.logger.exception("Failed to read res_db.json; reinitializing")
        return []

def write_db_atomic(db_path: Path, data):
    tmp = db_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(db_path)

def calculate_eu_fuel_compliance(dieselConsumption, methanolConsumption):
    """
    Calculate EU fuel compliance emissions and penalties for diesel and methanol consumption.
    
    Args:
        dieselConsumption: Diesel consumption in kg
        methanolConsumption: Methanol consumption in kg
        
    Returns:
        Dictionary with emission data including total CO2 and penalty
    """
    fuel_type_mapping = {
        'Diesel': 'MDO MGO (Grades DMX to DMB)',
        'Methanol': 'e-methanol E10'
    }
    
    fuel_results = {}
    if dieselConsumption > 0:
        fuel_results['Diesel'] = dieselConsumption
    if methanolConsumption > 0:
        fuel_results['Methanol'] = methanolConsumption
    
    emission_calculator = EUMarineEmissionCalculator()
    
    emission_fuel_data = []  # Contains fuel involved in CO2 production on the vessel  
    total_emission_tco2eq = 0
    emission_breakdown = {}

    for fuel_type, consumption_kg in fuel_results.items():
        if consumption_kg > 0:
            # Convert kg to tonnes for emission calculation
            consumption_tonnes = consumption_kg / 1000
            
            emission_fuel_type = fuel_type_mapping.get(fuel_type)
            if not emission_fuel_type:
                # print(f"No emission fuel mapping found for {fuel_type}")  # Disabled
                continue
            
            # All fuel consumption is within EU/EEA
            fuel_data_entry = {
                'fuel_type': emission_fuel_type,
                'fuel_consumption_within_eu': consumption_tonnes,
                'fuel_consumption_in_out_eu': 0.0,  # All within EU
                'is_biofuel': False,
                'biofuel_option': 3,
                'biofuel_percentage': 0,
                'biofuel_pathway': ''
            }
            
            emission_fuel_data.append(fuel_data_entry)
            # print(f"{fuel_type} ({emission_fuel_type}): {consumption_tonnes:.3f} tonnes within EU")  
    
    # Calculate emissions if all data is presented
    emission_results = None
    compliance_results = None
    
    if emission_fuel_data:
        try:
            # Validate fuel data
            validation = emission_calculator.validate_fuel_data(emission_fuel_data)
            if not validation['valid']:
                # print(f"Invalid fuel data for emission calculation: {validation['error']}")  
                return {
                    "emission": {
                        "total_co2": 0,
                        "penalty": 0
                    }
                }
            
            # Run Phase 2 emission calculation (includes both phase 1 and 2)
            emission_results = emission_calculator.calculate_emissions_phase2(emission_fuel_data, target_year=2025)
            
            # Extract emission breakdown per fuel
            fuel_breakdown = emission_results.get('fuel_breakdown', [])
            for fuel_calc in fuel_breakdown:
                original_fuel_type = None
                emission_fuel_type = fuel_calc.get('fuel_type', '')
                
                # Reverse map to original fuel type
                for orig_type, mapped_type in fuel_type_mapping.items():
                    if mapped_type == emission_fuel_type:
                        original_fuel_type = orig_type
                        break
                
                if original_fuel_type:
                    emission_breakdown[original_fuel_type] = {
                        'consumption_tonnes': fuel_calc.get('fuel_mass_total', 0),
                        'ghg_emission_tonnes': fuel_calc.get('ghg_emission', 0)
                    }
            
            # Extract compliance results
            final_results = emission_results.get('final_results', {})
            compliance_results = {
                'ghg_intensity_actual': final_results.get('ghg_intensity_actual', 0),
                'ghg_intensity_target': final_results.get('ghg_intensity_target_2025_2029', 0),
                'compliance_balance_tco2eq': final_results.get('compliance_balance_tco2eq', 0),
                'penalty_eur': final_results.get('penalty', 0),
                'total_ghg_emission_tonnes': final_results.get('ghg_emission', 0)
            }
            
            total_emission_tco2eq = final_results.get('ghg_emission', 0)
            
            # Disabled verbose emission calculation output
            # print(f"Emission calculation completed:")
            # print(f"---Total GHG Emission: {total_emission_tco2eq:.3f} tCO2eq")
            # print(f"---GHG Intensity Actual: {compliance_results['ghg_intensity_actual']:.6f} gCO2eq/MJ")
            # print(f"---GHG Intensity Target: {compliance_results['ghg_intensity_target']:.6f} gCO2eq/MJ")
            # print(f"---Compliance Balance: {compliance_results['compliance_balance_tco2eq']:.6f} tCO2eq")
            # print(f"---Penalty: EUR {compliance_results['penalty_eur']:.2f}")
            
        except Exception as e:
            # print(f"Emission calculation failed: {str(e)}")  # Disabled
            # Continue with fuel consumption results but no emissions
            pass  # Silent fail, error will be shown in main output
            
    return {
        "emission": {
            "total_co2": compliance_results.get('total_ghg_emission_tonnes', 0) if compliance_results else 0,
            "penalty": compliance_results.get('penalty_eur', 0) if compliance_results else 0
        }
    }

