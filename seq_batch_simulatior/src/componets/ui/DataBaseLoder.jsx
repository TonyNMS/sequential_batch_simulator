import React, { useState, useContext } from "react";
import { BatteryListContext, DieselEngienListContext, FuelCellListContext, MethanolEngineListContext } from "../../App";
import readCSV from "../funtion_utils/DatabseLoaderUtils";

import SimpleDatabaseUrl from "../../assets/temp_db_assets/simple_db_with_bsfc.csv?url"
import FullDatabseUrl from "../../assets/temp_db_assets/FullDatabase.csv?url"
const DataBaseLoader =()=>{
    /**
     * Read the Selected Database CSV 
     * Convert them into FC, Diesel , Methanol Object List 
     * Tehn send it back as context
     *      
     * */
    const [useSimpleDatabasem , setUseSimpleDatabase] = useState(true);
    const [diselGeneratorObjList, setDieselGeneratorObjList] = useContext(DieselEngienListContext);
    const [methnaolGeneratorObjList, setMethnaolGeneratorObjList] = useContext(MethanolEngineListContext);
    const [fuelCellObjList, setFuelCellObjList] = useContext(FuelCellListContext);
    const [batteryListObjContext, setBatteryObjList] = useContext(BatteryListContext);
    function handleChangeDatabase (){
        /**
         * Change the database pointer (new URL)
         * Then clear the previous context
         */
        setUseSimpleDatabase(!useSimpleDatabasem); // set state for local rendereing
        setDieselGeneratorObjList([]) // reset contexts
        setMethnaolGeneratorObjList([]) 
        setFuelCellObjList([])
        setBatteryObjList([])
    }
    async function  handleDatabaseSelection  (){
        /**
         * Call the selected CSV 
         * Parse all of the Diesel,Methanol, Fuel Cell, and Battery 
         */
        // Select the proper URL
        const db_url = useSimpleDatabasem ? SimpleDatabaseUrl : FullDatabseUrl;
        // Read the CSV and populate the temp object containers
        const tempRes  = await readCSV(db_url);
        // upload the Objects to the context
        console.log (tempRes);
        setDieselGeneratorObjList(tempRes[0]);
        setMethnaolGeneratorObjList(tempRes[1]);
        setFuelCellObjList(tempRes[2]);
        setBatteryObjList(tempRes[3]);
    }

    return (
        <>
            <div>
                <button onClick={handleChangeDatabase}> {useSimpleDatabasem ? "Simple Databse" : "Fuell Database"}</button>
                <button onClick ={handleDatabaseSelection}> Confirm </button>
            </div>
        </>
    )
}
export default DataBaseLoader