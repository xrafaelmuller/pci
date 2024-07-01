import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
file_path = 'task_ci.xlsx'
data = pd.read_excel(file_path)

# Group by Task and Environment
task_env_table = data.groupby(['Task', 'Used for Environment']).size().unstack(fill_value=0)

# Plot quantity of tasks per environment
task_counts = data['Used for Environment'].value_counts()

# Calculate exclusive tasks
exclusive_tasks = data.groupby('Task')['Used for Environment'].nunique()
exclusive_task_list = exclusive_tasks[exclusive_tasks == 1].index.tolist()
exclusive_task_env = data[data['Task'].isin(exclusive_task_list)][['Task', 'Used for Environment']].drop_duplicates()

# Streamlit App
st.title('Task Environment Analysis')

# Display Task Environment Table
st.subheader('Used for Environment Table per Task')
st.dataframe(task_env_table)

# Display Quantity of Tasks for Environment
st.subheader('Quantity of CIs per Environment')
fig, ax = plt.subplots()
task_counts.plot(kind='bar', ax=ax)
ax.set_xlabel('Environment')
ax.set_ylabel('Number of CIs')
ax.set_title('Quantity of CIs per Environment')
st.pyplot(fig)

# Display Count of Exclusive Tasks
st.subheader('Count of Exclusive Tasks')
st.write(f'There are {len(exclusive_task_list)} tasks that are exclusive to one environment.')

# Display Exclusive Tasks and their Environments
st.subheader('Exclusive Tasks and their Environments')
st.dataframe(exclusive_task_env)
