import { useState, useContext, createContext } from 'react'

import './App.css'
import VesselSpectIput from './componets/ui/VesselSpectInput';
import DataBaseLoader from './componets/ui/DataBaseLoder';
import ModelSelector from './componets/ui/ModelSelector';
import SimulateSection from './componets/ui/SimulateSection';
import DutyCycleLoader from './componets/ui/DutyCycleLoader';

export const DieselEngienListContext = createContext();
export const MethanolEngineListContext = createContext();
export const FuelCellListContext = createContext();
export const BatteryListContext = createContext();
export const WeightLimitContext = createContext();
export const VolumeLimitContext =createContext();
export const DutyCycleContext = createContext();
export const VesselNameTaskName = createContext();
export const BatchSimResults = createContext();
export const DieselTankInfoContext = createContext();
export const MethTankInfoContext = createContext();
export const HydroTankInfoContext = createContext();
function App() {
  /*App Context Zone*/
  /**
   * Include Engine Model List, (which also includes alt fuel engine and fuel cells)
   * Include Battery Model List
   * Include Max Power Dmeand
   * Incldue Start End Time
   * Include Total Weight of Modified System 
   * Include Total Volumn of modified System
   * Vessel Weight Limit 
   * Vessel Volume Limit
   * Simulation Results
   */
  const [dieselEngineObjList, setDieselEngineObjList] = useState([]);
  const [methanolEngineObjList, setMethanolEngineObjList] = useState([]);
  const [fuelCellObjList, setFuelCellObjList] = useState([]);
  const [batteryObjList, setBatteryObjList] = useState([]);
  const [weightLimit, setWeightLimit] = useState(0);
  const [volumeLimit, setVolumeLimit] = useState(0);
  const [dutyCycle, setDutyCycle] = useState({});
  const [vesselNameTaskName, setVesselNameTaskName] = useState([])
  const [batchSimResult, setBatchSimResult] = useState([])
  const [dieselTankInfo, setDiseltankInfo] = useState([])
  const [methTankInfo, setMethTankInfo] = useState([])
  const [hydroTankInfo, setHydrogenTankInfo] = useState([])
  return (
    <>
      <DieselEngienListContext.Provider value ={[dieselEngineObjList, setDieselEngineObjList]}>
        <MethanolEngineListContext.Provider value ={[fuelCellObjList, setFuelCellObjList]}>
          <FuelCellListContext.Provider value ={[methanolEngineObjList, setMethanolEngineObjList]}>
            <BatteryListContext.Provider value ={[batteryObjList, setBatteryObjList]}>
                      <WeightLimitContext.Provider value ={[weightLimit, setWeightLimit]}>
                        <VolumeLimitContext.Provider value ={[volumeLimit, setVolumeLimit]}>
                          <DutyCycleContext.Provider value ={[dutyCycle, setDutyCycle]}>
                            <VesselNameTaskName.Provider value ={[vesselNameTaskName, setVesselNameTaskName]}>
                              <BatchSimResults.Provider value = {[batchSimResult, setBatchSimResult]}>
                                <DieselTankInfoContext.Provider value = {[dieselTankInfo, setDiseltankInfo]}>
                                  <MethTankInfoContext.Provider value= {[methTankInfo, setMethTankInfo]}>
                                    <HydroTankInfoContext.Provider value = {[hydroTankInfo, setHydrogenTankInfo]}>
                                      <VesselSpectIput></VesselSpectIput>
                                      <DutyCycleLoader></DutyCycleLoader>
                                      <DataBaseLoader></DataBaseLoader>
                                      <ModelSelector></ModelSelector>
                                      <SimulateSection></SimulateSection>
                                    </HydroTankInfoContext.Provider>
                                  </MethTankInfoContext.Provider>
                                </DieselTankInfoContext.Provider>
                              </BatchSimResults.Provider>
                            </VesselNameTaskName.Provider>
                          </DutyCycleContext.Provider>
                        </VolumeLimitContext.Provider>
                      </WeightLimitContext.Provider>
            </BatteryListContext.Provider>
          </FuelCellListContext.Provider>
        </MethanolEngineListContext.Provider>
      </DieselEngienListContext.Provider>
    </>
  )
}

export default App
