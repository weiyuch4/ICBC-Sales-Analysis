import streamlit as st
import pandas as pd
from datetime import date
import SussexData


st.markdown("# Compare Sales :spiral_calendar_pad:")
st.markdown(
    """
    Compares sales data for any two specific dates and generates a detailed breakdown of transactions based on their 
    types
    ___
    """
)

data = SussexData.SussexData()

d = st.date_input("Enter First Date", date.today())
d2 = st.date_input("Enter Second Date", date.today())

all_tables = data.find_difference(d, d2)
sales_table = all_tables[0]
types_table = all_tables[1]

sales_df = pd.DataFrame(sales_table[0], index=sales_table[1])
st.dataframe(sales_df)

types_df = pd.DataFrame(types_table[0], index=types_table[1])
st.dataframe(types_df)
