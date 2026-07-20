import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.rotation import is_night_time


def t(hh, mm):
    return datetime.time(hh, mm)


def test_is_night_time_same_day_window():
    """A window that doesn't cross midnight (e.g. 13:00 -> 18:00, an unusual but valid config)."""
    assert is_night_time(t(14, 0), "13:00", "18:00") is True
    assert is_night_time(t(12, 59), "13:00", "18:00") is False
    assert is_night_time(t(18, 0), "13:00", "18:00") is False  # wake time is exclusive


def test_is_night_time_overnight_window():
    """The typical case: night starts in the evening and wraps past midnight."""
    assert is_night_time(t(23, 30), "23:00", "07:00") is True
    assert is_night_time(t(3, 0), "23:00", "07:00") is True
    assert is_night_time(t(12, 0), "23:00", "07:00") is False
    assert is_night_time(t(6, 59), "23:00", "07:00") is True
    assert is_night_time(t(7, 0), "23:00", "07:00") is False  # wake time is exclusive


def test_is_night_time_exact_boundaries():
    assert is_night_time(t(23, 0), "23:00", "07:00") is True   # off_time is inclusive


def test_is_night_time_malformed_strings_fail_safe():
    """A typo'd/empty config value should never accidentally force permanent standby."""
    assert is_night_time(t(23, 30), "", "07:00") is False
    assert is_night_time(t(23, 30), "not-a-time", "07:00") is False
    assert is_night_time(t(23, 30), "23:00", "") is False
    assert is_night_time(t(23, 30), None, "07:00") is False
