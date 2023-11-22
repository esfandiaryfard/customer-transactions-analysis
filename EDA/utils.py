import pandas as pd


class DataCleaner:
    def clean_data(self):
        # read users data
        users = pd.read_csv("data/users.csv")
        # remove null value
        users = users.dropna(subset=users.columns.difference(['unsubscription_date']))
        # read transactions data
        transactions = pd.read_csv("data/transactions.tsv", sep='\t')
        # remove null values
        transactions = transactions.dropna(subset=transactions.columns.difference(['unsubscription_date']))
        # join two dataset together
        dataset = pd.merge(users, transactions, on='user_id', how='inner', suffixes=('', '_transactions'))
        dataset = dataset.filter(regex='^(?!.*_transactions$)')
        # fix the data type
        dataset['subscription_date'] = pd.to_datetime(dataset['subscription_date'])
        dataset['unsubscription_date'] = pd.to_datetime(dataset['unsubscription_date'])
        dataset['transaction_timestamp'] = pd.to_datetime(dataset['transaction_timestamp'])
        users['subscription_date'] = pd.to_datetime(users['subscription_date'])
        users['unsubscription_date'] = pd.to_datetime(users['unsubscription_date'])

        return {"users": users, "transactions": transactions, "dataset": dataset}
