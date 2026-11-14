"""
Load World Countries data and prepare records for capital questions.

Exclude records with missing, blank or multiple capitals.
Currency and neighbouring-country preparation will be added later.
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
        name = country.get("name", {}).get("common", "")
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