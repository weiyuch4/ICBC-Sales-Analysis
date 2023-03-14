import streamlit as st
import pandas as pd
import datetime
import SussexData


st.markdown("# Compare Sales :spiral_calendar_pad:")
st.markdown(
    """
    Compares sales data for any two specific dates and generates a detailed breakdown of transactions based on their 
    types
    ___
    """
)

x = SussexData.SussexData()

d = st.date_input(
    "Enter First Date",
    datetime.date.today())

d2 = st.date_input(
    "Enter Second Date",
    datetime.date.today())

all_tables = x.find_difference(d, d2)
sales_table = all_tables[0]
trans_table = all_tables[1]

df2 = pd.DataFrame(sales_table[0], index=sales_table[1])

st.dataframe(df2)

df3 = pd.DataFrame(trans_table[0], index=trans_table[1])

st.dataframe(df3)
