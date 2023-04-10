import streamlit as st

import components.st_utils as st_utils
import nai_utils as nut
from dfm import DataFrameManager


st.set_page_config(layout="wide")

# Import the company data
if "dfm" not in st.session_state:
    connection = nut.get_db_engine().connect()
    dfm = DataFrameManager(connection)
    connection.close()
    st.session_state.dfm = dfm
else:
    dfm = st.session_state.dfm


STREAMLIT_STYLE = """
			<style>
			@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300&display=swap');
			html, body, [class*="css"]  {
			font-family: 'Lato', sans-serif;
			
			}
			
			footer {visibility: hidden;}
			</style>
			"""
# MainMenu {visibility: hidden;}
st.markdown(STREAMLIT_STYLE, unsafe_allow_html=True)

# Sidebar
st.sidebar.image("assets/blacklogo.png")

with open('assets/welcome_message_pre_auth.txt', 'r') as f:
    st.markdown(f.read())


if st_utils.check_password():
	# Interactive Search
	st.sidebar.markdown(
		":red[Disclaimer]: The companies, clients, contacts, and histories you are about to see are entirely fabricated. The scenarios are made up, but the problems are real."
	)
	user_text = st.sidebar.text_input("What do you want to know more about today?")
	if user_text:
		st_utils.sidebar_search(user_text, dfm)


	if not user_text:
		# Start of the unique page content
		st.title("Product Intelligence")
		col1, col2 = st.columns(2)
		with col1:
			st.markdown("Product stuff")


else:
    with open('assets/pre_auth_invite.txt', 'r') as f:
        st.markdown(f.read())