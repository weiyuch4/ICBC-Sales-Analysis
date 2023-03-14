import streamlit as st
import pandas as pd
import altair as alt
import datetime
import SussexData

st.markdown("# Monthly Breakdown :bar_chart:")
st.markdown(
    """
    Categorizes business transactions, calculates total amounts collected for each category per month, and 
    generates a histogram
    ___
    """
)

x = SussexData.SussexData()

number = st.number_input('Enter year', min_value=2000, value=datetime.date.today().year)

monthly_breakdown = x.get_yearly_sales(number)

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

if show:
    st.dataframe(chart)
