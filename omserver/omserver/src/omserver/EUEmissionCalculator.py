import pandas as pd 
from pathlib import Path 
from typing  import Dict, List, Any

class EUMarineEmissionCalculator:
    """
    EU Marine Emission Calculator implementing FuelEU Maritime Regulation
    
    This class handles all calculation logic for marine carbon emissions 
    according to EU regulations, making it reusable for both web API and 
    standalone applications.
    """
    
    # EU Regulation Constants
    CONSTANTS = {
        # Global Warming Potentials (IPCC AR4 values used in EU regulation)
        'GWP_CO2': 1,
        'GWP_CH4': 25,
        'GWP_N2O': 298,
        
        # GHG Intensity Targets (gCO2eq/MJ) - FuelEU Maritime
        'GHG_INTENSITY_BASELINE': 91.16,     # Baseline intensity (gCO2eq/MJ)
        'GHG_INTENSITY_TARGET_2025': 91.16,  # From EU regulation
        'GHG_INTENSITY_TARGET_2026': 89.34,
        'GHG_INTENSITY_TARGET_2027': 87.52,
        'GHG_INTENSITY_TARGET_2028': 85.70,
        'GHG_INTENSITY_TARGET_2029': 83.88,
        
        # Energy conversion factors
        'MJ_TO_GJ': 1000,
        'TONNES_TO_KG': 1000,
        'GRAMS_TO_TONNES': 1000000,
        
        # Default scope percentages
        'DEFAULT_FUEL_SCOPE_WITHIN_EU': 100.0,  # %
        'DEFAULT_FUEL_SCOPE_IN_OUT_EU': 50.0,   # %
        
        # Penalty calculation constants (EUR per tonne, MJ/tonne for VLSFO)
        'FUEL_PENALTY_RATE': 2400.00,  
        'VLSFO_LCV': 41000,
        
        # Biofuel calculation constants
        'FOSSIL_FUEL_COMPARATOR_RED': 94.0,  # Fixed constant from RED regulation
    }
    
    def __init__(self):
        """Initialize calculator with fuel properties data"""
        self.fuel_properties = self._load_fuel_properties()
        self.biofuel_factors = self._load_biofuel_factors()  # Now used for biofuel calculations
        
    def _load_fuel_properties(self) -> pd.DataFrame:
        """Load fuel properties from CSV file"""
        try:
            csv_path = Path(__file__).parent / 'lookup_tables' / 'fuel_properties.csv'
            df = pd.read_csv(csv_path)
            # Set pathway_name as index for faster lookups
            return df.set_index('pathway_name')
        except Exception as e:
            ####print(f"Failed to load fuel properties: {e}")
            return pd.DataFrame()
    
    def _load_biofuel_factors(self) -> pd.DataFrame:
        """Load biofuel emission factors from CSV file"""
        try:
            csv_path = Path(__file__).parent / 'lookup_tables' / 'biofuel_emission_factors.csv'
            
            if not csv_path.exists():
                ####print(f"Biofuel CSV file does not exist: {csv_path}")
                return pd.DataFrame()
            
            df = pd.read_csv(csv_path)
            
            # Strip whitespace from column names and string values
            df.columns = df.columns.str.strip()
            df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
            
            return df.set_index('pathway_name')
        except Exception as e:
            ####print(f"Failed to load biofuel factors: {e}")
            return pd.DataFrame()
    
    def get_fuel_properties(self, fuel_name: str) -> Dict[str, Any]:
        """Get fuel properties for a specific fuel type"""
        if fuel_name not in self.fuel_properties.index:
            raise ValueError(f"Fuel '{fuel_name}' not found in fuel properties database")
        
        props = self.fuel_properties.loc[fuel_name].to_dict()
        
        # Handle NaN values
        for key, value in props.items():
            if pd.isna(value):
                props[key] = 0.0
        
        return props
    
    def get_biofuel_pathways(self) -> Dict[str, Any]:
        """Get available biofuel pathways for frontend dropdown"""
        if self.biofuel_factors.empty:
            return {'pathways': [], 'error': 'Biofuel factors not loaded'}
        
        try:
            pathways = []
            for pathway_name in self.biofuel_factors.index:
                typical_value = self.biofuel_factors.loc[pathway_name, 'ghg_emissions_saving_typical_value']
                
                # Convert numpy types to Python types for JSON serialization
                pathways.append({
                    'name': str(pathway_name),  # Ensure string
                    'typical_value': int(typical_value) if pd.notna(typical_value) else 0  # Convert np.int64 to int
                })
            
            return {'pathways': pathways, 'error': None}
            
        except KeyError as e:
            error_msg = f"Column not found in biofuel factors: {e}. Available columns: {list(self.biofuel_factors.columns)}"
            ####print(error_msg)
            return {'pathways': [], 'error': error_msg}
        except Exception as e:
            error_msg = f"Error processing biofuel pathways: {e}"
            ####print(error_msg)
            return {'pathways': [], 'error': error_msg}
    
    def calculate_wtt_ghg_biofuel(self, ttw_co2: float, biofuel_percentage: float) -> float:
        """
        Calculate WtT GHG for biofuel using the biofuel formula
        
        Formula: WtT GHG = (((100 - percentage)/100) * 94) - TtWCO2
        
        Args:
            ttw_co2: Tank-to-Wake CO2 emissions (gCO2eq/MJ)
            biofuel_percentage: Percentage of biofuel (0-100)
            
        Returns:
            WtT GHG emissions (gCO2eq/MJ)
        """
        fossil_fuel_comparator = self.CONSTANTS['FOSSIL_FUEL_COMPARATOR_RED']
        
        # Formula: (((100 - percentage)/100) * 94) - TtWCO2
        wtt_ghg = (((100 - biofuel_percentage) / 100) * fossil_fuel_comparator) - ttw_co2
        
        return wtt_ghg
    
    def calculate_emissions_phase1(self, fuel_data: List[Dict[str, Any]], target_year: int = 2025) -> Dict[str, Any]:
        """
        Phase 1: Step-by-step calculation implementation
        
        Args:
            fuel_data: List of fuel consumption data dictionaries
            target_year: Target year for GHG intensity (2025-2029)
            
        Returns:
            Results with intermediate calculations populated step by step
        """
        ###print("Starting Phase 1 Emission Calculations")
        
        try:
            # Initialize results structure
            results = {
                'intermediate_calculations': {},
                'final_results': {},
                'fuel_breakdown': [],
                'calculation_steps': [],
                'current_step': 'initialized'
            }
            
            # Step 1: Load fuel properties for specified fuel types
            ####print("Step 1: Loading fuel properties for specified fuel types")
            step1_results = self._step1_load_fuel_properties(fuel_data)
            results['fuel_breakdown'] = step1_results['fuel_breakdown']
            results['calculation_steps'].append({
                'step': 1,
                'description': 'Fuel properties loaded from database',
                'status': 'completed',
                'fuels_processed': len(fuel_data)
            })
            ####print("Step 1 completed: Fuel properties loaded successfully")
            
            # Step 2: Calculate Tank-to-Wake (TtW) emissions
            ####print("Step 2: Calculating Tank-to-Wake (TtW) emissions")
            results['fuel_breakdown'] = self._step2_calculate_ttw_emissions(results['fuel_breakdown'])
            results['calculation_steps'].append({
                'step': 2,
                'description': 'Tank-to-Wake emissions calculated for CO2, CH4, N2O',
                'status': 'completed',
                'fuels_processed': len(fuel_data)
            })
            ####print("Step 2 completed: TtW emissions calculated successfully")
            
            # Step 3: Calculate fuel scope constants
            ####print("Step 3: Calculating fuel scope constants")
            results['fuel_breakdown'] = self._step3_calculate_fuel_scope(results['fuel_breakdown'])
            results['calculation_steps'].append({
                'step': 3,
                'description': 'Fuel scope constants applied (100% within EU, 50% in/out EU)',
                'status': 'completed',
                'fuels_processed': len(fuel_data)
            })
            ####print("Step 3 completed: Fuel scope constants applied successfully")
            
            # Step 4: Calculate energy values
            ####print("Step 4: Calculating energy values")
            results['fuel_breakdown'] = self._step4_calculate_energy_values(results['fuel_breakdown'])
            results['calculation_steps'].append({
                'step': 4,
                'description': 'Energy calculations completed (Energy in EU, Energy out of EU, FuelEU Energy, Energy Use in Scope)',
                'status': 'completed',
                'fuels_processed': len(fuel_data)
            })
            ###print("Step 4 completed: Energy calculations completed successfully")
            
            # Step 5: Calculate GHG Intensity
            ###print("Step 5: Calculating GHG Intensity")
            results['fuel_breakdown'] = self._step5_calculate_ghg_intensity(results['fuel_breakdown'], target_year)
            results['calculation_steps'].append({
                'step': 5,
                'description': 'GHG Intensity calculations completed (WtW GHG Intensity, GHG Intensity Target, TtWGHG Intensity, WtTGHG Intensity)',
                'status': 'completed',
                'fuels_processed': len(fuel_data)
            })
            ###print("Step 5 completed: GHG Intensity calculations completed successfully")
            
            # Step 6: Calculate Compliance and Penalties
            ###print("Step 6: Calculating Compliance and Penalties")
            results['fuel_breakdown'] = self._step6_calculate_compliance_penalties(results['fuel_breakdown'])
            results['calculation_steps'].append({
                'step': 6,
                'description': 'Compliance and Penalties calculations completed (Compliance Balance)',
                'status': 'completed',
                'fuels_processed': len(fuel_data)
            })
            results['current_step'] = 'phase1_completed'
            ###print("Step 6 completed: Compliance and Penalties calculations completed successfully")
            ###print("Phase 1 COMPLETED: All 6 steps successfully executed")
            
            # Format intermediate calculations for frontend display
            results['intermediate_calculations'] = self._format_step1_intermediate_calculations(results['fuel_breakdown'])
            
            return results
            
        except Exception as e:
            ###print(f"Phase 1 calculation error: {e}")
            raise
    
    def _step1_load_fuel_properties(self, fuel_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Step 1: Load and populate fuel properties for each specified fuel type
        """
        ###print(f"🔍 Loading properties for {len(fuel_data)} fuel types")
        
        fuel_breakdown = []
        
        for i, fuel in enumerate(fuel_data):
            fuel_type = fuel.get('fuel_type', '')
            fuel_within_eu = fuel.get('fuel_consumption_within_eu', 0)
            fuel_in_out_eu = fuel.get('fuel_consumption_in_out_eu', 0)
            
            # Biofuel parameters
            is_biofuel = fuel.get('is_biofuel', False)
            biofuel_option = fuel.get('biofuel_option', 3)  # Default to option 3 (unknown)
            biofuel_percentage = fuel.get('biofuel_percentage', 0)
            biofuel_pathway = fuel.get('biofuel_pathway', '')
            
            ###print(f"   Fuel {chr(65+i)}: {fuel_type}")
            
            try:
                # Get fuel properties from database
                props = self.get_fuel_properties(fuel_type)
                ###print(f"      Properties loaded: LCV={props.get('lcv_mj_per_g', 0)}")
                
                # Determine WtT GHG based on biofuel settings
                base_wtt_ghg = props.get('co2_eq_wtt_gco2eq_per_mj', 0)
                wtt_ghg = base_wtt_ghg  # Default to standard lookup
                biofuel_calculation_used = False
                
                if is_biofuel and biofuel_option in [1, 2]:
                    # Calculate TtW CO2 first (needed for biofuel formula)
                    cf_co2 = props.get('cf_co2_gco2_per_gfuel', 0)
                    lcv = props.get('lcv_mj_per_g', 0)
                    ttw_co2 = self._calculate_ttw_co2(cf_co2, lcv)
                    
                    percentage = biofuel_percentage
                    if biofuel_option == 2 and biofuel_pathway:
                        # Option 2: Get percentage from pathway lookup
                        try:
                            raw_percentage = self.biofuel_factors.loc[biofuel_pathway, 'ghg_emissions_saving_typical_value']
                            percentage = float(raw_percentage) if pd.notna(raw_percentage) else 0  # Convert numpy types
                        except KeyError:
                            ###print(f"Biofuel pathway '{biofuel_pathway}' not found, using default WtT GHG")
                            percentage = 0
                    
                    if 0 <= percentage <= 100:
                        wtt_ghg = self.calculate_wtt_ghg_biofuel(ttw_co2, percentage)
                        biofuel_calculation_used = True
                    else:
                        print(f"Invalid biofuel percentage ({percentage}%), using default WtT GHG")
                
                # Create fuel calculation object with properties
                fuel_calc = {
                    'fuel_index': i,
                    'fuel_letter': chr(65 + i),
                    'fuel_type': fuel_type,
                    'fuel_within_eu': fuel_within_eu,
                    'fuel_in_out_eu': fuel_in_out_eu,
                    'fuel_mass_total': fuel_within_eu + fuel_in_out_eu,
                    'no_engines': 1,  # Default value
                    
                    # Biofuel tracking
                    'is_biofuel': is_biofuel,
                    'biofuel_option': biofuel_option,
                    'biofuel_percentage': biofuel_percentage,
                    'biofuel_pathway': biofuel_pathway,
                    'biofuel_calculation_used': biofuel_calculation_used,
                    'base_wtt_ghg': base_wtt_ghg,
                    
                    # Fuel properties from database (with biofuel adjustment for WtT GHG)
                    'lcv': props.get('lcv_mj_per_g', 0),
                    'wtt_ghg': wtt_ghg,  # Adjusted for biofuel if applicable
                    'cf_co2': props.get('cf_co2_gco2_per_gfuel', 0),
                    'cf_ch4': props.get('cf_ch4_gch4_per_gfuel', 0),
                    'cf_n2o': props.get('cf_n2o_gn2o_per_gfuel', 0),
                    'c_slip': props.get('c_slip_percent', 0),
                    'e_value': props.get('e_value', 0),
                    'epsilon_sv': props.get('epsilon_sv', 0),
                    
                    # Status tracking
                    'properties_loaded': True,
                    'calculation_step': 1
                }
                
                fuel_breakdown.append(fuel_calc)
                ###print(f"      Fuel {chr(65+i)} properties: LCV={fuel_calc['lcv']}, WtT_GHG={fuel_calc['wtt_ghg']}, CF_CO2={fuel_calc['cf_co2']}")
                
            except Exception as e:
                ###print(f"      Error loading properties for {fuel_type}: {e}")
                raise ValueError(f"Failed to load properties for fuel {fuel_type}: {e}")
        
        ###print(f"Step 1 completed: Properties loaded for {len(fuel_breakdown)} fuels")
        
        return {
            'fuel_breakdown': fuel_breakdown
        }
    
    def _format_step1_intermediate_calculations(self, fuel_breakdown: List[Dict]) -> Dict[str, Any]:
        """
        Format Step 1 results for intermediate calculations table display
        Uses numeric indices to match dynamic fuel inputs
        """
        intermediate = {
            'fuel_input': {},
            'fuel_properties': {},
            'wtt_ghg': {},
            'fuel_consumption': {},
            'energy_calculations': {},
            'ghg_intensity': {},
            'compliance_penalties': {},
            'constants': {}
        }
        
        # Populate fuel input parameters (actual consumption values)
        intermediate['fuel_input']['fuel_within_eu'] = {}
        intermediate['fuel_input']['fuel_in_out_eu'] = {}
        
        # Populate fuel properties
        intermediate['fuel_properties']['lcv'] = {}
        intermediate['fuel_properties']['cf_co2'] = {}
        intermediate['fuel_properties']['cf_ch4'] = {}
        intermediate['fuel_properties']['cf_n2o'] = {}
        
        # Populate WtT GHG emissions
        intermediate['wtt_ghg']['wtt_ghg'] = {}
        intermediate['wtt_ghg']['c_slip'] = {}
        intermediate['wtt_ghg']['ttw_co2'] = {}
        intermediate['wtt_ghg']['ttw_ch4'] = {}
        intermediate['wtt_ghg']['ttw_n2o'] = {}
        
        # Populate fuel consumption scope
        intermediate['fuel_consumption']['fuel_scope_within_eu'] = {}
        intermediate['fuel_consumption']['fuel_scope_in_out_eu'] = {}
        
        # Populate energy calculations
        intermediate['energy_calculations']['energy_in_eu'] = {}
        intermediate['energy_calculations']['energy_out_eu'] = {}
        intermediate['energy_calculations']['fueleu_energy_in_eu'] = {}
        intermediate['energy_calculations']['fueleu_energy_out_eu'] = {}
        intermediate['energy_calculations']['energy_use_scope'] = {}
        
        # Populate GHG intensity
        intermediate['ghg_intensity']['wtw_ghg_intensity'] = {}
        intermediate['ghg_intensity']['ghg_intensity_target'] = {}
        intermediate['ghg_intensity']['ttw_ghg_intensity'] = {}
        intermediate['ghg_intensity']['wtt_ghg_intensity'] = {}
        
        # Populate compliance and penalties
        intermediate['compliance_penalties']['compliance_balance'] = {}
        intermediate['compliance_penalties']['ghg_emission'] = {}
        
        # Populate constants (same for all fuels)
        intermediate['constants']['gwp_co2'] = {}
        intermediate['constants']['gwp_ch4'] = {}
        intermediate['constants']['gwp_n2o'] = {}
        
        for fuel_calc in fuel_breakdown:
            # Use numeric index instead of letter
            fuel_index = fuel_calc['fuel_index']
            
            # Fuel input parameters (actual consumption values)
            intermediate['fuel_input']['fuel_within_eu'][fuel_index] = fuel_calc['fuel_within_eu']
            intermediate['fuel_input']['fuel_in_out_eu'][fuel_index] = fuel_calc['fuel_in_out_eu']
            
            # Fuel properties
            intermediate['fuel_properties']['lcv'][fuel_index] = fuel_calc['lcv']
            intermediate['fuel_properties']['cf_co2'][fuel_index] = fuel_calc['cf_co2']
            intermediate['fuel_properties']['cf_ch4'][fuel_index] = fuel_calc['cf_ch4']
            intermediate['fuel_properties']['cf_n2o'][fuel_index] = fuel_calc['cf_n2o']
            
            # WtT GHG emissions
            intermediate['wtt_ghg']['wtt_ghg'][fuel_index] = fuel_calc['wtt_ghg']
            intermediate['wtt_ghg']['c_slip'][fuel_index] = fuel_calc['c_slip']
            intermediate['wtt_ghg']['ttw_co2'][fuel_index] = fuel_calc.get('ttw_co2', 0)
            intermediate['wtt_ghg']['ttw_ch4'][fuel_index] = fuel_calc.get('ttw_ch4', 0)
            intermediate['wtt_ghg']['ttw_n2o'][fuel_index] = fuel_calc.get('ttw_n2o', 0)
            
            # Fuel consumption scope
            intermediate['fuel_consumption']['fuel_scope_within_eu'][fuel_index] = fuel_calc.get('fuel_scope_within_eu', 100.0)
            intermediate['fuel_consumption']['fuel_scope_in_out_eu'][fuel_index] = fuel_calc.get('fuel_scope_in_out_eu', 50.0)
            
            # Energy calculations
            intermediate['energy_calculations']['energy_in_eu'][fuel_index] = fuel_calc.get('energy_in_eu', 0)
            intermediate['energy_calculations']['energy_out_eu'][fuel_index] = fuel_calc.get('energy_out_eu', 0)
            intermediate['energy_calculations']['fueleu_energy_in_eu'][fuel_index] = fuel_calc.get('fueleu_energy_in_eu', 0)
            intermediate['energy_calculations']['fueleu_energy_out_eu'][fuel_index] = fuel_calc.get('fueleu_energy_out_eu', 0)
            intermediate['energy_calculations']['energy_use_scope'][fuel_index] = fuel_calc.get('energy_use_scope', 0)
            
            # GHG intensity
            intermediate['ghg_intensity']['wtw_ghg_intensity'][fuel_index] = fuel_calc.get('wtw_ghg_intensity', 0)
            intermediate['ghg_intensity']['ghg_intensity_target'][fuel_index] = fuel_calc.get('ghg_intensity_target', 0)
            intermediate['ghg_intensity']['ttw_ghg_intensity'][fuel_index] = fuel_calc.get('ttw_ghg_intensity', 0)
            intermediate['ghg_intensity']['wtt_ghg_intensity'][fuel_index] = fuel_calc.get('wtt_ghg_intensity', 0)
            
            # Compliance and penalties
            intermediate['compliance_penalties']['compliance_balance'][fuel_index] = fuel_calc.get('compliance_balance', 0)
            intermediate['compliance_penalties']['ghg_emission'][fuel_index] = fuel_calc.get('ghg_emission', 0)
            
            # Constants (same for all)
            intermediate['constants']['gwp_co2'][fuel_index] = self.CONSTANTS['GWP_CO2']
            intermediate['constants']['gwp_ch4'][fuel_index] = self.CONSTANTS['GWP_CH4']
            intermediate['constants']['gwp_n2o'][fuel_index] = self.CONSTANTS['GWP_N2O']
        
        return intermediate


    
    def _calculate_ttw_co2(self, cf_co2: float, lcv: float) -> float:
        """
        Calculate Tank-to-Wake CO2 emissions per MJ
        
        Formula: TtWCO2 = (CCO2 / LCV) × GWPCO2
        Excel equivalent: =C62/C61*C65
        
        Args:
            cf_co2: Carbon factor for CO2 (gCO2/gfuel)
            lcv: Lower Calorific Value (MJ/g)
            
        Returns:
            TtW CO2 emissions (gCO2eq/MJ)
        """
        if lcv <= 0:
            return 0.0
        
        # Formula: (cf_co2 / lcv) * gwp_co2
        ttw_co2_per_mj = (cf_co2 / lcv) * self.CONSTANTS['GWP_CO2']
        return ttw_co2_per_mj
    
    def _calculate_ttw_ch4(self, cf_ch4: float, lcv: float) -> float:
        """
        Calculate Tank-to-Wake CH4 emissions per MJ
        
        Formula: TtWCH4 = (CCH4 / LCV) × GWPCH4
        Excel equivalent: =C63/C61*C66
        
        Args:
            cf_ch4: Carbon factor for CH4 (gCH4/gfuel)
            lcv: Lower Calorific Value (MJ/g)
            
        Returns:
            TtW CH4 emissions (gCO2eq/MJ)
        """
        if lcv <= 0:
            return 0.0
        
        # Formula: (cf_ch4 / lcv) * gwp_ch4
        ttw_ch4_per_mj = (cf_ch4 / lcv) * self.CONSTANTS['GWP_CH4']
        return ttw_ch4_per_mj
    
    def _calculate_ttw_n2o(self, cf_n2o: float, lcv: float) -> float:
        """
        Calculate Tank-to-Wake N2O emissions per MJ
        
        Formula: TtWN2O = (CN2O / LCV) × GWPN2O
        Excel equivalent: =C64/C61*C67
        
        Args:
            cf_n2o: Carbon factor for N2O (gN2O/gfuel)
            lcv: Lower Calorific Value (MJ/g)
            
        Returns:
            TtW N2O emissions (gCO2eq/MJ)
        """
        if lcv <= 0:
            return 0.0
        
        # Formula: (cf_n2o / lcv) * gwp_n2o
        ttw_n2o_per_mj = (cf_n2o / lcv) * self.CONSTANTS['GWP_N2O']
        return ttw_n2o_per_mj

    def _step2_calculate_ttw_emissions(self, fuel_breakdown: List[Dict]) -> List[Dict]:
        """
        Phase 1 Step 2: Calculate Tank-to-Wake (TtW) emissions for all greenhouse gases
        
        This step calculates TtW emissions per MJ for CO2, CH4, and N2O using the formulas:
        - TtWCO2 = (CCO2 / LCV) × GWPCO2  [Excel: =C62/C61*C65]
        - TtWCH4 = (CCH4 / LCV) × GWPCH4  [Excel: =C63/C61*C66] 
        - TtWN2O = (CN2O / LCV) × GWPN2O  [Excel: =C64/C61*C67]
        
        Args:
            fuel_breakdown: List of fuel calculation dictionaries from Step 1
            
        Returns:
            Updated fuel breakdown with TtW emission values
        """
        ###print("Phase 1 Step 2: Calculating Tank-to-Wake (TtW) emissions...")
        
        for fuel_calc in fuel_breakdown:
            # Extract required values
            lcv = fuel_calc['lcv']
            cf_co2 = fuel_calc['cf_co2']
            cf_ch4 = fuel_calc['cf_ch4']
            cf_n2o = fuel_calc['cf_n2o']
            
            # Calculate TtW emissions per MJ for each greenhouse gas
            fuel_calc['ttw_co2'] = self._calculate_ttw_co2(cf_co2, lcv)
            fuel_calc['ttw_ch4'] = self._calculate_ttw_ch4(cf_ch4, lcv)
            fuel_calc['ttw_n2o'] = self._calculate_ttw_n2o(cf_n2o, lcv)
            
            # Calculate total TtW emissions per MJ
            fuel_calc['ttw_total_per_mj'] = (
                fuel_calc['ttw_co2'] + 
                fuel_calc['ttw_ch4'] + 
                fuel_calc['ttw_n2o']
            )
            
            ###print(f"   Fuel {fuel_calc['fuel_index']}: TtW CO2={fuel_calc['ttw_co2']:.6f}, "
                  #f"CH4={fuel_calc['ttw_ch4']:.6f}, N2O={fuel_calc['ttw_n2o']:.6f} gCO2eq/MJ")
        
        return fuel_breakdown

    def _step3_calculate_fuel_scope(self, fuel_breakdown: List[Dict]) -> List[Dict]:
        """
        Phase 1 Step 3: Calculate fuel scope constants
        
        This step applies standard fuel scope percentages:
        - Fuel Scope on Voyages & Ports Within EU/EEA: 100% for all fuels
        - Fuel Scope on Voyages in & out of EU/EEA: 50% for all fuels
        
        Args:
            fuel_breakdown: List of fuel calculation dictionaries from Step 2
            
        Returns:
            Updated fuel breakdown with fuel scope values
        """
        ###print("Phase 1 Step 3: Calculating fuel scope constants...")
        
        for fuel_calc in fuel_breakdown:
            # Apply standard fuel scope constants
            fuel_calc['fuel_scope_within_eu'] = 100.0  # 100% for within EU/EEA
            fuel_calc['fuel_scope_in_out_eu'] = 50.0   # 50% for in & out of EU/EEA
            
            ###print(f"   Fuel {fuel_calc['fuel_index']}: Scope Within EU=100%, In/Out EU=50%")
        
        return fuel_breakdown

    def _step4_calculate_energy_values(self, fuel_breakdown: List[Dict]) -> List[Dict]:
        """
        Phase 1 Step 4: Calculate energy values
        
        This step calculates 5 energy-related values based on Excel formulas:
        1. Energy in EU: =C61*C77*1000 (LCV × fuel_within_eu × 1000)
        2. Energy Out of EU: =C78*C61*1000 (fuel_in_out_eu × LCV × 1000)
        3. FuelEU Energy in EU: =C82*C80 (fuel_scope_within_eu × energy_in_eu)
        4. FuelEU Energy Out of EU: =C81*C79 (fuel_scope_in_out_eu × energy_out_eu)
        5. Energy Use in Scope: =(C78*C61*C80)+(C77*C61*C79) (complex formula)
        
        Args:
            fuel_breakdown: List of fuel calculation dictionaries from Step 3
            
        Returns:
            Updated fuel breakdown with energy values
        """
        ###print("Phase 1 Step 4: Calculating energy values...")
        
        for fuel_calc in fuel_breakdown:
            # Extract required values
            lcv = fuel_calc['lcv']  # C61: LCV in MJ/g
            fuel_within_eu = fuel_calc['fuel_within_eu']  # C77: Fuel consumption within EU (tonnes)
            fuel_in_out_eu = fuel_calc['fuel_in_out_eu']  # C78: Fuel consumption in/out EU (tonnes)
            fuel_scope_within_eu = fuel_calc['fuel_scope_within_eu']  # C82: 100%
            fuel_scope_in_out_eu = fuel_calc['fuel_scope_in_out_eu']  # C81: 50%
            
            # 1. Energy in EU: =C61*C77*1000 (LCV × fuel_within_eu × 1000)
            energy_in_eu = lcv * fuel_within_eu * 1000  # MJ
            
            # 2. Energy Out of EU: =C78*C61*1000 (fuel_in_out_eu × LCV × 1000)
            energy_out_eu = fuel_in_out_eu * lcv * 1000  # MJ
            
            # 3. FuelEU Energy in EU: =C82*C80 (fuel_scope_within_eu × energy_in_eu)
            # Note: C82 is fuel_scope_within_eu (100%), C80 is energy_in_eu
            fueleu_energy_in_eu = (fuel_scope_within_eu / 100) * energy_in_eu  # MJ
            
            # 4. FuelEU Energy Out of EU: =C81*C79 (fuel_scope_in_out_eu × energy_out_eu)
            # Note: C81 is fuel_scope_in_out_eu (50%), C79 is energy_out_eu
            fueleu_energy_out_eu = (fuel_scope_in_out_eu / 100) * energy_out_eu  # MJ
            
            # 5. Energy Use in Scope: =(C78*C61*C80)+(C77*C61*C79)
            # Breaking down: (fuel_in_out_eu × LCV × energy_in_eu) + (fuel_within_eu × LCV × energy_out_eu)
            # This seems like a complex formula - let me interpret it as:
            # (fuel_in_out_eu × LCV × fuel_scope_within_eu/100) + (fuel_within_eu × LCV × fuel_scope_in_out_eu/100)
            energy_use_scope = (
                (fuel_in_out_eu * lcv * fuel_scope_in_out_eu / 100) + 
                (fuel_within_eu * lcv * fuel_scope_within_eu / 100)
            )  # MJ
            
            # Store calculated values
            fuel_calc['energy_in_eu'] = energy_in_eu
            fuel_calc['energy_out_eu'] = energy_out_eu
            fuel_calc['fueleu_energy_in_eu'] = fueleu_energy_in_eu
            fuel_calc['fueleu_energy_out_eu'] = fueleu_energy_out_eu
            fuel_calc['energy_use_scope'] = energy_use_scope
            
            ###print(f"   Fuel {fuel_calc['fuel_index']}: Energy in EU={energy_in_eu:.2f}, "
                  #f"Energy out EU={energy_out_eu:.2f}, FuelEU in EU={fueleu_energy_in_eu:.2f}, "
                  #f"FuelEU out EU={fueleu_energy_out_eu:.2f}, Energy Use Scope={energy_use_scope:.2f} MJ")
        
        return fuel_breakdown

    def _step5_calculate_ghg_intensity(self, fuel_breakdown: List[Dict], target_year: int = 2025) -> List[Dict]:
        """
        Phase 1 Step 5: Calculate GHG Intensity values
        
        This step calculates 4 GHG intensity-related values:
        1. WtW GHG Intensity (GHGIEactual): =C68+C69+C70+C71 (sum of TtW emissions)
        2. GHG Intensity Target in 2025 (GHGIEtarget): 91.16 × 0.98 (calculated using constants)
        3. TtWGHG Intensity: =(1-C72)*(C69+C70+C71)+(C72*C66)/C61
        4. WtTGHG Intensity: =C68*C85
        
        Args:
            fuel_breakdown: List of fuel calculation dictionaries from Step 4
            target_year: Target year for GHG intensity calculation (default 2025)
            
        Returns:
            Updated fuel breakdown with GHG intensity values
        """
        ###print("Phase 1 Step 5: Calculating GHG Intensity...")
        
        for fuel_calc in fuel_breakdown:
            # Extract TtW emission values (C68, C69, C70, C71 equivalent)
            wtt_ghg = fuel_calc['wtt_ghg']  # WtT GHG emissions
            ttw_co2 = fuel_calc['ttw_co2']  # TtW CO2 emissions
            ttw_ch4 = fuel_calc['ttw_ch4']  # TtW CH4 emissions  
            ttw_n2o = fuel_calc['ttw_n2o']  # TtW N2O emissions
            
            # Extract additional values for TtWGHG and WtTGHG calculations
            c_slip = fuel_calc['c_slip'] / 100  # C72: Convert percentage to decimal
            gwp_ch4 = self.CONSTANTS['GWP_CH4']  # C66: GWP for CH4 (25)
            lcv = fuel_calc['lcv']  # C61: LCV
            energy_use_scope = fuel_calc['energy_use_scope']  # C85: Energy Use in Scope
            
            # 1. WtW GHG Intensity (GHGIEactual): Sum of all GHG emissions
            # This includes both Well-to-Tank (WtT) and Tank-to-Wake (TtW) emissions
            wtw_ghg_intensity = wtt_ghg + ttw_co2 + ttw_ch4 + ttw_n2o  # gCO2eq/MJ
            
            # 2. GHG Intensity Target: Calculate using constants (91.16 × 0.98)
            baseline_intensity = self.CONSTANTS['GHG_INTENSITY_BASELINE']  # 91.16
            reduction_factor = 0.98  # 2% reduction for 2025
            ghg_intensity_target = baseline_intensity * reduction_factor  # gCO2eq/MJ
            
            # 3. TtWGHG Intensity: =(1-C72)*(C69+C70+C71)+(C72*C66)/C61
            # This accounts for carbon slip effects on TtW emissions
            ttw_ghg_intensity = (
                (1 - c_slip) * (ttw_co2 + ttw_ch4 + ttw_n2o) + 
                (c_slip * gwp_ch4) / lcv
            )  # gCO2eq/MJ
            
            # 4. WtTGHG Intensity: =C68*C85
            # Well-to-Tank GHG intensity weighted by energy use in scope
            wtt_ghg_intensity = wtt_ghg * energy_use_scope  # gCO2eq
            
            # Store calculated values
            fuel_calc['wtw_ghg_intensity'] = wtw_ghg_intensity
            fuel_calc['ghg_intensity_target'] = ghg_intensity_target
            fuel_calc['ttw_ghg_intensity'] = ttw_ghg_intensity
            fuel_calc['wtt_ghg_intensity'] = wtt_ghg_intensity
            
            ###print(f"   Fuel {fuel_calc['fuel_index']}: WtW GHG Intensity={wtw_ghg_intensity:.6f} gCO2eq/MJ, "
                  #f"GHG Target={ghg_intensity_target:.6f} gCO2eq/MJ, "
                  #f"TtWGHG Intensity={ttw_ghg_intensity:.6f} gCO2eq/MJ, "
                  #f"WtTGHG Intensity={wtt_ghg_intensity:.6f} gCO2eq")
        
        return fuel_breakdown

    def _step6_calculate_compliance_penalties(self, fuel_breakdown: List[Dict]) -> List[Dict]:
        """
        Phase 1 Step 6: Calculate Compliance and Penalties
        
        This step calculates compliance-related values:
        1. Compliance Balance: =(C88-C90)*C85
        
        Args:
            fuel_breakdown: List of fuel calculation dictionaries from Step 5
            
        Returns:
            Updated fuel breakdown with compliance values
        """
        ###print("Phase 1 Step 6: Calculating Compliance and Penalties...")
        
        for fuel_calc in fuel_breakdown:
            # Get required values
            cf_co2 = fuel_calc.get('cf_co2', 0)  # gCO2/gfuel
            fuel_within_eu = fuel_calc.get('fuel_within_eu', 0)  # tonnes
            fuel_in_out_eu = fuel_calc.get('fuel_in_out_eu', 0)  # tonnes
            
            # Calculate GHG Emission
            ghg_emission = (cf_co2 * fuel_within_eu + cf_co2 * fuel_in_out_eu)
            fuel_calc['ghg_emission'] = ghg_emission
            
            # Get other required values for compliance balance
            ghg_intensity_target = fuel_calc.get('ghg_intensity_target', 0)  # gCO2eq/MJ
            wtt_ghg_intensity = fuel_calc.get('wtt_ghg_intensity', 0)  # gCO2eq/MJ
            energy_use_scope = fuel_calc.get('energy_use_scope', 0)  # MJ
            
            # Compliance Balance: =(C88-C90)*C85
            # Difference between actual and target intensity, weighted by energy use
            compliance_balance = (ghg_intensity_target - wtt_ghg_intensity) * energy_use_scope  # gCO2eq
            
            # Store calculated values
            fuel_calc['compliance_balance'] = compliance_balance
            
            ###print(f"   Fuel {fuel_calc['fuel_index']}: Compliance Balance={compliance_balance:.6f} gCO2eq")
        
        return fuel_breakdown

    def _calculate_single_fuel(self, fuel: Dict[str, Any], fuel_index: int) -> Dict[str, Any]:
        """Calculate emissions for a single fuel type"""
        fuel_type = fuel.get('fuel_type', '')
        fuel_within_eu = fuel.get('fuel_consumption_within_eu', 0)  # tonnes
        fuel_in_out_eu = fuel.get('fuel_consumption_in_out_eu', 0)  # tonnes
        
        # Get fuel properties
        props = self.get_fuel_properties(fuel_type)
        
        # Fuel properties extraction
        lcv = props.get('lcv_mj_per_g', 0)  # MJ/g
        wtt_ghg = props.get('co2_eq_wtt_gco2eq_per_mj', 0)  # gCO2eq/MJ
        cf_co2 = props.get('cf_co2_gco2_per_gfuel', 0)  # gCO2/gfuel
        cf_ch4 = props.get('cf_ch4_gch4_per_gfuel', 0)  # gCH4/gfuel
        cf_n2o = props.get('cf_n2o_gn2o_per_gfuel', 0)  # gN2O/gfuel
        c_slip = props.get('c_slip_percent', 0)  # %
        
        # Calculate TtW emissions per MJ using dedicated functions
        ttw_co2_per_mj = self._calculate_ttw_co2(cf_co2, lcv)  # gCO2eq/MJ
        ttw_ch4_per_mj = self._calculate_ttw_ch4(cf_ch4, lcv)  # gCO2eq/MJ  
        ttw_n2o_per_mj = self._calculate_ttw_n2o(cf_n2o, lcv)  # gCO2eq/MJ
        ttw_total_per_mj = ttw_co2_per_mj + ttw_ch4_per_mj + ttw_n2o_per_mj
        
        # Calculate energy content
        total_fuel_mass = (fuel_within_eu + fuel_in_out_eu) * self.CONSTANTS['TONNES_TO_KG']  # kg
        total_energy = total_fuel_mass * lcv * self.CONSTANTS['TONNES_TO_KG']  # MJ
        
        # Energy distribution
        fuel_within_mass = fuel_within_eu * self.CONSTANTS['TONNES_TO_KG']  # kg
        fuel_in_out_mass = fuel_in_out_eu * self.CONSTANTS['TONNES_TO_KG']  # kg
        
        energy_in_eu = fuel_within_mass * lcv * self.CONSTANTS['TONNES_TO_KG']  # MJ
        energy_out_eu = fuel_in_out_mass * lcv * self.CONSTANTS['TONNES_TO_KG']  # MJ
        
        # Apply scope percentages
        fuel_scope_within = self.CONSTANTS['DEFAULT_FUEL_SCOPE_WITHIN_EU']  # %
        fuel_scope_in_out = self.CONSTANTS['DEFAULT_FUEL_SCOPE_IN_OUT_EU']   # %
        
        energy_use_scope = (energy_in_eu * fuel_scope_within / 100 + 
                           energy_out_eu * fuel_scope_in_out / 100)  # MJ
        
        # Calculate total emissions
        wtt_emissions_total = total_energy * wtt_ghg  # gCO2eq
        ttw_emissions_total = total_energy * ttw_total_per_mj  # gCO2eq
        
        return {
            'fuel_index': fuel_index,
            'fuel_type': fuel_type,
            'fuel_mass_total': fuel_within_eu + fuel_in_out_eu,  # tonnes
            'fuel_within_eu': fuel_within_eu,
            'fuel_in_out_eu': fuel_in_out_eu,
            'no_engines': 1,  # Default value
            
            # Fuel properties
            'lcv': lcv,
            'wtt_ghg': wtt_ghg,
            'cf_co2': cf_co2,
            'cf_ch4': cf_ch4,
            'cf_n2o': cf_n2o,
            'c_slip': c_slip,
            
            # TtW calculations
            'ttw_co2': ttw_co2_per_mj,
            'ttw_ch4': ttw_ch4_per_mj,
            'ttw_n2o': ttw_n2o_per_mj,
            'ttw_total_per_mj': ttw_total_per_mj,
            
            # Energy calculations
            'energy_in_eu': energy_in_eu,  # MJ
            'energy_out_eu': energy_out_eu,  # MJ
            'energy_use_scope': energy_use_scope,  # MJ
            'fuel_scope_within_eu': fuel_scope_within,
            'fuel_scope_in_out_eu': fuel_scope_in_out,
            
            # Emissions totals
            'wtt_emissions_total': wtt_emissions_total,  # gCO2eq
            'ttw_emissions_total': ttw_emissions_total,  # gCO2eq
            
            # Intensities (for individual fuel)
            'wtt_intensity': wtt_ghg if energy_use_scope > 0 else 0,
            'ttw_intensity': ttw_total_per_mj if energy_use_scope > 0 else 0,
            'ghg_intensity_target': self.CONSTANTS['GHG_INTENSITY_TARGET_2025'],
            
            # Compliance calculations
            'compliance_balance': 0,  # Will be calculated at aggregate level
        }
    

    
    def get_constants(self) -> Dict[str, Any]:
        """Get all calculator constants"""
        return self.CONSTANTS.copy()
    
    def validate_fuel_data(self, fuel_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate input fuel data"""
        if not fuel_data:
            return {'valid': False, 'error': "No fuel data provided"}
        
        for i, fuel in enumerate(fuel_data):
            if not fuel.get('fuel_type'):
                return {'valid': False, 'error': f"Fuel type missing for fuel {i+1}"}
            
            if fuel.get('fuel_type') not in self.fuel_properties.index:
                return {'valid': False, 'error': f"Unknown fuel type: {fuel.get('fuel_type')}"}
            
            within_eu = fuel.get('fuel_consumption_within_eu', 0)
            in_out_eu = fuel.get('fuel_consumption_in_out_eu', 0)
            
            if within_eu < 0 or in_out_eu < 0:
                return {'valid': False, 'error': f"Negative fuel consumption values for fuel {i+1}"}
        
        return {'valid': True, 'error': None}

    def calculate_emissions_phase2(self, fuel_data: List[Dict[str, Any]], target_year: int = 2025) -> Dict[str, Any]:
        """
        Phase 2: Aggregate calculations for final results
        
        This phase performs aggregate calculations across all fuels to produce
        final results for the calculation results section.
        
        Args:
            fuel_data: List of fuel consumption data dictionaries
            target_year: Target year for GHG intensity (2025-2029)
            
        Returns:
            Results with final aggregate calculations
        """
        ###print("API: Starting Phase 2 calculations")
        
        try:
            # First run Phase 1 to get individual fuel calculations
            phase1_results = self.calculate_emissions_phase1(fuel_data, target_year)
            fuel_breakdown = phase1_results['fuel_breakdown']
            
            # Phase 2 aggregate calculations
            final_results = {}
            
            # 1. GHG Intensity Target 2025-2029 (GHGIEtarget) = C87*(1-0.02)
            # Using the baseline GHG intensity with 2% reduction for 2025-2029
            ghg_intensity_target_2025_2029 = self.CONSTANTS['GHG_INTENSITY_BASELINE'] * (1 - 0.02)
            final_results['ghg_intensity_target_2025_2029'] = ghg_intensity_target_2025_2029
            
            # 2. Leg Energy Total in EU = C81+D81+E81+F81+G81+H81 (sum of energy_in_eu)
            leg_energy_total_in_eu = sum(fuel['energy_in_eu'] for fuel in fuel_breakdown)
            final_results['leg_energy_total_in_eu'] = leg_energy_total_in_eu
            
            # 3. Leg Energy Total Out of EU = C82+D82+E82+F82+G82+H82 (sum of energy_out_eu)
            leg_energy_total_out_eu = sum(fuel['energy_out_eu'] for fuel in fuel_breakdown)
            final_results['leg_energy_total_out_eu'] = leg_energy_total_out_eu
            
            # 4. FuelEU Energy Total in EU = C95*C79 (leg_energy_total_in_eu * fuel_scope_within_eu)
            # Since all fuels have 100% scope within EU, this equals leg_energy_total_in_eu
            fueleu_energy_total_in_eu = leg_energy_total_in_eu * (self.CONSTANTS['DEFAULT_FUEL_SCOPE_WITHIN_EU'] / 100)
            final_results['fueleu_energy_total_in_eu'] = fueleu_energy_total_in_eu
            
            # 5. FuelEU Energy Total Out of EU = C96*C80 (leg_energy_total_out_eu * fuel_scope_in_out_eu)
            # Since all fuels have 50% scope in/out EU
            fueleu_energy_total_out_eu = leg_energy_total_out_eu * (self.CONSTANTS['DEFAULT_FUEL_SCOPE_IN_OUT_EU'] / 100)
            final_results['fueleu_energy_total_out_eu'] = fueleu_energy_total_out_eu
            
            # 6. Energy Use in Scope = (C85+D85+E85+F85+G85+H85)*1000000 (sum of energy_use_scope in MJ)
            energy_use_in_scope = sum(fuel['energy_use_scope'] for fuel in fuel_breakdown) * 1000000
            final_results['energy_use_in_scope'] = energy_use_in_scope
            
            # 7. WtT GHG Intensity = ((C68*C85*1000000)+(D68*D85*1000000)+...)/((C85*C73*1000000)+(D85*D73*1000000)+...)
            # Numerator: sum of (wtt_ghg * energy_use_scope * 1000000) for each fuel
            # Denominator: sum of (energy_use_scope * 1000000) for each fuel (C73 appears to be 1, not fuel_scope)
            wtt_numerator = sum(fuel['wtt_ghg'] * fuel['energy_use_scope'] * 1000000 for fuel in fuel_breakdown)
            wtt_denominator = sum(fuel['energy_use_scope'] * 1000000 for fuel in fuel_breakdown)
            wtt_ghg_intensity_aggregate = wtt_numerator / wtt_denominator if wtt_denominator > 0 else 0
            final_results['wtt_ghg_intensity_aggregate'] = wtt_ghg_intensity_aggregate
            
            # 8. TtW GHG Intensity = ((C89*C85*1000000)+(D89*D85*1000000)+...)/((C85*C73*1000000)+(D85*D73*1000000)+...)
            # Numerator: sum of (ttw_ghg_intensity * energy_use_scope * 1000000) for each fuel
            # Denominator: sum of (energy_use_scope * 1000000) for each fuel (C73 appears to be 1, not fuel_scope)
            ttw_numerator = sum(fuel['ttw_ghg_intensity'] * fuel['energy_use_scope'] * 1000000 for fuel in fuel_breakdown)
            ttw_denominator = sum(fuel['energy_use_scope'] * 1000000 for fuel in fuel_breakdown)
            ttw_ghg_intensity_aggregate = ttw_numerator / ttw_denominator if ttw_denominator > 0 else 0
            final_results['ttw_ghg_intensity_aggregate'] = ttw_ghg_intensity_aggregate
            
            # 9. GHG Intensity (GHGIEactual) = C100+C101 (WtT + TtW aggregate intensities)
            ghg_intensity_actual = wtt_ghg_intensity_aggregate + ttw_ghg_intensity_aggregate
            final_results['ghg_intensity_actual'] = ghg_intensity_actual
            
            # 10. Compliance Balance (gCO2eq) = (C94-C102)*C99 ((actual - target) * energy_use_scope)
            compliance_balance_gco2eq = (ghg_intensity_target_2025_2029 - ghg_intensity_actual) * energy_use_in_scope
            final_results['compliance_balance_gco2eq'] = compliance_balance_gco2eq
            
            # 11. Compliance Balance (tCO2eq) = C103/1000000 (convert gCO2eq to tCO2eq)
            compliance_balance_tco2eq = compliance_balance_gco2eq / 1000000
            final_results['compliance_balance_tco2eq'] = compliance_balance_tco2eq
            
            # 12. Penalty = IF(C103>0, "Not subject to a penalty", ABS(C103)/(C102*C107)*C108)
            # If compliance balance > 0, no penalty; otherwise calculate penalty
            if compliance_balance_gco2eq > 0:
                penalty = 0  # Not subject to a penalty
            else:
                # Constants for penalty calculation (C107=41000, C108=2400)
                vlsfo_lcv = self.CONSTANTS.get('VLSFO_LCV', 41000)  # C107: MJ/tonne for VLSFO
                fuel_penalty_rate = self.CONSTANTS.get('FUEL_PENALTY_RATE', 2400.00)  # C108: EUR per tonne
                
                # Formula: ABS(C103)/(C102*C107)*C108
                penalty = abs(compliance_balance_gco2eq) / (ghg_intensity_actual * vlsfo_lcv) * fuel_penalty_rate
            
            final_results['penalty'] = penalty
            
            # Add total GHG emission (sum of all fuels, in tonnes)
            total_ghg_emission = sum(fuel.get('ghg_emission', 0) for fuel in fuel_breakdown)
            final_results['ghg_emission'] = total_ghg_emission
            
            # Log Phase 2 results
            ###print(f"Phase 2 Results:")
            ###print(f"   GHG Intensity Target 2025-2029: {ghg_intensity_target_2025_2029:.6f} gCO2eq/MJ")
            ###print(f"   GHG Emission: {total_ghg_emission:.2f} tCO2eq")
            ###print(f"   Leg Energy Total in EU: {leg_energy_total_in_eu:.2f} MJ")
            ###print(f"   Leg Energy Total Out of EU: {leg_energy_total_out_eu:.2f} MJ")
            ###print(f"   FuelEU Energy Total in EU: {fueleu_energy_total_in_eu:.2f} MJ")
            ###print(f"   FuelEU Energy Total Out of EU: {fueleu_energy_total_out_eu:.2f} MJ")
            ###print(f"   Energy Use in Scope: {energy_use_in_scope:.2f} MJ")
            ###print(f"   WtT GHG Intensity (Aggregate): {wtt_ghg_intensity_aggregate:.6f} gCO2eq/MJ")
            ###print(f"   TtW GHG Intensity (Aggregate): {ttw_ghg_intensity_aggregate:.6f} gCO2eq/MJ")
            ###print(f"   GHG Intensity Actual: {ghg_intensity_actual:.6f} gCO2eq/MJ")
            ###print(f"   Compliance Balance: {compliance_balance_gco2eq:.2f} gCO2eq ({compliance_balance_tco2eq:.6f} tCO2eq)")
            ###print(f"   Penalty: EUR {penalty:.2f}")
            
            # Combine Phase 1 and Phase 2 results
            results = phase1_results.copy()
            results['final_results'] = final_results
            results['current_step'] = 'phase2_completed'
            
            ###print("Phase 2 COMPLETED: All aggregate calculations successfully executed")
            
            return results
            
        except Exception as e:
            ###print(f"Phase 2 calculation error: {e}")
            raise 