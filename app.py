"""
Run a fifteen-question geography quiz with scoring and replay.

Reuse the project's data preparation, question generation and scoring.
Store questions, progress and submitted answers in session state.
"""

import streamlit as st

from data_loader import (
    DATA_PATH,
    FLAGS_FOLDER,
    load_countries,
    prepare_capitals,
    prepare_flags,
    prepare_neighbors
)

from question_generator import DIFFICULTY_POINTS

from quiz_logic import (
    generate_quiz,
    check_answer,
    summarize_results
)


# Initialize session state.
if "questions" not in st.session_state:
    st.session_state.questions = None

if "answer_result" not in st.session_state:
    st.session_state.answer_result = None

if "question_index" not in st.session_state:
    st.session_state.question_index = 0

if "results" not in st.session_state:
    st.session_state.results = []


# Display the page title and description.
st.title("Around the Globe Quiz")

st.write(
    "15 questions: 5 capitals, 5 flags and "
    "5 neighbouring-country questions."
)


# Display setup controls.
if st.session_state.questions is None:
    difficulty = st.radio(
        "Choose your difficulty:",
        ["easy", "medium", "hard"],
        horizontal=True
    )

    st.write(
        "Points for each correct answer:",
        DIFFICULTY_POINTS[difficulty]
    )

    if st.button("Start quiz"):
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
            st.error("Cannot start the quiz: " + str(error))

        else:
            st.session_state.questions = questions
            st.session_state.answer_result = None
            st.session_state.question_index = 0
            st.session_state.results = []
            st.rerun()


# Display the current question or the final results.
if st.session_state.questions is not None:
    questions = st.session_state.questions
    question_index = st.session_state.question_index

    if question_index < len(questions):
        question = questions[question_index]

        st.subheader(
            "Question " + str(question_index + 1)
            + " of " + str(len(questions))
        )

        st.write("Topic:", question["topic"])
        st.write("Difficulty:", question["difficulty"])
        st.write("Points available:", question["points"])
        st.write(question["question"])

        if question["topic"] == "flags":
            try:
                with open(
                    question["flag_path"],
                    encoding="utf-8"
                ) as file:
                    flag_svg = file.read()

            except (OSError, UnicodeError) as error:
                st.error("Cannot read the flag: " + str(error))
                st.stop()

            else:
                st.image(flag_svg, width=300)

        selected_answer = st.radio(
            "Choose your answer:",
            question["options"],
            index=None,
            key="answer_" + str(question_index),
            disabled=st.session_state.answer_result is not None
        )

        if st.session_state.answer_result is None:
            if st.button("Submit answer"):
                if selected_answer is None:
                    st.warning("Please select an answer first.")

                else:
                    result = check_answer(question, selected_answer)

                    st.session_state.answer_result = result
                    st.session_state.results.append(result)

                    st.rerun()

        if st.session_state.answer_result is not None:
            result = st.session_state.answer_result

            if result["is_correct"]:
                st.success("Correct!")
            else:
                st.error(
                    "Incorrect. The correct answer is: "
                    + result["correct_answer"]
                )

            st.write("Points earned:", result["points_earned"])

            if st.button("Continue"):
                st.session_state.question_index += 1
                st.session_state.answer_result = None
                st.rerun()

    else:
        summary = summarize_results(st.session_state.results)

        st.success("You have completed the quiz!")
        st.subheader("Your results")

        st.write("Difficulty:", questions[0]["difficulty"])

        st.write(
            "Correct answers:",
            summary["correct_answers"],
            "out of",
            summary["answered_questions"]
        )

        st.write(
            "Score:",
            summary["score"],
            "out of",
            summary["maximum_score"]
        )

        st.write(
            "Accuracy:",
            round(summary["accuracy"], 1),
            "%"
        )

        if st.button("Play again"):
            # Remove any saved selections from the previous game.
            for i in range(len(questions)):
                answer_key = "answer_" + str(i)

                if answer_key in st.session_state:
                    del st.session_state[answer_key]

            # Reset the game.
            st.session_state.questions = None
            st.session_state.answer_result = None
            st.session_state.question_index = 0
            st.session_state.results = []

            st.rerun()