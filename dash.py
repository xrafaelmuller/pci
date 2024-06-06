import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Data Analysis for PCI Changes")

# Abrir o arquivo CSV
df = pd.read_csv("data.csv", sep=';', decimal=',')

df["Created"] = pd.to_datetime(df["Created"])

df = df.sort_values(by='Created', ascending=True)
df["Month"] = df["Created"].dt.strftime('%B %Y')  # Format the date to 'Month Year'

# Sidebar options
option = st.sidebar.selectbox("Graphs", ["Raw Data", "Graphs"])

# Filter options
month_options = ["All"] + list(df["Month"].unique())
month = st.sidebar.selectbox("Select Month", month_options)

# Filter by creator
creator_options = ["All"] + list(df["Created by"].unique())

# Control the visibility of the "Select Change Coordinator" dropdown
if month is not "All":
    creator = "All"
else:
    creator = st.sidebar.selectbox("Select Change Coordinator", creator_options)

# Filter the dataframe based on the selected month and creator
if month == "All" and creator == "All":
    df_filtered = df
elif month == "All":
    df_filtered = df[df["Created by"] == creator]
elif creator == "All":
    df_filtered = df[df["Month"] == month]
else:
    df_filtered = df[(df["Month"] == month) & (df["Created by"] == creator)]

# Display the filtered dataframe based on the selected option
if option == "Raw Data":
    st.write(df_filtered)

elif option == "Graphs":
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    pie_chart = px.pie(df_filtered, names='Type', color="Type", title="Types of Changes based on the selection")
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

    if month == "All" and creator == "All":
        # Calculate the average count of records per month
        average_per_month = df_filtered.groupby('Month')['Type'].count().mean()
    
        # Display the average count per month with reduced decimals
        st.subheader("Average of Change Records per Month")
        st.info(f"{average_per_month:.0f}")  # Adjust decimal precision here
    
        # Display the count of records in each month for each type
        types = df_filtered['Type'].unique()

        # Display the counts in boxes separated by type
        st.subheader("Count of Change Records in Each Month by Type")
        for type in types:
            st.subheader(f"{type}")
            type_filtered = df_filtered[df_filtered['Type'] == type]
            month_counts = type_filtered['Month'].value_counts().reset_index()
            month_counts.columns = ['Month', 'Count']
            month_count_dict = dict(zip(month_counts['Month'], month_counts['Count']))
            for month, count in month_count_dict.items():
                st.info(f"{month}: {count}")
