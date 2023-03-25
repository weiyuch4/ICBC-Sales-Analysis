import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
import SussexData

st.markdown("# Transaction Time Breakdown :clock1:")
st.markdown(
    """
    Categorizes transactions based on the time of day and day of the week they occur, enabling the recognition of 
    patterns and generating a histogram for improved visualization.
    ___
    """
)

data = SussexData.SussexData()

year = st.number_input('Enter year', min_value=2000, value=date.today().year)
month = st.number_input('Enter month', min_value=1, max_value=12, value=date.today().month)

monthly_breakdown = data.get_transaction_time(month, year)
chart = pd.DataFrame(monthly_breakdown)

bar_chart = alt.Chart(chart).mark_bar().encode(
    x=alt.X("Day:O",
            sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
    y="Transactions:Q",
    color=alt.Color("Transaction Time:N", sort=[]),
    tooltip=['Transaction Time:N', 'Transactions:Q']
).interactive()

st.altair_chart(bar_chart, use_container_width=True)

show = st.checkbox('Show Data')

index = 0
while index < len(monthly_breakdown['Transactions']):
    monthly_breakdown['Transactions'][index] = "{:,}".format(monthly_breakdown['Transactions'][index])
    index += 1

table = pd.DataFrame(monthly_breakdown)

if show:
    st.dataframe(table)
