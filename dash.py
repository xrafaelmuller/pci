import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Data Analysis for PCI Changes")

# Open the CSV file
df_with_duplicates = pd.read_csv("data.csv", sep=';', decimal=',')

# Remove duplicates from the 'task' column
df = df_with_duplicates.drop_duplicates(subset=['Task'])

df["Created"] = pd.to_datetime(df["Created"])

df = df.sort_values(by='Created', ascending=True)
df["Month"] = df["Created"].dt.strftime('%B %Y')  # Format the date to 'Month Year'
df["Week"] = df["Created"].dt.strftime('%U %Y')  # Format the date to 'Week Year'

# Sidebar options
option = st.sidebar.selectbox("Graphs", ["Raw Data", "Graphs"])

# Filter options
time_period = st.sidebar.selectbox("Time Period", ["Monthly", "Weekly"])
if time_period == "Monthly":
    time_column = "Month"
    time_format = '%B %Y'
    time_options = ["All"] + sorted(list(df["Month"].unique()), key=lambda x: pd.to_datetime(x))
else:
    time_column = "Week"
    time_format = '%U %Y'
    time_options = ["All"] + sorted(list(df["Week"].unique()))

if time_period == "Monthly":
    time_selection = st.sidebar.selectbox(f"Select Month", sorted(time_options))
else:
    time_selection = st.sidebar.selectbox(f"Select Week", sorted(time_options))

# Filter by creator
creator_options = ["All"] + list(df["Created by"].unique())

# Control the visibility of the "Select Change Coordinator" dropdown
if time_selection != "All":
    creator = "All"
else:
    creator = st.sidebar.selectbox("Select Change Coordinator", creator_options)

# Filter the dataframe based on the selected time period and creator
if time_selection == "All" and creator == "All":
    df_filtered = df
elif time_selection == "All":
    df_filtered = df[df["Created by"] == creator]
elif creator == "All":
    df_filtered = df[df[time_column] == time_selection]
else:
    df_filtered = df[(df[time_column] == time_selection) & (df["Created by"] == creator)]

# Display the filtered dataframe based on the selected option
if option == "Raw Data":
    st.write(df_filtered)

elif option == "Graphs":
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    c5, c6 = st.columns(2)

    type_counts = df_filtered['Type'].value_counts()

    pie_chart = px.pie(names=type_counts.index, values=type_counts.values, title="Types of Changes based on the selection")
    pie_chart.update_traces(textinfo='percent+label')
    c1.plotly_chart(pie_chart)


    pie_chart2 = px.pie(df_filtered, names='State', color="State", title="State")
    
    # Add count labels inside the pie chart
    pie_chart2.update_traces(textinfo='percent+label')
    
    c2.plotly_chart(pie_chart2)

    # Bar chart for top offender application name
    top_offender_applications = df_filtered['Application Name'].value_counts().nlargest(10)
    bar_chart = px.bar(top_offender_applications, x=top_offender_applications.index, y=top_offender_applications.values, labels={'x':'Rank Application Name', 'y':'Count'}, title="Rank by Application Names")
    c3.plotly_chart(bar_chart)

    # Line chart for peak by month
    monthly_counts = df_filtered['Month'].value_counts().sort_index()
    bar_chart_peak = px.line(monthly_counts, x=monthly_counts.index, y=monthly_counts.values, labels={'x':'Month', 'y':'Count'}, title="Peak by Month")
    c5.plotly_chart(bar_chart_peak)

    # Grouped bar chart for peak by month and type
    if time_period == "Monthly":
        grouped_counts = df_filtered.groupby(['Month', 'Type']).size().reset_index(name='Count')
    else:
        grouped_counts = df_filtered.groupby(['Week', 'Type']).size().reset_index(name='Count')

    # Bar chart for rank by record types
# Grouped bar chart for rank by application name and type
    grouped_applications = df_filtered.groupby(['Application Name', 'Type']).size().reset_index(name='Count')
    bar_chart_grouped_applications = px.bar(grouped_applications, x='Application Name', y='Count', color='Type', barmode='group', title="Rank by Application Names and Types")
    c4.plotly_chart(bar_chart_grouped_applications)


    
    bar_chart_grouped = px.bar(grouped_counts, x=time_column, y='Count', color='Type', barmode='group', title="Peak by Month and Type")
    c6.plotly_chart(bar_chart_grouped)

    if time_selection == "All" and creator == "All":
        # Calculate the average count of records per selected time period
        average_per_period = df_filtered.groupby(time_column)['Type'].count().mean()
    
        # Display the average count per period with reduced decimals
        st.subheader(f"Average of Change Records per {time_period}")
        st.info(f"{average_per_period:.0f}")  # Adjust decimal precision here
    
        # Display the count of records in each period for each type
        types = df_filtered['Type'].unique()

        # Display the counts in boxes separated by type
        st.subheader(f"Count of Change Records in Each {time_period} by Type")
        for type in types:
            st.subheader(f"{type}")
            type_filtered = df_filtered[df_filtered['Type'] == type]
            period_counts = type_filtered[time_column].value_counts().sort_index().reset_index()
            period_counts.columns = [time_period, 'Count']
            period_counts = period_counts.sort_values(by=time_period, key=lambda x: pd.to_datetime(x, format='%U %Y') if time_period == "Week" else pd.to_datetime(x, format='%B %Y'))
            period_count_dict = dict(zip(period_counts[time_period], period_counts['Count']))
            for period, count in period_count_dict.items():
                st.info(f"{period}: {count}")
