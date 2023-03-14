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

x = SussexData.SussexData()
age_groups = x.get_age_groups_premium()

df = pd.DataFrame(age_groups)

bar_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("Age Group:O",
            sort=['Under 16', '16-24', '25-34', '35-44', '45-54', '55-64', '65 and over']),
    y="Number of Clients:Q",
    tooltip=['Age Group:O', 'Number of Clients:Q']
).interactive()

st.altair_chart(bar_chart, use_container_width=True)

show = st.checkbox('Show Data')

if show:
    st.dataframe(df)
