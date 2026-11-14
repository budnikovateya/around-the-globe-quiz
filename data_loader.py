"""
Load World Countries data and prepare records for three quiz topics:
capitals, currencies and neighbouring countries.

Prepare each topic independently:
- Capitals: keep records with a nonempty name and exactly one nonblank capital.
- Currencies: keep records with a nonempty name and exactly one currency
  with a usable name and code.
- Neighbours: keep records with a nonempty name and at least one listed
  land neighbour. Retain border codes for later conversion to country names.
"""


import json
from pathlib import Path

# Locate the dataset relative to this Python file.
data_path = Path(__file__).parent / "data" / "countries.json"

try:
    with open(data_path, encoding="utf-8") as file:
        countries = json.load(file)

except FileNotFoundError:
    print("Cannot find data/countries.json. Check its name and location.")

except json.JSONDecodeError:
    print("The file is not valid JSON. Download countries.json again.")

  
else:
    quiz_countries = [] # Store capital-question records separately from the original data.

    for country in countries:
        name = country.get("name", {}).get("common", "").strip()
        capitals = country.get("capital", [])

        if name and len(capitals) == 1 and capitals[0].strip():  # Require one usable capital to avoid ambiguous questions.
            quiz_country = {
                "name": name,
                "capital": capitals[0]
            }

            quiz_countries.append(quiz_country)

    print("Records loaded:", len(countries))
    print("Countries with one usable capital:", len(quiz_countries))
    print()

    for country in quiz_countries[:5]:
        print(country["name"], "-", country["capital"])




    # Prepare currencies separately: a country may qualify for one topic only.
    currency_countries = []

    for country in countries:
        name = country.get("name", {}).get("common", "").strip()
        currencies = country.get("currencies", {})

        if name and len(currencies) == 1:  # Require exactly one currency to avoid multiple valid answers.
            for code, details in currencies.items():
                currency_name = details.get("name", "").strip()

                if code.strip() and currency_name:
                    currency_country = {
                        "name": name,
                        "currency_code": code.strip(),
                        "currency_name": currency_name
                    }

                    currency_countries.append(currency_country)

    print()
    print("Countries with one usable currency:", len(currency_countries))

    for country in currency_countries[:5]:
        print(
            country["name"],
            "-",
            country["currency_name"],
            "(" + country["currency_code"] + ")"
        )



       # Build a dictionary connecting country codes to readable names.
    country_names = {}

    for country in countries:
        code = country.get("cca3", "").strip()
        name = country.get("name", {}).get("common", "").strip()

        if code and name:
            country_names[code] = name

    # Prepare records with at least one listed land neighbour.
    neighboring_countries = []

    for country in countries:
        name = country.get("name", {}).get("common", "").strip()
        borders = country.get("borders", [])

        if name and len(borders) > 0:
            neighbor_names = []

            for border_code in borders:
                neighbor_names.append(country_names[border_code])

            neighboring_country = {
                "name": name,
                "borders": borders,
                "neighbor_names": neighbor_names
            }

            neighboring_countries.append(neighboring_country)

    print()
    print("Countries with listed land neighbours:", len(neighboring_countries))

    for country in neighboring_countries[:5]:
        print(country["name"], "-", ", ".join(country["neighbor_names"]))