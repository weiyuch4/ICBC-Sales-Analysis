import streamlit as st
import pandas as pd
import SussexData

st.markdown("# Total Sales :moneybag:")
st.markdown(
    """
    Calculates the total sales figures up to the present day
    ___
    """
)

x = SussexData.SussexData()
current_premiums = x.find_current_premiums()

df = pd.DataFrame(current_premiums[0], index=current_premiums[1])

st.dataframe(df)
