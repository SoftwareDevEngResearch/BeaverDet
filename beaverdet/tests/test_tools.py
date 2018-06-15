# -*- coding: utf-8 -*-
"""
PURPOSE:
    Unit tests for tools.py

CREATED BY:
    Mick Carter
    Oregon State University
    CIRE and Propulsion Lab
    cartemic@oregonstate.edu
"""


from math import sqrt
import pytest
import pint
import cantera as ct
from ..tube_design_tools import tools


def test_lookup_flange_class():
    """
    Tests the lookup_flange_class() function, which takes in a temperature,
    pressure, and a string for the desired flange material and returns the
    minimum required flange class. Dataframes are assumed to be good due to
    unit testing of their import function, get_flange_limits_from_csv().

    Conditions tested:
        - Function returns expected value within P, T limits
        - Proper error handling when temperature is outside allowable range
        - Proper error handling when pressure is outside allowable range
        - Proper error handling when desired material isn't in database
    """
    # ----------------------------INPUT TESTING----------------------------
    # check for error handling with non-string material
    # check for error handling with bad material

    # incorporate units with pint
    ureg = pint.UnitRegistry()
    quant = ureg.Quantity

    # set temperatures for various tests. Values are selected to create desired
    # error conditions based on known information from 316L P-T curves.
    temp_low = quant(-100, ureg.degC)       # temperature too low
    temp_high = quant(500, ureg.degC)       # temperature too high
    temp_good = quant(350, ureg.degC)       # temperature and units good

    # set pressures for various tests. Values are selected to create desired
    # error conditions based on known information from 316L P-T curves.
    press_low = quant(-10, ureg.bar)        # pressure too low
    press_high = quant(350, ureg.bar)       # pressure too high
    press_good = quant(125, ureg.bar)       # pressure and units good

    # pick material group and import lookup dataframe
    # note: T = 350 °C and P = 125 bar for group 2.3, class should be 1500
    material = '316L'   # 316L is in group 2.3

    # check for expected value within limits
    test_class = tools.lookup_flange_class(temp_good, press_good, material)
    assert test_class == '1500'

    # check for error handling with temperature too low/high
    test_temperatures = [temp_low, temp_high]
    for temperature in test_temperatures:
        with pytest.raises(ValueError, match='Temperature out of range.'):
            tools.lookup_flange_class(temperature, press_good, material)

    # check for error handling with pressure too low/high
    test_pressures = [press_low, press_high]
    for pressure in test_pressures:
        with pytest.raises(ValueError, match='Pressure out of range.'):
            tools.lookup_flange_class(temp_good, pressure, material)

    # check for error handling when material isn't in database
    with pytest.raises(ValueError, match='Desired material not in database.'):
        tools.lookup_flange_class(temp_good, press_good, 'unobtainium')

    # check for error handling with non-string material
    bad_materials = [0, 3.14, -7]
    for bad_material in bad_materials:
        with pytest.raises(ValueError,
                           match='Desired material non-string input.'):
            tools.lookup_flange_class(temp_good, press_good, bad_material)


def test_calculate_spiral_diameter():
    """
    Tests the calculate_spiral_diameter function, which takes the pipe inner
    diameter as a pint quantity, and the desired blockage ratio as a float
    and returns the diameter of the corresponding Shchelkin spiral.

    Conditions tested: ADD ZERO DIAMETER CASE
        - Good input
        - Proper handling with blockage ratio outside of 0<BR<100
        - Proper handling with tube of diameter 0
    """
    # incorporate units with pint
    ureg = pint.UnitRegistry()
    quant = ureg.Quantity

    # define a pipe inner diameter and blockage ratio
    test_diameter = quant(5.76, ureg.inch)
    test_blockage_ratio = 0.44

    # define expected result and actual result
    expected_spiral_diameter = test_diameter / 2 * \
        (1 - sqrt(1 - test_blockage_ratio))
    result = tools.calculate_spiral_diameter(test_diameter,
                                             test_blockage_ratio)

    # ensure good output
    assert expected_spiral_diameter == result.to(ureg.inch)

    # ensure proper handling with non-numeric blockage ratio
    with pytest.raises(ValueError, match='Non-numeric blockage ratio.'):
        tools.calculate_spiral_diameter(test_diameter, 'doompity doo')

    # ensure proper handling with blockage ratio outside allowable limits
    bad_blockage_ratios = [-35.124, 0, 1, 120.34]
    for ratio in bad_blockage_ratios:
        with pytest.raises(ValueError,
                           match='Blockage ratio outside of 0<BR<1'):
            tools.calculate_spiral_diameter(test_diameter, ratio)


def test_calculate_blockage_ratio():
    """
    Tests the get_blockage_ratio function, which takes arguments of det tube
    inner diameter and spiral blockage diameter.

    Conditions tested:
        - good input (both zero and nonzero)
        - units are mismatched
        - non-pint blockage diameter
        - non-numeric pint blockage diameter
        - blockage diameter with bad units
        - non-pint tube diameter
        - non-numeric pint tube diameter
        - tube diameter with bad units
        - blockage diameter < 0
        - blockage diameter >= tube diameter
        - tube diameter < 0
    """
    # incorporate units with pint
    ureg = pint.UnitRegistry()
    quant = ureg.Quantity

    # known good results from hand-calcs
    test_tube_diameter = quant(3.438, ureg.inch)
    test_blockage_diameter = quant(7./16., ureg.inch)
    hand_calc_blockage_ratio = 0.444242326717679

    # check for expected result with good input
    test_result = tools.calculate_blockage_ratio(test_tube_diameter,
                                                 test_blockage_diameter)
    assert (test_result - hand_calc_blockage_ratio) < 1e-8
    test_result = tools.calculate_blockage_ratio(test_tube_diameter,
                                                 quant(0, ureg.inch))
    assert (test_result - hand_calc_blockage_ratio) < 1e-8

    # check for correct handling when blockage diameter >= tube diameter
    with pytest.raises(ValueError,
                       match='blockage diameter >= tube diameter'):
        tools.calculate_blockage_ratio(test_blockage_diameter,
                                       test_tube_diameter)


def test_calculate_window_sf():
    """
    Tests the calculate_window_sf function, which calculates the factor of
    safety for a viewing window.

    Conditions tested:
        - good input (all potential errors are handled by
            accessories.check_pint_quantity)
    """
    ureg = pint.UnitRegistry()
    quant = ureg.Quantity

    width = quant(50, ureg.mm).to(ureg.inch)
    length = quant(20, ureg.mm).to(ureg.mile)
    pressure = quant(1, ureg.atm).to(ureg.torr)
    thickness = quant(1.2, ureg.mm).to(ureg.furlong)
    rupture_modulus = quant(5300, ureg.psi).to(ureg.mmHg)
    desired_safety_factor = 4

    test_sf = tools.calculate_window_sf(
        length,
        width,
        thickness,
        pressure,
        rupture_modulus
    )

    assert abs(test_sf - desired_safety_factor) / test_sf < 0.01


def test_calculate_window_thk():
    """
    Tests the calculate_window_thk function, which calculates the thickness of
    a viewing window.

    Conditions tested:
        - safety factor < 1
        - non-numeric safety factor
        - good input
    """
    ureg = pint.UnitRegistry()
    quant = ureg.Quantity

    width = quant(50, ureg.mm).to(ureg.inch)
    length = quant(20, ureg.mm).to(ureg.mile)
    pressure = quant(1, ureg.atm).to(ureg.torr)
    rupture_modulus = quant(5300, ureg.psi).to(ureg.mmHg)
    desired_thickness = quant(1.2, ureg.mm)

    # safety factor < 1
    safety_factor = [0.25, -7]
    for factor in safety_factor:
        with pytest.raises(ValueError, match='Window safety factor < 1'):
            tools.calculate_window_thk(
                length,
                width,
                factor,
                pressure,
                rupture_modulus
            )

    # non-numeric safety factor
    safety_factor = 'BruceCampbell'
    with pytest.raises(TypeError, match='Non-numeric window safety factor'):
        tools.calculate_window_thk(
            length,
            width,
            safety_factor,
            pressure,
            rupture_modulus
        )

    # good input
    safety_factor = 4
    test_thickness = tools.calculate_window_thk(
        length,
        width,
        safety_factor,
        pressure,
        rupture_modulus
    )
    test_thickness = test_thickness.to(desired_thickness.units).magnitude
    desired_thickness = desired_thickness.magnitude
    assert abs(test_thickness - desired_thickness) / test_thickness < 0.01


def test_get_pipe_dlf():
    """
    Tests get_pipe_dlf

    Conditions tested:
        - good input
            * load factor is 1
            * load factor is 2
            * load factor is 4
        - plus_or_minus outside of (0, 1)
        - pipe material not in materials list
    """
    ureg = pint.UnitRegistry()
    quant = ureg.Quantity

    # good input
    pipe_material = '316L'
    pipe_schedule = '80'
    nominal_pipe_size = '6'
    # from hand calcs, critical velocity is 1457.44 m/s, giving upper and lower
    # bounds of 1603.188 and 1311.700 m/s
    cj_speeds = [
        quant(1200, 'm/s'),     # DLF 1
        quant(1311, 'm/s'),     # DLF 1
        quant(1312, 'm/s'),     # DLF 4
        quant(1400, 'm/s'),     # DLF 4
        quant(1603, 'm/s'),     # DLF 4
        quant(1604, 'm/s'),     # DLF 2
        quant(2000, 'm/s')      # DLF 2
    ]
    expected_dlf = [1, 1, 4, 4, 4, 2, 2]
    for cj_speed, dlf in zip(cj_speeds, expected_dlf):
        test_dlf = tools.get_pipe_dlf(
            pipe_material,
            pipe_schedule,
            nominal_pipe_size,
            cj_speed
        )
        assert test_dlf == dlf

    # plus_or_minus outside of (0, 1)
    cj_speed = cj_speeds[0]
    bad_plus_minus = [-1, 0, 1, 2]
    for plus_minus in bad_plus_minus:
        try:
            tools.get_pipe_dlf(
                pipe_material,
                pipe_schedule,
                nominal_pipe_size,
                cj_speed,
                plus_minus
            )
        except ValueError as err:
            assert str(err) == 'plus_or_minus factor outside of (0, 1)'

    # pipe material not in materials list
    pipe_material = 'cheese'
    with pytest.raises(
            ValueError,
            match='Pipe material not found in materials_list.csv'
    ):
        tools.get_pipe_dlf(
            pipe_material,
            pipe_schedule,
            nominal_pipe_size,
            cj_speed
        )


def test_calculate_ddt_run_up():
    ureg = pint.UnitRegistry()
    quant = ureg.Quantity

    # use a unit diameter to match diameter-specific values from plot
    tube_diameter = quant(1, 'meter')

    # define gas mixture and relevant pint quantities
    mechanism = 'gri30.cti'
    gas = ct.Solution(mechanism)
    gas.TP = 300, 101325
    initial_temperature = quant(gas.T, 'K')
    initial_pressure = quant(gas.P, 'Pa')
    gas.set_equivalence_ratio(1, 'CH4', {'O2': 1, 'N2': 3.76})
    species_dict = gas.mole_fraction_dict()

    # test with bad blockage ratio
    bad_blockages = [-4., 0, 1]
    for blockage_ratio in bad_blockages:
        with pytest.raises(
                ValueError,
                match='Blockage ratio outside of correlation range'
        ):
            tools.calculate_ddt_run_up(
                blockage_ratio,
                tube_diameter,
                initial_temperature,
                initial_pressure,
                species_dict,
                mechanism
            )

    # define good blockage ratios and expected result from each
    good_blockages = [0.1, 0.2, 0.3, 0.75]
    good_results = [
        48.51385390428211,
        29.24433249370277,
        18.136020151133494,
        4.76070528967254
    ]

    # test with good inputs
    for blockage_ratio, result in zip(good_blockages, good_results):
        test_runup = tools.calculate_ddt_run_up(
            blockage_ratio,
            tube_diameter,
            initial_temperature,
            initial_pressure,
            species_dict,
            mechanism,
            phase_specification='gri30_mix'
        )

        assert (
                test_runup.units.format_babel() ==
                tube_diameter.units.format_babel()
        )

        assert 0.5 * result <= test_runup.magnitude <= 1.5 * result


def test_calculate_bolt_stress_areas():
    ureg = pint.UnitRegistry()
    quant = ureg.Quantity

    def compare(manual, tested):
        for key, value in manual.items():
            test_value = tested[key].to(
                value.units.format_babel()).magnitude
            value = value.magnitude
            assert abs(test_value - value) / value < 1e-4

    # test bolt > 100ksi
    thread_size = '1/4-28'
    thread_class = '2'
    bolt_max_tensile = quant(120, 'ksi')
    plate_max_tensile = quant(30, 'ksi')
    engagement_length = quant(0.5, 'in')
    hand_calc = {
        'screw area': quant(0.034934049, 'in^2'),
        'plate area': quant(0.308744082, 'in^2'),
        'minimum engagement': quant(0.452595544, 'in')
    }
    test_areas = tools.calculate_bolt_stress_areas(
        thread_size,
        thread_class,
        bolt_max_tensile,
        plate_max_tensile,
        engagement_length
    )
    compare(hand_calc, test_areas)

    # test bolt < 100ksi
    bolt_max_tensile = quant(80, 'ksi')
    hand_calc['screw area'] = quant(
        0.036374073,
        'in^2'
    )
    hand_calc['minimum engagement'] = quant(
        0.314168053,
        'in'
    )
    test_areas = tools.calculate_bolt_stress_areas(
        thread_size,
        thread_class,
        bolt_max_tensile,
        plate_max_tensile,
        engagement_length
    )
    compare(hand_calc, test_areas)

    # ensure warning when engagement length < minimum
    engagement_length = quant(0.05, 'in')
    with pytest.warns(
        Warning,
        match='Screws fail in shear, not tension.' +
              ' Plate may be damaged.' +
              ' Consider increasing bolt engagement length'
    ):
        tools.calculate_bolt_stress_areas(
            thread_size,
            thread_class,
            bolt_max_tensile,
            plate_max_tensile,
            engagement_length
        )


def test_calculate_window_bolt_sf():
    ureg = pint.UnitRegistry()
    quant = ureg.Quantity

    def compare(manual, tested):
        for key, value in manual.items():
            test_value = tested[key].to('').magnitude
            assert abs(test_value - value) / value < 1e-4

    max_pressure = quant(1631.7, 'psi')
    window_area = quant(5.75*2.5, 'in^2')
    num_bolts = 20
    thread_size = '1/4-28'
    thread_class = '2'
    bolt_max_tensile = quant(120, 'ksi')
    plate_max_tensile = quant(30, 'ksi')
    engagement_length = quant(0.5, 'in')

    hand_calc = {
        'bolt': 3.606968028,
        'plate': 7.969517321,
    }

    test_values = tools.calculate_window_bolt_sf(
        max_pressure,
        window_area,
        num_bolts,
        thread_size,
        thread_class,
        bolt_max_tensile,
        plate_max_tensile,
        engagement_length
    )

    compare(hand_calc, test_values)


def test_calculate_max_initial_pressure():
        ureg = pint.UnitRegistry()
        quant = ureg.Quantity

        # define required variables
        pipe_material = '316L'
        pipe_schedule = '80'
        pipe_nps = '6'
        welded = False
        desired_fs = 4
        initial_temperature = quant(300, 'K')
        species_dict = {'H2': 1, 'O2': 0.5}
        mechanism = 'gri30.cti'
        max_pressures = [quant(1200, 'psi'), False]
        error_tol = 1e-4

        max_solutions = [max_pressures[0], quant(149.046409603932, 'atm')]

        # test function output
        for max_pressure, max_solution in zip(max_pressures, max_solutions):
            test_result = tools.calculate_max_initial_pressure(
                pipe_material,
                pipe_schedule,
                pipe_nps,
                welded,
                desired_fs,
                initial_temperature,
                species_dict,
                mechanism,
                max_pressure=max_pressure,
                error_tol=error_tol
            )

            states = tools.calculate_reflected_shock_state(
                test_result,
                initial_temperature,
                species_dict,
                mechanism
            )

            # get dynamic load factor
            dlf = tools.get_pipe_dlf(
                pipe_material,
                pipe_schedule,
                pipe_nps,
                states['cj']['speed']
            )

            calc_max = states['reflected']['state'].P
            max_solution = max_solution.to('Pa').magnitude / dlf

            error = abs(max_solution - calc_max) / max_solution

            assert error <= 0.0005
