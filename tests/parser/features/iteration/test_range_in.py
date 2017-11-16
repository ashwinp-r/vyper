import pytest
from tests.setup_transaction_tests import chain as s, tester as t, ethereum_utils as u, check_gas, \
    get_contract_with_gas_estimation, get_contract, assert_tx_failed
from viper.exceptions import TypeMismatchException


def test_basic_in_list():
    code = """
def testin(x: num) -> bool:
    y = 1
    s = [1, 2, 3, 4]
    if (x + 1) in s:
        return True
    return False
    """

    c = get_contract(code)

    assert c.testin(0) is True
    assert c.testin(1) is True
    assert c.testin(2) is True
    assert c.testin(3) is True
    assert c.testin(4) is False
    assert c.testin(5) is False
    assert c.testin(-1) is False


def test_in_storage_list():
    code = """
allowed: num[10]

def in_test(x: num) -> bool:
    self.allowed = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    if x in self.allowed:
        return True
    return False
    """

    c = get_contract(code)

    assert c.in_test(1) is True
    assert c.in_test(9) is True
    assert c.in_test(11) is False
    assert c.in_test(-1) is False
    assert c.in_test(32000) is False


def test_cmp_in_list():
    code = """
def in_test(x: num) -> bool:
    if x in [9, 7, 6, 5]:
        return True
    return False
    """

    c = get_contract(code)

    assert c.in_test(1) is False
    assert c.in_test(-7) is False
    assert c.in_test(-9) is False
    assert c.in_test(5) is True
    assert c.in_test(7) is True


def test_mixed_in_list(assert_compile_failed):
    code = """
def testin() -> bool:
    s = [1, 2, 3, 4]
    if "test" in s:
        return True
    return False
    """
    assert_compile_failed(lambda: get_contract(code), TypeMismatchException)


def test_ownership(assert_tx_failed):
    code = """

owners: address[2]

def __init__():
    self.owners[0] = msg.sender

def set_owner(i: num, new_owner: address):
    assert msg.sender in self.owners
    self.owners[i] = new_owner

def is_owner() -> bool:
    return msg.sender in self.owners
    """

    c = get_contract(code)

    assert c.is_owner() is True  # contract creator is owner.
    assert c.is_owner(sender=t.k1) is False  # no one else is.

    # only an owner may set another owner.
    assert_tx_failed(lambda: c.set_owner(1, t.a1, sender=t.k1))

    c.set_owner(1, t.a1)
    assert c.is_owner(sender=t.k1) is True

    # Owner in place 0 can be replaced.
    c.set_owner(0, t.a1)
    assert c.is_owner() is False