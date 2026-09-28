import os
import random

import streamlit as st

from core.logic import (
    calculate_letter_distribution,
    calculate_statistics,
    clean_data,
    filter_by_english_letter,
    load_data,
    search_dictionary,
)


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Noongar Language Explorer",
    page_icon="📖",
    layout="wide",
)


# =========================================================
# LOAD DATASET
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "noongar_dictionary_english_noongar_corrected.csv",
)

try:
    data = load_data(FILE_PATH)
    data = clean_data(data)
except (FileNotFoundError, TypeError, ValueError) as error:
    st.error(f"Unable to load the dictionary: {error}")
    st.stop()


# =========================================================
# NAVIGATION
# =========================================================
st.sidebar.title("Navigation")
screen = st.sidebar.radio(
    "Select a screen:",
    [
        "1. Explorer",
        "2. Analysis & Visualisation",
        "3. Interactive Practice",
    ],
)


# =========================================================
# SCREEN 1 - EXPLORER
# =========================================================
if screen == "1. Explorer":
    st.title("Noongar Language Explorer")
    st.write(
        "Search and explore entries from the supplied "
        "English-Noongar dictionary dataset."
    )

    st.subheader("Search Dictionary")
    search_query = st.text_input(
        "Search for an English or Noongar term:",
        placeholder="Enter a search term...",
    )

    st.subheader("Filter by English Starting Letter")
    letter_options = ["All"] + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    selected_letter = st.selectbox(
        "Choose a starting letter:",
        letter_options,
    )

    results = data.copy()

    if search_query.strip():
        results = search_dictionary(results, search_query)

    if selected_letter != "All":
        results = filter_by_english_letter(results, selected_letter)

    st.subheader("Dictionary Results")
    if results.empty:
        st.info("No matching dictionary entries were found.")
    else:
        st.write(f"Entries found: {len(results)}")
        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# SCREEN 2 - ANALYSIS AND VISUALISATION
# =========================================================
elif screen == "2. Analysis & Visualisation":
    st.title("Dictionary Analysis & Visualisation")
    st.write(
        "Explore statistics and visualisations calculated "
        "from the supplied dictionary dataset."
    )

    stats = calculate_statistics(data)

    st.subheader("Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", stats["total_records"])
    with col2:
        st.metric("Unique English Terms", stats["unique_english_terms"])
    with col3:
        st.metric("Unique Noongar Entries", stats["unique_noongar_entries"])
    with col4:
        st.metric("Duplicate English Records", stats["duplicate_english_terms"])

    st.subheader("Starting Letter Distribution")
    distribution = calculate_letter_distribution(data)

    if distribution.empty:
        st.info("No letter distribution is available for the current dataset.")
    else:
        st.bar_chart(distribution, x="Letter", y="Count")

        with st.expander("View Distribution Data"):
            st.dataframe(
                distribution,
                use_container_width=True,
                hide_index=True,
            )


# =========================================================
# SCREEN 3 - INTERACTIVE PRACTICE
# =========================================================

elif screen == "3. Interactive Practice":

    st.title("Interactive Practice")

    st.write(
        "Test your knowledge using entries taken directly "
        "from the supplied dictionary dataset."
    )

    # At least four records are needed:
    # one correct answer and three incorrect answers.
    if len(data) < 4:

        st.warning(
            "At least four dictionary entries are required "
            "for the practice activity."
        )

    else:

        # -------------------------
        # Set up session state
        # -------------------------

        if "score" not in st.session_state:
            st.session_state.score = 0

        if "questions_answered" not in st.session_state:
            st.session_state.questions_answered = 0

        if "question_index" not in st.session_state:
            st.session_state.question_index = None

        if "answer_options" not in st.session_state:
            st.session_state.answer_options = []

        if "answered" not in st.session_state:
            st.session_state.answered = False

        if "last_answer_correct" not in st.session_state:
            st.session_state.last_answer_correct = None

        # -------------------------
        # Generate new question
        # -------------------------

        if st.session_state.question_index is None:

            # Select one random row from the dataset.
            question_row = data.sample(n=1)

            question_index = question_row.index[0]

            correct_answer = data.loc[
                question_index,
                "Noongar",
            ]

            # Remove the correct row before choosing
            # incorrect answer options.
            other_rows = data.drop(index=question_index)

            incorrect_answers = (
                other_rows["Noongar"]
                .dropna()
                .drop_duplicates()
            )

            # Make sure the correct answer cannot also
            # appear as an incorrect option.
            incorrect_answers = incorrect_answers[
                incorrect_answers != correct_answer
            ]

            if len(incorrect_answers) >= 3:

                # Randomly choose three incorrect answers.
                incorrect_answers = incorrect_answers.sample(
                    n=3
                ).tolist()

                # Put the three incorrect answers and
                # correct answer into one list.
                answer_options = (
                    incorrect_answers + [correct_answer]
                )

                # Randomise their order.
                random.shuffle(answer_options)

                # Save the question and options.
                st.session_state.question_index = question_index

                st.session_state.answer_options = answer_options

            else:

                st.warning(
                    "There are not enough unique dictionary "
                    "entries to create a practice question."
                )

        # -------------------------
        # Display score
        # -------------------------

        score_column, question_column = st.columns(2)

        with score_column:
            st.metric(
                "Score",
                st.session_state.score,
            )

        with question_column:
            st.metric(
                "Questions Answered",
                st.session_state.questions_answered,
            )

        # -------------------------
        # Display question
        # -------------------------

        if st.session_state.question_index is not None:

            question_index = st.session_state.question_index

            english_term = data.loc[
                question_index,
                "English",
            ]

            correct_answer = data.loc[
                question_index,
                "Noongar",
            ]

            st.subheader("Question")

            st.write(
                f"Which recorded Noongar entry matches "
                f"the English entry **{english_term}**?"
            )

            selected_answer = st.radio(
                "Choose an answer:",
                st.session_state.answer_options,
                index=None,
                disabled=st.session_state.answered,
            )

            # -------------------------
            # Check answer
            # -------------------------

            if st.button(
                "Check Answer",
                disabled=st.session_state.answered,
            ):

                if selected_answer is None:

                    st.warning(
                        "Please select an answer first."
                    )

                else:

                    st.session_state.questions_answered += 1
                    st.session_state.answered = True

                    if selected_answer == correct_answer:

                        st.session_state.score += 1
                        st.session_state.last_answer_correct = True

                    else:

                        st.session_state.last_answer_correct = False

                    st.rerun()

            # -------------------------
            # Display feedback
            # -------------------------

            if st.session_state.answered:

                if st.session_state.last_answer_correct:

                    st.success("Correct!")

                else:

                    st.error("Incorrect.")

                st.info(
                    f"Recorded answer: {correct_answer}"
                )

                # -------------------------
                # Next question
                # -------------------------

                if st.button("Next Question"):

                    st.session_state.question_index = None
                    st.session_state.answer_options = []
                    st.session_state.answered = False
                    st.session_state.last_answer_correct = None

                    st.rerun()

        # -------------------------
        # Reset practice
        # -------------------------

        st.divider()

        if st.button("Reset Practice"):

            st.session_state.score = 0
            st.session_state.questions_answered = 0
            st.session_state.question_index = None
            st.session_state.answer_options = []
            st.session_state.answered = False
            st.session_state.last_answer_correct = None

            st.rerun()
