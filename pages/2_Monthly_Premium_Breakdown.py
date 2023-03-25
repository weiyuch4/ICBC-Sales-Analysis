import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
import SussexData

st.markdown("# Monthly Breakdown :bar_chart:")
st.markdown(
    """
    Categorizes business transactions, calculates total amounts collected for each category per month, and 
    generates a histogram
    ___
    """
)

data = SussexData.SussexData()

year = st.number_input('Enter year', min_value=2000, value=date.today().year)

monthly_breakdown = data.get_yearly_sales(year)
chart = pd.DataFrame(monthly_breakdown)

bar_chart = alt.Chart(chart).mark_bar().encode(
    x=alt.X("Month:O",
            sort=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                  'September', 'October', 'November', 'December']),
    y="Premiums:Q",
    color="Transaction Type:N",
    tooltip=['Transaction Type:N', 'Premiums:Q']
).interactive()

st.altair_chart(bar_chart, use_container_width=True)

show = st.checkbox('Show Data')

index = 0
while index < len(monthly_breakdown['Premiums']):
    monthly_breakdown['Premiums'][index] = "{:,}".format(monthly_breakdown['Premiums'][index])
    index += 1

table = pd.DataFrame(monthly_breakdown)

if show:
    st.dataframe(table)
