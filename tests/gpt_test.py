import pytest
from utils.utils import *

def test_calc_rake():
    assert calc_rake(2, 0.25, 10) == 0.1
    assert calc_rake(4, 0.25, 20) == 0.4
    assert calc_rake(6, 0.25, 30) == 0.6

def test_return_max_potlimit_betsize():
    previous_aggro_action = Action(1, True, BET, 2, 4, 0.5, False, 10, 0.1, 0, 3, 1)
    assert return_max_potlimit_betsize(previous_aggro_action, 10, 4, 2, 20, 0.25, 1) == (4, 12)
    previous_aggro_action = Action(1, True, RAISE, 3, 8, 0.75, False, 20, 0.2, 0, 3, 2)
    assert return_max_potlimit_betsize(previous_aggro_action, 15, 8, 5, 25, 0.5, 2) == (4.5, 22)

def test_return_standard_max_potlimit_betsize():
    previous_aggro_action = Action(1, True, BET, 2, 4, 0.5, False, 10, 0.1, 0, 3, 1)
    assert return_standard_max_potlimit_betsize(previous_aggro_action, 10, 4, 2, 20, 0.25, 1) == (1, 24)
    previous_aggro_action = Action(1, True, RAISE, 3, 8, 0.75, False, 20, 0.2, 0, 3, 2)
    assert return_standard_max_potlimit_betsize(previous_aggro_action, 15, 8, 5, 25, 0.5, 2) == (2, 42)
