import React, { createContext, useContext, useState } from "react";
import { buildCombinations, commitBatchSimulation, markUnrealisticCombos, modelicaParameterMapping, filterIncapbleSystem, parseDutyCycle } from "../funtion_utils/SimulateSectionUtil.jsx";
import { BatteryListContext, DieselEngienListContext, FuelCellListContext, MethanolEngineListContext } from "../../App";
import { dutyCycleInfo, singleIteration } from "../funtion_utils/TestingConfigUnits.jsx";

const  POSSIBLE_BATTERY_COUNT = [0,1]
const  POSSIBLE_OPTIMAL_LOWER_PERCENTAGE = [0.05]
const  POSSBILE_OPTIMAL_UPPER_PERCENTAGE = [0.05]
const SimulateSection =()=>{
    /**
     * Parse the Battery / Generator Object List into Catesian product.
     * Commit The Simulation, Awaiting feed back from the backend
     * Then Update the Result Context
     */
    const  [simulationStatus, setSimulationStatus] = useState();
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
        const numSlots = 3
        
        // Build Preliminary combinations
        let combinations = await buildCombinations(
            dieGenObjList, methGenObjList,fcObjList, batObjList, POSSIBLE_BATTERY_COUNT,
            POSSIBLE_OPTIMAL_LOWER_PERCENTAGE,POSSBILE_OPTIMAL_UPPER_PERCENTAGE, numSlots
        );
        
        // parse Ducty cycle, extract startTime, endTime and max power
        const dutyCycleInfo= await parseDutyCycle();
        
        //mark combination with spacing problems
        combinations= await markUnrealisticCombos({combos : combinations, vollimit: 60000, weighLimit:60000, numslots : numSlots});
        
        //remove IncapbleSystem
        combinations= await filterIncapbleSystem({combos: combinations, numslots :numSlots, max_power_required : dutyCycleInfo.maxPower });
        console.log(combinations)
        const mappedParameters = await modelicaParameterMapping(combinations, numSlots);
        console.log(mappedParameters)
        console.log(dutyCycleInfo)
        //At this point all prepation has completed
        // Prepare to talk to the backend

    
         
        await commitBatchSimulation({ moParams:mappedParameters, startTime: dutyCycleInfo.startTime.toString(), 
            endTime:dutyCycleInfo.endTime.toString(), modelName:"SEA_CHANGE_TEST1", numSlot: numSlots});
    }
    async function handleDebug(){
        const debug= singleIteration
        await commitBatchSimulation({ moParams:debug, startTime: dutyCycleInfo.startTime.toString(), 
            endTime:dutyCycleInfo.endTime.toString(), modelName:"SEA_CHANGE_TEST1", numSlot: 3});

    }
    return(
    <>
        <div>
            <button onClick={handleSimulation}> Commit Simulation </button>
            <button onClick ={handleDebug}>Debug Run</button>
        </div>
    </>
    )
}
export default SimulateSection;