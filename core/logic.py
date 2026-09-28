import os
import pandas as pd


REQUIRED_COLUMNS = ["English", "Noongar"]


def load_data(file_path):
	"""Load and validate the Noongar dictionary CSV."""
	if isinstance(file_path, os.PathLike):
		file_path = os.fspath(file_path)
	if not isinstance(file_path, str) or file_path.strip() == "":
		raise ValueError("A valid file path must be provided.")
	if not os.path.isfile(file_path):
		raise FileNotFoundError(f"Data file not found: {file_path}")
	try:
		data = pd.read_csv(file_path)
	except Exception as error:
		raise ValueError(f"Unable to read the CSV file: {error}") from error
	validate_columns(data)
	return data


def validate_columns(data):
	"""Check that the dataset contains the required columns."""
	if not isinstance(data, pd.DataFrame):
		raise TypeError("Data must be a pandas DataFrame.")
	missing_columns = [column for column in REQUIRED_COLUMNS if column not in data.columns]
	if missing_columns:
		raise ValueError("Missing required column(s): " + ", ".join(missing_columns))
	return True


def clean_data(data):
	"""Remove incomplete entries and trim dictionary values."""
	validate_columns(data)
	cleaned_data = data.dropna(subset=REQUIRED_COLUMNS).copy()
	for column in REQUIRED_COLUMNS:
		cleaned_data[column] = cleaned_data[column].astype(str).str.strip()
	cleaned_data = cleaned_data[
		(cleaned_data["English"] != "") & (cleaned_data["Noongar"] != "")
	]
	return cleaned_data.reset_index(drop=True)


def search_dictionary(data, query):
	"""Search both dictionary columns using a case-insensitive partial match."""
	validate_columns(data)
	if not isinstance(query, str) or not query.strip():
		return data.iloc[0:0].copy()
	query = query.strip().lower()
	english = data["English"].fillna("").astype(str).str.lower()
	noongar = data["Noongar"].fillna("").astype(str).str.lower()
	matches = english.str.contains(query, regex=False) | noongar.str.contains(
		query, regex=False
	)
	return data.loc[matches].copy()


def filter_by_english_letter(data, letter):
	"""Return entries whose English term starts with the specified letter."""
	validate_columns(data)
	if not isinstance(letter, str) or len(letter.strip()) != 1 or not letter.strip().isalpha():
		return data.iloc[0:0].copy()
	letter = letter.strip().lower()
	english = data["English"].fillna("").astype(str).str.lower()
	return data[english.str.startswith(letter)].copy()


def calculate_statistics(data):
	"""Calculate basic dictionary statistics."""
	validate_columns(data)
	total_records = len(data)
	return {
		"total_records": total_records,
		"unique_english_terms": data["English"].nunique(),
		"unique_noongar_entries": data["Noongar"].nunique(),
		"duplicate_english_terms": total_records - data["English"].nunique(),
	}


def calculate_letter_distribution(data):
	"""Count how many English dictionary entries begin with each letter."""
	validate_columns(data)
	counts = {}
	for english_term in data["English"]:
		if pd.isna(english_term):
			continue
		english_term = str(english_term).strip()
		if not english_term or not english_term[0].isalpha():
			continue
		first_letter = english_term[0].upper()
		counts[first_letter] = counts.get(first_letter, 0) + 1
	distribution = pd.DataFrame(list(counts.items()), columns=["Letter", "Count"])
	return distribution.sort_values("Letter").reset_index(drop=True) if not distribution.empty else distribution