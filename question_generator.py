"""
Generate multiple-choice geography questions from prepared country data.

Topics
------
- Capitals: identify a country's capital.
- Flags: identify the country represented by a flag image.
- Neighbours: identify a country sharing a listed land border.

Each generator returns a dictionary containing the question text,
four distinct shuffled options, the correct answer, the target country
code, the topic, the difficulty and the available points.
Flag questions also include the path to the flag image.

Difficulty rules
----------------
Wrong answers are selected using geographic similarity to the target:
- Easy: countries from different regions.
- Medium: countries from the same region.
- Hard: countries from the same subregion.

These rules use geography; they do not measure visual flag similarity.
Correct answers are worth 1, 2 or 3 points respectively.

Validation
----------
Exclude repeated answer labels and previously used target codes supplied
by the caller. Neighbour questions exclude all listed neighbours from
the wrong-answer pool. Raise ValueError if the difficulty is invalid
or no eligible target has enough suitable wrong answers.

Running this file directly previews each topic at every difficulty.
Importing it makes the functions available without running the preview.
"""
import random

from data_loader import (
    DATA_PATH,
    FLAGS_FOLDER,
    load_countries,
    prepare_capitals,
    prepare_flags,
    prepare_neighbors
)

DIFFICULTY_POINTS = {
    "easy": 1,
    "medium": 2,
    "hard": 3
}


def get_wrong_capitals(target, capital_countries, difficulty):
    """
    Collect distinct wrong capital labels for a target and difficulty.

    Parameters
    ----------
    target : dict
        Prepared record for the country being asked about.
    capital_countries : list of dict
        Records returned by prepare_capitals.
    difficulty : str
        Validated level: easy, medium or hard.

    Returns
    -------
    list of str
        Wrong capital names matching the geographic rule.
        Labels are compared without distinguishing letter case.
    """
    wrong_answers = []

    # Mark the correct label as seen so it cannot become a wrong answer.
    seen_labels = [target["capital"].casefold()]

    for country in capital_countries:
        capital = country["capital"]
        label = capital.casefold()
        suitable = False

        if difficulty == "easy":
            suitable = bool(
                target["region"]
                and country["region"]
                and country["region"] != target["region"]
            )

        elif difficulty == "medium":
            suitable = bool(
                target["region"]
                and country["region"] == target["region"]
            )

        elif difficulty == "hard":
            suitable = bool(
                target["subregion"]
                and country["subregion"] == target["subregion"]
            )

        if suitable and label not in seen_labels:
            wrong_answers.append(capital)
            seen_labels.append(label)

    return wrong_answers


def generate_capital_question(
    capital_countries,
    difficulty,
    excluded_codes=None
):
    """
    Generate a capital question with four distinct shuffled options.

    Parameters
    ----------
    capital_countries : list of dict
        Records returned by prepare_capitals.
    difficulty : str
        Requested level: easy, medium or hard.
    excluded_codes : list of str, optional
        Country codes already used for capital questions in this quiz.

    Returns
    -------
    dict
        Topic, country code, difficulty, points, question text,
        options and correct answer.

    Raises
    ------
    ValueError
        If the difficulty is invalid or no unused country has enough
        distinct wrong answers at the requested difficulty.
    """
    if difficulty not in DIFFICULTY_POINTS:
        raise ValueError("Difficulty must be easy, medium or hard.")

    if excluded_codes is None:
        excluded_codes = []

    eligible = []

    for country in capital_countries:
        if country["country_code"] not in excluded_codes:
            wrong_answers = get_wrong_capitals(
                country,
                capital_countries,
                difficulty
            )

            if len(wrong_answers) >= 3:
                eligible.append({
                    "target": country,
                    "wrong_answers": wrong_answers
                })

    if not eligible:
        raise ValueError(
            "No unused country has three valid wrong capitals for "
            + difficulty + "."
        )

    selected = random.choice(eligible)
    target = selected["target"]

    options = random.sample(selected["wrong_answers"], 3)
    options.append(target["capital"])
    random.shuffle(options)

    return {
        "topic": "capitals",
        "country_code": target["country_code"],
        "difficulty": difficulty,
        "points": DIFFICULTY_POINTS[difficulty],
        "question": "What is the capital of " + target["name"] + "?",
        "options": options,
        "correct_answer": target["capital"]
    }

def get_wrong_flag_countries(target, flag_countries, difficulty):
    """
    Collect distinct wrong country names using geographic similarity.

    Parameters
    ----------
    target : dict
        Prepared record for the country whose flag will be displayed.
    flag_countries : list of dict
        Records returned by prepare_flags.
    difficulty : str
        Validated level: easy, medium or hard.

    Returns
    -------
    list of str
        Wrong country names matching the geographic rule.
        Names are compared without distinguishing letter case.
    """
    wrong_answers = []
    seen_labels = [target["name"].casefold()]

    for country in flag_countries:
        if country["country_code"] == target["country_code"]:
            continue

        name = country["name"]
        label = name.casefold()
        suitable = False

        if difficulty == "easy":
            suitable = bool(
                target["region"]
                and country["region"]
                and country["region"] != target["region"]
            )

        elif difficulty == "medium":
            suitable = bool(
                target["region"]
                and country["region"] == target["region"]
            )

        elif difficulty == "hard":
            suitable = bool(
                target["subregion"]
                and country["subregion"] == target["subregion"]
            )

        if suitable and label not in seen_labels:
            wrong_answers.append(name)
            seen_labels.append(label)

    return wrong_answers


def generate_flag_question(
    flag_countries,
    difficulty,
    excluded_codes=None
):
    """
    Generate a flag question with four distinct shuffled country names.

    Parameters
    ----------
    flag_countries : list of dict
        Records returned by prepare_flags.
    difficulty : str
        Requested level: easy, medium or hard.
    excluded_codes : list of str, optional
        Country codes that must not be selected as targets.

    Returns
    -------
    dict
        Topic, country code, difficulty, points, question text,
        flag image path, options and correct answer.

    Raises
    ------
    ValueError
        If the difficulty is invalid or no unused target has
        three distinct wrong answers at the requested difficulty.
    """
    if difficulty not in DIFFICULTY_POINTS:
        raise ValueError("Difficulty must be easy, medium or hard.")

    if excluded_codes is None:
        excluded_codes = []

    eligible = []

    for country in flag_countries:
        if country["country_code"] not in excluded_codes:
            wrong_answers = get_wrong_flag_countries(
                country,
                flag_countries,
                difficulty
            )

            if len(wrong_answers) >= 3:
                eligible.append({
                    "target": country,
                    "wrong_answers": wrong_answers
                })

    if not eligible:
        raise ValueError(
            "No unused country has three valid wrong flag answers for "
            + difficulty + "."
        )

    selected = random.choice(eligible)
    target = selected["target"]

    options = random.sample(selected["wrong_answers"], 3)
    options.append(target["name"])
    random.shuffle(options)

    return {
        "topic": "flags",
        "country_code": target["country_code"],
        "difficulty": difficulty,
        "points": DIFFICULTY_POINTS[difficulty],
        "question": "Which country does this flag belong to?",
        "flag_path": target["flag_path"],
        "options": options,
        "correct_answer": target["name"]
    }

def get_wrong_neighbors(target, neighbor_countries, difficulty):
    """
    Collect distinct country names that are not listed land neighbours.

    Parameters
    ----------
    target : dict
        Prepared record for the country being asked about.
    neighbor_countries : list of dict
        Records returned by prepare_neighbors.
    difficulty : str
        Validated level: easy, medium or hard.

    Returns
    -------
    list of str
        Wrong country names matching the geographic rule.
        The target and all its listed neighbours are excluded.
        Names are compared without distinguishing letter case.
    """
    wrong_answers = []
    seen_labels = [target["name"].casefold()]

    for name in target["neighbor_names"]:
        seen_labels.append(name.casefold())

    for country in neighbor_countries:
        code = country["country_code"]

        if code == target["country_code"] or code in target["borders"]:
            continue

        name = country["name"]
        label = name.casefold()
        suitable = False

        if difficulty == "easy":
            suitable = bool(
                target["region"]
                and country["region"]
                and country["region"] != target["region"]
            )

        elif difficulty == "medium":
            suitable = bool(
                target["region"]
                and country["region"] == target["region"]
            )

        elif difficulty == "hard":
            suitable = bool(
                target["subregion"]
                and country["subregion"] == target["subregion"]
            )

        if suitable and label not in seen_labels:
            wrong_answers.append(name)
            seen_labels.append(label)

    return wrong_answers

def generate_neighbor_question(
    neighbor_countries,
    difficulty,
    excluded_codes=None
):
    """
    Generate a land-neighbour question with four distinct shuffled options.

    Parameters
    ----------
    neighbor_countries : list of dict
        Records returned by prepare_neighbors.
    difficulty : str
        Requested level: easy, medium or hard.
    excluded_codes : list of str, optional
        Country codes that must not be selected as targets.

    Returns
    -------
    dict
        Question details with exactly one listed land neighbour
        among the four options.

    Raises
    ------
    ValueError
        If the difficulty is invalid or no unused target has
        enough suitable answers.
    """
    if difficulty not in DIFFICULTY_POINTS:
        raise ValueError("Difficulty must be easy, medium or hard.")

    if excluded_codes is None:
        excluded_codes = []

    eligible = []

    for country in neighbor_countries:
        if (
            country["country_code"] not in excluded_codes
            and country["neighbor_names"]
        ):
            wrong_answers = get_wrong_neighbors(
                country,
                neighbor_countries,
                difficulty
            )

            if len(wrong_answers) >= 3:
                eligible.append({
                    "target": country,
                    "wrong_answers": wrong_answers
                })

    if not eligible:
        raise ValueError(
            "No unused country has a usable neighbour and three "
            "valid wrong answers for " + difficulty + "."
        )

    selected = random.choice(eligible)
    target = selected["target"]

    correct_answer = random.choice(target["neighbor_names"])

    options = random.sample(selected["wrong_answers"], 3)
    options.append(correct_answer)
    random.shuffle(options)

    return {
        "topic": "neighbors",
        "country_code": target["country_code"],
        "difficulty": difficulty,
        "points": DIFFICULTY_POINTS[difficulty],
        "question": (
            "Which country shares a land border with "
            + target["name"] + "?"
        ),
        "options": options,
        "correct_answer": correct_answer
    }

def main():
    """Preview each topic at every difficulty."""
    try:
        countries = load_countries(DATA_PATH)

        capital_countries = prepare_capitals(countries)
        flag_countries = prepare_flags(countries, FLAGS_FOLDER)
        neighbor_countries = prepare_neighbors(countries)

    except (OSError, ValueError) as error:
        print("Cannot prepare the preview:", error)
        return

    topics = ["capitals", "flags", "neighbors"]

    for topic in topics:
        print()
        print("TOPIC:", topic)

        used_codes = []

        for difficulty in DIFFICULTY_POINTS:
            try:
                if topic == "capitals":
                    question = generate_capital_question(
                        capital_countries,
                        difficulty,
                        used_codes
                    )

                elif topic == "flags":
                    question = generate_flag_question(
                        flag_countries,
                        difficulty,
                        used_codes
                    )

                else:
                    question = generate_neighbor_question(
                        neighbor_countries,
                        difficulty,
                        used_codes
                    )

            except ValueError as error:
                print("Cannot generate", topic, difficulty, "question:", error)
                continue

            used_codes.append(question["country_code"])

            print()
            print(
                "Difficulty:", question["difficulty"],
                "| Points:", question["points"]
            )
            print(question["question"])

            if topic == "flags":
                print("Flag file (preview only):", question["flag_path"])

            for i in range(len(question["options"])):
                print(i + 1, "-", question["options"][i])

            print(
                "Correct answer (preview only):",
                question["correct_answer"]
            )

if __name__ == "__main__":
    main()