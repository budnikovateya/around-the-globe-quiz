"""
Run a fifteen-question geography quiz with scoring and replay.

Display questions in a centered area and show compact final results.
Reuse the project's data preparation, quiz logic and analysis functions.
"""

from io import BytesIO

import streamlit as st
import matplotlib.pyplot as plt

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

from analysis import (
    summarize_by_topic,
    create_topic_chart,
    create_accuracy_chart,
    calculate_guessing_baseline
)


def format_answer_option(option):
    """
    Create a bold answer label.

    Parameters
    ----------
    option : str
        Original answer text.

    Returns
    -------
    str
        A Markdown label. The radio control retains the original value.
    """
    return "**" + option + "**"


st.set_page_config(
    page_title="Around the Globe Quiz",
    page_icon="🌍",
    layout="wide"
)


# Style the page and leave room below Streamlit's toolbar.
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 4rem;
        padding-bottom: 1rem;
    }

    h1 {
        font-size: 2rem !important;
    }

    h2 {
        font-size: 1.5rem !important;
    }

    h3 {
        font-size: 1.2rem !important;
    }

    .st-key-question_heading h3 {
        font-size: 32px !important;
        font-weight: 700 !important;
        line-height: 1.3;
    }

    .st-key-question_heading {
        margin-bottom: 24px;
    }

    [class*="st-key-answer_"] p {
        font-size: 22px !important;
        font-weight: 700;
        line-height: 1.25;
    }
        [data-testid="stExpander"] summary p {
        font-size: 24px !important;
        font-weight: 700 !important;
        line-height: 1.4;
    }</style>
    """,
    unsafe_allow_html=True
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


# Difficulty-selection screen.
if st.session_state.questions is None:
    with st.container(horizontal_alignment="center"):
        with st.container(width=1000):
            st.title("Around the Globe Quiz")

            st.write(
                "15 questions: 5 capitals, 5 flags and "
                "5 neighbouring-country questions."
            )

            difficulty = st.radio(
                "Choose your difficulty:",
                ["easy", "medium", "hard"],
                horizontal=True
            )

            st.write(
                "Points for each correct answer:",
                DIFFICULTY_POINTS[difficulty]
            )

            if st.button("Start quiz", type="primary"):
                try:
                    countries = load_countries(DATA_PATH)

                    capital_countries = prepare_capitals(countries)
                    flag_countries = prepare_flags(
                        countries,
                        FLAGS_FOLDER
                    )
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


# Question and results screens.
if st.session_state.questions is not None:
    questions = st.session_state.questions
    question_index = st.session_state.question_index

    if question_index < len(questions):
        question = questions[question_index]

        with st.container(horizontal_alignment="center"):
            with st.container(width=1000):
                st.caption(
                    "Question " + str(question_index + 1)
                    + " of " + str(len(questions))
                    + " | " + question["topic"]
                    + " | " + question["difficulty"]
                    + " | Points: " + str(question["points"])
                )

                with st.container(key="question_heading"):
                    st.subheader(question["question"])

                # Display a flag beside its answer options.
                if question["topic"] == "flags":
                    try:
                        with open(
                            question["flag_path"],
                            encoding="utf-8"
                        ) as file:
                            flag_svg = file.read()

                    except (OSError, UnicodeError) as error:
                        st.error(
                            "Cannot read the flag: " + str(error)
                        )
                        st.stop()

                    image_column, answer_column = st.columns([1, 2])

                    with image_column:
                        st.image(flag_svg, width=260)

                    with answer_column:
                        selected_answer = st.radio(
                            "Choose your answer:",
                            question["options"],
                            index=None,
                            key="answer_" + str(question_index),
                            format_func=format_answer_option,
                            width="stretch",
                            disabled=(
                                st.session_state.answer_result
                                is not None
                            )
                        )

                else:
                    selected_answer = st.radio(
                        "Choose your answer:",
                        question["options"],
                        index=None,
                        key="answer_" + str(question_index),
                        format_func=format_answer_option,
                        width="stretch",
                        disabled=(
                            st.session_state.answer_result is not None
                        )
                    )

                if st.session_state.answer_result is None:
                    if st.button("Submit answer", type="primary"):
                        if selected_answer is None:
                            st.warning("Please select an answer first.")

                        else:
                            result = check_answer(
                                question,
                                selected_answer
                            )

                            st.session_state.answer_result = result
                            st.session_state.results.append(result)
                            st.rerun()

                else:
                    result = st.session_state.answer_result

                    if result["is_correct"]:
                        st.success(
                            "Correct! Points earned: "
                            + str(result["points_earned"])
                        )
                    else:
                        st.error(
                            "Incorrect. Correct answer: "
                            + result["correct_answer"]
                            + ". Points earned: 0"
                        )

                    if st.button("Continue", type="primary"):
                        st.session_state.question_index += 1
                        st.session_state.answer_result = None
                        st.rerun()

    else:
        summary = summarize_results(st.session_state.results)

        # Display the heading and replay control.
        heading_column, replay_column = st.columns([4, 1])

        with heading_column:
            st.subheader("Your results")
            st.caption(
                "Quiz completed | Difficulty: "
                + questions[0]["difficulty"]
            )

        with replay_column:
            if st.button("Play again", type="primary"):
                for i in range(len(questions)):
                    answer_key = "answer_" + str(i)

                    if answer_key in st.session_state:
                        del st.session_state[answer_key]

                st.session_state.questions = None
                st.session_state.answer_result = None
                st.session_state.question_index = 0
                st.session_state.results = []
                st.rerun()

        # Display overall performance.
        correct_column, score_column, accuracy_column = st.columns(3)

        with correct_column:
            st.metric(
                label="Correct answers",
                value=(
                    str(summary["correct_answers"])
                    + " / "
                    + str(summary["answered_questions"])
                )
            )

        with score_column:
            st.metric(
                label="Weighted score",
                value=(
                    str(summary["score"])
                    + " / "
                    + str(summary["maximum_score"])
                )
            )

        with accuracy_column:
            st.metric(
                label="Accuracy",
                value=str(round(summary["accuracy"], 1)) + "%"
            )

        topic_summary = summarize_by_topic(
            st.session_state.results
        )

        # Export matching chart canvases at their original resolution.
        left_column, right_column = st.columns(2)

        with left_column:
            fig = create_topic_chart(topic_summary)

            chart_image = BytesIO()

            fig.savefig(
                chart_image,
                format="png",
                dpi="figure",
                bbox_inches=None
            )

            st.image(chart_image.getvalue(), width=440)
            plt.close(fig)

        with right_column:
            accuracy_fig = create_accuracy_chart(summary)

            accuracy_image = BytesIO()

            accuracy_fig.savefig(
                accuracy_image,
                format="png",
                dpi="figure",
                bbox_inches=None
            )

            st.image(accuracy_image.getvalue(), width=440)
            plt.close(accuracy_fig)

        # Numerical details can be expanded when needed.
        with st.expander("Comparison with random guessing"):
            baseline = calculate_guessing_baseline(questions)

            st.write(
                "Expected correct answers:",
                round(baseline["expected_correct"], 2),
                "out of",
                len(questions)
            )

            st.write(
                "Expected weighted score:",
                round(baseline["expected_score"], 2)
            )

            st.write(
                "Random-guessing score spread (standard deviation):",
                round(baseline["score_standard_deviation"], 2)
            )

            st.caption(
                "Assumes independent random choices among four "
                "options. These are averages over hypothetical games, "
                "not guaranteed results."
            )

        st.caption(
            "Five questions per topic: these results describe "
            "this game, not your overall geography knowledge."
        )