import { useState, useContext, createContext } from 'react'

import './App.css'
import VesselSpectIput from './componets/ui/VesselSpectInput';
import DataBaseLoader from './componets/ui/DataBaseLoder';
import ModelSelector from './componets/ui/ModelSelector';
import SimulateSection from './componets/ui/SimulateSection';

export const DieselEngienListContext = createContext();
export const MethanolEngineListContext = createContext();
export const FuelCellListContext = createContext();
export const BatteryListContext = createContext();
export const MaxPowerDemandContext = createContext();
export const StartAndStopTimeContext = createContext();
export const SystemTotalWeightContext = createContext();
export const SystemTotalVolumeContext = createContext();
export const WeightLimitContext = createContext();
export const VolumeLimitContext =createContext();
export const DutyCycleContext = createContext();
export const VesselNameTaskName = createContext();
export const BatchSimResults = createContext();
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
  const [maxPowerDemand, setMaxPowerDemand] = useState(0);
  const [startAndStopTime, setStartAndStopTime] = useState();
  const [systemTotalWeight, setSystemTotalWeight] = useState(0);
  const [systemTotalVolume, setSystemTotalVolume] = useState(0);
  const [weightLimit, setWeightLimit] = useState(0);
  const [volumeLimit, setVolumeLimit] = useState(0);
  const [dutyCycle, setDutyCycle] = useState([]);
  const [vesselNameTaskName, setVesselNameTaskName] = useState([])
  const [batchSimResult, setBatchSimResult] = useState([])
  return (
    <>
      <DieselEngienListContext.Provider value ={[dieselEngineObjList, setDieselEngineObjList]}>
        <MethanolEngineListContext.Provider value ={[fuelCellObjList, setFuelCellObjList]}>
          <FuelCellListContext.Provider value ={[methanolEngineObjList, setMethanolEngineObjList]}>
            <BatteryListContext.Provider value ={[batteryObjList, setBatteryObjList]}>
              <MaxPowerDemandContext.Provider value = {[maxPowerDemand, setMaxPowerDemand]}>
                <StartAndStopTimeContext.Provider value ={[startAndStopTime, setStartAndStopTime]}>
                  <SystemTotalWeightContext.Provider value ={[systemTotalWeight, setSystemTotalWeight]}>
                    <SystemTotalVolumeContext.Provider value ={[systemTotalVolume, setSystemTotalVolume]}>
                      <WeightLimitContext.Provider value ={[weightLimit, setWeightLimit]}>
                        <VolumeLimitContext.Provider value ={[volumeLimit, setVolumeLimit]}>
                          <DutyCycleContext.Provider value ={[dutyCycle, setDutyCycle]}>
                            <VesselNameTaskName.Provider value ={[vesselNameTaskName, setVesselNameTaskName]}>
                              <BatchSimResults.Provider value = {[batchSimResult, setBatchSimResult]}>
                                <VesselSpectIput></VesselSpectIput>
                                <DataBaseLoader></DataBaseLoader>
                                <ModelSelector></ModelSelector>
                                <SimulateSection></SimulateSection>
                              </BatchSimResults.Provider>
                            </VesselNameTaskName.Provider>
                          </DutyCycleContext.Provider>
                        </VolumeLimitContext.Provider>
                      </WeightLimitContext.Provider>
                    </SystemTotalVolumeContext.Provider>
                  </SystemTotalWeightContext.Provider>
                </StartAndStopTimeContext.Provider>
              </MaxPowerDemandContext.Provider>
            </BatteryListContext.Provider>
          </FuelCellListContext.Provider>
        </MethanolEngineListContext.Provider>
      </DieselEngienListContext.Provider>
    </>
  )
}

export default App
