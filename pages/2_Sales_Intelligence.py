from datetime import datetime

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
    st.title('NarrativAI: Sales Intelligence')
    # Instantiate Q strings, company data, and sidebar
    qs_params = st.experimental_get_query_params()
    dfm = nut.get_dfm()
    st_utils.create_sidebar(qs_params, dfm)

    passed_contact = qs_params['contact_uuid'][0] if 'contact_uuid' in qs_params else None
    earliest = datetime(2022,1,1)

    col1, col2 = st.columns(2)
    clients = dfm.clients.name.to_list()
    if passed_contact:
        
        clients = [dfm.get_contact_client_name_from_id(passed_contact)] + clients
    with col1:
        st.markdown('## 🏢 Client Details')
        client_name = st.selectbox('Select a client:', clients)
        if client_name != "":
            st_utils.print_client_details(dfm.clients[dfm.clients.name == client_name],dfm)

    with col2:
        st.markdown('## 🧑‍🤝‍🧑 Contact Details')
        contacts = dfm.contacts[dfm.contacts.client_id== dfm.clients[dfm.clients.name == client_name].client_id.iloc[0]].full_name.to_list()
        if passed_contact:
            contacts.remove(qs_params['name'][0])
            contacts.insert(0, qs_params['name'][0])
        if client_name != '':
            contact_name = st.selectbox('Select a contact:', contacts)
            st_utils.print_contact_details(dfm.contacts[dfm.contacts.full_name==contact_name])


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