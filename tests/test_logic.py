import pandas as pd
import pytest

from core.logic import (
    load_data,
    validate_columns,
    clean_data,
    search_dictionary,
    filter_by_english_letter,
    calculate_statistics,
    calculate_letter_distribution,
)


def test_validate_columns_valid():
    """A DataFrame containing both required columns should be valid."""
    data = pd.DataFrame({
        "English": ["example"],
        "Noongar": ["value"],
    })

    assert validate_columns(data) is True


def test_validate_columns_missing_column():
    """A DataFrame missing a required column should raise ValueError."""
    data = pd.DataFrame({
        "English": ["example"],
    })

    with pytest.raises(ValueError):
        validate_columns(data)


def test_validate_columns_wrong_input():
    """Input that is not a DataFrame should raise TypeError."""
    with pytest.raises(TypeError):
        validate_columns(["example"])


def test_clean_data_removes_missing_values():
    """Rows containing missing dictionary values should be removed."""
    data = pd.DataFrame({
        "English": ["first", "second", None],
        "Noongar": ["value1", None, "value3"],
    })

    result = clean_data(data)

    assert len(result) == 1
    assert result.iloc[0]["English"] == "first"


def test_clean_data_removes_outer_spaces():
    """Whitespace at the start and end of values should be removed."""
    data = pd.DataFrame({
        "English": [" example "],
        "Noongar": [" value "],
    })

    result = clean_data(data)

    assert result.loc[0, "English"] == "example"
    assert result.loc[0, "Noongar"] == "value"


def test_search_dictionary_english():
    """The search should find a partial English match."""
    data = pd.DataFrame({
        "English": ["apple", "banana", "orange"],
        "Noongar": ["value1", "value2", "value3"],
    })

    result = search_dictionary(data, "ban")

    assert len(result) == 1
    assert result.iloc[0]["English"] == "banana"


def test_search_dictionary_case_insensitive():
    """Searches should not depend on uppercase or lowercase letters."""
    data = pd.DataFrame({
        "English": ["Apple", "Banana"],
        "Noongar": ["value1", "value2"],
    })

    result = search_dictionary(data, "APPLE")

    assert len(result) == 1
    assert result.iloc[0]["English"] == "Apple"


def test_search_dictionary_empty_query():
    """An empty search should return no results."""
    data = pd.DataFrame({
        "English": ["apple"],
        "Noongar": ["value1"],
    })

    result = search_dictionary(data, "")

    assert result.empty


def test_filter_by_english_letter():
    """Filtering should return entries beginning with the chosen letter."""
    data = pd.DataFrame({
        "English": ["apple", "banana", "blueberry"],
        "Noongar": ["value1", "value2", "value3"],
    })

    result = filter_by_english_letter(data, "b")

    assert len(result) == 2
    assert result.iloc[0]["English"] == "banana"
    assert result.iloc[1]["English"] == "blueberry"


def test_filter_invalid_letter():
    """An invalid letter filter should return no results."""
    data = pd.DataFrame({
        "English": ["apple", "banana"],
        "Noongar": ["value1", "value2"],
    })

    result = filter_by_english_letter(data, "AB")

    assert result.empty


def test_calculate_statistics():
    """Statistics should correctly count records and unique values."""
    data = pd.DataFrame({
        "English": ["apple", "apple", "banana"],
        "Noongar": ["value1", "value2", "value3"],
    })

    result = calculate_statistics(data)

    assert result["total_records"] == 3
    assert result["unique_english_terms"] == 2
    assert result["unique_noongar_entries"] == 3
    assert result["duplicate_english_terms"] == 1


def test_calculate_letter_distribution():
    """The function should correctly count starting English letters."""
    data = pd.DataFrame({
        "English": ["apple", "apricot", "banana"],
        "Noongar": ["value1", "value2", "value3"],
    })

    result = calculate_letter_distribution(data)

    assert result.loc[result["Letter"] == "A", "Count"].iloc[0] == 2
    assert result.loc[result["Letter"] == "B", "Count"].iloc[0] == 1


def test_load_data_missing_file():
    """Trying to load a nonexistent CSV should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_data("file_that_does_not_exist.csv")


def test_load_data_empty_path():
    """An empty file path should raise ValueError."""
    with pytest.raises(ValueError):
        load_data("")


def test_load_data_valid_file(tmp_path):
    """A valid CSV file should load into a DataFrame without error."""
    csv_file = tmp_path / "dictionary.csv"
    pd.DataFrame({
        "English": ["apple", "banana"],
        "Noongar": ["value1", "value2"],
    }).to_csv(csv_file, index=False)

    result = load_data(str(csv_file))

    assert list(result.columns) == ["English", "Noongar"]
    assert len(result) == 2