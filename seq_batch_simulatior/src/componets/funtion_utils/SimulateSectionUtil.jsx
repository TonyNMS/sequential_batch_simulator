import React from "react";

export const commitBatchSimulation = ()=>{
    /**
     * Inform Backed to start simulation
     * Need Filtered Power Train Configuration Input
     * Need Model Name
     * Returns Simulation Results
     */


}

export function cartesianProducts(arrays){
    /**
     * Takes an array of flattend (Diesel Engine / Count)(AltGen / Count)(Battery /Count) sub arries 
     * Returns the flattened array of all possible combination 
     */

}
export async function buildCombinations(dieList, methList, fcList, batList, POS_DIE_COUNT, 
    POS_METH_COUNT, POS_BAT_COUNT, POS_OPT_LOW, POS_OPT_HIGHER){
    /**
     * Takes in list of generators (meth and die), list of batteries, list of fuel cell
     * Takes in possbile numbers of generatos, fuel cell and batteries
     * Takes in possble bound 
     * ## ASSUME THERE 5
     */
    const combinedList = [...dieList, ...methList, ...fcList];
    
    const engineOptions =combinedList.flatMap(engine =>
        POS_OPT_LOW.flatMap(lo=>
            POS_OPT_HIGHER.map(hi=>({
                engine,lo,hi
            }))
        )
    )
    

}  
export async function modelicaParameterMapping(){
    /**
     * 
     */
}
export function filterOutUnrealisticCombos(combos){

}

function sequenceOfLength(oengineOptions, length){
    /**
     * This a local helper function, create all possible 
     */
}
