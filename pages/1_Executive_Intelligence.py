import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, MO

import streamlit as st

import components.st_utils as st_utils
import components.nai_utils as nut
import components.authenticate as authenticate

st_utils.style_page()
qs_params = st.experimental_get_query_params()
print(qs_params)
# if not nut.check_auth(qs_params):
#     authenticate.set_st_state_vars()
# else:
#     st.session_state["authenticated"] = True

if True:
#if (st.session_state["authenticated"]) or  (nut.check_auth(qs_params)):
    st.title("NarrativAI: Executive Intelligence")
    # Instantiate Q strings, company data, and sidebar
    dfm = nut.get_dfm()
    st_utils.create_sidebar(qs_params, dfm)

    # Important Variables
    earliest = datetime(2022, 1, 1)
    latest = datetime.today() + relativedelta(weekday=MO(-2))

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("### Time Period")
        period_select = st.selectbox("Period", ["Monthly", "Weekly"])

    with col2:
        st.markdown("### Summary Selection")
        if period_select == "Monthly":
            summary_select = st.selectbox('Monthly Updates', options = dfm.exec_summaries[dfm.exec_summaries.period_length == "month"].sort_values(by='start_date').period)
        elif period_select == "Weekly":
            summary_select = st.selectbox('Weekly Updates', options = dfm.exec_summaries[dfm.exec_summaries.period_length == "week"].sort_values(by='start_date').period)

    get_exec_summary = st.button('Get Update')

    if "date" in qs_params:
        date_obj = datetime.strptime(qs_params["date"][0], '%Y-%m-%d')

        url_select = date_obj.strftime('%B %Y')
        print(url_select)



    if get_exec_summary:
        st.write(
            dfm.exec_summaries.loc[
                (dfm.exec_summaries.period == summary_select)
            ].exec_summary.iloc[0]
        )
        st.markdown("--------")

    if  "date" in qs_params and not get_exec_summary:
        try:
            st.write(
                dfm.exec_summaries.loc[
                    (dfm.exec_summaries.period == url_select)
                ].exec_summary.iloc[0]
            )
        except IndexError as e:
            st.write(f'Searching for {date_obj}:')
            st.write("No summary for this period, please use the selectors above.")
            
        st.markdown("--------")

elif "NAI_no_group_assignedDEV" in st.session_state["user_cognito_groups"]:
    st.markdown("You've been registered, but you're not yet approved for access. We will let you know as soon as you are approved!")
else:
    with open("assets/welcome_message_pre_auth.txt", "r") as f:
        st.markdown(f.read())
    with open("assets/pre_auth_invite.txt", "r") as f:
        st.markdown(f.read())

# # Add login/logout buttons
# if st.session_state["authenticated"]:
#     authenticate.button_logout()
# else:
#     authenticate.button_login()