import React from "react";
import DutyCycle from "../../assets/model_assets/2024-04_FC_Cardinal_buoy_maintenance Adjusted Again85.txt?url"



export async function buildCombinations(dieList, methList, fcList, batList,  POS_BAT_COUNT, POS_OPT_LOW, POS_OPT_HIGHER, numSlots){
    /**
     * Takes in list of generators (meth and die), list of batteries, list of fuel cell
     * Takes in possbile numbers of generators, fuel cell and batteries
     * Takes in possble bound 
     * Combine the list of generators and fuel cell into one list
     * Map the combined list to each combination of upper and lower bound
     * Remove Combinations where higher bound is smaller than the lower bound 
     * Generate All Configs, (Sequence of generator with individual upper and lower bound, battery and battery count)
     * ## ASSUME THERE 5 Slots in the generator
     */

    // Combine all generators and fuel cells
    // const combinedList = [...dieList, ...methList, ...fcList];
    const combinedList = [...dieList, ...methList];
    
    // map every engine with every kind ofupper and lower bound (optimal zone)
    const engineOptions =combinedList.flatMap(engine =>
        POS_OPT_LOW.flatMap(lo=>
            POS_OPT_HIGHER.map(hi=>({
                engine,lo,hi
            }))
        )
    );
    
    // Filter out combos with higher bound lower than   
    //const engineOptionsFiltered = engineOptions.filter(item => item.hi >= item.lo);
    // Gneerate all possible configurations
    const allConfigs = generateAllPowerTrains({
        engineOptions: engineOptions,
        numSlots: numSlots,
        batteries: batList ,
        batteryCounts: POS_BAT_COUNT,
    });
    return allConfigs;

}
  
export async function parseDutyCycle() {
  const res = await fetch(DutyCycle);
  const text = await res.text();

  const lines = text.trim().split(/\r?\n/);

  const dataLines = lines.slice(2);

  const times = [];
  const powers = [];

  for (const line of dataLines) {
    const parts = line.trim().split(/\s+/);
    if (parts.length >= 2) {
      const t = parseFloat(parts[0]);
      const p = parseFloat(parts[1]);

      if (!isNaN(t) && !isNaN(p)) {
        times.push(t);
        powers.push(p);
      }
    }
  }

  const startTime = times[0] ?? null;
  const endTime = times.length > 0 ? times[times.length - 1] : null;
  const maxPower =
    powers.length > 0
      ? powers.reduce((max, p) => (p > max ? p : max), -Infinity)
      : null;

  return {
    startTime,
    endTime,
    maxPower,
  };
}

export async function markUnrealisticCombos({combos, vollimit, weighLimit, numslots}){
    /**
     * This function loop thorugh every configuration object and determine it exceed weight/ volumn limit
     * It add a flag once in the configuration object to single this config is bad 
     */

    // loop though all config objects 
    let tempoCombos=[];
    for (const config of combos){
        // extract the generator objects
        let totalWight = 0;
        let totalVolume = 0;
        for (let i = 1; i <= numslots; i++){
            if(config[`slot ${i}`] != null){
                // add to the weight and volume 
                totalWight += config[`slot ${i}`].engine_mass;
                totalVolume += config[`slot ${i}`].engine_volume;
            }
        }
        // check if the the weight aand volume exceed demand
        if (totalVolume > vollimit || totalWight > weighLimit){
            tempoCombos.push({...config, check : false})
        }else{
            tempoCombos.push({...config, check : true})
        }
    }

    return tempoCombos

}

export async function filterIncapbleSystem({combos, numslots, max_power_required}){
    /**
     * This function loop through every combinations and determine if the generators alone can handle the peak demand
     */
    let tempoCombos=[];
    for (const config of combos){
        // extract the generator objects
        let max_power  = 0;
        for (let i = 1; i <= numslots; i++){
            if(config[`slot ${i}`] != null){
                // add to the weight and volume 
                max_power += config[`slot ${i}`].engine_p_max;
            }
        }
        // check if the generators alone can meet the demand 
        // if it can then push into the result array
        if (max_power > max_power_required){
            tempoCombos.push({config});
        }    
    }
    return tempoCombos;
}

export async function modelicaParameterMapping(combos, numslots){
    /**
     * This function will map prepared configuration with real modelica variable 
     */
    const changed_parameters =[];
    for(const config of combos){
        // Prepare empty container for modelica parameter of this config
        let temp_changed_parameter ={
            instance : config,
            modelica_parameters :[]
        };
        /*Engien parameters */
        for (let  i = 1; i <= numslots; i++){
            //if there is a generator, in the slot
            
            if(config["config"][`slot ${i}`] != null){
                // Engine On
                temp_changed_parameter.modelica_parameters.push({param:`gen${i}_is_on`, value:"true"})
                // Engine Power
                temp_changed_parameter.modelica_parameters.push({param:`generator_P_rat_${i}`, value:(config["config"][`slot ${i}`].engine_p_max * 1000).toString()})
                temp_changed_parameter.modelica_parameters.push({param:`generator_P_idle_${i}`, value:(config["config"][`slot ${i}`].engine_p_min * 1000).toString()})
                // check what types of generator it is 
                if (config["config"][`slot ${i}`].engine_fuel_type === "Diesel"){
                    // Fuel
                    temp_changed_parameter.modelica_parameters.push({param : `generator_FLHV_${i}`, value:"45.9e6"})
                    temp_changed_parameter.modelica_parameters.push({param : `generator_Frho_${i}`, value:"846"})
                    temp_changed_parameter.modelica_parameters.push({param : `generator_Frho_liq_${i}`, value:"846"})
                    temp_changed_parameter.modelica_parameters.push({param : `generator_FcarbonContent_${i}`, value:"0.86"})
                    temp_changed_parameter.modelica_parameters.push({param : `generator_MolarMass_${i}`, value:"0.223"})  
                }else if(config["config"][`slot ${i}`].engine_fuel_type === "Methanol"){
                    // Fuel
                    temp_changed_parameter.modelica_parameters.push({param : `generator_FLHV_${i}`, value:"23e6"})
                    temp_changed_parameter.modelica_parameters.push({param : `generator_Frho_${i}`, value:"791"})
                    temp_changed_parameter.modelica_parameters.push({param : `generator_Frho_liq_${i}`, value:"791"})
                    temp_changed_parameter.modelica_parameters.push({param : `generator_FcarbonContent_${i}`, value:"0.34"})
                    temp_changed_parameter.modelica_parameters.push({param : `generator_MolarMass_${i}`, value:"0.223"})
                }else{
                    // Fuel using place holder until property of hydrogen are confirmed
                    temp_changed_parameter.modelica_parameters.push({param : `generator_FLHV_${i}`, value:"45.9e6"})
                    temp_changed_parameter.modelica_parameters.push({param : `generator_Frho_${i}`, value:"846"})
                    temp_changed_parameter.modelica_parameters.push({param : `generator_Frho_liq_${i}`, value:"846"})
                    temp_changed_parameter.modelica_parameters.push({param : `generator_FcarbonContent_${i}`, value:"0"})
                    temp_changed_parameter.modelica_parameters.push({param : `generator_MolarMass_${i}`, value:"0.223"})
                }
                // BSFC Upper and Lower Bound
                temp_changed_parameter.modelica_parameters.push(
                    {param :`mCtrl_user_defined_BSFC_percentage_${i}`, value: config["config"][`slot ${i}_upper`].toString()})
                temp_changed_parameter.modelica_parameters.push(
                    {param :`mCtrl_user_defined_BSFC_percentage_${i}_lower`, value: config["config"][`slot ${i}_lower`].toString()})
            }else{
                // if there is no engine at that position,
                // then make sure this engine is turned off 
                temp_changed_parameter.modelica_parameters.push({param:`gen${i}_is_on`, value:"false"})
            }
        }
        
        /*Battery parameters */
        if(config["config"]["battery_count"] > 0){  
            // if therei s a battery
            temp_changed_parameter.modelica_parameters.push(
                {
                    param:"battery_P_max", 
                    value:(config["config"]["battery"].battery_max_charge_power * config["config"]["battery_count"]).toString()
                })
            temp_changed_parameter.modelica_parameters.push(
                {
                    param:"battery_Capacity", 
                    value:(config["config"]["battery"].battery_capcity * 3600000 * config["config"]["battery_count"]).toString()
                })
        }else{
            // if there is not a battery, the battery does not output power
            temp_changed_parameter.modelica_parameters.push({param:"battery_P_max", value:"0.1"})
        }
        changed_parameters.push(temp_changed_parameter);
    }

    return changed_parameters

}

function sequencesOfLength(oengineOptions, length){
    /**
     * This a local helper function, create all possible sequenecy of engine arrangements 
     */
    let result = [[]]
    for (let i = 0; i < length; i++) {
            result = result.flatMap(seq =>
            oengineOptions.map(opt => [...seq, opt])
        );
    
    }
    return result;
}


function generateSlotConfigs(engineOptions, numSlots) {
   /**
    * This Function Generate all sequence of generators / fuelcell
    */
  const configs = [];

  for (let k = 1; k <= numSlots; k++) {
    const prefixes = sequencesOfLength(engineOptions, k);

    for (const prefix of prefixes) {
      const padded = [...prefix];
      while (padded.length < numSlots) {
        padded.push(null); // empty slot
      }
      configs.push(padded);
    }
  }
  return configs;
}


function generateAllPowerTrains({engineOptions, numSlots, batteries,batteryCounts,}) {
    /**
    * This function takes in the engine options and battery list and counts.
    * @call generateSlotConfigs() to generate all sequences of engine arrangement. 
    * Then it assignes all possible battery configurition to each sequence engine arrangment.
    */
  const slotConfigs = generateSlotConfigs(engineOptions, numSlots);
  const results = [];

  for (const slots of slotConfigs) {
    for (const battery of batteries) {
      for (const count of batteryCounts) {
        //  to skip “no battery” configs:
        // if (count === 0) continue;

        // Build final object with slot1, slot1_upper, etc.
        const config = {};

        slots.forEach((slot, idx) => {
          const slotIndex = idx + 1;

          if (slot === null) {
            config[`slot ${slotIndex}`] = null;
            config[`slot ${slotIndex}_upper`] = null;
            config[`slot ${slotIndex}_lower`] = null;
          } else {
            config[`slot ${slotIndex}`] = slot.engine;
            config[`slot ${slotIndex}_upper`] = slot.hi;
            config[`slot ${slotIndex}_lower`] = slot.lo;
          }
        });

        config.battery = battery;
        config.battery_count = count;

        results.push(config);
      }
    }
  }
  return results;
}


export const commitBatchSimulation = async ({moParams, startTime,endTime,modelName,numSlot})=>{
    /**
     * Inform Backed to start simulation
     * Need Model Name
     * Need the complete modelica parameter
     * Returns Simulation Results
     */
    await fetch("http://127.0.0.1:5000/seq_model/simulate_batch",
        {
            method:"POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                model_name: modelName,
                start_time: startTime,
                stop_time: endTime,
                list_of_config_combinations:moParams,
                number_of_slots : numSlot
            }),

        }
    ).then(
        console.log("done")
    )


}
