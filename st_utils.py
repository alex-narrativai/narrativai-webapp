from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, MO
from urllib.parse import urlparse

import streamlit as st
from streamlit_javascript import st_javascript

import nai_utils as nut


# --- USER AUTHENTICATION ---
def check_password():
    """Returns `True` if the user had the correct password."""
    return True

    def password_entered(testing=True):
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True


def draw_logo_on_top():
    st.sidebar.image("app/assets/blacklogo.png")


def style_page():
    """
    This function styles the Streamlit page.
    """
    # Set the page icon
    st.set_page_config(
        page_title="NarrativAI Demo",
        page_icon="❓",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    # st.sidebar.image("assets/blacklogo.png")
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

    # CSS to inject contained in a string
    hide_table_row_index = """
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)


def print_contact_details(contact):
    """
    This function prints the contact details using Streamlit markdown.

    :param contact: A pandas DataFrame containing a single row of contact details.
    """
    # Display the contact's full name as an H2 heading
    st.markdown(f"## {contact.full_name.iloc[0]}")
    # Display the contact's role as an H4 heading
    st.markdown(f"#### {contact.role.iloc[0]}")
    # Display the contact's relationship summary as markdown, updating heading levels
    st.markdown(contact.relationship_summary.iloc[0].replace("##", "####"))


def print_client_details(client, dfm):
    """
    This function prints the client details using Streamlit markdown.

    :param client: A pandas DataFrame containing a single row of client details.
    :param dfm: A DataFrameManager instance containing data from related tables.
    """
    # Display the client's name as an H2 heading
    st.markdown(f"## {client.name.iloc[0]}")
    # Display the client's account status and stage as an H4 heading
    st.markdown(f"#### {client.account_status.iloc[0]} | {client.stage.iloc[0]}")

    # Check if the client is a key account and display a message if true
    if dfm.key_accounts.client_id.eq(client.client_id).any():
        st.markdown(f"## This is a Key Account")

    # Display the client's relationship summary as markdown, updating heading levels
    st.markdown(client.relationship_summary.iloc[0].replace("##", "###"))


def create_sidebar(qs_params, dfm):
    url_string = st_javascript("await fetch('').then(r => window.parent.location.href)")
    parsed_url = urlparse(url_string)

    domain = f"{parsed_url.scheme}://{parsed_url.hostname}"
    if parsed_url.port:
        domain += f":{parsed_url.port}"

    st.sidebar.markdown(':red[Disclaimer]: The companies, clients, contacts, and histories you are about to see are entirely fabricated. The scenarios are made up, but the problems are real.')
    st.sidebar.write('-------')
    user_text = st.sidebar.text_input("What do you want to know more about today?", key="ei_search")
    
    if 'query' in qs_params:
        user_text = qs_params['query'][0]
    if user_text:
        sidebar_search(user_text, dfm, domain)
    else:
        st.sidebar.write("Try things like 'tell me about last October?' or 'what's the status of Los Pollos Hermanos?' or even 'Tell me about Audrey from Planet Express'!")

def sidebar_search(search_string, dfm, domain):
    #@st.cache_data
    def get_possibles(search_string, _dfm, domain):
        return nut.user_string_parser(search_string, dfm, domain)

    possibles = get_possibles(search_string, dfm, domain)
    
    #st.sidebar.write(possibles)
    if len(possibles["LONG_MATCH"]) > 0:
        #print(possibles["LONG_MATCH"][1])
        possibles = nut.user_string_parser(possibles["LONG_MATCH"][0], dfm, domain)
        print("# Long Match")
        st.sidebar.write("No exact matches found, but we found some close ones. Did you mean:")

        print_side_bar_results(possibles, possibles["LONG_MATCH"], dfm, domain)

    elif possibles["GO_FISH"] != "":
        st.sidebar.write("# Go Fish!")
        st.sidebar.write(possibles["GO_FISH"])
    else:
        st.sidebar.write(
            f"# NarrativAI: {len(possibles['CLIENTS'] + possibles['CONTACTS'] + possibles['EMPLOYEES'] +possibles['DATES'])} Results"
        )
        print_side_bar_results(possibles, search_string, dfm, domain)

    st.sidebar.write("--------")
    st.sidebar.write("Want to take this search outside of the demo? Ask GPT!")
    ask_gpt = st.sidebar.button("Ask GPT")
    if ask_gpt:
        st.sidebar.write(gpt_utils.gpt_question(search_string))

    
def print_side_bar_results(possibles, search_string, dfm, domain):
    if possibles["CLIENTS"] != []:
        # st.sidebar.write("# Clients")
        for c in possibles["CLIENTS"]:
            #for c in client.itertuples():
                link = nut.string_to_markdown_url(
                    c.name,
                    page="Customer_Success",
                    query_params={
                        "client_uuid": c.client_id,
                        "name": c.name,
                        "stage": c.stage,
                        "status": c.account_status,
                        "query": search_string,
                    },
                    dfm=dfm,
                    host=domain
                )
                st.sidebar.write(f"## {link}", unsafe_allow_html=True)
                st.sidebar.write(
                    f"### {c.account_status[0] + c.account_status[1:].lower()} | [{c.url}]({c.url})"
                )
                st.sidebar.write(
                    f"### Next Steps\n{c.relationship_summary.split('Next Steps')[1].split('Client Priorities')[0]}"
                )
                # st.sidebar.write('--------')
    if possibles["CONTACTS"] != []:
        # st.sidebar.write("# Contacts")
        for contact in possibles["CONTACTS"]:
            for c in contact.itertuples():
                link = nut.string_to_markdown_url(
                    c.full_name,
                    page="Sales_Intelligence",
                    query_params={
                        "contact_uuid": c.contact_id,
                        "name": c.full_name,
                        "query": search_string,
                    },
                    dfm=dfm,
                    host=domain
                )
                st.sidebar.write(f"## {link}\n{c.role}", unsafe_allow_html=True)
                st.sidebar.write(
                    c.relationship_summary.split("Contact Questions")[0]
                )
                # st.sidebar.write('--------')
    if possibles["EMPLOYEES"] != []:
        # TODO - Add employee page and link to it (Company Update)
        st.sidebar.write("# Employees")
        for employee in possibles["EMPLOYEES"]:
            for e in employee.itertuples():
                st.sidebar.write(employee.name)

    if possibles["DATES"] != []:
        st.sidebar.write("# Executive Summaries")
        for date in possibles["DATES"]:
            # dt = dfm.weekly[dfm.weekly.date == date]
            summ = nut.date_parser(date, dfm)
            if summ is not None:
                summary = " ".join(summ.split("\n")[1:])[:250].replace("#", "") + "..."
                report_title = summ.split("\n")[0].replace(
                    "#", ""
                )  # .split(':')[1].strip()
                link = nut.string_to_markdown_url(
                    f"{date} Update",
                    page="Executive_Intelligence",
                    query_params={"date": date, "query": search_string},
                    dfm=dfm,
                    host=domain
                )
                st.sidebar.write(f"## {link}", unsafe_allow_html=True)
                st.sidebar.write(f"{summary}")
            else:
                st.markdown("Sorry, I couldn't find any executive summaries for that date. Please check the Executive Intelligence tab for more information.")