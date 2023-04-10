import calendar
from datetime import datetime

import streamlit as st
import pandas as pd

import components.st_utils as st_utils
import nai_utils as nut
from dfm import DataFrameManager

st_utils.style_page()


# Import the company data
if "dfm" not in st.session_state:
    connection = nut.get_db_engine().connect()
    dfm = DataFrameManager(connection)
    connection.close()
    st.session_state.dfm = dfm
else:
    dfm = st.session_state.dfm


# Sidebar
st.sidebar.image("assets/blacklogo.png")


if True:  # st_utils.check_password():
    # Top Message
    st.title("Company Metrics")
    st.write(":red[This area is under-going heavy construction]:, so please excuse the mess.")


    # Interactive Search
    st.sidebar.markdown(
        ":red[Disclaimer]: The companies, clients, contacts, and histories you are about to see are entirely fabricated. The scenarios are made up, but the problems are real."
    )
    user_text = st.sidebar.text_input("What do you want to know more about today?")
    if user_text:
        st_utils.sidebar_search(user_text, dfm)

    earliest = datetime(2022, 1, 1)

    col1, col2, col3, col4 = st.columns(4)

    currency_symbol = '£'
    money_format = currency_symbol + "{0:,.0f}"
    date_format = "{:%m-%Y}"
    format_dict = {}
    for c in dfm.financials.columns:
        if "MRR" in c:
            format_dict[c] = money_format
        elif "Date" in c:
            format_dict[c] = date_format
        elif "Month" not in c:
            format_dict[c] = "{0:,.0f}"

    financials = dfm.financials.loc[earliest:][[
        "Date",
        "New MRR",
        "Expansion MRR",
        "Total MRR",
        "New Customers",
        "Expansions",
        "Customer Churn",
        "Contractions",
        "Total Customers",
    ]]
    
    with col1:
        metrics = st.multiselect(
            "Select metrics to display", options=financials.columns
        )  # , default=['New MRR','Churned MRR','MRR'])
    # with col2:
    #     currency_code = st.selectbox(
    #         "Select currency to display",
    #         options=[
    #             "GBP",
    #             "USD",
    #             "EUR",
    #             "CAD",
    #             "AUD",
    #             "NZD",
    #             "CHF",
    #             "SEK",
    #             "NOK",
    #             "DKK",
    #             "MXN",
    #             "BRL",
    #             "ZAR",
    #             "INR",
    #             "JPY",
    #             "CNY",
    #             "HKD",
    #             "SGD"
    #         ],
    #     )

    st.line_chart(financials, x="Date", y=metrics, use_container_width=True)

    st.table(financials.style.format(format_dict))
    # st.table(dfm.financials.between_time(earliest.time(),datetime.now().time()).head())

# st.table(dfm.financials.drop(['reactivations','reactivation_mrr'], axis=1).tail())

else:
    with open("assets/welcome_message_pre_auth.txt", "r") as f:
        st.markdown(f.read())
    with open("assets/pre_auth_invite.txt", "r") as f:
        st.markdown(f.read())
