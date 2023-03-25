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

data = SussexData.SussexData()
postal_codes = data.get_postal_code_breakdown()
chart = pd.DataFrame(postal_codes)

bar_chart = alt.Chart(chart).mark_bar().encode(
    x="Postal Code:O",
    y="Number of Clients:Q",
    tooltip=['Postal Code:O', 'Number of Clients:Q']
).interactive()

st.altair_chart(bar_chart, use_container_width=True)

show = st.checkbox('Show Data')

index = 0
while index < len(postal_codes['Number of Clients']):
    postal_codes['Number of Clients'][index] = "{:,}".format(postal_codes['Number of Clients'][index])
    index += 1

table = pd.DataFrame(postal_codes)

if show:
    st.dataframe(table)
