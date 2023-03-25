import streamlit as st
import pandas as pd
import altair as alt
import SussexData

st.markdown("# Age Group Breakdown :busts_in_silhouette:")
st.markdown(
    """
    Classifies clients into different age groups, tallies the total number of clients in each group, 
    and produces a histogram
    ___
    """
)

data = SussexData.SussexData()
age_groups = data.get_age_groups_premium()
chart = pd.DataFrame(age_groups)

bar_chart = alt.Chart(chart).mark_bar().encode(
    x=alt.X("Age Group:O",
            sort=['Under 16', '16-24', '25-34', '35-44', '45-54', '55-64', '65 and over']),
    y="Number of Clients:Q",
    tooltip=['Age Group:O', 'Number of Clients:Q']
).interactive()

st.altair_chart(bar_chart, use_container_width=True)

show = st.checkbox('Show Data')

index = 0
while index < len(age_groups['Number of Clients']):
    age_groups['Number of Clients'][index] = "{:,}".format(age_groups['Number of Clients'][index])
    index += 1

table = pd.DataFrame(age_groups)

if show:
    st.dataframe(table)
