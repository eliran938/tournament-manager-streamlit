import pandas as pd
import ui_components


def test_empty_score_is_not_result():
    assert ui_components.has_match_result(float("nan"), float("nan")) is False


def test_one_empty_score_is_not_result():
    assert ui_components.has_match_result(2, float("nan")) is False
    assert ui_components.has_match_result(float("nan"), 1) is False


def test_empty_string_is_not_result():
    assert ui_components.has_match_result("", "") is False
    assert ui_components.has_match_result(" ", "2") is False


def test_zero_zero_is_valid_result():
    assert ui_components.has_match_result(0, 0) is True
    assert ui_components.format_display_score(0, 0) == "0 - 0"


def test_regular_score_display():
    assert ui_components.has_match_result(3, 1) is True
    assert ui_components.format_display_score(3, 1) == "3 - 1"


def test_string_numbers_are_valid():
    assert ui_components.has_match_result("2", "0") is True
    assert ui_components.format_display_score("2", "0") == "2 - 0"