import streamlit as st


def display_data(df):
    """Display a pandas DataFrame in Streamlit.
    """
    if df is None:
        st.error("No data to display")
        return
    st.dataframe(df.head(50))
