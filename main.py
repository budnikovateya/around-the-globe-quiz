import json
from pathlib import Path

data_path = Path(__file__).parent / "data" / "countries.json"

try:
    with open(data_path, encoding="utf-8") as file:
        countries = json.load(file)

except FileNotFoundError:
    print("File not found. Put countries.json inside the data folder.")

except json.JSONDecodeError:
    print("The file is not valid JSON. Download countries.json again.")

else:
    print("Number of records loaded:", len(countries))

    for country in countries[:5]:
        print(country["name"]["common"])
        print("Capitals:", country.get("capital", []))
        print("Currencies:", country.get("currencies", {}))
        print()