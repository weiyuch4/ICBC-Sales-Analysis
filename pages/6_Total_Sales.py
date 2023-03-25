from datetime import datetime
from datetime import date
import streamlit as st
import pandas as pd
import SussexData

st.markdown("# Total Sales :moneybag:")
st.markdown(
    """
    Computes the total sales figures up to the present date and the total sales data from the same date in the prior 
    year for the designated year
    ___
    """
)

data = SussexData.SussexData()

today = date.today()

first_day_of_month = datetime(today.year, today.month, 1)
this_month_sales = data.get_total_premiums(first_day_of_month, today)

first_day_of_year = datetime(today.year, 1, 1)
this_year_sales = data.get_total_premiums(first_day_of_year, today)

this_month_sales[0]['Total Sales'].append(this_year_sales[0]['Total Sales'][0])
this_month_sales[1].append(this_year_sales[1][0])

sales_table = pd.DataFrame(this_month_sales[0], index=this_month_sales[1])

st.dataframe(sales_table)

given_year = st.number_input('Enter year', min_value=2000, value=date.today().year-1)

given_year_today = datetime(given_year, today.month, today.day)

given_first_day_of_month = datetime(given_year, given_year_today.month, 1)
given_month_sales = data.get_total_premiums(given_first_day_of_month, given_year_today)

given_first_day_of_year = datetime(given_year, 1, 1)
given_year_sales = data.get_total_premiums(given_first_day_of_year, given_year_today)

given_month_sales[0]['Total Sales'].append(given_year_sales[0]['Total Sales'][0])
given_month_sales[1].append(given_year_sales[1][0])

given_year_sales_table = pd.DataFrame(given_month_sales[0], index=given_month_sales[1])

st.dataframe(given_year_sales_table)
