import streamlit as st


def perform_analysis(df):
    if df is None:
        st.warning("No data to analyze")
        return
    st.header("Dataset Summary")
    st.write(df.describe(include='all'))
