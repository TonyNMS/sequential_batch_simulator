import base64
import json
import os


def test_upload(client):
    model_data = ""
    with open(os.path.join(os.path.dirname(__file__), "ElectricVessel_SA3.mo"),
              "r") as model:
        model_data = base64.b64encode(
            model.read().encode("utf-8")).decode("utf-8")

    res = client.post("/model/upload",
                      json={
                          "model_name": "ElectricVessel_SA3",
                          "model_data": model_data
                      })

    assert json.loads(res.data) == {
        "name": "ElectricVessel_SA3",
        "status": "Model written"
    }


def test_simulate(client):
    res = client.post("/model/simulate",
                      json={
                          "model_name":
                          "ElectricVessel_SA3",
                          "overrides": [{
                              "param": "battery_SOC_start",
                              "value": 0.6
                          }]
                      })

    with open(
            os.path.join(os.path.dirname(__file__),
                         "ElectricVessel_SA3_res.csv")) as result_file:
        expected_result = result_file.read()

    assert json.loads(res.data) == {
        "name": "ElectricVessel_SA3",
        "result": expected_result
    }


def test_simulate_batch(client):
    res = client.post("/model/simulate_batch",
                      json={
                          "model_name":
                          "ElectricVessel_SA3",
                          "params": [{
                              "name": "battery_SOC_start",
                              "start": 0,
                              "stop": 1,
                              "step": 0.2
                          }]
                      })

    assert len(json.loads(res.data)["results"]) == 6


def test_get_class_names(client):
    res = client.post("/model/get_class_names",
                      json={"model_name": "ElectricVessel_SA3"})

    assert json.loads(res.data).sort() == [
        "ElectricVessel_SA3", "ModelicaServices", "Complex", "Modelica"
    ].sort()


def test_get_parameter_names(client):
    res = client.post("/model/get_parameter_names",
                      json={
                          "model_name": "ElectricVessel_SA3",
                          "class": "ElectricVessel_SA3"
                      })

    assert json.loads(res.data).sort() == [
        "battery_SOC_start", "battery_P_max", "battery_capacity",
        "battery_set_SOC_final_start", "LoadPInput", "P_nominal", "N_gen"
    ].sort()
