import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.title("Data App Assignment, due on Oct 6th")
st.write("### Sherelle McDaniel")

st.write("### Input Data and Examples")
df = pd.read_csv("Superstore_Sales_utf8.csv", parse_dates=True)
st.dataframe(df)

# This bar chart will not have solid bars--but lines--because the detail data is being graphed independently
st.bar_chart(df, x="Category", y="Sales")

# Now let's do the same graph where we do the aggregation first in Pandas... (this results in a chart with solid bars)
st.dataframe(df.groupby("Category").sum())
# Using as_index=False here preserves the Category as a column.  If we exclude that, Category would become the datafram index and we would need to use x=None to tell bar_chart to use the index
st.bar_chart(df.groupby("Category", as_index=False).sum(), x="Category", y="Sales", color="#04f")

# Aggregating by time
# Here we ensure Order_Date is in datetime format, then set is as an index to our dataframe
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df.set_index('Order_Date', inplace=True)
# Here the Grouper is using our newly set index to group by Month ('ME')
sales_by_month = df.filter(items=['Sales']).groupby(pd.Grouper(freq='ME')).sum()

st.dataframe(sales_by_month)

# Here the grouped months are the index and automatically used for the x axis
st.line_chart(sales_by_month, y="Sales")

st.write("## My Additions")
# Handle column naming variations defensively ('Sub_Category' vs 'Sub-Category')
subcat_col = "Sub_Category" if "Sub_Category" in df.columns else "Sub-Category"

category_list = df["Category"].unique()
selected_category = st.selectbox("Select a Category:", options=category_list)

# Filter available subcategories based on the chosen category
available_subcats = df[df["Category"] == selected_category][subcat_col].unique()

selected_subcategories = st.multiselect(
    f"Select Sub-Categories in {selected_category}:",
    options=available_subcats,
    default=available_subcats  # Pre-select all so the chart and metrics populate immediately
)

# Filter the dataframe by both selections
filtered_df = df[
    (df["Category"] == selected_category) & 
    (df[subcat_col].isin(selected_subcategories))
]

# Ensure the user has selected at least one subcategory before graphing
if not selected_subcategories:
    st.warning("Please select at least one sub-category to view data.")
else:
    st.write("### Monthly Sales for Selected Sub-Categories")
  
    # Aggregating monthly sales
    filtered_sales_by_month = (
      filtered_df.filter(items=["Sales"])
      .groupby(pd.Grouper(freq="ME"))
      .sum()
    )
    st.line_chart(filtered_sales_by_month, y="Sales")

st.write("### Key Performance Metrics")
    
# Calculations for selected items
selected_sales = filtered_df["Sales"].sum()
selected_profit = filtered_df["Profit"].sum()
selected_margin = (selected_profit / selected_sales * 100) if selected_sales != 0 else 0.0

# Overall baseline calculations (all products across all categories)
total_company_sales = df["Sales"].sum()
total_company_profit = df["Profit"].sum()
overall_company_margin = (
    (total_company_profit / total_company_sales * 100) 
    if total_company_sales != 0 else 0.0
)

# Difference between selected margin and overall company margin
margin_delta = selected_margin - overall_company_margin

# Display using 3 columns
col1, col2, col3 = st.columns(3)

col1.metric(
    label="Total Sales", 
    value=f"${selected_sales:,.2f}"
)
col2.metric(
    label="Total Profit", 
    value=f"${selected_profit:,.2f}"
)
col3.metric(
    label="Overall Profit Margin", 
    value=f"{selected_margin:.2f}%", 
    delta=f"{margin_delta:+.2f}%"
)
