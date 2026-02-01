import streamlit as st

from app.page_leaderboard import render as render_leaderboard
from app.page_model_detail import render as render_model_detail
from app.page_requirement_detail import render as render_requirement_detail
from app.page_methodology import render as render_methodology
from app.page_validation import render as render_validation


def main() -> None:
    st.set_page_config(
        page_title="Model Card Transparency Tracker",
        page_icon=":mag:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    pages = {
        "Leaderboard": render_leaderboard,
        "Model Deep Dive": render_model_detail,
        "Requirement Deep Dive": render_requirement_detail,
        "Methodology & Validation": render_methodology,
        "Human Validation": render_validation,
    }

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Page", list(pages.keys()))

    pages[selection]()


if __name__ == "__main__":
    main()
