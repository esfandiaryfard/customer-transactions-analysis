from django.views.generic import TemplateView
from .utils import DataCleaner
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
import seaborn as sns


class DataVisualizationView(TemplateView):
    template_name = 'data_visualization.html'

    @staticmethod
    def plot_to_base64(plt):
        image_stream = BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)
        return base64.b64encode(image_stream.read()).decode('utf-8')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the clean data
        data_class = DataCleaner()
        dataset = data_class.clean_data()
        users = dataset['users']
        dataset = dataset['dataset']

        # ---AVG subscription KPI---
        # Calculate subscription duration for each user
        users['subscription_duration'] = (users['unsubscription_date'] - users['subscription_date']).dt.days
        # Calculate the average subscription duration
        average_subscription_duration = round(users['subscription_duration'].mean(), 1)
        # Create the Matplotlib plot
        plt.figure(figsize=(3, 1))
        plt.text(0.5, 0.5, f'Average Subscription Day: \n {average_subscription_duration}', fontsize=12, ha='center',
                 va='center')
        plt.axis('off')  # Turn off the axes
        # Convert the plot to base64
        subscription = self.plot_to_base64(plt)
        context['subscription'] = subscription

        # ---Churn Rate KPI---
        # remove month 7 because we have no info of registered users in month 7 so it has negative effect
        filtered_users = users[
            ~((users['unsubscription_date'].dt.month == 7) & (users['unsubscription_date'].dt.year == 2023))]
        # Calculate churn rate
        churn_rate = (filtered_users['unsubscription_date'].notnull().sum() / len(filtered_users)) * 100
        plt.figure(figsize=(3, 1))
        plt.text(0.5, 0.5, f'Churn Rate:\n{churn_rate:.2f}%', fontsize=12, ha='center', va='center')
        plt.axis('off')  # Turn off the axes
        # Convert the plot to base64
        churn = self.plot_to_base64(plt)
        context['churn'] = churn

        # ---AVG Failed KPI---
        # Calculate the percentage of failure for each transaction
        dataset['failure_percentage'] = (dataset['status'] == 'Failed').astype(int) * 100
        average_failure_percentage = dataset['failure_percentage'].mean()
        plt.figure(figsize=(4, 1))
        plt.text(0.5, 0.5, f'Average Percentage of Failed Transactions:\n {average_failure_percentage:.2f}%',
                 fontsize=12, ha='center', va='center')
        plt.axis('off')  # Turn off the axes
        # Convert the plot to base64
        failed = self.plot_to_base64(plt)
        context['failed'] = failed

        # ---Plotting the number of users for each operator---
        operator_counts = users['phone_operator'].value_counts()
        plt.figure(figsize=(8, 4))
        plt.bar(operator_counts.index, operator_counts.values, color='skyblue')
        plt.xlabel('Phone Operator')
        plt.ylabel('Number of Subscribed Users')
        plt.title('Histogram of Subscribed Users by Phone Operator')
        # Convert the plot to base64
        operator_user = self.plot_to_base64(plt)
        context['operator_user'] = operator_user

        # ---Most used os for our customers---
        users['subscription_date'] = pd.to_datetime(users['subscription_date'])
        plt.figure(figsize=(8, 4))
        sns.countplot(x='os_name', data=users)
        plt.xlabel('OS Name')
        plt.ylabel('Number of Subscribed Users')
        plt.title('Distribution of Subscribed Users by OS Name')
        # Convert the plot to base64
        os = self.plot_to_base64(plt)
        context['os'] = os

        # --compare of sub and unsubscription rate over time--
        daily_user_counts = users.groupby(users['subscription_date'].dt.to_period("D")).size()
        un_daily_user_counts = users.groupby(users['unsubscription_date'].dt.to_period("D")).size()
        combined_counts = pd.concat([daily_user_counts, un_daily_user_counts], axis=1,
                                    keys=['Subscribed', 'Unsubscribed'])
        plt.figure(figsize=(15, 5))
        plt.plot(combined_counts.index.astype(str), combined_counts['Subscribed'].values, marker='o', linestyle='-',
                 label='Subscribed')
        plt.plot(combined_counts.index.astype(str), combined_counts['Unsubscribed'].values, marker='o', linestyle='-',
                 label='Unsubscribed')
        plt.title('Number of Registered Users Each Day')
        plt.ylabel('Sum of Users')
        plt.tight_layout()
        plt.legend()
        # Convert the plot to base64
        rate = self.plot_to_base64(plt)
        context['rate'] = rate

        # ---churn by operators---
        churn_by_operator = users.groupby('phone_operator')['unsubscription_date'].count() / \
                            users.groupby('phone_operator')['user_id'].count() * 100
        plt.figure(figsize=(8, 4))
        plt.pie(churn_by_operator, labels=churn_by_operator.index, autopct='%1.1f',
                colors=['skyblue', 'lightcoral', 'lightgreen'])
        plt.title('Churn Rate by Phone Operator')
        # Convert the plot to base64
        op_churn = self.plot_to_base64(plt)
        context['op_churn'] = op_churn

        # --Calculate subscription durations--
        users['subscription_duration'] = users['unsubscription_date'] - users['subscription_date']
        users['subscription_duration_days'] = users['subscription_duration'].dt.days
        plt.figure(figsize=(8, 4))
        plt.hist(users['subscription_duration_days'].dropna(), bins=5, color='skyblue', edgecolor='black')
        plt.xlabel('Subscription Duration (Days)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Subscription Durations')
        # Convert the plot to base64
        subscription_duration = self.plot_to_base64(plt)
        context['subscription_duration'] = subscription_duration

        # ---Calculate the correlation matrix---
        correlation_matrix = dataset[
            ['subscription_date', 'os_version', 'unsubscription_date', 'transaction_timestamp', 'pricepoint']].corr()
        plt.figure(figsize=(10, 7))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Correlation Matrix')
        # Convert the plot to base64
        correlation = self.plot_to_base64(plt)
        context['correlation'] = correlation

        # ---most churned os versions---
        churn_by_os = users.groupby('os_version')['unsubscription_date'].count() / users.groupby('os_version')[
            'user_id'].count() * 100
        top5_churn_by_oa = churn_by_os.sort_values(ascending=False).head(5)
        plt.figure(figsize=(8, 4))
        # Plot the bar chart for the top 5 phone operators
        top5_churn_by_oa.plot(kind='bar', color='skyblue')
        plt.xlabel('Os version')
        plt.ylabel('Churn Rate (%)')
        plt.title('Top 5 Churn Rates by Phone Operator')
        # Convert the plot to base64
        os_churn = self.plot_to_base64(plt)
        context['os_churn'] = os_churn

        # --Calculate user distribution across affiliates--
        affiliate_distribution = users['affiliate'].value_counts()
        plt.figure(figsize=(8, 4))
        plt.pie(affiliate_distribution, labels=affiliate_distribution.index, autopct='%1.1f',
                wedgeprops=dict(width=0.3, edgecolor='w', linewidth=2), colors=['red', 'blue', 'green'])
        plt.title('Distribution of Users Across Affiliates (Donut Chart)')
        # Convert the plot to base64
        affiliates = self.plot_to_base64(plt)
        context['affiliates'] = affiliates
        
        # --Calculate subscription rates by affiliate--
        subscription_rates = users.groupby('affiliate')['user_id'].count() / len(users) * 100
        plt.figure(figsize=(8, 4))
        plt.pie(subscription_rates, labels=subscription_rates.index, autopct='%1.1f',
                wedgeprops=dict(width=0.3, edgecolor='w', linewidth=2), colors=['red', 'blue', 'green'])
        plt.title('Subscription Rates by Affiliate (Donut Chart)')
        # Convert the plot to base64
        affiliates = self.plot_to_base64(plt)
        context['affiliates'] = affiliates
        # 
        # subscription by service point
        plt.figure(figsize=(8, 4))
        sns.countplot(x='service', data=users, palette='viridis')
        plt.title('Distribution of Subscriptions by Service')
        plt.xlabel('Service')
        plt.ylabel('Number of Subscriptions')
        plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
        # Convert the plot to base64
        sub_affiliates = self.plot_to_base64(plt)
        context['sub_affiliates'] = sub_affiliates

        # --Device Preference by Service--
        plt.figure(figsize=(8, 4))
        sns.countplot(x='service', hue='os_name', data=users, palette='Set2')
        plt.title('Device Preference by Service')
        plt.xlabel('Service/Product')
        plt.ylabel('Number of Subscribers')
        plt.legend(title='Device Preference')
        # Convert the plot to base64
        device = self.plot_to_base64(plt)
        context['device'] = device

        # --Phone Operator Preference by Service--
        plt.figure(figsize=(8, 4))
        sns.countplot(x='service', hue='phone_operator', data=users, palette='Set2')
        plt.title('Phone Operator Preference by Service')
        plt.xlabel('Phone Operator')
        plt.ylabel('Number of Subscribers')
        plt.legend(title='Device Preference')
        # Convert the plot to base64
        op_service = self.plot_to_base64(plt)
        context['op_service'] = op_service

        # --Create a stacked bar chart for Aggregator vs. Operator Distribution--
        plt.figure(figsize=(8, 4))
        sns.countplot(x='aggregator', hue='phone_operator', data=users, palette='viridis', edgecolor='k')
        plt.title('Aggregator vs. Operator Distribution')
        plt.xlabel('Aggregator')
        plt.ylabel('Number of Subscribers')
        plt.legend(title='Phone Operator')
        # Convert the plot to base64
        aggregator = self.plot_to_base64(plt)
        context['aggregator'] = aggregator

        # --Calculate the daily transaction success rate--
        daily_success_rate = (
                dataset[dataset['status'] == 'Delivered'].resample(
                    'D', on='transaction_timestamp').size() / dataset.resample('D', on='transaction_timestamp').size())
        daily_unsuccess_rate = (
                dataset[dataset['status'] == 'Failed'].resample(
                    'D', on='transaction_timestamp').size() / dataset.resample('D', on='transaction_timestamp').size())
        plt.figure(figsize=(15, 4))
        plt.plot(daily_success_rate.index, daily_success_rate, marker='o', linestyle='-', color='b',
                 label='Success Rate')
        plt.plot(daily_unsuccess_rate.index, daily_unsuccess_rate, marker='o', linestyle='-', color='r',
                 label='Failure Rate')
        plt.title('Transaction Success Rate Over Time')
        plt.xlabel('Date')
        plt.ylabel('Rate')
        plt.ylim(0, 1)  # Set y-axis limit to represent percentages (0-100%)
        plt.legend()
        # Convert the plot to base64
        daily_transaction = self.plot_to_base64(plt)
        context['daily_transaction'] = daily_transaction

        return context
