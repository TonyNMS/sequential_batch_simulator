
const readCSV =async (path)=>{
    let temp_battery_container;
    // Read CSV and Extract Rows 
    let rows;
    
    try{
        const res = await fetch(path);
        const text = await res.text();
        rows = text.trim().split(/\r?\n/).map(row => parseCsvLine(row));
    }catch(e){
        console.error(e)
    }
    const tempRes  =  extractGeneratorAndFuelCell(rows);
    temp_battery_container = extractBattery(rows);
    // Return elements in temp_battery_container
    // 0 = diesel eng list, 1 = meth engine list, 2 = hydrogen engine lis
    return [tempRes[0], tempRes[1], tempRes[2], temp_battery_container];
}
export default readCSV

function extractGeneratorAndFuelCell (rows) {
    /**
     * From CSV Extract All of the Diesle, Methanol Generator, as well as Fuel Cell
     * returns list of Generators
     */
    const temp_die_eng_container = [];
    const temp_alt_eng_container = [];
    const temp_fuelcell_container=[];

    let i = 1;
    while (i < rows.length){
        // extracting the first row
        const row =rows[i];
        // if the row is empty, skip this row and keep going 
        if (!row||row.length ===0){i++; continue}
        const name = row[0]?.trim();
        const fuel = row[6]?.trim();
        if (!name || !fuel){i++; continue}
        if (fuel === "Diesel" || fuel === "Methanol" || fuel === "FC"){
            const engineObj ={
                engine_name: name,
                engine_p_max: Number(row[1]),
                engine_p_min: Number(row[2]),
                engine_cost: Number(row[3]),
                engine_mass: Number(row[4]),
                engine_volume: Number(row[5]),
                engine_bsfc: row[7]?.toString() ?? "",
                engine_fcc:  row[8]?.toString() ?? "",
                engine_fuel_type: fuel,
                engine_db_index: row[9]?.toString() ?? "default_eng_idx",
                engine_retrofit_cost:Number(row[10])
            };
            if (fuel === "Diesel") {temp_die_eng_container.push(engineObj)};
            if (fuel === "Methanol") {temp_alt_eng_container.push(engineObj)};
            if (fuel === "FC") {temp_fuelcell_container.push(engineObj)};
            i++;
        }
    }
    return [temp_die_eng_container, temp_alt_eng_container, temp_fuelcell_container];
}

function extractBattery (rows){
    /**
     * From CSV Extract All of the Battery
     * returns list of Generators
     */
    const temp_battery_container = [];
    let i = 1;
    while (i < rows.length){
        const row = rows[i];
        if (!row || row.length === 0) { i++; continue; }

        const name     = row[11]?.trim();  
        if (!name) { i++; continue; }    

        const cap      = Number(row[12]); 
        const cost     = Number(row[13]);
        const mass     = Number(row[14]);
        const volume   = Number(row[15]);
        const voltage  = Number(row[16]);
        const current  = Number(row[17]);
        const cRate    = Number(row[18]);
        const bat_db_idx = row[19]?.toString() ?? "DF_DB_IDX";
        const bat_abb = row[20]?.toString() ?? "DF_ABB";
        const bat_cyl_lim = Number(row[21]);
      
        temp_battery_container.push({
            battery_name: name,
            battery_capcity: cap,
            battery_cost: cost,
            battery_mass: mass,
            battery_volume: volume,
            battery_voltage: voltage,
            battery_current: current,
            battery_max_c_rate: cRate,
            battery_charge_rate: cRate * current,
            battery_max_charge_power: voltage * current,
            battery_db_index:bat_db_idx,
            battery_abbreviation: bat_abb,
            battery_cycle_limit:bat_cyl_lim
        });
        i++
    }
    return temp_battery_container;
}

function parseCsvLine(line) {
  const result = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];

    if (char === '"') {
      // Handle escaped double quote ("")
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i++; // skip the next "
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === "," && !inQuotes) {
      // Only split on commas that are NOT inside quotes
      result.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  result.push(current);
  return result;
}
