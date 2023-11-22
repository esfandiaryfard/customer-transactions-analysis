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

    def average_subscription_duration_plot(self, users):
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
        return self.plot_to_base64(plt)

    def churn_rate_plot(self, users):
        # Remove month 7 because we have no info of registered users in month 7 so it has a negative effect
        filtered_users = users[
            ~((users['unsubscription_date'].dt.month == 7) & (users['unsubscription_date'].dt.year == 2023))]
        # Calculate churn rate
        churn_rate = (filtered_users['unsubscription_date'].notnull().sum() / len(filtered_users)) * 100
        plt.figure(figsize=(3, 1))
        plt.text(0.5, 0.5, f'Churn Rate:\n{churn_rate:.2f}%', fontsize=12, ha='center', va='center')
        plt.axis('off')  # Turn off the axes
        # Convert the plot to base64
        return self.plot_to_base64(plt)

    def average_failure_plot(self, dataset):
        # Calculate the percentage of failure for each transaction
        dataset['failure_percentage'] = (dataset['status'] == 'Failed').astype(int) * 100
        average_failure_percentage = dataset['failure_percentage'].mean()
        plt.figure(figsize=(4, 1))
        plt.text(0.5, 0.5, f'Average Percentage of Failed Transactions:\n {average_failure_percentage:.2f}%',
                 fontsize=12, ha='center', va='center')
        plt.axis('off')  # Turn off the axes
        # Convert the plot to base64
        return self.plot_to_base64(plt)

    def operator_user_plot(self, users):
        # Plotting the number of users for each operator
        operator_counts = users['phone_operator'].value_counts()
        plt.figure(figsize=(8, 4))
        plt.bar(operator_counts.index, operator_counts.values, color='skyblue')
        plt.xlabel('Phone Operator')
        plt.ylabel('Number of Subscribed Users')
        plt.title('Histogram of Subscribed Users by Phone Operator')
        # Convert the plot to base64
        return self.plot_to_base64(plt)

    def os_plot(self, users):
        # Most used OS for our customers
        users['subscription_date'] = pd.to_datetime(users['subscription_date'])
        plt.figure(figsize=(8, 4))
        sns.countplot(x='os_name', data=users)
        plt.xlabel('OS Name')
        plt.ylabel('Number of Subscribed Users')
        plt.title('Distribution of Subscribed Users by OS Name')
        # Convert the plot to base64
        return self.plot_to_base64(plt)


    def subscription_unsubscription_rate_plot(self, users):
        # Compare subscription and unsubscription rate over time
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
        return self.plot_to_base64(plt)

    def churn_by_operator_plot(self, users):
        # Churn by operators
        churn_by_operator = users.groupby('phone_operator')['unsubscription_date'].count() / \
                            users.groupby('phone_operator')['user_id'].count() * 100
        plt.figure(figsize=(8, 4))
        plt.pie(churn_by_operator, labels=churn_by_operator.index, autopct='%1.1f',
                colors=['skyblue', 'lightcoral', 'lightgreen'])
        plt.title('Churn Rate by Phone Operator')
        # Convert the plot to base64
        return self.plot_to_base64(plt)

    def subscription_duration_distribution_plot(self, users):
        # Subscription durations distribution
        users['subscription_duration'] = users['unsubscription_date'] - users['subscription_date']
        users['subscription_duration_days'] = users['subscription_duration'].dt.days
        plt.figure(figsize=(8, 4))
        plt.hist(users['subscription_duration_days'].dropna(), bins=5, color='skyblue', edgecolor='black')
        plt.xlabel('Subscription Duration (Days)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Subscription Durations')
        # Convert the plot to base64
        return self.plot_to_base64(plt)

    def correlation_matrix_plot(self, dataset):
        # Calculate the correlation matrix
        correlation_matrix = dataset[
            ['subscription_date', 'os_version', 'unsubscription_date', 'transaction_timestamp', 'pricepoint']].corr()
        plt.figure(figsize=(10, 7))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Correlation Matrix')
        # Convert the plot to base64
        return self.plot_to_base64(plt)

    def most_churned_os_versions_plot(self, users):
        # Most churned OS versions
        churn_by_os = users.groupby('os_version')['unsubscription_date'].count() / users.groupby('os_version')[
            'user_id'].count() * 100
        top5_churn_by_oa = churn_by_os.sort_values(ascending=False).head(5)
        plt.figure(figsize=(8, 4))
        # Plot the bar chart for the top 5 OS versions
        top5_churn_by_oa.plot(kind='bar', color='skyblue')
        plt.xlabel('OS version')
        plt.ylabel('Churn Rate (%)')
        plt.title('Top 5 Churn Rates by OS Version')
        # Convert the plot to base64
        return self.plot_to_base64(plt)

    def user_distribution_across_affiliates_plot(self, users):
        # User distribution across affiliates
        affiliate_distribution = users['affiliate'].value_counts()
        plt.figure(figsize=(4, 4))
        plt.pie(affiliate_distribution, labels=affiliate_distribution.index, autopct='%1.1f',
                wedgeprops=dict(width=0.3, edgecolor='w', linewidth=2), colors=['red', 'blue', 'green'])
        plt.title('Distribution of Users Across Affiliates (Donut Chart)')
        # Convert the plot to base64
        return self.plot_to_base64(plt)

    def subscription_rates_by_affiliate_plot(self, users):
        # Subscription rates by affiliate
        subscription_rates = users.groupby('affiliate')['user_id'].count() / len(users) * 100
        plt.figure(figsize=(4, 4))
        plt.pie(subscription_rates, labels=subscription_rates.index, autopct='%1.1f',
                wedgeprops=dict(width=0.3, edgecolor='w', linewidth=2), colors=['red', 'blue', 'green'])
        plt.title('Subscription Rates by Affiliate (Donut Chart)')
        # Convert the plot to base64
        return self.plot_to_base64(plt)

    def subscription_by_service_plot(self, users):
        # Subscription by service point
        plt.figure(figsize=(8, 4))
        sns.countplot(x='service', data=users, palette='viridis')
        plt.title('Distribution of Subscriptions by Service')
        plt.xlabel('Service')
        plt.ylabel('Number of Subscriptions')
        plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
        # Convert the plot to base64
        return self.plot_to_base64(plt)

    def device_preference_by_service_plot(self, users):
        # Device Preference by Service
        plt.figure(figsize=(8, 4))
        sns.countplot(x='service', hue='os_name', data=users, palette='Set2')
        plt.title('Device Preference by Service')
        plt.xlabel('Service/Product')
        plt.ylabel('Number of Subscribers')
        plt.legend(title='Device Preference')
        # Convert the plot to base64
        return self.plot_to_base64(plt)

    def phone_operator_preference_by_service_plot(self, users):
        # Phone Operator Preference by Service
        plt.figure(figsize=(8, 4))
        sns.countplot(x='service', hue='phone_operator', data=users, palette='Set2')
        plt.title('Phone Operator Preference by Service')
        plt.xlabel('Phone Operator')
        plt.ylabel('Number of Subscribers')
        plt.legend(title='Device Preference')
        # Convert the plot to base64
        return self.plot_to_base64(plt)

    def aggregator_vs_operator_distribution_plot(self, users):
        # Aggregator vs. Operator Distribution
        plt.figure(figsize=(8, 4))
        sns.countplot(x='aggregator', hue='phone_operator', data=users, palette='viridis', edgecolor='k')
        plt.title('Aggregator vs. Operator Distribution')
        plt.xlabel('Aggregator')
        plt.ylabel('Number of Subscribers')
        plt.legend(title='Phone Operator')
        # Convert the plot to base64
        return self.plot_to_base64(plt)

    def daily_transaction_success_rate_plot(self, dataset):
        # Daily Transaction Success Rate
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
        return self.plot_to_base64(plt)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the clean data
        data_class = DataCleaner()
        dataset = data_class.clean_data()
        users = dataset['users']
        dataset = dataset['dataset']

        context['subscription'] = self.average_subscription_duration_plot(users)
        context['churn'] = self.churn_rate_plot(users)
        context['failed'] = self.average_failure_plot(dataset)
        context['operator_user'] = self.operator_user_plot(users)
        context['os'] = self.os_plot(users)
        context['rate'] = self.subscription_unsubscription_rate_plot(users)
        context['op_churn'] = self.churn_by_operator_plot(users)
        context['subscription_duration'] = self.subscription_duration_distribution_plot(users)
        context['correlation'] = self.correlation_matrix_plot(dataset)
        context['os_churn'] = self.most_churned_os_versions_plot(users)
        context['affiliates'] = self.user_distribution_across_affiliates_plot(users)
        context['rate_affiliates'] = self.subscription_rates_by_affiliate_plot(users)
        context['sub_affiliates'] = self.subscription_by_service_plot(users)
        context['device'] = self.device_preference_by_service_plot(users)
        context['op_service'] = self.phone_operator_preference_by_service_plot(users)
        context['aggregator'] = self.aggregator_vs_operator_distribution_plot(users)
        context['daily_transaction'] = self.daily_transaction_success_rate_plot(dataset)

        return context

