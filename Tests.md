# Tests

## `experiments.py`

* [x] `TestMatrix()`
  * [x] `__init__()`
    * [x] num_replicates <= 0
      * ValueError('bad number of replicates')
        * [x] <0
        * [x] = 0
    * [x] Non-iterable equivalence
      - [x] creates iterable (`len(self.equivalence)` gives no error)
    * [x] Iterable equivalence with non-numeric
      - [x] TypeError('equivalence has non-numeric items')
    * [x] equivalence <= 0
      * [x] ValueError('equivalence <= 0')
        * [x] <0
        * [x] =0
    * [x] Non-iterable diluent_mole_fraction
      - [x] creates iterable (`len(self.diluent_mole_fraction)` gives no error)
    * [x] Iterable diluent_mole_fraction with non-numeric
      - [x] TypeError('diluent_mole_fraction has non-numeric items')
    * [x] diluent_mole_fraction outside of [0, 1)
      * [x] bad
        * ValueError('diluent mole fraction outside of [0, 1)')
        * [x] <0
        * [x] \>1
        * [x] =1
      * [x] good
        * [x] =0
        * [x] =0.99
  * [x] `_build_replicate()`
    * [x] compare output current_replicate to hand-calcs
      * [x] diluted
      * [x] undiluted
  * [x] `generate_test_matrices()`
    * [x] `self.replicates` contains no `None`
    * [x] each replicate contains the same items
    * [x] each replicate is in a different order
  * [x] `save()`
    * [x] files write to disk as expected (delete)

## `thermochem.py`

* [x] `calculate_laminar_flamespeed()`

  * [x] move tests from `test_tools.py`

* [x] `calculate_get_eq_sound_speed()`
  * [x] move tests from `test_tools.py`

* [ ] `Mixture`

  * [ ] `__init__()`
    * [ ] no unit registry is given
    * [ ] unit registry is given
    * [ ] bad fuel
      * [ ] ValueError('Bad fuel')
    * [ ] bad oxidizer
      * [ ] ValueError('Bad oxidizer')
    * [ ] bad diluent
      * [ ] ValueError('Bad diluent')
    * [ ] diluent and mole fraction are given
      * [ ] `self.diluted not None`
    * [ ] diluent and mole fraction not given
      * [ ] `self.diluted is None`
  * [ ] `set_equivalence()`
    * contains nothing very special, will get all branches run through as long as:
      * [ ] successful `__init__` without dilution
      * [ ] successful `__init__` with dilution
  * [ ] `add_diluent()`
    * [ ] bad diluent
      * [ ] ValueError('Bad diluent: {}'.format(diluent))
    * [ ] diluent is fuel or oxidizer
      * ValueError('You can\'t dilute with fuel or oxidizer!')
        * [ ] fuel
        * [ ] oxidizer
    * [ ] mole fraction > 1
      * [ ] ValueError('Bro, do you even mole fraction?')
  * [ ] `get_mass()`
    * compare against hand calcs
      * [ ] undiluted
      * [ ] diluted

  - [ ] `get_pressures()`
    - compare against hand calcs
      - [ ] undiluted
      - [ ] diluted

  