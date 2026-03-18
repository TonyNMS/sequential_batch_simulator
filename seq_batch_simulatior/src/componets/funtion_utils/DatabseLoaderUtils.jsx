
const DEFAULT_YIELD_EVERY = 500;

const yieldToMain = () =>
  new Promise((resolve) => {
    if (typeof requestAnimationFrame === "function") {
      requestAnimationFrame(() => resolve());
      return;
    }
    setTimeout(resolve, 0);
  });

const readCSV = async (path, options = {}) => {
    const yieldEvery = options.yieldEvery ?? DEFAULT_YIELD_EVERY;
    const temp_die_eng_container = [];
    const temp_alt_eng_container = [];
    const temp_fuelcell_container = [];
    const temp_battery_container = [];

    try {
        const res = await fetch(path);
        if (!res.ok) {
            throw new Error(`Failed to load CSV: ${res.status}`);
        }
        const text = await res.text();
        if (!text.trim()) {
            return [temp_die_eng_container, temp_alt_eng_container, temp_fuelcell_container, temp_battery_container];
        }
        const lines = text.trim().split(/\r?\n/);

        for (let i = 1; i < lines.length; i++) {
            const line = lines[i];
            if (!line) {
                continue;
            }
            const row = parseCsvLine(line);
            if (!row || row.length === 0) {
                continue;
            }

            const name = row[0]?.trim();
            const fuel = row[6]?.trim();
            if (name && fuel && (fuel === "Diesel" || fuel === "Methanol" || fuel === "FC" || fuel === "MIX20"|| fuel === "MIX30"|| fuel === "MIX50")) {
                const engineObj = {
                    engine_name: name,
                    engine_p_max: Number(row[1]),
                    engine_p_min: Number(row[2]),
                    engine_cost: Number(row[3]),
                    engine_mass: Number(row[4]),
                    engine_volume: Number(row[5]),
                    engine_bsfc: row[7]?.toString() ?? "",
                    engine_fcc: row[8]?.toString() ?? "",
                    engine_fuel_type: fuel,
                    engine_db_index: row[9]?.toString() ?? "default_eng_idx",
                    engine_retrofit_cost: Number(row[10])
                };
                if (fuel === "Diesel" || fuel === "MIX20"|| fuel === "MIX30"|| fuel === "MIX50") {
                    temp_die_eng_container.push(engineObj);
                }
                if (fuel === "Methanol") {
                    temp_alt_eng_container.push(engineObj);
                }
                if (fuel === "FC") {
                    temp_fuelcell_container.push(engineObj);
                }
            }

            const batName = row[11]?.trim();
            if (batName) {
                const cap = Number(row[12]);
                const cost = Number(row[13]);
                const mass = Number(row[14]);
                const volume = Number(row[15]);
                const voltage = Number(row[16]);
                const current = Number(row[17]);
                const cRate = Number(row[18]);
                const bat_db_idx = row[19]?.toString() ?? "DF_DB_IDX";
                const bat_abb = row[20]?.toString() ?? "DF_ABB";
                const bat_cyl_lim = Number(row[21]);

                temp_battery_container.push({
                    battery_name: batName,
                    battery_capcity: cap,
                    battery_cost: cost,
                    battery_mass: mass,
                    battery_volume: volume,
                    battery_voltage: voltage,
                    battery_current: current,
                    battery_max_c_rate: cRate,
                    battery_charge_rate: cRate * current,
                    battery_max_charge_power: voltage * current,
                    battery_db_index: bat_db_idx,
                    battery_abbreviation: bat_abb,
                    battery_cycle_limit: bat_cyl_lim
                });
            }

            if (i % yieldEvery === 0) {
                await yieldToMain();
            }
        }
    } catch (e) {
        console.error(e);
    }

    return [temp_die_eng_container, temp_alt_eng_container, temp_fuelcell_container, temp_battery_container];
};
export default readCSV

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
