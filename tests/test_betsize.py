from utils.utils import (
    return_max_potlimit_betsize,
    return_standard_max_potlimit_betsize,
    Action,
    RAISE,
    BET,
)

###########################
### betsizes ###
###########################

### PREFLOP ###
# sb calls pre, bb raise
def test_sbcall_bbraise():
    bb = 10
    penultimate_betsize = 5
    previous_action = Action("Big Blind", True, RAISE, 5, 10, False, 20, 0, 0, 2, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 10.0
    last_aggro_street_total = 10.0
    pot = 20.0
    res = return_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (20, 30.0), res


def test_utgraise_utg13bet():
    # utg raise, utg+1 3bet
    bb = 10
    penultimate_betsize = 10
    previous_action = Action("UTG+1", True, RAISE, 35, 35, False, 20, 0, 0, 2, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 0.0
    last_aggro_street_total = 35.0
    pot = 50.0
    res = return_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (60, 120.0), res


def test_sbraise():
    # bb facing sb raise
    bb = 10
    penultimate_betsize = 10
    previous_action = Action("Dealer", True, RAISE, 20, 30, False, 20, 0, 0, 2, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 10.0
    last_aggro_street_total = 30.0
    pot = 40.0
    res = return_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (50, 90.0), res


def test_sblimp():
    bb = 20
    penultimate_betsize = 20
    previous_action = Action("Dealer", True, RAISE, 10, 20, False, 20, 0, 0, 2, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 20.0
    last_aggro_street_total = 20.0
    pot = 40.0
    res = return_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (40, 60.0), res


def test_nonblind_preflop():
    bb = 20
    penultimate_betsize = 20
    previous_action = Action("Dealer", True, RAISE, 10, 20, False, 20, 0, 0, 2, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 0.0
    last_aggro_street_total = 20.0
    pot = 30.0
    res = return_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (40, 70), res


def test_sb_unopened():
    bb = 20
    penultimate_betsize = 20
    previous_action = Action("Dealer", True, RAISE, 10, 20, False, 20, 0, 0, 2, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 10.0
    last_aggro_street_total = 20.0
    pot = 30.0
    res = return_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (40, 60), res


### Other
def test_raise_over_post():
    bb = 5
    penultimate_betsize = 10
    previous_action = Action("Dealer", True, BET, 10, 10, False, 20, 0, 0, 2, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 5.0
    last_aggro_street_total = 15.0
    pot = 20.0
    res = return_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (20, 40), res


def test_uopened_postflop():
    bb = 10
    penultimate_betsize = 0
    previous_action = None
    current_player_stack = 1000.0
    current_player_street_total = 10.0
    last_aggro_street_total = 10.0
    pot = 20.0
    res = return_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (0, 20), res


# precursor to next hand
def test_raise():
    bb = 10
    penultimate_betsize = 0
    previous_action = Action(
        "Big Blind", False, BET, 71.5, 71.5, False, 20, 0, 0, 2, 0, 0
    )
    current_player_stack = 894.0
    current_player_street_total = 0.0
    last_aggro_street_total = 71.5
    pot = 143.0
    res = return_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (143.0, 286.0), res


def test_reraise():
    bb = 10
    penultimate_betsize = 71.5
    previous_action = Action(
        "Big Blind", False, RAISE, 213.5, 285, False, 20, 0, 0, 2, 0, 0
    )
    current_player_stack = 894.0
    current_player_street_total = 71.5
    last_aggro_street_total = 285.0
    pot = 428.0
    res = return_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (498.5, 926.5), res


def test_pre_reraise():
    bb = 10
    penultimate_betsize = 20
    previous_action = Action("Dealer", False, RAISE, 70, 70, False, 20, 0, 0, 2, 0, 0)
    current_player_stack = 2000.0
    current_player_street_total = 20.0
    last_aggro_street_total = 70.0
    pot = 100.0
    res = return_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (120, 220), res


###########################
### Standard betsizes ###
###########################


# sb calls pre, bb raise
def test_standard_sbcall_bbraise():
    bb = 10
    penultimate_betsize = 5
    previous_action = Action("Big Blind", True, RAISE, 5, 10, False, 20, 0, 0, 2, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 10.0
    last_aggro_street_total = 10.0
    pot = 20.0
    res = return_standard_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (10, 30.0), res


def test_standard_utgraise_utg13bet():
    # utg raise, utg+1 3bet
    bb = 10
    penultimate_betsize = 10
    previous_action = Action("UTG+1", True, RAISE, 35, 35, False, 20, 0, 0, 2, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 0.0
    last_aggro_street_total = 35.0
    pot = 50.0
    res = return_standard_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (35, 120.0), res


def test_standard_sbraise():
    # bb facing sb raise
    bb = 10
    penultimate_betsize = 10
    previous_action = Action("Dealer", True, RAISE, 20, 30, False, 20, 0, 0, 2, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 10.0
    last_aggro_street_total = 30.0
    pot = 40.0
    res = return_standard_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (30, 90.0), res


def test_standard_sblimp():
    bb = 20
    penultimate_betsize = 20
    previous_action = Action("Dealer", True, RAISE, 10, 20, False, 20, 0, 0, 2, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 20.0
    last_aggro_street_total = 20.0
    pot = 40.0
    res = return_standard_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (20, 60.0), res


def test_standard_nonblind_preflop():
    bb = 20
    penultimate_betsize = 20
    previous_action = Action("Dealer", True, RAISE, 10, 20, False, 20, 0, 0, 2, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 0.0
    last_aggro_street_total = 20.0
    pot = 30.0
    res = return_standard_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (20, 70), res


def test_standard_sb_unopened():
    bb = 20
    penultimate_betsize = 20
    previous_action = Action("Dealer", True, RAISE, 10, 20, False, 0, 0, 0, 0, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 10.0
    last_aggro_street_total = 20.0
    pot = 30.0
    res = return_standard_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (20, 60), res


### Other
def test_standard_raise_over_post():
    bb = 5
    penultimate_betsize = 10
    previous_action = Action("Dealer", True, BET, 10, 10, False, 0, 0, 0, 0, 0, 0)
    current_player_stack = 1000.0
    current_player_street_total = 5.0
    last_aggro_street_total = 15.0
    pot = 20.0
    res = return_standard_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (10, 40), res


def test_standard_uopened_postflop():
    bb = 10
    penultimate_betsize = 0
    previous_action = None
    current_player_stack = 1000.0
    current_player_street_total = 10.0
    last_aggro_street_total = 10.0
    pot = 20.0
    res = return_standard_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (0, 20), res


# precursor to next hand
def test_standard_raise():
    bb = 10
    penultimate_betsize = 0
    previous_action = Action(
        "Big Blind", False, BET, 71.5, 71.5, False, 0, 0, 0, 0, 0, 0
    )
    current_player_stack = 894.0
    current_player_street_total = 0.0
    last_aggro_street_total = 71.5
    pot = 143.0
    res = return_standard_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (71.5, 286.0), res


def test_standard_reraise():
    bb = 10
    penultimate_betsize = 71.5
    previous_action = Action(
        "Big Blind", False, RAISE, 213.5, 285, False, 0, 0, 0, 0, 0, 0
    )
    current_player_stack = 894.0
    current_player_street_total = 71.5
    last_aggro_street_total = 285.0
    pot = 428.0
    res = return_standard_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (285.0, 926.5), res


def test_standard_pre_reraise():
    bb = 10
    penultimate_betsize = 20
    previous_action = Action("Dealer", False, RAISE, 70, 70, False, 0, 0, 0, 0, 0, 0)
    current_player_stack = 2000.0
    current_player_street_total = 20.0
    last_aggro_street_total = 70.0
    pot = 100.0
    res = return_standard_max_potlimit_betsize(
        previous_action,
        current_player_stack,
        current_player_street_total,
        last_aggro_street_total,
        pot,
        bb,
        penultimate_betsize,
    )
    assert res == (70, 220), res
