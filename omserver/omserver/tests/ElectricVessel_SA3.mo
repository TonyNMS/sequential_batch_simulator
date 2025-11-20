model ElectricVessel_SA3
  import Modelica.Blocks.Tables.CombiTable1Ds;
  // Repository of External Models for Local use
  /*tricontroller*/
  model tricontroller
    model BatteryDispatchableControllerSimulationBase_1
    "Base interface for battery/dispatchable energy sources controller."
      parameter Real batteryP_start=0 "Start power of the battery" annotation (Dialog(tab="Initialization"));
      parameter Real SOC_max=0.9 "Max state of charge" annotation (Dialog(group="Operational constraints"));
      parameter Real SOC_min=0.1 "Minimum state of charge" annotation (Dialog(group="Operational constraints"));
      parameter Modelica.Units.SI.Power P_charging_max=2e5 "Maximum charge rate of the battery"
        annotation (Dialog(group="Operational constraints"));
      parameter Modelica.Units.SI.Power P_charging_min=-P_charging_max "Maximum discharge rate of the battery" annotation (Dialog(group="Operational constraints"));
    
      model MicrogridDualBattery
        function cubicStep "Cubic step function"
          input Real tau "Abcissa";
          output Real y "Value";
        algorithm
          y := if tau < 0 then 0 else (if tau > 1 then 1 else (3 - 2*tau)*tau^2);
        end cubicStep;
        parameter Real SOC_max = 0.9 "Maximum state of charge" annotation(
          Dialog(group = "Battery"));
        parameter Real SOC_min = 0.1 "Minimum state of charge" annotation(
          Dialog(group = "Battery"));
        parameter Modelica.Units.SI.Power P_charging_max = 2e5 "Max Chargin Rate" annotation(
          Dialog(group = "Battery"));
        parameter Modelica.Units.SI.Power P_charging_min = -P_charging_max "MAx discharge rate" annotation(
          Dialog(group = "Battery"));
        parameter Real batteryP_start = 0;
        Modelica.Units.SI.Power P_net = -P_load "Net avalibale power (renewable proudction -load)";
        output Modelica.Units.SI.Power P_surplus "Surplus power";
        Modelica.Blocks.Interfaces.RealInput P_load "Load power in W" annotation(
          Placement(transformation(extent = {{-140, -60}, {-100, -20}})));
        Modelica.Blocks.Interfaces.RealInput P_renew "Power produced by renewable eneergy sources in W" annotation(
          Placement(transformation(extent = {{-140, 20}, {-100, 60}})));
        Modelica.Blocks.Interfaces.RealOutput P_battery(start = batteryP_start) "Battery charing power" annotation(
          Placement(transformation(extent = {{101.22303368743393, 30.733820212460365}, {121.22303368743393, 50.733820212460365}}, rotation = 0.0, origin = {0.0, 0.0})));
        Modelica.Blocks.Interfaces.RealOutput P_charge(start = 0) "Battery charing power" annotation(
          Placement(transformation(extent = {{101.22303368743393, -4.4895499856367}, {121.22303368743393, 15.5104500143633}}, rotation = 0.0, origin = {0.0, 0.0})));
        Modelica.Blocks.Interfaces.RealInput SOC(min = SOC_min, max = SOC_max) "State of charge in p.u." annotation(
          Placement(transformation(extent = {{-20, -20}, {20, 20}}, rotation = 270, origin = {0, 120})));
        parameter Real smooth_charge_percentage = 0.1;
        Real smooth_soc_max;
        //Smooth the charge close to SOC_max, starting at smooth_charge_percentage from SOC_max
        Real smooth_soc_min;
        //Smooth the charge close to SOC_min, starting at smooth_charge_percentage from SOC_min
      end MicrogridDualBattery;
      
      Modelica.Blocks.Interfaces.RealInput P_renew "Power produced by renewable energy sources (photovoltaics, wind, hydro)" annotation(
        Placement(transformation(extent = {{-120, -20}, {-80, 20}})));
      Modelica.Blocks.Interfaces.RealInput P_load "Load power" annotation(
        Placement(transformation(origin = {0, -2}, extent = {{-120, -80}, {-80, -40}}), iconTransformation(extent =   {{-120, -80}, {-80, -40}})));
      Modelica.Blocks.Interfaces.RealInput SOC "State of Charge" annotation(
        Placement(transformation(extent = {{-120, 40}, {-80, 80}})));
      MicrogridDualBattery microgridDualBattery annotation(
        Placement(transformation(origin = {12.4331, -10.169}, extent = {{-39.9102, -37.3081}, {25.044, 29.6461}})));
    equation
      connect(P_renew, microgridDualBattery.P_renew) annotation(
        Line(points = {{-100, 0}, {-63.5, 0}, {-63.5, -1}, {-34, -1}}, color = {0, 0, 127}));
      connect(SOC, microgridDualBattery.SOC) annotation(
        Line(points = {{-100, 60}, {5, 60}, {5, 26}}, color = {0, 0, 127}));
      connect(P_load, microgridDualBattery.P_load) annotation(
        Line(points = {{-100, -62}, {-58, -62}, {-58, -28}, {-34, -28}}, color = {0, 0, 127}));
    
    annotation(
        Icon(coordinateSystem(preserveAspectRatio = false), graphics = {Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {0, 0, 0}, fillColor = {215, 215, 215}, fillPattern = FillPattern.Solid), Text(extent = {{-38, 26}, {38, -30}}, lineColor = {255, 255, 255}, fillColor = {215, 215, 215}, fillPattern = FillPattern.Solid, textString = "C"), Text(extent = {{-100, -110}, {100, -130}}, lineColor = {0, 0, 0}, fillColor = {215, 215, 215}, fillPattern = FillPattern.Solid, textString = "%name")}),
        Diagram(coordinateSystem(preserveAspectRatio = false)));
    end BatteryDispatchableControllerSimulationBase_1;
    model MicrogridDualBattery
        
        function cubicStep "Cubic step function"
          input Real tau "Abcissa";
          output Real y "Value";
        algorithm
          y := if tau < 0 then 0 else (if tau > 1 then 1 else (3 - 2*tau)*tau^2);
        end cubicStep;
        
        function minLocal
          input Real a;
          input Real b;
          output Real result;
        algorithm
          result := if a < b then a else b;
        end minLocal;
        
        function maxLocal
          input Real a;
          input Real b;
          output Real result;
        algorithm
          result := if a > b then a else b;
        end maxLocal;
              
        parameter Real SOC_max = 0.9 "Maximum state of charge" annotation(
          Dialog(group = "Battery"));
        parameter Real SOC_min = 0.1 "Minimum state of charge" annotation(
          Dialog(group = "Battery"));
        parameter Modelica.Units.SI.Power P_charging_max = 2e5 "Max Chargin Rate" annotation(
          Dialog(group = "Battery"));
        parameter Modelica.Units.SI.Power P_charging_min = -P_charging_max "MAx discharge rate" annotation(
          Dialog(group = "Battery"));
        parameter Real batteryP_start = 0;
        Modelica.Units.SI.Power P_net = -P_load "Net avalibale power (renewable proudction -load)";
        output Modelica.Units.SI.Power P_surplus "Surplus power";
        Modelica.Blocks.Interfaces.RealInput P_load "Load power in W" annotation(
          Placement(transformation(extent = {{-140, -60}, {-100, -20}})));
        Modelica.Blocks.Interfaces.RealInput P_renew "Power produced by renewable eneergy sources in W" annotation(
          Placement(transformation(extent = {{-140, 20}, {-100, 60}})));
        Modelica.Blocks.Interfaces.RealOutput P_battery(start = batteryP_start) "Battery charing power" annotation(
          Placement(transformation(extent = {{101.22303368743393, 30.733820212460365}, {121.22303368743393, 50.733820212460365}}, rotation = 0.0, origin = {0.0, 0.0})));
        Modelica.Blocks.Interfaces.RealOutput P_charge(start = 0) "Battery charing power" annotation(
          Placement(transformation(extent = {{101.22303368743393, -4.4895499856367}, {121.22303368743393, 15.5104500143633}}, rotation = 0.0, origin = {0.0, 0.0})));
        Modelica.Blocks.Interfaces.RealInput SOC(min = SOC_min, max = SOC_max) "State of charge in p.u." annotation(
          Placement(transformation(extent = {{-20, -20}, {20, 20}}, rotation = 270, origin = {0, 120})));
        parameter Real smooth_charge_percentage = 0.1;
        Real smooth_soc_max;
        //Smooth the charge close to SOC_max, starting at smooth_charge_percentage from SOC_max
        Real smooth_soc_min;
        //Smooth the charge close to SOC_min, starting at smooth_charge_percentage from SOC_min
        equation
         smooth_soc_max = (1 - cubicStep((1 + (SOC - SOC_max)*(1/smooth_charge_percentage))));
         smooth_soc_min = cubicStep((SOC - SOC_min)*(1/smooth_charge_percentage));
         P_charge = minLocal(P_charging_max*smooth_soc_max, P_renew*smooth_soc_max);
         P_battery = minLocal(P_charging_max*smooth_soc_max, maxLocal(P_charging_min*smooth_soc_min,P_net * (if P_net >=0 then smooth_soc_max else smooth_soc_min)));
         P_surplus = P_net - P_battery;
    end MicrogridDualBattery;
  
//The BatterySimBase properties which triController is extended
    parameter Real batteryP_start=0 "Start power of the battery" annotation (Dialog(tab="Initialization"));
    parameter Real SOC_max=0.9 "Max state of charge" annotation (Dialog(group="Operational constraints"));
    parameter Real SOC_min=0.1 "Minimum state of charge" annotation (Dialog(group="Operational constraints"));
    parameter Modelica.Units.SI.Power P_charging_max=2e5 "Maximum charge rate of the battery" annotation (Dialog(group="Operational constraints"));
    parameter Modelica.Units.SI.Power P_charging_min=-P_charging_max "Maximum discharge rate of the battery" annotation (Dialog(group="Operational constraints"));
    Modelica.Blocks.Interfaces.RealInput P_renew "Power produced by renewable energy sources (photovoltaics, wind, hydro)" annotation(Placement(transformation(extent = {{-120, -20}, {-80, 20}})));
    Modelica.Blocks.Interfaces.RealInput P_load "Load power" annotation(Placement(transformation(origin = {0, -2}, extent = {{-120, -80}, {-80, -40}}), iconTransformation(extent =   {{-120, -80}, {-80, -40}})));
    Modelica.Blocks.Interfaces.RealInput SOC "State of Charge" annotation(Placement(transformation(extent = {{-120, 40}, {-80, 80}})));
    MicrogridDualBattery microgridDualBattery(SOC_max = SOC_max, SOC_min = SOC_min, P_charging_max = P_charging_max, P_charging_min = P_charging_min) annotation(Placement(transformation(origin = {12.4331, -10.169}, extent = {{-39.9102, -37.3081}, {25.044, 29.6461}})));  
//triconbtroller's property
    Modelica.Blocks.Interfaces.RealOutput P_charge annotation(
      Placement(transformation(origin = {62, 24}, extent = {{109.7, 57.7424}, {129.7, 77.7424}}), iconTransformation(extent = {{109.7, 57.7424}, {129.7, 77.7424}})));
    Modelica.Blocks.Interfaces.RealOutput P_discharge annotation(
      Placement(transformation(origin = {62, 24}, extent = {{111.681, 20.3277}, {131.681, 40.3277}}), iconTransformation(extent = {{111.681, 20.3277}, {131.681, 40.3277}})));
    Modelica.Blocks.Math.Max max annotation(
      Placement(transformation(origin = {60, 24}, extent = {{51.7311, 16.113}, {61.479, 25.8609}})));
    Modelica.Blocks.Math.Min min annotation(
      Placement(transformation(origin = {62, 22}, extent = {{51.7311, -23.887}, {61.479, -14.1391}})));
    Modelica.Blocks.Sources.Constant const(k = 0) annotation(
      Placement(transformation(origin = {56, 24}, extent = {{30.9926, -5.29879}, {41.747, 5.45561}})));
    Modelica.Blocks.Math.Gain gain(k = 1/P_charging_min) annotation(
      Placement(transformation(origin = {62, 24}, extent = {{81.7507, -21.8674}, {87.4594, -16.1587}})));
    Modelica.Blocks.Interfaces.RealInput P_renew2 "Power produced by renewable energy sources" annotation(
      Placement(transformation(origin = {18.8513, 117.637}, extent = {{-20, -20}, {20, 20}}, rotation = -90), iconTransformation(origin = {18.8513, 115.637}, extent = {{-20, -20}, {20, 20}}, rotation = -90)));
    Modelica.Blocks.Interfaces.RealInput P_load2 "Load power" annotation(
      Placement(transformation(extent = {{-20.0, -20.000000000000007}, {20.0, 20.000000000000007}}, rotation = -90.0, origin = {-41.14871906326192, 115.63724607162698})));
    Modelica.Blocks.Interfaces.RealInput SOC2 "Stae of charge" annotation(
      Placement(transformation(origin = {78.8513, 119.637}, extent = {{-20, -20}, {20, 20}}, rotation = -90), iconTransformation(origin = {78.8513, 115.637}, extent = {{-20, -20}, {20, 20}}, rotation = -90)));
    Modelica.Blocks.Interfaces.RealOutput P_charge2 annotation(
      Placement(transformation(origin = {62, 24}, extent = {{113.679, -16.5313}, {133.679, 3.4687}}), iconTransformation(extent = {{113.679, -16.5313}, {133.679, 3.4687}})));
    Modelica.Blocks.Interfaces.RealOutput R_discharge2 annotation(
      Placement(transformation(origin = {62, 24}, extent = {{114.036, -51.4993}, {134.036, -31.4993}}), iconTransformation(extent = {{114.036, -51.4993}, {134.036, -31.4993}})));
    Modelica.Blocks.Math.Max max2 annotation(
      Placement(transformation(origin = {110, 50}, extent = {{55.0038, -144.432}, {64.7517, -134.685}})));
    Modelica.Blocks.Math.Min min2 annotation(
      Placement(transformation(origin = {110, 50}, extent = {{55.0038, -184.432}, {64.7517, -174.685}})));
    Modelica.Blocks.Sources.Constant const2(k = 0) annotation(
      Placement(transformation(origin = {110, 50}, extent = {{34.2653, -165.844}, {45.0197, -155.09}})));
    Modelica.Blocks.Math.Gain gain2(k = 1/P_charging_min) annotation(
      Placement(transformation(origin = {-38.9365, 369.535}, extent = {{233.96, -501.948}, {249.669, -486.239}})));
    MicrogridDualBattery microgridDuallBattery2(P_charging_min = P_charging_min, P_charging_max = P_charging_max, SOC_min = SOC_min, SOC_max = SOC_max) annotation(
      Placement(transformation(origin = {110, 50}, extent = {{-20.6004, -178.843}, {14.3538, -143.889}})));
    Modelica.Blocks.Math.Add add(k2 = +1/(P_charging_max), k1 = +1/(P_charging_max)) annotation(
      Placement(transformation(origin = {64, 24}, extent = {{68, 20}, {88, 40}})));
    Modelica.Blocks.Math.Add add2(k1 = +1/(P_charging_max), k2 = +1/(P_charging_max)) annotation(
      Placement(transformation(origin = {114, 52}, extent = {{70.6288, -143.395}, {90.6288, -123.395}})));
    Modelica.Blocks.Sources.RealExpression DieselCharging(y = microgridDualBattery.P_charge) annotation(
      Placement(transformation(origin = {62, 24}, extent = {{22, 36}, {42, 56}})));
    Modelica.Blocks.Sources.RealExpression DieselCharging2(y = microgridDuallBattery2.P_charge) annotation(
      Placement(transformation(origin = {110, 50}, extent = {{28.4491, -126.525}, {48.4491, -106.525}})));
    
  equation
    connect(P_renew, microgridDualBattery.P_renew) annotation(
      Line(points = {{-100, 0}, {-63.5, 0}, {-63.5, -1}, {-34, -1}}, color = {0, 0, 127}));
    connect(SOC, microgridDualBattery.SOC) annotation(
      Line(points = {{-100, 60}, {5, 60}, {5, 26}}, color = {0, 0, 127}));
    connect(P_load, microgridDualBattery.P_load) annotation(
      Line(points = {{-100, -62}, {-58, -62}, {-58, -28}, {-34, -28}}, color = {0, 0, 127}));
    connect(P_load2, microgridDuallBattery2.P_load) annotation(
      Line(points = {{-42, 116}, {-40, 116}, {-40, 12}, {-70, 12}, {-70, -118}, {86, -118}}, color = {0, 0, 127}));
    connect(P_renew2, microgridDuallBattery2.P_renew) annotation(
      Line(points = {{18, 118}, {20, 118}, {20, 48}, {-50, 48}, {-50, -104}, {86, -104}}, color = {0, 0, 127}));
    connect(SOC2, microgridDuallBattery2.SOC) annotation(
      Line(points = {{78, 120}, {78, 46}, {70, 46}, {70, -74}, {106, -74}, {106, -90}}, color = {0, 0, 127}));
    connect(microgridDualBattery.P_battery, min.u2) annotation(
      Line(points = {{42, 0}, {113, 0}}, color = {0, 0, 127}));
    connect(microgridDualBattery.P_battery, max.u1) annotation(
      Line(points = {{42, 0}, {60, 0}, {60, 18}, {62, 18}, {62, 48}, {110, 48}}, color = {0, 0, 127}));
    connect(const.y, max.u2) annotation(
      Line(points = {{98, 24}, {104, 24}, {104, 42}, {110, 42}}, color = {0, 0, 127}));
    connect(const.y, min.u1) annotation(
      Line(points = {{98, 24}, {106, 24}, {106, 6}, {113, 6}}, color = {0, 0, 127}));
    connect(DieselCharging.y, add.u1) annotation(
      Line(points = {{106, 70}, {120, 70}, {120, 60}, {130, 60}}, color = {0, 0, 127}));
    connect(max.y, add.u2) annotation(
      Line(points = {{122, 44}, {126, 44}, {126, 48}, {130, 48}}, color = {0, 0, 127}));
    connect(add.y, P_charge) annotation(
      Line(points = {{154, 54}, {160, 54}, {160, 94}, {182, 94}, {182, 92}}, color = {0, 0, 127}));
    connect(min.y, gain.u) annotation(
      Line(points = {{124, 3}, {134.5, 3}, {134.5, 5}, {143, 5}}, color = {0, 0, 127}));
    connect(P_discharge, gain.y) annotation(
      Line(points = {{184, 54}, {166, 54}, {166, 4}, {150, 4}}, color = {0, 0, 127}));
    connect(DieselCharging2.y, add2.u1) annotation(
      Line(points = {{160, -66}, {176, -66}, {176, -75}, {183, -75}}, color = {0, 0, 127}));
    connect(max2.y, add2.u2) annotation(
      Line(points = {{176, -90}, {180, -90}, {180, -87}, {183, -87}}, color = {0, 0, 127}));
    connect(microgridDuallBattery2.P_battery, max2.u1) annotation(
      Line(points = {{126, -104}, {138, -104}, {138, -86}, {164, -86}}, color = {0, 0, 127}));
    connect(microgridDuallBattery2.P_battery, min2.u2) annotation(
      Line(points = {{126, -104}, {140, -104}, {140, -132}, {164, -132}}, color = {0, 0, 127}));
    connect(const2.y, max2.u2) annotation(
      Line(points = {{156, -110}, {160, -110}, {160, -92}, {164, -92}}, color = {0, 0, 127}));
    connect(const2.y, min2.u1) annotation(
      Line(points = {{156, -110}, {160, -110}, {160, -126}, {164, -126}}, color = {0, 0, 127}));
    connect(min2.y, gain2.u) annotation(
      Line(points = {{176, -130}, {186, -130}, {186, -124}, {194, -124}}, color = {0, 0, 127}));
    connect(P_charge2, add2.y) annotation(
      Line(points = {{186, 18}, {160, 18}, {160, -48}, {218, -48}, {218, -81}, {206, -81}}, color = {0, 0, 127}));
    connect(gain2.y, R_discharge2) annotation(
      Line(points = {{212, -124}, {236, -124}, {236, -58}, {234, -58}, {234, -18}, {186, -18}}, color = {0, 0, 127}));
  end tricontroller;
  /*BatteryDualControl*/
  model BatteryDualControl
    partial model BatteryBase "Battery"
  
      parameter Modelica.Units.SI.Energy capacity(displayUnit="kWh", min=capacity_min, max=capacity_max)=20*3600*1e6 "Capacity [Ws]";
      parameter Boolean capacity_free_=false "If true, then capacity is free in the optimization"  annotation (Dialog(group="Design",tab="Optimization"));
      
      parameter Boolean use_SOC_constraint = true "If true, SOC is constrained in the optimization" annotation (Dialog(group="Constraints",tab="Optimization"));
      parameter Real SOC_min(unit="1")=0.1 "Minimum State Of Charge" annotation (Dialog(enable=use_SOC_constraint,group="Constraints",tab="Optimization"));
      parameter Real SOC_max(unit="1") = 0.9 "Maximum State Of Charge" annotation (Dialog(enable=use_SOC_constraint,group="Constraints",tab="Optimization"));
      parameter Boolean set_SOC_final_start_ = false "If true, SOC at final time equals start value" annotation (Dialog(group="Constraints",tab="Optimization"));
      parameter Modelica.Units.SI.Power P_max=2e5 "Maximum charging rate [W]"
        annotation (Dialog(group="Control"));
      parameter Modelica.Units.SI.Power P_min=-P_max "Maximum discharging rate [W]"
        annotation (Dialog(group="Control"));
      parameter Real SOC_start(unit="1")=0.5 annotation (Dialog(group="Initialization"));
      
    
      Modelica.Units.SI.Energy charge(min=SOC_min*capacity, max=SOC_max*capacity) "Battery Charge";
      Real SOC(unit="1") "State of Charge";
      Modelica.Units.SI.Power P_out "Total power into battery storage (internal losses between storage power and connector power)";
      Modelica.Electrical.Analog.Interfaces.PositivePin p annotation (Placement(
            transformation(extent={{90,-10},{110,10}}), iconTransformation(extent={{90,-10},
                {110,10}})));   
      parameter Modelica.Units.SI.Energy capacity_min=1e-3 "Minimum capacity in the optimization"
        annotation (Dialog(
          enable=capacity_free_,
          group="Design",
          tab="Optimization"));
      parameter Modelica.Units.SI.Energy capacity_max=200*3600*1e6 "Maximum maximum capacity in the optimization"
        annotation (Dialog(
          enable=capacity_free_,
          group="Design",
          tab="Optimization"));
      Modelica.Units.SI.Power P_loss "Power loss from (dis)charging"; 
  
    equation
      SOC*capacity = charge;
      capacity*der(SOC) = P_out;
        assert(SOC >=0, "Error: Battery is empty in "+getInstanceName()+" at time = "+String(time),level=AssertionLevel.error);
        assert((SOC <= 1), "Error: Battery reached maximum level in "+getInstanceName()+" at time = "+String(time),level=AssertionLevel.error);
    
    initial equation
      SOC=SOC_start;
      
    end BatteryBase;
    extends BatteryBase;
    parameter Real eff_charge(unit="1")=0.9 "Charge effciency";
    parameter Real eff_discharge(unit="1")= eff_charge "Discharge efficiency";
    
    Modelica.Blocks.Interfaces.RealInput P_charge "Charging rate [p.u.]" annotation(
      Placement(transformation(origin = {-80, 40}, extent = {{-20, -20}, {20, 20}}), iconTransformation(origin = {-80, 38}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput P_discharge "Discharging rate [p.u.]" annotation(
      Placement(transformation(origin = {-80, -40}, extent = {{-20, -20}, {20, 20}}), iconTransformation(origin = {-80, -40}, extent = {{-20, -20}, {20, 20}})));
    
    Modelica.Units.SI.Power P_charge_abs "Denormalized charging rate";
    Modelica.Units.SI.Power P_discharge_abs "Denormalized charging rate";
    
  equation
    P_charge_abs = P_charge*(P_max-0)+0;
    P_discharge_abs = P_discharge*(-P_min-0)+0;
    P_loss = (1 - eff_charge)*P_charge_abs + (1/eff_discharge - 1)*P_discharge_abs;
    P_out = P_charge_abs - P_discharge_abs - P_loss;
  
    p.i*p.v=P_charge_abs - P_discharge_abs;
  annotation(
      uses(Modelica(version = "4.0.0")),
    Icon(graphics = {Rectangle(origin = {4, -6}, fillPattern = FillPattern.VerticalCylinder, lineThickness = 1.25, extent = {{-54, 48}, {54, -48}}, radius = 4), Rectangle(origin = {-19, 51}, extent = {{-15, 7}, {15, -7}}), Rectangle(origin = {-19, 51}, lineThickness = 3, extent = {{-15, 7}, {15, -7}}, radius = 2), Rectangle(origin = {23, 51}, lineThickness = 3, extent = {{-15, 7}, {15, -7}}, radius = 3)}),
    Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}})),
    version = "");
  end BatteryDualControl;
  /*Converter_ACDC*/
  model Converter_ACDC
    // Converter component used by Converter ACDC
    partial model Converter
      type Time_yr = Real(final quantity = "Time", final unit = "yr");
      type PerPower = Real(final quantity = "PerPower");
      type PerPower_PerkW = PerPower(final unit = "1/kW");
      type PerPowerTime = Real(final quantity = "perPowerTime");
      type PerPowerTime_PerkWyr = PerPowerTime(final unit = "1/(kW.yr)");
      
      function sign_approx "Sign function with C2-continuous approximation "
        input Real u "Variable to take sign of";
        input Real eps = 1e-3 "Smoothing epsilon";
        output Real y "Approximated sign(u)";
      algorithm
        y := u/sqrt(u^2 + eps^2);
      end sign_approx;
      
      function heaviside_approx "Heaviside step function with C2-continuous approximation "
        input Real u "Variable to take Heaviside of";
        input Real eps = 1e-3 "Smoothing epsilon";
        output Real y "Approximated heaviside(u)";
      algorithm
        y := (sign_approx(u, eps) + 1)/2;
      end heaviside_approx;
      
      parameter Real efficiency = 0.99 "Effciency";
      parameter Modelica.Units.SI.Power P_max = 2e5 "Maximum source power [W]";
      parameter Boolean P_max_free_ = false "If true then P_max is a design parameter";
      Modelica.Units.SI.Power power_prim(start = 0, max = P_max, min = -P_max);
      Modelica.Units.SI.Power power_sec(start = 0, max = P_max, min = -P_max);
      Modelica.Units.SI.Power loss;
      parameter Time_yr lifetime = 10 "Expected lifetime [yr]";
      parameter PerPower_PerkW capex_p = 0 "CAPEX per maximum power [kW]";
      parameter PerPowerTime_PerkWyr fixed_opex_p = 0 "OPEX per kW per year [1/(kWyr)]";
      parameter Modelica.Units.SI.Power power_nominal = 1e6 "nominal power, for smoothing purpose ";
    equation
      loss = (1 - efficiency)*power_prim*heaviside_approx(power_prim, power_nominal/50) + (1 - efficiency)*power_sec*heaviside_approx(power_sec, power_nominal/50);
      power_prim + power_sec = loss;
    end Converter;
  
//DefaultFlow Component used by Converter_ACDC
    model DefaultFlow
      type DefaultFlowPosition = enumeration(NONE, NORTH, NORTHEAST, EAST, SOUTHEAST, SOUTH, SOUTHWEST, WEST, NORTHWEST, EAST80, WEST80, EAST60, WEST60);
      parameter DefaultFlowPosition defaultFlow = if set_DC_voltage then DefaultFlowPosition.WEST80 else DefaultFlowPosition.EAST80 "Position of the connector that provides the flow that is being externally defined";
    end DefaultFlow;
  
//Pin_AC Connecters used by Converter_ACDC
    connector Pin_AC "Pin of an electrical component"
      Modelica.Units.SI.Voltage v "Potential at the pin" annotation(
        unassignedMessage = "An electrical potential cannot be uniquely calculated.
    The reason could be that
    - a ground object is missing (Modelica.Electrical.Analog.Basic.Ground)
      to define the zero potential of the electrical circuit, or
    - a connector of an electrical component is not connected.");
      flow Modelica.Units.SI.Current i "Current flowing into the pin" annotation(
        unassignedMessage = "An electrical current cannot be uniquely calculated.
    The reason could be that
    - a ground object is missing (Modelica.Electrical.Analog.Basic.Ground)
      to define the zero potential of the electrical circuit, or
    - a connector of an electrical component is not connected.");
      annotation(
        defaultComponentName = "pin",
        Icon(coordinateSystem(preserveAspectRatio = true, extent = {{-100, -100}, {100, 100}}), graphics = {Ellipse(extent = {{100, 100}, {-100, -100}}, lineColor = {0, 140, 72}, fillColor = {0, 140, 72}, fillPattern = FillPattern.Solid)}),
      Diagram(coordinateSystem(preserveAspectRatio = true, extent = {{-100, -100}, {100, 100}})));
    end Pin_AC;

  //eleIn Connecters used by Converter_ACDC
    connector elecIn "Electrical reference values received through connector"
      connector RealConnector = Real "'Real' as connector" annotation(
      defaultComponentName = "u",
      Icon(graphics = {Rectangle(extent = {{100, -100}, {-100, 100}}, lineColor = {0, 0, 127}, fillColor = {0, 0, 127}, fillPattern = FillPattern.Solid)}, coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, preserveAspectRatio = true, initialScale = 0.2)),
      Diagram(coordinateSystem(preserveAspectRatio = true, initialScale = 0.2, extent = {{-100.0, -100.0}, {100.0, 100.0}}), graphics = {Text(lineColor = {0, 0, 127}, extent = {{-10.0, 60.0}, {-10.0, 85.0}}, textString = "%name"), Rectangle(extent = {{100, -50}, {0, 50}}, lineColor = {0, 0, 127}, fillColor = {0, 0, 127}, fillPattern = FillPattern.Solid)}));
      // Maximum power point performances
      input RealConnector i_mp(final quantity = "ElectricCurrent", final unit = "A") "Maximum power point current";
      input RealConnector v_mp(final quantity = "ElectricPotential", final unit = "V") "Maximum power point voltage";
      input RealConnector P_mp(final quantity = "Power", final unit = "W") "Maximum power point power";
      // Actual power
      input RealConnector P(final quantity = "Power", final unit = "W") "Actual power";
      annotation(
      Icon(coordinateSystem(initialScale = 0.2), graphics = {Ellipse(extent = {{-10, 10}, {10, -10}}, lineColor = {0, 0, 0}, lineThickness = 0.5), Ellipse(extent = {{-50, 50}, {50, -50}}, lineColor = {95, 95, 95}, fillColor = {95, 95, 95}, fillPattern = FillPattern.Solid, lineThickness = 0.5), Ellipse(extent = {{-40, 40}, {40, -40}}, lineColor = {95, 95, 95}, fillColor = {255, 204, 51}, fillPattern = FillPattern.Solid, lineThickness = 0.5), Polygon(points = {{-20, 80}, {20, 80}, {0, 44}, {-20, 80}}, lineColor = {95, 95, 95}, fillColor = {95, 95, 95}, fillPattern = FillPattern.Solid, lineThickness = 0.5)}),
      Diagram(coordinateSystem(initialScale = 0.2)));
    end elecIn;
  
  
    type DefaultFlowPosition = enumeration(NONE, NORTH, NORTHEAST, EAST, SOUTHEAST, SOUTH, SOUTHWEST, WEST, NORTHWEST, EAST80, WEST80, EAST60, WEST60);
    //properties belongs to Converter
    extends Converter;
    //properties belongs to DefaultFlow
    final DefaultFlowPosition defaultFlow = if set_DC_voltage then DefaultFlowPosition.WEST80 else DefaultFlowPosition.EAST80;
    //properties belongs to Converter_ACDC
    parameter Boolean set_DC_voltage = true "If true, voltage will be set at DC pin";
    parameter Modelica.Units.SI.Voltage V_ref_DC = 48 "Reference DC source voltage on DC pin" annotation(
      Dialog(enable = not use_V_in and not set_DC_voltage));
    parameter Modelica.Units.SI.Voltage V_ref_AC = 48 "Reference AC source voltage on AC pin" annotation(
      Dialog(enable = not use_V_in and not set_DC_voltage));
    parameter Boolean use_V_in = false "if true, DC voltage is an input" annotation(
      choices(checkBox = true),
      Dialog(tab = "Interfaces", group = "Inputs"));
    parameter Boolean use_pvInfo = false "true to set the voltage through pVInfo, false for connecting Real signal" annotation(
      choices(checkBox = true),
      Dialog(tab = "Interfaces", group = "Inputs"));
    Pin_AC pin_AC annotation(
      Placement(transformation(extent = {{70, -10}, {90, 10}}), iconTransformation(extent = {{70, -10}, {90, 10}})));
    Modelica.Electrical.Analog.Interfaces.NegativePin pin_DC annotation(
      Placement(transformation(extent = {{-90, -10}, {-70, 10}}), iconTransformation(extent = {{-90, -10}, {-70, 10}})));
    Modelica.Blocks.Sources.RealExpression realExpression(y = if set_DC_voltage then V_ref_DC else V_ref_AC) if not use_V_in annotation(
      Placement(transformation(origin = {0, -6}, extent = {{-92, 82}, {-72, 102}})));
    Modelica.Blocks.Interfaces.RealInput V_in if (not use_pvInfo) and (use_V_in) "Voltage setpint, DC if set_DC_voltage ==true, else AC voltage" annotation(
      Placement(transformation(extent = {{-20.0, -20.0}, {20.0, 20.0}}, rotation = -90.0, origin = {2, 112}), iconTransformation(extent = {{-20, -20}, {20, 20}}, rotation = -90, origin = {4, 80})));
    elecIn pVInfo if use_pvInfo and use_V_in "PhotoVoltaic information through port" annotation(
      Placement(transformation(origin = {-4.8, 12.3}, extent = {{-27.2, 35.7}, {6.8, 69.7}}), iconTransformation(extent = {{-32, 42}, {8, 82}})));
    
  protected 
    Modelica.Blocks.Interfaces.RealInput V_node "DC Voltage used" annotation(
      Placement(transformation(origin = {24, 38}, extent = {{-20, -20}, {20, 20}}, rotation = -90), iconTransformation(origin = {26, 40}, extent = {{-20, -20}, {20, 20}}, rotation = -90))); 
  equation
    if set_DC_voltage then
      pin_DC.v = V_node;
    else
      pin_AC.v = V_node;
    end if;
    power_prim = pin_AC.v*pin_AC.i;
    power_sec = pin_DC.v*pin_DC.i;
    connect(V_node, V_in) annotation(
      Line(points = {{24, 38}, {24, 78}, {2, 78}, {2, 112}}, color = {0, 0, 127}));
    connect(V_node, pVInfo.v_mp) annotation(
      Line(points = {{24, 38}, {24, 78}, {-22, 78}, {-22, 65}, {-15, 65}}, color = {0, 0, 127}));
    connect(realExpression.y, V_node) annotation(
      Line(points = {{-71, 86}, {-38, 86}, {-38, 38}, {24, 38}}, color = {0, 0, 127}));
    annotation(
      Icon(coordinateSystem(preserveAspectRatio = false), graphics = {Rectangle(extent = {{-80, 60}, {80, -60}}, lineColor = {0, 0, 0}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, radius = 5), Line(points = {{-74, -56}, {76, 56}}, color = {0, 0, 0}), Text(extent = {{4, -10}, {84, -50}}, lineColor = {0, 140, 72}, textString = "~"), Text(extent = {{-86, 56}, {-6, 16}}, lineColor = {0, 0, 255}, textString = "="), Text(extent = {{-80, -66}, {80, -80}}, lineColor = {0, 0, 0}, textString = "%name")}),
      Diagram(coordinateSystem(preserveAspectRatio = false)));
  end Converter_ACDC;
  /*Transformer*/
  model Transformer
    partial model Converter
      type Time_yr = Real(final quantity = "Time", final unit = "yr");
      type PerPower = Real(final quantity = "PerPower");
      type PerPower_PerkW = PerPower(final unit = "1/kW");
      type PerPowerTime = Real(final quantity = "perPowerTime");
      type PerPowerTime_PerkWyr = PerPowerTime(final unit = "1/(kW.yr)");
      
      function sign_approx "Sign function with C2-continuous approximation "
        input Real u "Variable to take sign of";
        input Real eps = 1e-3 "Smoothing epsilon";
        output Real y "Approximated sign(u)";
      algorithm
        y := u/sqrt(u^2 + eps^2);
      end sign_approx;
      
      function heaviside_approx "Heaviside step function with C2-continuous approximation "
        input Real u "Variable to take Heaviside of";
        input Real eps = 1e-3 "Smoothing epsilon";
        output Real y "Approximated heaviside(u)";
      algorithm
        y := (sign_approx(u, eps) + 1)/2;
      end heaviside_approx;
      parameter Real efficiency = 0.99 "Effciency";
      parameter Modelica.Units.SI.Power P_max = 2e5 "Maximum source power [W]";
      parameter Boolean P_max_free_ = false "If true then P_max is a design parameter";
      Modelica.Units.SI.Power power_prim(start = 0, max = P_max, min = -P_max);
      Modelica.Units.SI.Power power_sec(start = 0, max = P_max, min = -P_max);
      Modelica.Units.SI.Power loss;
      parameter Time_yr lifetime = 10 "Expected lifetime [yr]";
      parameter PerPower_PerkW capex_p = 0 "CAPEX per maximum power [kW]";
      parameter PerPowerTime_PerkWyr fixed_opex_p = 0 "OPEX per kW per year [1/(kWyr)]";
      parameter Modelica.Units.SI.Power power_nominal = 1e6 "nominal power, for smoothing purpose ";
    equation
      loss = (1 - efficiency)*power_prim*heaviside_approx(power_prim, power_nominal/50) + (1 - efficiency)*power_sec*heaviside_approx(power_sec, power_nominal/50);
      power_prim + power_sec = loss;
    end Converter;
    
    model DefaultFlow
      type DefaultFlowPosition = enumeration(NONE, NORTH, NORTHEAST, EAST, SOUTHEAST, SOUTH, SOUTHWEST, WEST, NORTHWEST, EAST80, WEST80, EAST60, WEST60);
      parameter DefaultFlowPosition defaultFlow = if set_DC_voltage then DefaultFlowPosition.WEST80 else DefaultFlowPosition.EAST80 "Position of the connector that provides the flow that is being externally defined";
    end DefaultFlow;
    
    connector Pin_AC "Pin of an electrical component"
      Modelica.Units.SI.Voltage v "Potential at the pin" annotation(
        unassignedMessage = "An electrical potential cannot be uniquely calculated.
    The reason could be that
    - a ground object is missing (Modelica.Electrical.Analog.Basic.Ground)
      to define the zero potential of the electrical circuit, or
    - a connector of an electrical component is not connected.");
      flow Modelica.Units.SI.Current i "Current flowing into the pin" annotation(
        unassignedMessage = "An electrical current cannot be uniquely calculated.
    The reason could be that
    - a ground object is missing (Modelica.Electrical.Analog.Basic.Ground)
      to define the zero potential of the electrical circuit, or
    - a connector of an electrical component is not connected.");
      annotation(
        defaultComponentName = "pin",
        Icon(coordinateSystem(preserveAspectRatio = true, extent = {{-100, -100}, {100, 100}}), graphics = {Ellipse(extent = {{100, 100}, {-100, -100}}, lineColor = {0, 140, 72}, fillColor = {0, 140, 72}, fillPattern = FillPattern.Solid)}),
      Diagram(coordinateSystem(preserveAspectRatio = true, extent = {{-100, -100}, {100, 100}})));
    end Pin_AC;
    
// Propertied belongs to Transformer
    extends Converter;
    Pin_AC pin_prim  annotation (Placement(transformation(
          extent={{-10.0,90.0},{10.0,110.0}},
          rotation=0.0,
          origin={0.0,0.0})));
    Pin_AC pin_sec   annotation (Placement(transformation(
            extent={{-10.0,-110.0},{10.0,-90.0}},
            rotation=0.0,
            origin={0.0,0.0})));
    parameter Modelica.Units.SI.Voltage V_ref=48 "Reference AC source voltage on secondary pin."; 
  equation
    pin_sec.v=V_ref;
  
    power_prim=pin_prim.v*pin_prim.i;
    power_sec=pin_sec.v*pin_sec.i; 
  
    annotation(Icon(coordinateSystem(preserveAspectRatio=false), graphics={
          Text(
            extent={{-100,10},{100,-10}},
            lineColor={0,0,0},
            textString="%name",
            origin={-82,0},
            rotation=90),
          Rectangle(
            extent={{-60,-80},{60,-94}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{-54,40},{54,-68}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid),
          Polygon(
            points={{-6,22},{12,22},{4,-2},{26,-2},{-2,-44},{2,-14},{-20,-14},{-6,
                22}},
            lineColor={255,255,255},
            pattern=LinePattern.None,
            fillColor={255,255,255},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{-6,84},{6,46}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{-10,56},{10,52}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{-10,68},{10,62}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{-10,78},{10,74}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{-50,78},{-30,74}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{-50,68},{-30,62}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{-50,56},{-30,52}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{-46,84},{-34,46}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{34,84},{46,46}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{30,56},{50,52}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{30,68},{50,62}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{30,78},{50,74}},
            lineColor={0,0,0},
            pattern=LinePattern.None,
            fillColor={0,0,0},
            fillPattern=FillPattern.Solid)}),
                               Diagram(coordinateSystem(preserveAspectRatio=false)));
  end Transformer;
  /*ElectricalGrid*/
  model ElectricalGrid
    model ElectricGrid_base
      partial model TemplateSource_AC
        //Pin_AC used by TemplateSource_AC
        connector Pin_AC "Pin of an electrical component"
          Modelica.Units.SI.Voltage v "Potential at the pin" annotation(
            unassignedMessage = "An electrical potential cannot be uniquely calculated.
        The reason could be that
        - a ground object is missing (Modelica.Electrical.Analog.Basic.Ground)
          to define the zero potential of the electrical circuit, or
        - a connector of an electrical component is not connected.");
          flow Modelica.Units.SI.Current i "Current flowing into the pin" annotation(
            unassignedMessage = "An electrical current cannot be uniquely calculated.
        The reason could be that
        - a ground object is missing (Modelica.Electrical.Analog.Basic.Ground)
          to define the zero potential of the electrical circuit, or
        - a connector of an electrical component is not connected.");
          annotation(
            defaultComponentName = "pin",
            Icon(coordinateSystem(preserveAspectRatio = true, extent = {{-100, -100}, {100, 100}}), graphics = {Ellipse(extent = {{100, 100}, {-100, -100}}, lineColor = {0, 140, 72}, fillColor = {0, 140, 72}, fillPattern = FillPattern.Solid)}),
            Diagram(coordinateSystem(preserveAspectRatio = true, extent = {{-100, -100}, {100, 100}})));
        end Pin_AC;
        parameter Modelica.Units.SI.Voltage V_ref(displayUnit = "kV") = 20e3 "Grid reference AC voltage";
        parameter Boolean use_V_in = false "If true, voltage is an input" annotation(
          choices(checkBox = true),
          Dialog(tab = "Interfaces", group = "Inputs"));
        Modelica.Units.SI.Power P_out "Power output from grid";
        Pin_AC p annotation(
          Placement(transformation(extent = {{-110, -10}, {-90, 10}}), iconTransformation(extent = {{-110, -10}, {-90, 10}})));
        Modelica.Blocks.Interfaces.RealInput V_in if use_V_in annotation(
          Placement(transformation(extent = {{126, 26}, {86, 66}})));
      protected
        Modelica.Blocks.Interfaces.RealOutput V_set_node annotation(
          Placement(transformation(extent = {{6, 64}, {-14, 84}})));
        Modelica.Blocks.Sources.RealExpression V_parameter(y = 20000) if not use_V_in annotation(
          Placement(transformation(extent = {{74, 58}, {42, 90}})));
      equation
        p.v = V_set_node;
        P_out = -p.v*p.i;
        connect(V_parameter.y, V_set_node) annotation(
          Line(points = {{40, 74}, {-4, 74}}, color = {0, 0, 127}));
        connect(V_in, V_set_node) annotation(
          Line(points = {{106, 46}, {24, 46}, {24, 74}, {-4, 74}}, color = {0, 0, 127}));
      end TemplateSource_AC;
    
// Function max_approx used by ElectricGrid_base
      function max_approx "Max function approximation with continuous derivatives"
        input Real u1 "Argument 1";
        input Real u2 "Argument 2";
        input Real du = 0.1 "Smoothing interval, active when u1-u2 is within +/- 0.5*du";
        output Real y "max(u1,u2)";
      protected
        Real uu = -(u1 - u2)/du + 0.5 "Normalized position in smoothing interval";
      algorithm
        y := -du*noEvent(if uu < 0 then uu - 0.5 else (if uu > 1 then 0 else uu*(1 - uu*uu + 0.5*uu^3) - 0.5)) + u2;
      end max_approx;
    
// Function min_approx used by ElectricGrid_base
      function min_approx "Min function approximation with continuous deriatives"
        input Real u1 "Argument 1";
        input Real u2 "Argument 2";
        input Real du = 0.1 "Smoothing interval, active when u1-u2 is within +/- 0.5*du";
        output Real y "min(u1,u2)";
      protected
        Real uu = (u1 - u2)/du + 0.5 "Normalized position in smoothing interval";
      algorithm
        y := u2 + du*noEvent(if uu < 0 then uu - 0.5 else (if uu > 1 then 0 else uu*(1 - uu*uu + 0.5*uu^3) - 0.5));
      end min_approx;
    
      type PerPower = Real(final quantity = "PerPower");
      type PerPower_PerkW = PerPower(final unit = "1/kW");
      //Properties of ElectricGrid_base
      extends TemplateSource_AC;
      parameter Real factor_sellprice = 1 "Quota between sell price and purchase price" annotation(
        Dialog(tab = "Economy"));
      parameter PerPower_PerkW gridPrice = 1 "Electric grid price in [1/kWh], only used if use_price_input is false" annotation(
        Dialog(tab = "Economy"));
      parameter Boolean use_price_input = true "Use input for electric grid price" annotation(
        choices(checkBox = true),
        Dialog(tab = "Interfaces", group = "Inputs"));
      parameter Modelica.Units.SI.Power power_nominal = 1e5 "Nominal power, for smoothing purposes" annotation(
        Dialog(tab = "Numerics"));
      Modelica.Blocks.Interfaces.RealOutput current_price "Current electrical price from grid" annotation(
        Placement(transformation(extent = {{-10, -10}, {10, 10}}, rotation = 90, origin = {-46, 110}), iconTransformation(extent = {{-10, -10}, {10, 10}}, rotation = 90, origin = {-46, 110})));
      Real opex "Operational cost, per second";
      Modelica.Blocks.Interfaces.RealInput price if use_price_input annotation(
        Placement(transformation(extent = {{126, -20}, {86, 20}})));
    protected
      parameter Modelica.Units.SI.Power power_threshold = power_nominal/100;
      Modelica.Blocks.Sources.RealExpression price_parameter(y = gridPrice) if not use_price_input annotation(
        Placement(transformation(extent = {{2, 12}, {-34, 42}})));
    equation
      opex = (current_price*max_approx(P_out - power_threshold/2, 0, power_threshold))/3600/1000 + (min_approx(P_out + power_threshold/2, 0, power_threshold)*current_price*factor_sellprice)/3600/1000;
      connect(price_parameter.y, current_price) annotation(
        Line(points = {{-35.8, 27}, {-46, 27}, {-46, 110}}, color = {0, 0, 127}));
      connect(price, current_price) annotation(
        Line(points = {{106, 0}, {-46, 0}, {-46, 110}}, color = {0, 0, 127}));
    end ElectricGrid_base;
    
    model OptimizationConstraint "Block for time-invariant inequality constraints in the optimization"
      parameter Boolean exp_constraint_active = true "Use this parameter to turn on and off the constraint";
      parameter Real min_val = -Modelica.Constants.inf "Minimum value of exp" annotation(
        Dialog(group = "Constraining values"));
      parameter Real max_val = Modelica.Constants.inf "Maximum value of exp" annotation(
        Dialog(group = "Constraining values"));
      input Real exp(min = if exp_constraint_active then min_val else -Modelica.Constants.inf, max = if exp_constraint_active then max_val else Modelica.Constants.inf) "Expression to be constrained" annotation(
        Dialog(group = "Expression", enable = exp_constraint_active));
    equation
      if exp_constraint_active then
        assert(exp >= min_val, "Minimum constraint violated in " + getInstanceName() + " at t=" + String(time) + ": Adjust the constraint or control strategy to ensure the problem is feasible", level = AssertionLevel.warning);
        assert(exp <= max_val, "Maximum constraint violated in " + getInstanceName() + " at t=" + String(time) + ": Adjust the constraint or control strategy to ensure the problem is feasible", level = AssertionLevel.warning);
      end if;
      annotation(
        defaultComponentName = "constraint_",
        Icon(graphics = {Rectangle(extent = {{-100, 40}, {100, -40}}, fillColor = {215, 215, 215}, fillPattern = FillPattern.Solid), Text(extent = {{-80, 40}, {80, -40}}, fillColor = {215, 215, 215}, fillPattern = FillPattern.Solid, textString = "Constraint"), Text(extent = {{-112, 32}, {112, -32}}, fillColor = {215, 215, 215}, fillPattern = FillPattern.Solid, textString = "%name", origin = {-2, 58})}));
    end OptimizationConstraint;
    //Properties of ElectricalGrid
    extends ElectricGrid_base(V_parameter(y = 20000));
    OptimizationConstraint constraint_importExport(exp = P_out, min_val = -P_export_max, max_val = P_import_max) if use_power_constraints annotation(
      Placement(transformation(extent = {{26, -46}, {46, -26}})));
     parameter Modelica.Units.SI.Power P_peak = 1e9 "Peak power over time horizon (used in optimization)" annotation(
      Dialog(group = "Power peak", tab = "Optimization", enable = false));
    parameter Boolean P_peak_free_ = false "If true, then power peak is free in the optimization" annotation(
      Dialog(group = "Power peak", tab = "Optimization"));
    parameter Boolean use_power_constraints = false "If true, power import/export is constrained in the optimization" annotation(
      Dialog(group = "Import/export constraints", tab = "Optimization"));
    parameter Modelica.Units.SI.Power P_export_max = Modelica.Constants.inf "Maximal power export" annotation(
      Dialog(enable = use_power_constraints, group = "Import/export constraints", tab = "Optimization"));
    parameter Modelica.Units.SI.Power P_import_max = Modelica.Constants.inf "Maximal power import" annotation(
      Dialog(enable = use_power_constraints, group = "Import/export constraints", tab = "Optimization"));
  equation
  
  end ElectricalGrid;
  /*Electrical Load*/
  model ElectricLoad
    //Connects Pin_AC used by ElectricLoad
    connector Pin_AC "Pin of an electrical component"
      Modelica.Units.SI.Voltage v "Potential at the pin" annotation(
        unassignedMessage = "An electrical potential cannot be uniquely calculated.
    The reason could be that
    - a ground object is missing (Modelica.Electrical.Analog.Basic.Ground)
      to define the zero potential of the electrical circuit, or
    - a connector of an electrical component is not connected.");
      flow Modelica.Units.SI.Current i "Current flowing into the pin" annotation(
        unassignedMessage = "An electrical current cannot be uniquely calculated.
    The reason could be that
    - a ground object is missing (Modelica.Electrical.Analog.Basic.Ground)
      to define the zero potential of the electrical circuit, or
    - a connector of an electrical component is not connected.");
      annotation(
      defaultComponentName = "pin",
      Icon(coordinateSystem(preserveAspectRatio = true, extent = {{-100, -100}, {100, 100}}), graphics = {Ellipse(extent = {{100, 100}, {-100, -100}}, lineColor = {0, 140, 72}, fillColor = {0, 140, 72}, fillPattern = FillPattern.Solid)}),
      Diagram(coordinateSystem(preserveAspectRatio = true, extent = {{-100, -100}, {100, 100}})));
    end Pin_AC;
    parameter Boolean use_input = true "If true, load is an input";
    input Real load_in = 0 "Load by input in [W], only used if use_input is false" annotation (Dialog(enable=(not use_input)));
  
    Modelica.Blocks.Interfaces.RealOutput P_load
      "Connector of Real output signal"                                            annotation (Placement(
          transformation(extent={{100,50},{120,70}})));
  
    Pin_AC n annotation (Placement(transformation(extent={{90,-10},{110,10}}), iconTransformation(extent={{90,-10},{110,10}})));
  
    Modelica.Blocks.Interfaces.RealInput P if use_input
      annotation (Placement(transformation(extent={{-120,-16},{-80,24}})));
  
  protected
    Modelica.Blocks.Sources.RealExpression realExpression(y=100) if not
      use_input                                                                       annotation (Placement(transformation(extent={{-100,74},{-80,94}})));
  
  equation
    n.i=P_load/n.v;
  
    connect(realExpression.y,P_load)  annotation (Line(points={{-79,84},{12,84},{12,
            60},{110,60}}, color={0,0,127}));
    connect(P, P_load) annotation (Line(points={{-100,4},{12,4},{12,60},{110,60}},
                               color={0,0,127}));
  
      annotation (Placement(transformation(extent={{-120,-12},{-80,30}})),
                Icon(coordinateSystem(preserveAspectRatio=false), graphics={
          Rectangle(
            extent={{-100,100},{100,-100}},
            lineColor={0,0,0},
            fillColor={255,255,255},
            fillPattern=FillPattern.Solid,
            radius=20),
          Rectangle(
            extent={{-60,-24},{56,-62}},
            lineColor={175,175,175},
            fillColor={175,175,175},
            fillPattern=FillPattern.Solid,
            radius=20),
          Rectangle(
            extent={{-60,14},{56,-44}},
            lineColor={175,175,175},
            fillColor={175,175,175},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{-80,28},{76,6}},
            lineColor={175,175,175},
            fillColor={175,175,175},
            fillPattern=FillPattern.Solid,
            radius=10),
          Rectangle(
            extent={{-31,8},{31,-8}},
            lineColor={0,128,255},
            fillColor={175,175,175},
            fillPattern=FillPattern.Solid,
            radius=10,
            origin={-28,51},
            rotation=90,
            pattern=LinePattern.None),
          Rectangle(
            extent={{-31,8},{31,-8}},
            lineColor={175,175,175},
            fillColor={175,175,175},
            fillPattern=FillPattern.Solid,
            radius=10,
            origin={28,51},
            rotation=90),
          Text(
            extent={{-100,-110},{100,-130}},
            lineColor={0,0,0},
            fillColor={175,175,175},
            fillPattern=FillPattern.Solid,
            textString="%name")}),                                 Diagram(
          coordinateSystem(preserveAspectRatio=false)));
  end ElectricLoad;
  //HardCodeDutyCycle
  model HardCodeDutyCycle "Hard code the duty cycle into the componenet, so that no external csv references are nedded"
   import Modelica.Blocks.Tables.CombiTable1Ds;
   //Define the duty cycle
   parameter Real dutyCycleRaw[11, 2] =  [0,	452.494;
                                60,	452.494;
                                120,	452.494;
                                180,	452.494;
                                240,	452.494;
                                300,	452.494;
                                360,	452.494;
                                420,	452.494;
                                480,	452.494;
                                540,	452.494;
                                600,	452.494];                            
   Modelica.Blocks.Tables.CombiTable1Ds dutyCycleTable(
    table=dutyCycleRaw,
    smoothness=Modelica.Blocks.Types.Smoothness.LinearSegments,
    extrapolation=Modelica.Blocks.Types.Extrapolation.LastTwoPoints  
   ) annotation(
      Placement(transformation(origin = {-2, 0},extent = {{-10, -10}, {10, 10}}, rotation = 180)));
   Real y;
   Modelica.Blocks.Interfaces.RealOutput out annotation(
      Placement(transformation(origin = {-110, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 180), iconTransformation(origin = {-110, 0}, extent = {{10, -10}, {-10, 10}}, rotation = -0)));
  equation
   y=dutyCycleTable.y[1];
   dutyCycleTable.u=time;
   connect(dutyCycleTable.y[1], out) annotation(
      Line(points = {{-13, 0}, {-110, 0}}, color = {0, 0, 127})); 
  annotation(
      uses(Modelica(version = "4.0.0")));
end HardCodeDutyCycle;
  //Repository Ends
  /*Compoents Parameters Exposed to API*/
  parameter Real battery_SOC_start = 1;
  parameter Modelica.Units.SI.Power battery_P_max =10000000;
  parameter Modelica.Units.SI.Energy battery_capacity =  2.2464e+8/(2);
  parameter Boolean battery_set_SOC_final_start = true;
  parameter .Modelica.Units.SI.Power LoadPInput = 6465.26;
  parameter .Modelica.Units.SI.Power P_nominal = 1e9 "Nominal power in the micro grid";
  parameter Integer N_gen = 1 "Number of Generators";
  
  tricontroller tricontroller1(P_charging_max = battery2.P_max,SOC_min = 0) annotation(
    Placement(transformation(origin = {-70, 54}, extent = {{-10, -10}, {10, 10}})));
  BatteryDualControl battery1(SOC_start = battery_SOC_start, P_max = battery_P_max, capacity = battery_capacity, set_SOC_final_start_ = battery_set_SOC_final_start)  annotation(
    Placement(transformation(origin = {-28, 62}, extent = {{-10, -10}, {10, 10}})));
  BatteryDualControl battery2(SOC_start = battery_SOC_start, capacity = battery_capacity, P_max = battery_P_max, set_SOC_final_start_ = battery_set_SOC_final_start)  annotation(
    Placement(transformation(origin = {-28, 42}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression LoadPower(y = LoadPInput) annotation(
    Placement(transformation(origin = {-95, 76}, extent = {{-5, -4}, {5, 4}})));
  Modelica.Blocks.Sources.RealExpression BattSOC(y = battery2.SOC)  annotation(
    Placement(transformation(origin = {-95, 68}, extent = {{-5, -4}, {5, 4}})));
  Modelica.Blocks.Sources.RealExpression ChargingPower(y=0) annotation(
    Placement(transformation(origin = {-95, 54}, extent = {{-5, -4}, {5, 4}})));
  Converter_ACDC converter_ACDC(efficiency = 0.99,V_ref_DC = 400,power_nominal = P_nominal,P_max = 1e9,set_DC_voltage = true)annotation(
    Placement(transformation(origin = {8, 52}, extent = {{-10, -10}, {10, 10}})));
  Transformer transformer(efficiency = 0.99,power_nominal = P_nominal,P_max = 1e10,V_ref = 400) annotation(
    Placement(transformation(origin = {26, 26}, extent = {{-10, -10}, {10, 10}})));
  ElectricalGrid electricalGrid(power_nominal = P_nominal,V_ref = 400,use_V_in = false) annotation(
    Placement(transformation(origin = {45, 52}, extent = {{-7, -6}, {7, 6}})));
  Modelica.Blocks.Sources.Sine sine(f = 50)  annotation(
    Placement(transformation(origin = {84, 52}, extent = {{10, -10}, {-10, 10}}, rotation = -0)));
  ElectricLoad electricLoad(use_input = false) annotation(
    Placement(transformation(origin = {26, -2}, extent = {{6, -6}, {-6, 6}}, rotation = -0)));
  Modelica.Blocks.Math.Gain gain annotation(
    Placement(transformation(origin = {47, 1}, extent = {{5, -5}, {-5, 5}}, rotation = -0)));
  Modelica.Blocks.Logical.LessEqual lessEqual annotation(
    Placement(transformation(origin = {26, -29}, extent = {{8, -9}, {-8, 9}}, rotation = -0)));
  Modelica.Blocks.Sources.RealExpression zeroval(y = 11000)  annotation(
    Placement(transformation(origin = {80, -36}, extent = {{10, -10}, {-10, 10}}, rotation = -0)));
  Modelica.Blocks.Logical.Switch OnShoreCharingStation annotation(
    Placement(transformation(origin = {-26, -56}, extent = {{10, -10}, {-10, 10}}, rotation = -0)));
  Modelica.Blocks.Sources.RealExpression Onshore_Charging_System annotation(
    Placement(transformation(origin = {22, -48}, extent = {{10, -10}, {-10, 10}}, rotation = -0)));
  Modelica.Blocks.Sources.RealExpression offuse annotation(
    Placement(transformation(origin = {22, -64}, extent = {{10, -10}, {-10, 10}}, rotation = -0)));
  HardCodeDutyCycle hardCodeDutyCycle annotation(
    Placement(transformation(origin = {80, 0}, extent = {{-10, -10}, {10, 10}})));
  
equation
  connect(tricontroller1.P_charge, battery1.P_charge) annotation(
    Line(points = {{-58.03, 60.7742}, {-46.06, 60.7742}, {-46.06, 65.7742}, {-36.03, 65.7742}}, color = {0, 0, 127}));
  connect(tricontroller1.P_discharge, battery1.P_discharge) annotation(
    Line(points = {{-57.8319, 57.0328}, {-47.6638, 57.0328}, {-47.6638, 58.0328}, {-35.8319, 58.0328}}, color = {0, 0, 127}));
  connect(tricontroller1.P_charge2, battery2.P_charge) annotation(
    Line(points = {{-57.6321, 53.3469}, {-49.2642, 53.3469}, {-49.2642, 46.3469}, {-35.6321, 46.3469}}, color = {0, 0, 127}));
  connect(tricontroller1.R_discharge2, battery2.P_discharge) annotation(
    Line(points = {{-57.5964, 49.8501}, {-53.1928, 49.8501}, {-53.1928, 37.8501}, {-35.5964, 37.8501}}, color = {0, 0, 127}));
  connect(LoadPower.y, tricontroller1.P_load2) annotation(
    Line(points = {{-89.5, 76}, {-74, 76}, {-74, 66}}, color = {0, 0, 127}));
  connect(LoadPower.y, tricontroller1.P_load) annotation(
    Line(points = {{-89.5, 76}, {-84, 76}, {-84, 48}, {-80, 48}}, color = {0, 0, 127}));
  connect(BattSOC.y, tricontroller1.SOC2) annotation(
    Line(points = {{-89.5, 68}, {-78, 68}, {-78, 74}, {-62, 74}, {-62, 66}}, color = {0, 0, 127}));
  connect(BattSOC.y, tricontroller1.SOC) annotation(
    Line(points = {{-89.5, 68}, {-84, 68}, {-84, 60}, {-80, 60}}, color = {0, 0, 127}));
  connect(ChargingPower.y, tricontroller1.P_renew) annotation(
    Line(points = {{-89.5, 54}, {-79.5, 54}}, color = {0, 0, 127}));
  connect(ChargingPower.y, tricontroller1.P_renew2) annotation(
    Line(points = {{-89.5, 54}, {-83.5, 54}, {-83.5, 72}, {-67.5, 72}, {-67.5, 66}}, color = {0, 0, 127}));
  connect(battery1.p, converter_ACDC.pin_DC) annotation(
    Line(points = {{-18, 62}, {-8, 62}, {-8, 52}, {0, 52}}, color = {0, 0, 255}));
  connect(battery2.p, converter_ACDC.pin_DC) annotation(
    Line(points = {{-18, 42}, {-8, 42}, {-8, 52}, {0, 52}}, color = {0, 0, 255}));
  connect(electricalGrid.p, converter_ACDC.pin_AC) annotation(
    Line(points = {{38, 52}, {16, 52}}, color = {0, 140, 72}));
  connect(converter_ACDC.pin_AC, transformer.pin_prim) annotation(
    Line(points = {{16, 52}, {26, 52}, {26, 36}}, color = {0, 140, 72}));
  connect(sine.y, electricalGrid.price) annotation(
    Line(points = {{73, 52}, {51, 52}}, color = {0, 0, 127}));
  connect(electricLoad.n, transformer.pin_sec) annotation(
    Line(points = {{20, -2}, {6, -2}, {6, 10}, {26, 10}, {26, 16}}, color = {0, 140, 72}));
  connect(gain.y, electricLoad.P) annotation(
    Line(points = {{41.5, 1}, {32, 1}, {32, -2}}, color = {0, 0, 127}));
  connect(gain.y, lessEqual.u1) annotation(
    Line(points = {{42, 2}, {44, 2}, {44, -29}, {36, -29}}, color = {0, 0, 127}));
  connect(zeroval.y, lessEqual.u2) annotation(
    Line(points = {{70, -36}, {36, -36}}, color = {0, 0, 127}));
  connect(lessEqual.y, OnShoreCharingStation.u2) annotation(
    Line(points = {{17, -29}, {0, -29}, {0, -56}, {-14, -56}}, color = {255, 0, 255}));
  connect(offuse.y, OnShoreCharingStation.u3) annotation(
    Line(points = {{11, -64}, {-14, -64}}, color = {0, 0, 127}));
  connect(Onshore_Charging_System.y, OnShoreCharingStation.u1) annotation(
    Line(points = {{11, -48}, {-14, -48}}, color = {0, 0, 127}));
  connect(hardCodeDutyCycle.out, gain.u) annotation(
    Line(points = {{69, 0}, {55.5, 0}, {55.5, 2}, {54, 2}}, color = {0, 0, 127}));
  annotation(
    Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}})),
    version = "",
    uses(Modelica(version = "4.0.0")),
  Icon(graphics = {Rectangle(origin = {1, 31}, fillPattern = FillPattern.VerticalCylinder, lineThickness = 1.25, extent = {{-37, 37}, {37, -37}}, radius = 4), Rectangle(origin = {-19, 79}, extent = {{-15, 7}, {15, -7}}), Rectangle(origin = {0, 72}, lineThickness = 3, extent = {{-12, 4}, {12, -4}}, radius = 2), Text(origin = {4, -33}, extent = {{60, -24}, {-60, 24}}, textString = "Electric Vessel", fontSize = 26)}));
end ElectricVessel_SA3;
