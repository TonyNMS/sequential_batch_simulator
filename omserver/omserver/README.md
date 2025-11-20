# omserver

Server backend providing an API to access OpenModelica simulations.

## Setup Instructions

This project uses [PDM](https://pdm.fming.dev/) (Python Dependency Manager) for dependency management. Follow these steps when cloning the project to a new machine:

### Prerequisites

1. **Install Python 3.12 or higher**
   ```bash
   python3 --version  # Should be >= 3.12
   ```

2. **Install PDM**
   ```bash
   # On Linux/macOS
   curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 -
   
   # Or using pip
   pip install --user pdm
   
   # Or using pipx (recommended)
   pipx install pdm
   ```

   After installation, you may need to add PDM to your PATH. Check the installation output for instructions.

### Initial Setup (After Cloning)

1. **Navigate to the project directory**
   ```bash
   cd /path/to/omserver/omserver
   ```

2. **Install project dependencies**
   ```bash
   pdm install
   ```
   
   This will:
   - Create a virtual environment (if not using PEP 582 mode)
   - Install all dependencies from `pyproject.toml` and `pdm.lock`
   - Install the project itself in editable mode

3. **Verify installation**
   ```bash
   pdm list  # Shows installed packages
   ```

### Running the Server

**Option 1: Using PDM run (Recommended)**
```bash
cd src
pdm run flask --app omserver run --debug
```

**Option 2: Activate the virtual environment first**
```bash
# Get the virtual environment path
pdm venv activate

# Or manually activate (path shown by pdm venv)
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Then run Flask
cd src
flask --app omserver run --debug
```

**Option 3: Using the start script**
```bash
cd src
pdm run bash start_server.bash
```

### Troubleshooting

**Problem: "ModuleNotFoundError: No module named 'openpyxl'" (or other dependencies)**

**Solution:** Make sure you've run `pdm install` and are using `pdm run` or have activated the PDM virtual environment:
```bash
# Reinstall dependencies
pdm install

# Then use pdm run
cd src
pdm run flask --app omserver run --debug
```

**Problem: "pdm: command not found"**

**Solution:** PDM is not installed or not in your PATH. Install PDM (see Prerequisites) and ensure it's in your PATH.

**Problem: "Python version mismatch"**

**Solution:** This project requires Python 3.12 or higher. Install the correct Python version and ensure PDM uses it:
```bash
pdm use python3.12  # or your Python 3.12+ path
pdm install
```

### Updating Dependencies

If dependencies are updated in the repository:
```bash
pdm sync  # Syncs with pdm.lock
# or
pdm install  # Reinstalls everything
```

### Development

To install development dependencies:
```bash
pdm install --dev
```

To run tests:
```bash
pdm run pytest
```

## API

### model

#### upload

POST only. Receives a model file to be stored on the server.

```json
{
    "model_name": "name of model",
    "model_data": "model code"
}
```

- `model_name` The name for the model to be assigned on the server.
- `model_data` a base64 encoded OpenModelica model file.

#### delete

POST only. Deletes a model from the server.

```json
{
    "model_name": "name of model"
}
```

- `model_name` Name of the model to delete.

#### simulate

POST only. Runs a simulation of the given model name and returns the output values.

```json
{
    "model_name": "ElectricVessel_SA3",
    "overrides": [{"param": "battery_SOC_start", "value": 60},
                  {"param": "N_gen", "value": 3}]
}
```

- `model_name` Name of the model to simulate.
- `overrides` List of objects specifying a parameter and its value. These set non-default values for model parameters for the simulation.

Returns the name of the model simulated and its outputs as CSV.

```json
{
    "name": "name of model",
    "result": "output CSV"
}
```

- `name` Name of the model simulated.
- `result` CSV formatted simulation results.

#### get_class_names

POST only. Returns the names of all currently loaded classes.

```json
{
    "model_name": "name of model"
}
```

- `model_name` Name of the model to load before checking loaded classes.

#### get_parameter_names

POST only. Returns the names of all parameters of a given class.

```json
    "model_name": "name of model"
    "class": "class name"
```

- `model_name` Name of the model to load before checking for parameter names.
- `class` Name of the class to get parameter names for.
