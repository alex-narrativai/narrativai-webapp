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
    st.title("NarrativAI: Metrics")
    
    # Instantiate Q strings, company data, and sidebar
    qs_params = st.experimental_get_query_params()
    dfm = nut.get_dfm()
    st_utils.create_sidebar(qs_params, dfm)
    st.write("This page is under construction. Please check back later.")

# # Add login/logout buttons
# if st.session_state["authenticated"]:
#     authenticate.button_logout()
# else:
#     authenticate.button_login()