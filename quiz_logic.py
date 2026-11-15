"""
Assemble a fifteen-question geography quiz and calculate scores.

Each quiz contains five capital questions, five flag questions and
five land-neighbour questions, presented in shuffled topic order.
All questions use the requested difficulty.

Running this file directly checks quiz assembly and demonstrates
scoring with sample answers.
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


def check_answer(question, selected_answer):
    """
    Check a selected option and return an answer record.

    Parameters
    ----------
    question : dict
        A question returned by a question generator.
    selected_answer : str
        The option selected by the player.

    Returns
    -------
    dict
        Question details, correctness, and earned and available points.

    Raises
    ------
    ValueError
        If the selected answer is not an available option.
    """
    if selected_answer not in question["options"]:
        raise ValueError("Choose one of the available answer options.")

    is_correct = selected_answer == question["correct_answer"]
    points_earned = 0

    if is_correct:
        points_earned = question["points"]

    return {
        "topic": question["topic"],
        "country_code": question["country_code"],
        "difficulty": question["difficulty"],
        "question": question["question"],
        "selected_answer": selected_answer,
        "correct_answer": question["correct_answer"],
        "is_correct": is_correct,
        "points_available": question["points"],
        "points_earned": points_earned
    }


def summarize_results(results):
    """
    Calculate totals for the supplied answer records.

    Parameters
    ----------
    results : list of dict
        Records returned by check_answer, one per answered question.

    Returns
    -------
    dict
        Number answered, number correct, earned and available points,
        and percentage accuracy. An empty list produces zero values.
        Available points cover the recorded answers only.
    """
    correct_answers = 0
    score = 0
    maximum_score = 0

    for result in results:
        if result["is_correct"]:
            correct_answers += 1

        score += result["points_earned"]
        maximum_score += result["points_available"]

    answered_questions = len(results)
    accuracy = 0.0

    if answered_questions > 0:
        accuracy = correct_answers / answered_questions * 100

    return {
        "answered_questions": answered_questions,
        "correct_answers": correct_answers,
        "score": score,
        "maximum_score": maximum_score,
        "accuracy": accuracy
    }


def main():
    """Preview fifteen questions and demonstrate scoring with sample answers."""
    difficulty = input("Choose easy, medium or hard: ").strip().lower()

    while difficulty not in DIFFICULTY_POINTS:
        print("Please enter easy, medium or hard.")
        difficulty = input("Your choice: ").strip().lower()

    try:
        countries = load_countries(DATA_PATH)

        capital_countries = prepare_capitals(countries)
        flag_countries = prepare_flags(countries, FLAGS_FOLDER)
        neighbor_countries = prepare_neighbors(countries)

        questions = generate_quiz(
            capital_countries,
            flag_countries,
            neighbor_countries,
            difficulty
        )

    except (OSError, ValueError) as error:
        print("Cannot create the quiz:", error)
        return

    topic_counts = {
        "capitals": 0,
        "flags": 0,
        "neighbors": 0
    }

    for question in questions:
        topic_counts[question["topic"]] += 1

    print()
    print("Questions generated:", len(questions))
    print("Selected difficulty:", difficulty)

    for topic in topic_counts:
        print(topic, ":", topic_counts[topic])

    for i in range(len(questions)):
        question = questions[i]

        print()
        print(
            "Question", i + 1,
            "| Topic:", question["topic"],
            "| Difficulty:", question["difficulty"]
        )
        print(question["question"])

        if question["topic"] == "flags":
            print("Flag file:", question["flag_path"])

        for j in range(len(question["options"])):
            print(j + 1, "-", question["options"][j])

        print(
            "Correct answer (preview only):",
            question["correct_answer"]
        )

    # Demonstration only: these are not answers submitted by a player.
    first_question = questions[0]

    correct_result = check_answer(
        first_question,
        first_question["correct_answer"]
    )

    second_question = questions[1]

    for option in second_question["options"]:
        if option != second_question["correct_answer"]:
            wrong_result = check_answer(second_question, option)
            break

    summary = summarize_results([correct_result, wrong_result])

    print()
    print("Scoring demonstration: one correct and one incorrect sample answer")
    print(
        "Correct answers:", summary["correct_answers"],
        "out of", summary["answered_questions"]
    )
    print(
        "Score:", summary["score"],
        "out of", summary["maximum_score"]
    )
    print("Accuracy:", summary["accuracy"], "%")
    
if __name__ == "__main__":
    main()