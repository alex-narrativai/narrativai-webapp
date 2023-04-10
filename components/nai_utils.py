import os
import re
import string
import urllib.parse
from datetime import datetime

from sqlalchemy import create_engine
import pandas as pd
import spacy
import streamlit as st
from streamlit_javascript import st_javascript

from dotenv import load_dotenv

from components.gpt_utils import *
from components.dfm import DataFrameManager

load_dotenv()

VENDOR_NAME = os.getenv("VENDOR_NAME")
VENDOR_SUMMARY = os.getenv("VENDOR_SUMMARY")
VENDOR_FEATURES = os.getenv("VENDOR_FEATURES")

URL_CODE = os.getenv("URL_CODE")


def check_auth(qs_params):
    return "url_code " in qs_params


@st.cache_data
def get_dfm():
    connection = get_db_engine().connect()
    dfm = DataFrameManager(connection)
    connection.close()
    return dfm


def get_db_engine():
    """
    This function creates a connection to the PostgreSQL database using provided connection parameters.

    :return: A SQLAlchemy engine connected to the PostgreSQL database.
    """
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    conn_string = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    engine = create_engine(conn_string)
    return engine


def user_string_parser(user_string, dfm, domain):
    """
    This function processes the user input string to extract relevant entities and then
    searches for these entities in the provided DataFrameManager object.

    :param user_string: The user input string to process.
    :param dfm: The DataFrameManager object containing the relevant data.
    :return: A tuple containing the type of entity found and the results of the search.
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(user_string)
    possibles = {
        "CLIENTS": [],
        "CONTACTS": [],
        "DATES": [],
        "EMPLOYEES": [],
        "LONG_MATCH": [],
        "GO_FISH": "",
    }
    for client in dfm.clients.itertuples():
        for c in client.client_name.lower().split(" "):
            if c in user_string.lower().strip(string.punctuation):
                print("FOUND A CLIENT IN REGULAR SEARCH: ", c)
                possibles["CLIENTS"].append(client)
                break
    if doc.ents:
        for ent in doc.ents:
            print("YEEHAW ITS AN: ", ent.text, ent.start_char, ent.end_char, ent.label_)
        for ent in doc.ents:
            if ent.label_ in ["DATE"]:
                output = gpt_date_search(user_string)
                print(output)
                res = extract_date_string(output)
                possibles["DATES"].append(res)
            else:
                if (
                    dfm.clients.client_name.str.contains(ent.text).any()
                    and len(possibles["CLIENTS"]) == 0
                ):
                    print("YEEHAW IT'S A CLIENT!")
                    possibles["CLIENTS"].append(
                        [dfm.clients[dfm.clients.client_name.str.contains(ent.text)]]
                    )
                if dfm.contacts.full_name.str.contains(ent.text).any():
                    possibles["CONTACTS"].append(
                        pd.concat(
                            [
                                dfm.contacts[dfm.contacts.full_name == ent.text],
                                dfm.contacts[dfm.contacts.first_name == ent.text],
                                dfm.contacts[dfm.contacts.last_name == ent.text],
                            ]
                        )
                    )
                if dfm.employees.full_name.str.contains(ent.text).any():
                    possibles["EMPLOYEES"].append(
                        dfm.employees[dfm.employees.full_name == ent.text]
                    )
    if (
        (len(possibles["CLIENTS"]) > 0)
        or (len(possibles["CONTACTS"]) > 0)
        or (len(possibles["DATES"]) > 0)
        or (len(possibles["EMPLOYEES"]) > 0)
    ):
        return possibles
    else:
        print("Starting long search...")
        ent_index = (
            dfm.clients[["name"]].values.tolist()
            + dfm.contacts[["full_name"]].values.tolist()
        )
        responses = []
        for ix in split_list(ent_index, 250):
            output = gpt_name_search(user_string, ix)
            print(output)
            if output.startswith("YES"):
                possibles["LONG_MATCH"].append(output.split("YES")[1])
                print(possibles)
                return possibles
        print("Starting gpt search...")
        prompt = f"""Answer this question from a business user at NarrativAI. If you don't know the answer just say so. 
        Answer in succinct bullet points if possible. {user_string}"""
        possibles[
            "GO_FISH"
        ] = f"### I can't match ':red[{user_string}]' to anything in my system - time to go ask the oracle... \n\n {gpt_question(prompt)}"
        return possibles


def named_parser(records: list, dfm: object):
    """
    This function parses a list of UUIDs and finds the corresponding client and contact
    records in the provided DataFrameManager object.

    :param records: A list of UUIDs to search for.
    :param dfm: The DataFrameManager object containing the relevant data.
    :return: A tuple containing lists of found clients and contacts.
    """
    clients = []
    contacts = []
    for rec in records:
        if isinstance(rec, list):
            for r in rec:
                try:
                    clients.append(dfm.clients[dfm.clients.client_id == r])
                except TypeError as e:
                    try:
                        contacts.append(dfm.contacts[dfm.contacts.contact_id == r])
                    except TypeError as e:
                        pass

    return clients, contacts


def date_parser(date_string: str, dfm: object):
    """
    This function searches for a specific date in the provided DataFrameManager object
    and returns the corresponding executive summary.

    :param date_string: The date string to search for.
    :param dfm: The DataFrameManager object containing the relevant data.
    :return: The executive summary associated with the specified date.
    """
    try:
        if date_string is not None:
            return dfm.exec_summaries[
                dfm.exec_summaries.start_date == date_string
            ].exec_summary.iloc[0]

        return "No executive summary found for the specified date."
    except IndexError as e:
        return "No executive summary found for the specified date."


def extract_uuids(string):
    """
    This function extracts UUIDs from a given string.

    :param string: The input string to search for UUIDs.
    :return: A list of UUIDs found in the string, or None if no UUIDs are found.
    """
    uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"  # Matches UUIDs in the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    matches = re.findall(uuid_pattern, string)
    if matches:
        return matches
    else:
        return None


def split_list(original_list, records):
    """
    This function splits a given list into smaller lists of a specified size.

    :param original_list: The input list to be split.
    :param records: The number of records in each new list.
    :return: A list of new lists containing the split records.
    """
    new_lists = []
    for i in range(0, len(original_list), records):
        new_lists.append(original_list[i : i + records])
    return new_lists


def string_to_markdown_url(
    label, page="", host="localhost:8501", query_params={}, target="_self", dfm=None
):
    print(host)
    """
    This function converts a given string into a markdown-formatted URL.

    :param string: The input string to be converted.
    :param page: The page to which the URL should be linked.
    :param host: The host on which the page is running.
    :param query_params: A dictionary of potential query string parameters.
    :return: A markdown-formatted URL string.
    """

    print(host)
    query_params["label"] = label
    query_string = urllib.parse.urlencode(query_params)
    url = f"{host}/{page}?{query_string}"

    if target == "_blank":
        markdown_url = f"[{label}](/?test)"

    elif target == "_self":  # This is the default
        tool_tip = ""
        if "contact_uuid" in query_params:
            contact = dfm.contacts[
                dfm.contacts.contact_id == query_params["contact_uuid"]
            ]
            tool_tip = f"{contact.role.iloc[0]} | {dfm.get_contact_client_name_from_id(query_params['contact_uuid'])}"
        elif "client_uuid" in query_params:
            client = dfm.clients[dfm.clients.client_id == query_params["client_uuid"]]
            tool_tip = f"{client.account_status.iloc[0]} | {client.stage.iloc[0]}"

        markdown_url = (
            f'<a href="{url}" target = "_self" title="{tool_tip}"> {label}</a>'
        )

    return markdown_url


def extract_date_string(sentence):
    """
    This function extracts a date string from a given sentence.

    :param sentence: The input sentence to search for a date string.
    :return: The date string in the format YYYY-MM-DD if found, or None if no date string is found.
    """
    date_pattern = r"\d{4}-\d{2}-\d{2}"  # Matches date strings in the format YYYY-MM-DD
    match = re.search(date_pattern, sentence)
    if match:
        return match.group(0)
    else:
        return None


def convert_currency_code_to_symbol(code):
    if code == "USD":
        return "$"
    elif code == "EUR":
        return "€"
    elif code == "GBP":
        return "£"
    elif code == "CAD":
        return "C$"
    elif code == "AUD":
        return "A$"
    elif code == "NZD":
        return "NZ$"
    elif code == "CHF":
        return "CHF"
    elif code == "SEK":
        return "SEK"
    elif code == "NOK":
        return "NOK"
    elif code == "DKK":
        return "DKK"
    elif code == "MXN":
        return "MX$"
    elif code == "BRL":
        return "R$"
    elif code == "ZAR":
        return "ZAR"
    elif code == "INR":
        return "₹"
    elif code == "JPY":
        return "¥"
    elif code == "CNY":
        return "¥"
    elif code == "HKD":
        return "HK$"
    elif code == "SGD":
        return "S$"
    elif code == "TWD":
        return "NT$"
    elif code == "KRW":
        return "₩"
    elif code == "TRY":
        return "₺"
    elif code == "RUB":
        return "₽"
    elif code == "PLN":
        return "zł"
    elif code == "THB":
        return "฿"
    elif code == "IDR":
        return "Rp"
    elif code == "MYR":
        return "RM"
    elif code == "PHP":
        return "₱"
    elif code == "VND":
        return "₫"
    elif code == "CZK":
        return "Kč"
    elif code == "HUF":
        return "Ft"
    elif code == "ILS":
        return "₪"
    elif code == "AED":
        return "د.إ"
    elif code == "ARS":
        return "ARS"
    elif code == "BOB":
        return "BOB"
    elif code == "CLP":
        return "CLP"
    elif code == "COP":
        return "COP"
