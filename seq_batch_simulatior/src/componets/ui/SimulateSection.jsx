import React, { createContext, useContext, useRef, useState } from "react";
import { buildCombinations, commitBatchSimulation, markUnrealisticCombos, modelicaParameterMapping, filterIncapbleSystem, parseDutyCycle } from "../funtion_utils/SimulateSectionUtil.jsx";
import { BatteryListContext, DieselEngienListContext, FuelCellListContext, MethanolEngineListContext } from "../../App";
import { dutyCycleInfo, singleIteration } from "../funtion_utils/TestingConfigUnits.jsx";

const  POSSIBLE_BATTERY_COUNT = [0,1,5,10]
const  POSSIBLE_OPTIMAL_LOWER_PERCENTAGE = [0.05]
const  POSSBILE_OPTIMAL_UPPER_PERCENTAGE = [0.001]
const SimulateSection =()=>{
    /**
     * Parse the Battery / Generator Object List into Catesian product.
     * Commit The Simulation, Awaiting feed back from the backend
     * Then Update the Result Context
     */
    const  [simulationStatus, setSimulationStatus] = useState();
    const  [engineSlots, setEngineSlots] = useState(2);
    const  egnine_slots_input = useRef(null);
    const  [dieGenObjList, setDiegenObjList] = useContext(DieselEngienListContext);
    const  [methGenObjList, setMethGenObjList] = useContext(MethanolEngineListContext);
    const  [batObjList, setBatObjList] = useContext(BatteryListContext);
    const  [fcObjList, setFCObjList] = useContext(FuelCellListContext);
    async function handleSimulation () {
        /**
         * @call buildCombinations()
         * @call pasrseDutyCycle()
         * @call markUnrealisticCombos()
         * @call filterIncapableSystem()
         * @call modelicaparameterMapping()
         * @call commitBatchSimulation()
         */
        
        /*Check if components are loaded in list */
        if (dieGenObjList.length === 0 ||methGenObjList.length === 0||batObjList.length === 0){
            alert ("No Generators  or Batterys Were found");
            console.log("Check Database");
            return;
        }

        
        // Build Preliminary combinations
        let combinations = await buildCombinations(
            dieGenObjList, methGenObjList,fcObjList, batObjList, POSSIBLE_BATTERY_COUNT,
            POSSIBLE_OPTIMAL_LOWER_PERCENTAGE,POSSBILE_OPTIMAL_UPPER_PERCENTAGE, engineSlots
        );
        
        // parse Ducty cycle, extract startTime, endTime and max power
        const dutyCycleInfo= await parseDutyCycle();
        
        //mark combination with spacing problems
        combinations= await markUnrealisticCombos({combos : combinations, vollimit: 60000, weighLimit:60000, numslots : engineSlots});
        
        //remove IncapbleSystem
        combinations= await filterIncapbleSystem({combos: combinations, numslots :engineSlots, max_power_required : dutyCycleInfo.maxPower });
        console.log(combinations)
        const mappedParameters = await modelicaParameterMapping(combinations, engineSlots);
        console.log(mappedParameters)
        console.log(dutyCycleInfo)
        //At this point all prepation has completed
        // Prepare to talk to the backend

    
        
        await commitBatchSimulation({ moParams:mappedParameters, startTime: dutyCycleInfo.startTime.toString(), 
            endTime:dutyCycleInfo.endTime.toString(), modelName:"SEACHANGE_TEST_85MCR_batch", numSlot: engineSlots});
    }

    // A separate debug simulation
    async function handleDebug(){
        const debug= singleIteration
        // Debugging case has 1 diesel 1 methanol and no battery
        await commitBatchSimulation({ moParams:debug, startTime: dutyCycleInfo.startTime.toString(), 
            endTime:dutyCycleInfo.endTime.toString(), modelName:"SEACHANGE_TEST_85MCR_batch", numSlot: engineSlots});

    }

    function handleConfirmEngineSlots(){
        const valueEngineSlot = document.getElementById("engine_slots_input").value;
        if (valueEngineSlot !== null && isNaN(valueEngineSlot) && valueEngineSlot >0 && valueEngineSlot){
            setEngineSlots(valueEngineSlot);
        }else{
            alert("Make sure to put a number");
            return;
        }
    }
    return(
    <>  
        <div>
            <label> Number of Generator On Board </label>
            <input 
                type="number"
                placeholder="Enter an integer from 1 to 10" 
                defaultValue={2}
                value = {engineSlots}
                ref ={egnine_slots_input}
                id="engine_slots_input"></input>
            <button onClick={handleConfirmEngineSlots}>Confirm Engine Slots</button>
        </div>
        <div>
            <button onClick={handleSimulation}> Commit Simulation </button>
            <button onClick ={handleDebug}>Debug Run</button>
        </div>
    </>
    )
}
export default SimulateSection;