# omserver

Server backend providing an API to access OpenModelica simulations.

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
