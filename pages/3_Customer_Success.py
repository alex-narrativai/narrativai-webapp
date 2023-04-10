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
    st.title("NarrativAI: Customer Success")
    # Instantiate Q strings, company data, and sidebar
    qs_params = st.experimental_get_query_params()
    dfm = nut.get_dfm()
    print(dfm.clients.account_status.unique())
    st_utils.create_sidebar(qs_params, dfm)


    qs_params = st.experimental_get_query_params()
    print(qs_params)
    print(st.session_state)
    passed_client = qs_params['client_uuid'][0] if 'client_uuid' in qs_params else None


    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Start of the unique page content

        prospect = st.selectbox(
            "Prospective Clients",
            dfm.clients[dfm.clients.account_status == "PROSPECT"].client_name,
        )
        pr = st.button("Get Prospect Summary")

    with col2:
        customer = st.selectbox(
            "Current Clients",
            dfm.clients[dfm.clients.account_status == "CUSTOMER"].client_name,
        )
        ct = st.button("Get Client Summary")

    with col3:
        churned = st.selectbox(
            "Churned Clients", dfm.clients[dfm.clients.account_status == "CHURN"].client_name
        )
        cc = st.button("Get Ex-Client Summary")

    if passed_client:
        st_utils.print_client_details(dfm.clients[dfm.clients.client_name == qs_params['name'][0]], dfm)
    if pr:
        st_utils.print_client_details(dfm.clients[dfm.clients.client_name == prospect], dfm)

    if cc:
        st_utils.print_client_details(dfm.clients[dfm.clients.client_name == churned], dfm)

    if ct:
        st_utils.print_client_details(dfm.clients[dfm.clients.client_name == customer], dfm)



else:
    with open('assets/welcome_message_pre_auth.txt', 'r') as f:
        st.markdown(f.read())
    with open('assets/pre_auth_invite.txt', 'r') as f:
        st.markdown(f.read())


# # Add login/logout buttons
# if st.session_state["authenticated"]:
#     authenticate.button_logout()
# else:
#     authenticate.button_login()