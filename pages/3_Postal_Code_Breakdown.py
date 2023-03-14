import streamlit as st
import pandas as pd
import altair as alt
import SussexData

st.markdown("# Postal Code Breakdown :round_pushpin:")
st.markdown(
    """
    Finds the ten postal codes with the largest clientele
    ___
    """
)

x = SussexData.SussexData()
top_postal_codes = x.get_postal_code_breakdown()

df = pd.DataFrame(top_postal_codes)

bar_chart = alt.Chart(df).mark_bar().encode(
    x="Postal Code:O",
    y="Number of Clients:Q",
    tooltip=['Postal Code:O', 'Number of Clients:Q']
).interactive()

st.altair_chart(bar_chart, use_container_width=True)

show = st.checkbox('Show Data')

if show:
    st.dataframe(df)
