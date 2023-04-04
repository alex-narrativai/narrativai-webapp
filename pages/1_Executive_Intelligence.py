import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, MO

import streamlit as st

import st_utils
import nai_utils as nut
import authenticate

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

    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    with col1:
        st.markdown("### Monthly")

    with col4:
        st.markdown("### Weekly")

    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

    with col1:
        year_select = st.selectbox("Year", ["", 2022, 2023])
        month_search = st.button("Search", key="month_search")

    with col2:
        if year_select == "":
            month_select = st.selectbox("Month", [""])
        elif year_select == 2023:
            month_select = st.selectbox(
                "Month", list(calendar.month_name[: datetime.today().month + 1])
            )
        else:
            month_select = st.selectbox("Month", list(calendar.month_name))

    with col4:
        week_select = st.date_input(
            "Date", datetime.today() - timedelta(14), earliest, latest
        )
        week_search = st.button("Search", key="week_search")

    passed_in_summary = (
        nut.date_parser(qs_params["date"][0], dfm) if "date" in qs_params else None
    )

    if month_search:
        if month_select and year_select:
            st.markdown(
                dfm.monthly.loc[
                    (dfm.monthly.month_name == month_select)
                    & (dfm.monthly.year == year_select)
                ].exec_summary.iloc[0]
            )
            st.markdown("--------")
        else:
            st.markdown("## Select both month and year.")

    elif week_search:
        lastMonday = week_select + relativedelta(weekday=MO(-1))
        print(lastMonday)
        st.markdown(
            dfm.weekly[dfm.weekly.start_date == str(lastMonday)].exec_summary.iloc[0]
        )
        st.markdown("--------")

    elif passed_in_summary:
        st.markdown(passed_in_summary)
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