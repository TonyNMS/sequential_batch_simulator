import React, { createContext, useContext, useState } from "react";
import { buildCombinations, commitBatchSimulation } from "../funtion_utils/SimulateSectionUtil";
import { BatteryListContext, DieselEngienListContext, FuelCellListContext, MethanolEngineListContext } from "../../App";

const  POSSIBLE_DIESEL_GEN_COUNT = [1,2,3,4,5]
const  POSSIBLE_ALT_FUEL_GEN_COUNT = [0]
const  POSSIBLE_BATTERY_COUNT = [0,1,2,5,10,15,16,20,25]
const  POSSIBLE_OPTIMAL_LOWER_PERCENTAGE = [0.5,1,2,3,4,5]
const  POSSBILE_OPTIMAL_UPPER_PERCENTAGE = [0.5,1,2,3,4,5]
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
         * @call filterOutUnrealisticCombos()
         * @call modelicaparameterMapping()
         * @call commitBatchSimulation()
         */
        
        /*Check if components are loaded in list */

        if (dieGenObjList.length === 0 ||methGenObjList.length === 0||batObjList.length === 0){
            alert ("No Generators  or Batterys Were found");
            console.log("Check Database");
            return;
        }

        const combinations = buildCombinations(
            dieGenObjList, methGenObjList,fcObjList, batObjList, 
            POSSIBLE_DIESEL_GEN_COUNT, POSSIBLE_ALT_FUEL_GEN_COUNT, POSSIBLE_BATTERY_COUNT,
            POSSIBLE_OPTIMAL_LOWER_PERCENTAGE,POSSBILE_OPTIMAL_UPPER_PERCENTAGE
        )
        commitBatchSimulation();
    }
    return(
    <>
        <div>
            <button> Commite Simulation </button>
        </div>
    </>
    )
}
export default SimulateSection;