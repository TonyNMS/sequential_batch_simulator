# Sequential Batch Simulator Handover

Last reviewed: 2026-05-19

## Purpose

The Sequential Batch Simulator is a local desktop/web workflow for comparing vessel power-train configurations against a duty cycle. The React frontend lets a user load a vessel specification, a component database, a Modelica vessel model, and a duty-cycle text file. The Flask backend then runs OpenModelica simulations for generated configuration combinations, calculates fuel/emissions metrics, stores batch results, and exports Excel workbooks.

The repository has two main applications:

- `seq_batch_simulatior/`: React + Vite frontend.
- `omserver/omserver/`: Flask backend that talks to OpenModelica through ZMQ.

Note: the frontend folder is currently named `seq_batch_simulatior` and several component folders/files use misspellings such as `componets`, `funtion_utils`, `DataBaseLoder`, and `VesselSpectInput`. Keep these names unless you are doing a deliberate rename across imports.

## Current Architecture

```text
User browser
  |
  | HTTP requests to http://127.0.0.1:5000
  v
React/Vite frontend
  |
  | Uploads model and duty cycle, posts generated batch configs
  v
Flask backend: omserver
  |
  | Starts OpenModelica compiler process through OMCConnection
  v
OpenModelica simulation
  |
  | Writes CSV outputs into Flask instance folder
  v
Result processing, emissions calculation, JSON DB, Excel export
```

## Key Files

### Frontend

- `seq_batch_simulatior/src/App.jsx`: application context providers and top-level component ordering.
- `seq_batch_simulatior/src/componets/ui/VesselSpectInput.jsx`: vessel name, task name, weight/volume limits, and tank inputs.
- `seq_batch_simulatior/src/componets/ui/DutyCycleLoader.jsx`: uploads `.txt` duty-cycle files to the backend.
- `seq_batch_simulatior/src/componets/ui/DataBaseLoder.jsx`: loads simple or full component CSV assets into React state.
- `seq_batch_simulatior/src/componets/ui/ModelSelector.jsx`: uploads the selected Modelica `.mo` file to the backend.
- `seq_batch_simulatior/src/componets/ui/SimulateSection.jsx`: generates configuration combinations and starts batch simulation.
- `seq_batch_simulatior/src/componets/funtion_utils/SimulateSectionUtil.jsx`: combination generation, filtering, Modelica parameter mapping, and `/seq_model/simulate_batch` call.
- `seq_batch_simulatior/src/assets/temp_db_assets/`: bundled component databases.
- `seq_batch_simulatior/src/assets/model_assets/`: bundled Modelica models and sample duty cycles.

### Backend

- `omserver/omserver/src/omserver/__init__.py`: Flask app factory, CORS setup, blueprint registration.
- `omserver/omserver/src/omserver/seq_model.py`: active sequential simulation API used by the frontend.
- `omserver/omserver/src/omserver/model.py`: older/general model API with extra reporting endpoints.
- `omserver/omserver/src/omserver/OMCConnection.py`: starts `omc` and communicates over ZMQ.
- `omserver/omserver/src/omserver/ModelicaSequentialParaPaser.py`: rewrites BSFC, fuel-consumption tables, and generator switches in uploaded `.mo` files.
- `omserver/omserver/src/omserver/EUEmissionCalculator.py`: FuelEU/CO2 and penalty calculations.
- `omserver/omserver/src/omserver/ExcelGenerator.py`: batch result Excel export.
- `omserver/omserver/src/omserver/lookup_tables/`: fuel properties and biofuel emission factors.
- `omserver/omserver/tests/`: legacy tests for the older `/model` API.

## Local Setup

### Prerequisites

- Node.js and npm for the Vite frontend.
- Python 3.12 or higher.
- PDM for backend dependency management.
- OpenModelica installed locally.
- Windows users should confirm the OpenModelica executable exists at one of:
  - `C:\Program Files\OpenModelica1.22.1-64bit\bin\omc.exe`
  - `%OMC_EXE%`
  - `%OPENMODELICAHOME%\bin\omc.exe`
  - any `omc.exe` visible on `PATH`

`OMCConnection.py` currently checks the hardcoded OpenModelica 1.22.1 path first, then environment variables and PATH.

### Backend

From `omserver/omserver`:

```powershell
pdm install
cd src
pdm run flask --app omserver run --debug
```

Expected backend URL:

```text
http://127.0.0.1:5000
```

The frontend has this backend URL hardcoded in several files. If the backend port changes, update those fetch calls or introduce a Vite environment variable.

### Frontend

From `seq_batch_simulatior`:

```powershell
npm install
npm run dev
```

Vite will print the frontend URL, usually:

```text
http://localhost:5173
```

## Normal User Workflow

1. Start the Flask backend.
2. Start the Vite frontend.
3. Open the frontend in a browser.
4. Enter vessel name, task name, tank values, and vessel weight/volume limits, then press `Confirm`.
5. Upload a duty-cycle `.txt` file. The backend stores the file in the Flask instance folder and returns:
   - absolute duty-cycle file path
   - start time
   - end time
   - maximum power
6. Choose and confirm the component database.
7. Press `Load Sequential Model` to upload `SEACHANGE_TEST_85MCR_batch.mo` to the backend instance folder.
8. Enter number of generator slots.
9. Optionally set methanol mass percentage and toggle max power guard.
10. Press `Commit Simulation`.
11. Wait for backend simulation logs. On completion, the backend stores the batch in `res_db.json` and writes an Excel workbook into the Flask instance folder.

## Active API Contract

### `POST /seq_model/upload`

Uploads a Modelica model to the Flask instance folder.

Request JSON:

```json
{
  "model_name": "SEACHANGE_TEST_85MCR_batch",
  "model_data": "base64-encoded .mo file"
}
```

Response:

```json
{
  "name": "SEACHANGE_TEST_85MCR_batch",
  "status": "Model written"
}
```

### `POST /seq_model/upload_dutyCycle`

Uploads a duty-cycle `.txt` file using multipart form-data with a `file` field.

Response:

```json
{
  "status": true,
  "file_path": "absolute path to saved file",
  "startTime": 0,
  "endTime": 12345,
  "maxPower": 999999
}
```

The parser skips the first two lines and reads time/power from whitespace-separated columns.

### `POST /seq_model/simulate_batch`

Runs the sequential batch simulation.

Request JSON fields currently sent by the frontend:

```json
{
  "model_name": "SEACHANGE_TEST_85MCR_batch",
  "start_time": "0",
  "stop_time": "12345",
  "list_of_config_combinations": [],
  "number_of_slots": 3,
  "vesselName": "DefaultVessel",
  "taskName": "DefaultTask",
  "methMassFraction": 0.2
}
```

Important structure inside each combination:

- `instance.config.slot 1`, `slot 2`, `slot 3`, etc. hold engine/fuel-cell objects or `null`.
- `instance.config.slot N_lower` and `slot N_upper` hold operating bounds.
- `instance.config.battery` holds a battery object.
- `instance.config.battery_count` holds the battery count.
- `modelica_parameters` holds `{ "param": "...", "value": "..." }` override pairs for OpenModelica.

Current response is minimal:

```json
{
  "avalible_batches": []
}
```

Most useful output is written to files rather than returned to the browser.

## Simulation Flow

1. Frontend parses the component CSV into diesel, methanol, fuel-cell, and battery lists.
2. `buildCombinations` creates ordered generator/fuel-cell slot combinations and battery-count combinations.
3. `markUnrealisticCombos` marks combinations over the volume/weight limits. At present, the marking is not used to filter the list before simulation.
4. `filterIncapbleSystem` optionally removes configurations whose generator power cannot exceed duty-cycle peak demand.
5. `modelicaParameterMapping` converts selected engines, batteries, fuel types, duty-cycle path, and control bounds into Modelica override parameters.
6. Backend receives the batch and loops over every configuration.
7. For each configuration, `ModelicaSequentialParamParser` rewrites the uploaded `.mo` file's BSFC/FCC arrays and generator switches.
8. Backend calls OpenModelica through `OMCConnection`, runs `simulate(...)`, and reads `{model_name}_res.csv`.
9. `process_simmultion_result` extracts time series, generator power, battery power/SOC, energy totals, fuel usage, emissions, penalties, and configuration metadata.
10. Backend appends the batch to `res_db.json`.
11. `ExcelGenerator` writes a multi-sheet `.xlsx` workbook with batch summary, iteration overview, and detailed iteration sheets.

## Data Inputs

### Component CSV

The frontend CSV parser expects columns by position:

- Engine fields: name, max power, min power, cost, mass, volume, fuel type, BSFC, FCC, database index, retrofit cost.
- Battery fields: name, capacity, cost, mass, volume, voltage, current, C-rate, database index, abbreviation, cycle limit.

Recognized fuel types include:

- `Diesel`
- `Methanol`
- `FC`
- `MIX5`, `MIX20`, `MIX30`, `MIX40`, `MIX50`, `MIX60`, `MIX70`, `MIX80`, `MIX90`, `MIX97`
- `HFO`, `HFO_MIX60`, `HFO_MIX80`, `HFO_MIX90`

### Duty Cycle

Duty-cycle files must be `.txt`. The backend expects two header lines followed by whitespace-separated data rows. The first column is time, the second column is power.

### Modelica Model

The active frontend uploads:

```text
seq_batch_simulatior/src/assets/model_assets/SEACHANGE_TEST_85MCR_batch.mo
```

The model must contain parameter names that match the frontend override generation and backend parser, including:

- `genN_is_on`
- `generator_P_rat_N`
- `generator_P_idle_N`
- `generator_FLHV_N`
- `generator_Frho_N`
- `generator_Frho_liq_N`
- `generator_FcarbonContent_N`
- `generator_MolarMass_N`
- `mCtrl_user_defined_BSFC_percentage_N`
- `mCtrl_user_defined_BSFC_percentage_N_lower`
- `BSFC_Curve_N[:, 2]`
- `Engine_Fuel_Consumption_Look_Up_Table_Diesle_N[:, 2]`
- `combiTable1Ds.fileName`
- `battery_P_max`
- `battery_Capacity`

## Outputs

The backend writes runtime files under Flask's `instance_path`. In local development this is normally an `instance` folder adjacent to the Flask package execution context.

Important generated files:

- Uploaded model: `{instance_path}/{model_name}.mo`
- Uploaded duty cycle: `{instance_path}/{uploaded_filename}.txt`
- Latest simulation CSV: `{instance_path}/{model_name}_res.csv`
- Batch result database: `{instance_path}/res_db.json`
- Excel export: `{instance_path}/{sanitized_batch_title}.xlsx`

The Excel workbook contains:

- `Batch_Summary`
- `Iterations_Overview`
- one sheet per iteration

## Known Risks and Maintenance Notes

- Frontend fetch URLs are hardcoded to `http://127.0.0.1:5000`.
- The active `/seq_model/simulate_batch` endpoint returns little information to the frontend. Operators need backend logs or the generated Excel file to confirm details.
- `markUnrealisticCombos` adds `check: false` to invalid configs but does not remove those configs before simulation.
- In `App.jsx`, the methanol and fuel-cell context providers appear swapped: `MethanolEngineListContext` is given fuel-cell state and `FuelCellListContext` is given methanol state. Confirm behavior before refactoring because existing UI code may have adapted to it.
- `VesselSpectInput.jsx` also appears to swap volume and weight context variables in naming. The saved values still flow into the simulator, but the names are easy to misread.
- OpenModelica is controlled through a single default port, `10000`. The legacy parallel simulation notes explain that true parallel OMC workers need unique ports per worker.
- The backend rewrites the uploaded `.mo` file before every sequential simulation. This is expected, but it means a failed run can leave the instance copy in the last attempted configuration state.
- Several strings contain mojibake from encoding issues, especially currency symbols and arrows. Avoid editing generated outputs manually until encoding is cleaned up.
- Legacy tests target the `/model` blueprint and may not cover the active `/seq_model` path used by the frontend.
- `seq_paralle_model.py` currently only imports `M` from `pymongo` and does not implement a usable parallel simulation module.

## Troubleshooting

### Backend cannot find OpenModelica

Check OpenModelica installation and set one of:

```powershell
$env:OMC_EXE = "C:\Path\To\omc.exe"
$env:OPENMODELICAHOME = "C:\Path\To\OpenModelica"
```

Then restart Flask.

### Browser shows upload or simulation failure

Check that:

- Flask is running on port `5000`.
- The duty-cycle file is `.txt`.
- `Load Sequential Model` was pressed before simulation.
- The duty-cycle upload completed and returned start/end times.
- The component database was confirmed before simulation.

### `OMC did not become ready in time`

Likely causes:

- OpenModelica executable not found or not starting.
- Port `10000` already in use.
- Multiple OMC processes are trying to bind the same port.

For parallel workers, assign each `OMCConnection` a different port.

### Simulation CSV is missing

Check backend console logs for OpenModelica errors from `getErrorString()`. Also confirm:

- model name in the request matches the uploaded `.mo` filename without extension
- `combiTable1Ds.fileName` points to a valid duty-cycle file path
- Modelica override parameter names still match the model

### Excel export fails

The Excel export assumes expected result keys are present. Missing CSV columns or failed result processing can cause workbook generation to fail. Inspect `{model_name}_res.csv` and compare expected columns in `seq_model.py` and `ExcelGenerator.py`.

## Recommended Next Improvements

1. Replace hardcoded backend URLs with a Vite environment variable.
2. Fix or deliberately document the methanol/fuel-cell context swap.
3. Filter out `check: false` configurations before simulation if vessel limits should be enforced.
4. Add `/seq_model` tests for upload, duty-cycle parsing, parameter mapping, and a mocked simulation run.
5. Return batch title, Excel filename, and status from `/seq_model/simulate_batch`.
6. Introduce unique OMC ports before re-enabling parallel simulation.
7. Move shared API request logic into one frontend client module.
8. Normalize spelling and naming only with a repo-wide import-safe refactor.

## Quick Start Checklist for a New Developer

- Read this file and `omserver/omserver/README.md`.
- Install OpenModelica and confirm `omc.exe` can start.
- Run `pdm install` in `omserver/omserver`.
- Run the Flask backend from `omserver/omserver/src`.
- Run `npm install` and `npm run dev` in `seq_batch_simulatior`.
- In the UI, confirm vessel settings, upload a duty cycle, confirm database, load model, and run a small one-slot simulation first.
- Inspect backend logs, `res_db.json`, and generated `.xlsx` output before changing simulation logic.
