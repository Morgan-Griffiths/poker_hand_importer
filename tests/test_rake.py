from utils import calc_rake


def test_rake_hi_players2():
    bb = 10
    num_players = 2
    pot = 20
    rake = calc_rake(num_players, bb, pot)
    assert rake == 1, rake


def test_rake_hi_players5():
    bb = 5
    num_players = 5
    pot = 115
    rake = calc_rake(num_players, bb, pot)
    assert rake == 3, rake


def test_rake_hi_players2_small():
    bb = 10
    num_players = 2
    pot = 10
    rake = calc_rake(num_players, bb, pot)
    assert rake == 0.5, rake


def test_rake_hi_players6():
    bb = 10
    num_players = 6
    pot = 75
    rake = calc_rake(num_players, bb, pot)
    assert rake == 3.75, rake


def test_rake_hi_players3():
    bb = 10
    num_players = 3
    pot = 70
    rake = calc_rake(num_players, bb, pot)
    assert rake == 2, rake
