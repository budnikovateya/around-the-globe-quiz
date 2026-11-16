"""
Summarize quiz results, create charts and calculate a guessing baseline.

Use pandas for topic summaries, Matplotlib for visualization
and NumPy for numerical calculations.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def summarize_by_topic(results):
    """
    Calculate performance statistics for each topic.

    Parameters
    ----------
    results : list of dict
        Answer records returned by check_answer.

    Returns
    -------
    pandas.DataFrame
        One row per answered topic with question count, correct answers,
        percentage accuracy, earned points and available points.
        Empty input produces an empty table with the same columns.
    """
    columns = [
        "topic",
        "answered",
        "correct",
        "accuracy",
        "score",
        "maximum_score"
    ]

    if not results:
        return pd.DataFrame(columns=columns)

    results_df = pd.DataFrame(results)

    topic_summary = (
        results_df.groupby("topic")
        .agg(
            answered=("is_correct", "size"),
            correct=("is_correct", "sum"),
            accuracy=("is_correct", "mean"),
            score=("points_earned", "sum"),
            maximum_score=("points_available", "sum")
        )
        .reset_index()
    )

    topic_summary["accuracy"] = (
        topic_summary["accuracy"] * 100
    ).round(1)

    return topic_summary


def create_topic_chart(topic_summary):
    """
    Create a vertical bar chart of accuracy by topic.

    Parameters
    ----------
    topic_summary : pandas.DataFrame
        A nonempty table returned by summarize_by_topic.

    Returns
    -------
    matplotlib.figure.Figure
        A figure measuring 900 by 525 pixels at its original resolution.

    Raises
    ------
    ValueError
        If the summary table is empty.
    """
    if topic_summary.empty:
        raise ValueError("No topic results are available to plot.")

    fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)

    ax.bar(
        topic_summary["topic"],
        topic_summary["accuracy"],
        color="#B9A3D9"
    )

    ax.set_xlabel("Topic")
    ax.set_ylabel("Correct answers (%)")
    ax.set_title("Your accuracy by topic")
    ax.set_ylim(0, 100)

    fig.subplots_adjust(
        left=0.14,
        right=0.97,
        bottom=0.20,
        top=0.86
    )

    return fig


def create_accuracy_chart(summary):
    """
    Create a pie chart of correct and incorrect answers.

    Parameters
    ----------
    summary : dict
        Overall totals returned by summarize_results.

    Returns
    -------
    matplotlib.figure.Figure
        A figure measuring 900 by 525 pixels at its original resolution.

    Raises
    ------
    ValueError
        If there are no answered questions.
    """
    answered = summary["answered_questions"]

    if answered == 0:
        raise ValueError("No answered questions are available to plot.")

    correct = summary["correct_answers"]
    incorrect = answered - correct

    fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)

    ax.pie(
        [correct, incorrect],
        labels=["Correct", "Incorrect"],
        colors=["#B9A3D9", "#F4E5A1"],
        autopct="%1.1f%%",
        startangle=90
    )

    ax.set_title("Overall answer accuracy")
    ax.set_aspect("equal")

    fig.subplots_adjust(
        left=0.12,
        right=0.88,
        bottom=0.08,
        top=0.86
    )

    return fig


def calculate_guessing_baseline(questions):
    """
    Calculate expected performance under independent random guessing.

    Parameters
    ----------
    questions : list of dict
        Generated questions, each with four options, exactly one
        correct answer and a positive point value.

    Returns
    -------
    dict
        Expected correct-answer count, expected weighted score
        and standard deviation of the weighted score.

    Raises
    ------
    ValueError
        If the question list is empty.
    """
    if not questions:
        raise ValueError("Questions are needed to calculate a baseline.")

    point_values = []

    for question in questions:
        point_values.append(question["points"])

    points = np.array(point_values, dtype=float)

    probability = 0.25

    expected_correct = len(questions) * probability
    expected_score = probability * points.sum()

    score_variance = (
        probability * (1 - probability) * (points ** 2).sum()
    )

    score_standard_deviation = np.sqrt(score_variance)

    return {
        "expected_correct": float(expected_correct),
        "expected_score": float(expected_score),
        "score_standard_deviation": float(score_standard_deviation)
    }