from nose.tools import assert_equal, assert_true

# from helper_functions import *

def test_upper_trimed_mean():
    a = upper_trimed_mean(range(1, 101), .7)
    b = np.mean(range(1, 71))

    assert_equals(a, b)
