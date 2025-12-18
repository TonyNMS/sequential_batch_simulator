import React, { createContext, useContext, useRef, useState } from "react";
import { buildCombinations, commitBatchSimulation, markUnrealisticCombos, modelicaParameterMapping, filterIncapbleSystem} from "../funtion_utils/SimulateSectionUtil.jsx";
import { BatteryListContext, DieselEngienListContext, FuelCellListContext, MethanolEngineListContext, DutyCycleContext, VolumeLimitContext, WeightLimitContext, VesselNameTaskName } from "../../App";
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
    const  egnine_slots_input = useRef(null);
    const  [dieGenObjList, setDiegenObjList] = useContext(DieselEngienListContext);
    const  [methGenObjList, setMethGenObjList] = useContext(MethanolEngineListContext);
    const  [batObjList, setBatObjList] = useContext(BatteryListContext);
    const  [fcObjList, setFCObjList] = useContext(FuelCellListContext);
    const  [dutyCycleObject, setDutyCycleObject] = useContext(DutyCycleContext);
    const  [volLimit, setVolumnLimit] = useContext(VolumeLimitContext);
    const  [weightLim, setWeightLimit] = useContext(WeightLimitContext);
    const  [taskVesselName, setTaskName] = useContext(VesselNameTaskName);
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
        volLimit ? Number(volLimit): 60000 
        weightLim ? Number(weightLim) : 60000
        taskVesselName[0] ? taskVesselName[0] : "PlaceHolderVessel" 
        taskVesselName[1] ? taskVesselName[1] : "PlaceHolderTask"
        // Build Preliminary combinations
        let combinations = await buildCombinations(
            dieGenObjList, methGenObjList,fcObjList, batObjList, POSSIBLE_BATTERY_COUNT,
            POSSIBLE_OPTIMAL_LOWER_PERCENTAGE,POSSBILE_OPTIMAL_UPPER_PERCENTAGE, egnine_slots_input.current? Number(egnine_slots_input.current.value) : 1);
        

        //mark combination with spacing problems
        combinations= await markUnrealisticCombos({
            combos : combinations, vollimit: volLimit ? Number(volLimit): 60000, 
            weighLimit:weightLim ? Number(weightLim) : 60000, 
            numslots : egnine_slots_input.current? Number(egnine_slots_input.current.value) : 1});
        
        //remove IncapbleSystem
        combinations= await filterIncapbleSystem({
            combos: combinations, 
            numslots :egnine_slots_input.current? Number(egnine_slots_input.current.value) : 1, 
            max_power_required : dutyCycleObject.maxPower });
        console.log(combinations)
        const mappedParameters = await modelicaParameterMapping(
            combinations, 
            egnine_slots_input.current? Number(egnine_slots_input.current.value) : 1, 
            dutyCycleObject.dutyCyclePath.replace(/\\/g, "/"));
        console.log(mappedParameters)
        console.log(dutyCycleObject)

        //At this point all prepation has completed
        // Prepare to talk to the backend
        await commitBatchSimulation({ 
            moParams:mappedParameters, 
            startTime: dutyCycleObject.startTime.toString(), 
            endTime:dutyCycleObject.endTime.toString(), 
            modelName:"SEACHANGE_TEST_85MCR_batch", 
            numSlot: egnine_slots_input.current? Number(egnine_slots_input.current.value) : 1,
            vesselName: taskVesselName[0] ? taskVesselName[0] : "PlaceHolderVessel",
            taskName:  taskVesselName[1] ? taskVesselName[1] : "PlaceHolderTask"});
    }

    // A separate debug simulation
    async function handleDebug(){
        const debug= singleIteration
        // Debugging case has 1 diesel 1 methanol and no battery
        await commitBatchSimulation({ moParams:debug, startTime: dutyCycleInfo.startTime.toString(), 
            endTime:dutyCycleInfo.endTime.toString(), modelName:"SEACHANGE_TEST_85MCR_batch", numSlot: egnine_slots_input.current? Number(egnine_slots_input.current.value) : 1});

    }
    return(
    <>  
        <div>
            <label> Number of Generator On Board </label>
            <input 
                type="number"
                placeholder="Enter an integer from 1 to 10" 
                ref ={egnine_slots_input}
                id="engine_slots_input"></input>
        </div>
        <div>
            <button onClick={handleSimulation}> Commit Simulation </button>
            <button onClick ={handleDebug}>Debug Run</button>
        </div>
    </>
    )
}
export default SimulateSection;