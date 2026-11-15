
import random

from data_loader import DATA_PATH, load_countries, prepare_capitals


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


def main():
    """Preview one capital question per difficulty without repeated targets."""
    try:
        countries = load_countries(DATA_PATH)
        capital_countries = prepare_capitals(countries)

        used_codes = []

        for difficulty in DIFFICULTY_POINTS:
            question = generate_capital_question(
                capital_countries,
                difficulty,
                used_codes
            )

            used_codes.append(question["country_code"])

            print()
            print(
                "Difficulty:", question["difficulty"],
                "| Points:", question["points"]
            )
            print(question["question"])

            for i in range(len(question["options"])):
                print(i + 1, "-", question["options"][i])

            # This answer reveal is for development, not the player interface.
            print(
                "Correct answer (preview only):",
                question["correct_answer"]
            )

    except (OSError, ValueError) as error:
        print("Cannot generate capital questions:", error)


if __name__ == "__main__":
    main()