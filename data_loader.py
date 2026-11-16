"""
Load World Countries data and prepare geography quiz records.

Cleaning decisions:
- Prepare capitals, flags and neighbours independently.
- Require a nonempty country name and country code.
- Capitals: keep exactly one nonblank capital.
- Flags: keep records with an available local SVG flag file.
- Neighbours: require at least one listed land neighbour and require
  all listed border codes to resolve to country names.

"""

import json
from pathlib import Path


DATA_PATH = Path(__file__).parent / "data" / "countries.json"
FLAGS_FOLDER = Path(__file__).parent / "data" / "flags"


def load_countries(path):
    """
    Read country records from a JSON file.

    Parameters
    ----------
    path : pathlib.Path
        Location of the countries JSON file.

    Returns
    -------
    list of dict
        Original country records.

    Raises
    ------
    OSError
        If the file cannot be opened or read.
    ValueError
        If the JSON is invalid or is not a list of country dictionaries.
    """
    with open(path, encoding="utf-8") as file:
        countries = json.load(file)

    if not isinstance(countries, list):
        raise ValueError("Country data must be a list.")

    for country in countries:
        if not isinstance(country, dict):
            raise ValueError("Each country record must be a dictionary.")

    return countries


def prepare_capitals(countries):
    """
    Select countries with exactly one usable capital.

    Parameters
    ----------
    countries : list of dict
        Original World Countries records.

    Returns
    -------
    list of dict
        Records containing country_code, name, capital, region and subregion.
    """
    records = []

    for country in countries:
        name = country.get("name", {}).get("common", "").strip()
        country_code = country.get("cca3", "").strip()
        capitals = country.get("capital", [])

        if name and country_code and len(capitals) == 1:
            capital = capitals[0].strip()

            if capital:
                records.append({
                    "country_code": country_code,
                    "name": name,
                    "capital": capital,
                    "region": country.get("region", "").strip(),
                    "subregion": country.get("subregion", "").strip()
                })

    return records


def prepare_flags(countries, flags_folder):
    """
    Select UN-member countries with available, usable flag files.

    Parameters
    ----------
    countries : list of dict
        Original World Countries records.
    flags_folder : pathlib.Path
        Folder containing SVG files named with lowercase country codes.

    Returns
    -------
    list of dict
        Records containing country_code, name, flag_path, region and subregion.
        Only records explicitly marked as UN members are included.
        Indonesia, Monaco, Romania and Chad are excluded because their flags
        form pairs that can be difficult to distinguish in a quiz image.
        Records without a nonempty name, code or matching file are excluded.

    Raises
    ------
    FileNotFoundError
        If the flag folder does not exist.
    """
    if not flags_folder.is_dir():
        raise FileNotFoundError(
            "Cannot find the flag folder: " + str(flags_folder)
        )

    ambiguous_flag_codes = ["IDN", "MCO", "ROU", "TCD"]
    records = []

    for country in countries:
        if country.get("unMember", False) is not True:
            continue

        name = country.get("name", {}).get("common", "").strip()
        country_code = country.get("cca3", "").strip()

        if country_code in ambiguous_flag_codes:
            continue

        if name and country_code:
            flag_path = flags_folder / (country_code.lower() + ".svg")

            if flag_path.is_file():
                records.append({
                    "country_code": country_code,
                    "name": name,
                    "flag_path": str(flag_path),
                    "region": country.get("region", "").strip(),
                    "subregion": country.get("subregion", "").strip()
                })

    return records


def prepare_neighbors(countries):
    """
    Select countries whose listed land neighbours can all be identified.

    Parameters
    ----------
    countries : list of dict
        Original World Countries records.

    Returns
    -------
    list of dict
        Records containing country_code, name, borders and neighbor_names.
        Countries with no borders or unresolved border codes are excluded.
    """
    country_names = {}

    for country in countries:
        code = country.get("cca3", "").strip()
        name = country.get("name", {}).get("common", "").strip()

        if code and name:
            country_names[code] = name

    records = []

    for country in countries:
        name = country.get("name", {}).get("common", "").strip()
        country_code = country.get("cca3", "").strip()
        borders = country.get("borders", [])

        if name and country_code and borders:
            neighbor_names = []

            for border_code in borders:
                if border_code in country_names:
                    neighbor_names.append(country_names[border_code])

            if len(neighbor_names) == len(borders):
                records.append({
                    "country_code": country_code,
                    "name": name,
                    "region": country.get("region", "").strip(),
                    "subregion": country.get("subregion", "").strip(),
                    "borders": borders.copy(),
                    "neighbor_names": neighbor_names
                })

    return records


def main():
    """Load the dataset and print counts and examples for each topic."""
    try:
        countries = load_countries(DATA_PATH)

    except FileNotFoundError:
        print("Cannot find the dataset:", DATA_PATH)
        print("Place countries.json inside the data folder.")

    except (ValueError, UnicodeDecodeError):
        print("Cannot read the dataset as valid UTF-8 country JSON.")
        print("Check that you downloaded the actual countries.json file.")

    except OSError as error:
        print("Cannot open or read the dataset:", error)

    else:
        capital_countries = prepare_capitals(countries)
        neighboring_countries = prepare_neighbors(countries)

        # Handle a missing flag folder separately from a missing JSON file.
        try:
            flag_countries = prepare_flags(countries, FLAGS_FOLDER)

        except FileNotFoundError as error:
            print(error)
            print("Place the SVG flag files inside data/flags.")
            return

        print("Records loaded:", len(countries))

        print()
        print("Countries with one usable capital:", len(capital_countries))
        for country in capital_countries[:5]:
            print(country["name"], "-", country["capital"])

        print()
        print("Countries with available flag files:", len(flag_countries))
        for country in flag_countries[:5]:
            print(country["name"], "-", country["flag_path"])

        if not flag_countries:
            print("No matching SVG files found. Check filenames such as ita.svg.")

        print()
        print(
            "Countries with usable land neighbours:",
            len(neighboring_countries)
        )
        for country in neighboring_countries[:5]:
            print(
                country["name"],
                "-",
                ", ".join(country["neighbor_names"])
            )


if __name__ == "__main__":
    main()