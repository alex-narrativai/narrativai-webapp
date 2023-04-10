import os
from datetime import datetime

import openai
import spacy

import components.nai_utils as nut


OPENAI_API_KEY = os.getenv("OPENAI_KEY")
openai.api_key = OPENAI_API_KEY

def gpt_name_search(ent_text, ent_index, ent_type="Company and Contact Name"):
    OPENAI_API_KEY = os.getenv("OPENAI_KEY")
    openai.api_key = OPENAI_API_KEY
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"You are a researcher cross referencing colloquial names to a list of formal names to find potential matches.",
            },
            {
                "role": "system",
                "content": f"{ent_type} index for reference containing company and full names. {ent_index}",
            },
            {
                "role": "user",
                "content": f"If {ent_text} is referring to a name or company name or any similar version of one from the above list, respond with them items from the list that match, seperated by commas. Include partial matches - for example 'Planet' could match 'Planet Express'. Start with YES if there is a match, and NO if there is not.",
            },
        ],
        n=1,
        stop=None,
        temperature=0.1,
    )

    # Extract the generated transcript from the AI model's response
    parsed = completion.choices[0]["message"]["content"]

    # Return the generated transcript and usage information
    return parsed


def gpt_date_search(date_string, first_of_week="Monday"):

    OPENAI_API_KEY = os.getenv("OPENAI_KEY")
    openai.api_key = OPENAI_API_KEY
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"You are a simple natural language parser helping to identify a date from a sentence. Assume that today is {datetime.today()} - so any reference to 'last October' would be October 2022 for example.",
            },
            {
                "role": "system",
                "content": f"You will output a string corresponding to the first date of a given time period. For example, if you are passed 'What happened two weeks ago?' you will respond with the date of the first day of the week in question. Consider {first_of_week} to be the first day of a week. If just a month is given assume this year and return the date of the first of the given month of this year. If a day of the week is given return the first day of the week. Output format:: YYYY-MM-DD",
            },
            {
                "role": "user",
                "content": f"Extract the date from: {date_string}. Only respond with either the first of the month or a Monday. Only respond with the date string: YYYY-MM-DD",
            },
        ],
        n=1,
        stop=None,
        temperature=0.1,
    )

    # Extract the generated transcript from the AI model's response
    parsed = completion.choices[0]["message"]["content"]

    # Return the generated transcript and usage information
    return parsed

def gpt_question(question):
    OPENAI_API_KEY = os.getenv("OPENAI_KEY")
    openai.api_key = OPENAI_API_KEY
    """
    Parses conversation transcripts and summaries for mentions of a specific target relevant to the vendor.

    Parameters:
        transcript (str): A string containing the conversation transcript to be parsed.
        parse_target (str): The target to be parsed from the transcript.
        client_name (str): The name of the customer company in the transcript.
        vendor (str): The name of the vendor.
        vendor_description (str): Description of the vendor being analyzed.
        output (str): The expected output format.

    Returns:
        str: A string containing the parsed transcript in the specified output format.

    """
    print(question)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"You are Q&A GPT - Answer in succinct sentences, ideally in bullet points. If you don't know the answer to a question, just say so. Output should be in markdown format.",
            },
            {"role": "user", "content": f"{question}"},
        ],
        n=1,
        stop=None,
        temperature=0.4,
    )

    # Extract the generated transcript from the AI model's response
    parsed = completion.choices[0]["message"]["content"]

    # Return the generated transcript and usage information
    return parsed


def gpt_search_records(user_string, dfm):
    OPENAI_API_KEY = os.getenv("OPENAI_KEY")
    openai.api_key = OPENAI_API_KEY
    ent_index = (
        dfm.clients[["name"]].values.tolist()
        + dfm.contacts[["full_name"]].values.tolist()
    )

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(user_string)
    print(doc.ents)

    for ent in doc.ents:
        if ent.label_ in ["ORG", "PERSON"]:
            responses = []
            summaries = []
            print(ent)
            for r in responses:
                if r is not None:
                    for uuid in r:
                        client_records = dfm.clients[
                            dfm.clients.client_id == uuid
                        ].relationship_summary
                        if len(client_records) > 0:
                            summaries.append(client_records.iloc[0])
                        contact_records = dfm.contacts[
                            dfm.contacts.contact_id == uuid
                        ].relationship_summary
                        if len(contact_records) > 0:
                            summaries.append(contact_records.iloc[0])
            return summaries

        elif ent.label_ in ["DATE"]:
            output = gpt_date_search(user_string)
            print(output)
            res = nut.extract_date_string(output)
            return [dfm.monthly[dfm.monthly.start_date == res].exec_summary.iloc[0]]
