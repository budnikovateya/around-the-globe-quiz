"""
Assemble a fifteen-question geography quiz from the question generators.

Each quiz contains five capital questions, five flag questions and
five land-neighbour questions, presented in shuffled topic order.
All questions use the requested difficulty.
"""

import random

from question_generator import (
    DIFFICULTY_POINTS,
    generate_capital_question,
    generate_flag_question,
    generate_neighbor_question
)


QUESTIONS_PER_TOPIC = 5


def generate_quiz(
    capital_countries,
    flag_countries,
    neighbor_countries,
    difficulty
):
    """
    Build fifteen questions across three topics at one difficulty.

    Parameters
    ----------
    capital_countries : list of dict
        Records returned by prepare_capitals.
    flag_countries : list of dict
        Records returned by prepare_flags.
    neighbor_countries : list of dict
        Records returned by prepare_neighbors.
    difficulty : str
        Requested level: easy, medium or hard.

    Returns
    -------
    list of dict
        Fifteen question dictionaries in shuffled topic order,
        with five questions per topic.
        Target countries do not repeat within the same topic.

    Raises
    ------
    ValueError
        If the difficulty is invalid or a generator cannot supply
        a question with the required options and exclusions.
    """
    if difficulty not in DIFFICULTY_POINTS:
        raise ValueError("Difficulty must be easy, medium or hard.")

    topics = ["capitals", "flags", "neighbors"]

    question_topics = topics * QUESTIONS_PER_TOPIC
    random.shuffle(question_topics)

    questions = []

    used_codes = {
        "capitals": [],
        "flags": [],
        "neighbors": []
    }

    for topic in question_topics:
        if topic == "capitals":
            question = generate_capital_question(
                capital_countries,
                difficulty,
                used_codes[topic]
            )

        elif topic == "flags":
            question = generate_flag_question(
                flag_countries,
                difficulty,
                used_codes[topic]
            )

        else:
            question = generate_neighbor_question(
                neighbor_countries,
                difficulty,
                used_codes[topic]
            )

        questions.append(question)
        used_codes[topic].append(question["country_code"])

    return questions