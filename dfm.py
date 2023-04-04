import calendar
import uuid

from sqlalchemy import text, engine
import pandas as pd


class DataFrameManager:
    """
    A class used to manage and interact with various dataframes. The dataframes
    are read from a PostgreSQL database using the provided connection object.
    """

    def __init__(self, conn: engine.base.Connection):
        """
        Initializes the DataFrameManager with the dataframes read from the
        provided database connection.

        :param conn: A SQLAlchemy connection object.
        """
        self.clients = pd.read_sql(text("select * from clients"), conn)
        self.contacts = pd.read_sql(text("select * from contacts"), conn)
        self.interactions = pd.read_sql(text("select * from interactions"), conn)

        self.employees = pd.read_sql(text("select * from employees"), conn)
        self.interactions_contacts = pd.read_sql(
            text("select * from interactions_contacts"), conn
        )
        self.interactions_employees = pd.read_sql(
            text("select * from interactions_employees"), conn
        )
        self.financials = pd.read_sql(text("select * from financials"), conn)
        self.documents = pd.read_sql(text("select * from documents"), conn)
        self.weekly = pd.read_sql(text("select * from weekly"), conn)
        self.monthly = pd.read_sql(text("select * from monthly"), conn)
        self.key_accounts = pd.read_sql(text("select * from key_accounts"), conn)

        # Financials table pre-processing
        self.financials["date"] = pd.to_datetime(self.financials["date"])
        self.financials["bk-date"] = self.financials.date
        self.financials["month"] = self.financials.date.apply(
            lambda x: f" {x.year} {calendar.month_name[x.month]}"
        )
        self.financials = self.financials.set_index("date")
        self.financials["date"] = self.financials["bk-date"]
        self.financials['total_customers'] = self.financials['customers']
        self.financials['total_mrr'] = self.financials['mrr']
        self.financials.drop(["bk-date",'mrr', 'customers'], axis=1, inplace=True)

        self.financials = convert_column_names(self.financials)

        self.dataframes = [
            self.clients,
            self.contacts,
            self.interactions,
            self.employees,
            self.interactions_contacts,
            self.interactions_employees,
            self.financials,
            self.documents,
            self.weekly,
            self.monthly,
            self.key_accounts,
        ]

        for df in self.dataframes:
            if "Unnamed" in df.columns[0]:
                df.drop(df.columns[0], axis=1, inplace=True)
            df.fillna("", inplace=True)

    def filtered_search(self, df_name: str, column: str, value):
        """
        Searches for records in the specified dataframe where the specified
        column matches the provided value.

        :param df_name: The name of the dataframe to search.
        :param column: The name of the column to filter on.
        :param value: The value to search for in the specified column.
        :return: A filtered dataframe containing the matching records.
        """
        if hasattr(self, df_name):
            df = getattr(self, df_name)
            return df[df[column] == value]
        else:
            raise ValueError(f"No dataframe with name '{df_name}' found.")

    def get_columns_single_table(self, df_name: str, columns: list):
        if hasattr(self, df_name):
            df = getattr(self, df_name)
            return df[columns]
        else:
            raise ValueError(f"No dataframe with name '{df_name}' found.")

    def get_contact_full_name_from_id(self, contact_id):
        contact_id = uuid.UUID(contact_id) if type(contact_id) == str else contact_id
        names = self.contacts[self.contacts.contact_id == contact_id][
            ["first_name", "last_name"]
        ].iloc[0]
        return names.first_name + " " + names.last_name

    def get_contact_client_id_from_id(self, contact_id):
        contact_id = uuid.UUID(contact_id) if type(contact_id) == str else contact_id
        return self.contacts[self.contacts.contact_id == contact_id].client_id.iloc[0]

    def get_contact_client_name_from_id(self, contact_id):
        contact_id = uuid.UUID(contact_id) if type(contact_id) == str else contact_id
        return self.clients[
            self.clients.client_id == self.get_contact_client_id_from_id(contact_id)
        ].name.iloc[0]

    def get_contact_fact_by_id_and_fact_name(self, contact_id, fact_name):
        contact_id = uuid.UUID(contact_id) if type(contact_id) == str else contact_id
        return self.contacts[self.contacts.contact_id == contact_id][fact_name].iloc[0]

    def get_client_id_by_name(self, client_name):
        return self.clients[self.clients.name == client_name].client_id.iloc[0]

    def get_client_name_by_id(self, client_id):
        client_id = uuid.UUID(client_id) if type(client_id) == str else client_id
        return self.clients[self.clients.client_id == client_id].name.iloc[0]

    def get_client_fact_by_id_and_fact_name(self, client_id, fact_name):
        client_id = uuid.UUID(client_id) if type(client_id) == str else client_id
        return self.clients[self.clients.client_id == client_id][fact_name].iloc[0]

    def get_client_id_by_contact_full_name(self, contact_name):
        return self.clients[
            self.clients.client_id
            == self.contacts[self.contacts.full_name == contact_name].client_id.iloc[0]
        ].client_id.iloc[0]

    def get_interaction_fact_by_id_and_fact_name(self, interaction_id, fact_name):
        interaction_id = uuid.UUID(interaction_id) if type(interaction_id) == str else interaction_id
        return self.interactions[self.interactions.interaction_id == interaction_id][
            fact_name
        ].iloc[0]


# Utility functions for DFM
def convert_column_names(df):
    """
    Converts the column names of a DataFrame from lower snakecase to proper capitalisation and spacing.

    Parameters:
        df (pandas.DataFrame): The DataFrame to convert column names of.

    Returns:
        pandas.DataFrame: The DataFrame with the converted column names.
    """
    new_column_names = []

    for column_name in df.columns:
        acronym_list = ["MRR"]
        words = column_name.split("_")
        new_words = [word.capitalize() for word in words]
        for i, s in enumerate(new_words):
            if s.upper() in acronym_list:
                new_words[i] = s.upper()
        new_column_names.append(" ".join(new_words))

    df.columns = new_column_names

    return df
