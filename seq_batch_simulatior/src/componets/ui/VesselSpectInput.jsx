import React, { useContext, useRef } from "react";
import {VolumeLimitContext, WeightLimitContext, VesselNameTaskName, DieselTankInfoContext, MethTankInfoContext, HydroTankInfoContext} from "../../App.jsx"
const VesselSpectIput =()=>{
    /*This Component Updated the Vessel and Task Specification*/

    /*Retriving the context of weight limit. volume limit and Vessel Name/ Task Name  */

    const [VesselWeightLimitContext, setVesselWeightLimitContext] = useContext(VolumeLimitContext);
    const [VesselVolumeLimitContext, setVesselVolumeLimitConte] = useContext(WeightLimitContext);
    const [VesselNameTaskNameContext, setVesselNameTestNameContext] = useContext(VesselNameTaskName);
    const [dieTankVolContext, setDieTankContext] = useContext(DieselTankInfoContext);
    const [methTankVolContext, setMethTankContext] = useContext(MethTankInfoContext);
    const [hydroTankVolContext, setHydroTankContext] = useContext(HydroTankInfoContext);
    // Refs for inputs (no re-render while typing)
    const vesselNameRef = useRef(null);
    const taskNameRef = useRef(null);
    const weightLimitRef = useRef(null);
    const volumeLimitRef = useRef(null); 
    const dieTankVolRef  = useRef(null); 
    const methTankVolRef= useRef(null); 
    const hydroTankVolRef = useRef(null);
    const dieTankVolLimRef = useRef(null); 
    const methTankVolLimRef= useRef(null);
    const hydroTankVolLimRef = useRef(null);

    function handleConfirmInput() {
      const vesselName = vesselNameRef.current?.value.trim();
      const taskName = taskNameRef.current?.value.trim();
      const weightLimit = weightLimitRef.current?.value;
      const volumeLimit = volumeLimitRef.current?.value;
      const dieTankVol = dieTankVolRef.current? dieTankVolRef.current.value : "230236"
      const methTankVol = methTankVolRef.current? methTankVolRef.current.value : "230236"
      const hydroTankVol = hydroTankVolRef.current? hydroTankVolRef.current.value : "230236"
      const dieTankVolLim = dieTankVolLimRef.current? dieTankVolLimRef.current.value : "0.85"
      const methTankVolLim = methTankVolLimRef.current? methTankVolLimRef.current.value : "0.85"
      const hydroTankVolLim = hydroTankVolLimRef.current? hydroTankVolLimRef.current.value : "0.85"
      // Basic validation
      if (!vesselName || !taskName || !weightLimit || !volumeLimit) {
        alert("Please fill in all fields before confirming.")
        console.warn("Please fill in all fields before confirming.");
        return;
      }

      // Update contexts
      setVesselNameTestNameContext([vesselName, taskName]);
      setVesselWeightLimitContext(Number(weightLimit));
      setVesselVolumeLimitConte(Number(volumeLimit));
      setDieTankContext([dieTankVol, dieTankVolLim]);
      setMethTankContext([methTankVol, methTankVolLim]);
      setHydroTankContext([hydroTankVol, hydroTankVolLim]);
    }
    return (
    <>
      <div>
        <div>
          <>
            <p>Confirm Your Vessel Name</p>
            <input
              type="text"
              name="vessel_name"
              ref={vesselNameRef}
              placeholder="Vessel name"
            />
            <p>Input Task Name</p>
            <input
              type="text"
              name="task_name"
              ref={taskNameRef}
              placeholder="Task name"
            />
          </>
        </div>

        <div>
          <>
            <p>Confirm Diesel Fuel Mass </p>
            <div>
               <input type="number" name="diesel_mass" ref={dieTankVolRef}  placeholder="Diesel Mass (Ton)"/>
               <input type="number" name="avalible_tank_percetage" ref={dieTankVolLimRef} placeholder="Diesel Tank Avalible %"/>
            </div>
            <p>Confirm Alterntive Fuel Mass</p>
            <div>
                <input type="number" name="alt_fuel_mass" ref={methTankVolRef} placeholder="AltFuel Mass"/>
                <input type="number" name="avalible_tank_percetage" ref={methTankVolLimRef} placeholder="Altfuel Tank Avalible %"/>
            </div>
            <p>Confirm Hydrogen Fuel Tank Mass</p>
              <div>
                <input type="number" name="hydro_fuel_mass" ref={hydroTankVolRef} placeholder="Hydrogen Mass"/>
                <input type="number" name="hydro_tank_percetage" ref = {hydroTankVolLimRef} placeholder="Hydrogen Tank Avalible %"/>
              </div>

            <p>Confirm the Weight Limit on the vessel</p>
            <input
              type="number"
              name="weight_limit"
              ref={weightLimitRef}
              placeholder="Weight limit"
            />
            <p>Confirm the Volume Limit on the vessel</p>
            <input
              type="number"
              name="volume_limit"
              ref={volumeLimitRef}
              placeholder="Volume limit"
            />
            <button onClick={handleConfirmInput}>Confirm</button>
          </>
          
        </div>
      </div>
    </>
  );
}
export  default VesselSpectIput;