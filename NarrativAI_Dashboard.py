import streamlit as st

import components.st_utils as st_utils
import components.nai_utils as nut
import components.authenticate as authenticate

st_utils.style_page()
qs_params = st.experimental_get_query_params()
# authenticate.set_st_state_vars()

URL_CODE = "indfhg-34343928-dfaloajhsdfuc-343456"


st.title('Welcome to NarrativAI!')
with open('assets/welcome_message_pre_auth.txt', 'r') as f:
    st.markdown(f.read())



if True:
#if (st.session_state["authenticated"] and ("NAI_DEV" in st.session_state["user_cognito_groups"] or "EA_INVITE" in st.session_state["user_cognito_groups"])):
    # Instantiate Q strings, company data, and sidebar
    
    dfm = nut.get_dfm()
    st_utils.create_sidebar(qs_params, dfm)
    
    with open('assets/welcome_message_post_auth.txt', 'r') as f:
        st.markdown(f.read())
        
elif "NAI_no_group_assignedDEV" in st.session_state["user_cognito_groups"]:
    st.markdown("You've been registered, but you're not yet approved for access. We will let you know as soon as you are approved!")

else:
    with open('assets/pre_auth_invite.txt', 'r') as f:
        st.markdown(f.read())

# # Add login/logout buttons
# if st.session_state["authenticated"]:
#     authenticate.button_logout()
# else:
#     authenticate.button_login()