# STEP 1 : IMPORTING AND LOADING THE DATA SETS---

import pandas as pd
import numpy as np

print("...EXTRACT DATA...")

sales = pd.read_csv("C:/Users/karthik reddy/OneDrive/Desktop/AdventureWorks/AdventureWorks_Sales_2017.csv")
customer = pd.read_csv("C:/Users/karthik reddy/OneDrive/Desktop/AdventureWorks/AdventureWorks_Customers.csv",encoding = 'latin1')
product = pd.read_csv("C:/Users/karthik reddy/OneDrive/Desktop/AdventureWorks/AdventureWorks_Products.csv")
territories = pd.read_csv("C:/Users/karthik reddy/OneDrive/Desktop/AdventureWorks/AdventureWorks_Territories.csv")

print(f"Successfully loaded sales: {len(sales)}")
print(f"Successfully loaded customer: {len(customer)}")
print(f"Successfully loaded product : {len(product)}")
print(f"Successfully loaded Territories: {len(territories)}")


# STEP 2 : INSPECTING THE SALES AND CUSTOMER DATA SETS---

print("\n....2.INSPECTING DATA....")
def inspect_data(df, table_name):
    print(f"\n===============================================")
    print(f"          INSPECTING : {table_name.upper()}")
    print(f"\n===============================================")

    print("\n----1. FIRST 5 ROWS-----")
    print(df.head())

    print("\n---2. SHAPE (ROWS AND COLUMS)---")
    print(df.shape)

    print("\n ----3. SCHEMA AND DATA TYPE---")
    df.info()

    print("\n---4. MISSING VALUES-----")
    print(df.isnull().sum())

    print("\n---5. SUMMARY STATES----")
    print(df.describe())
    
inspect_data(sales,"Sales Table")
inspect_data(customer,"Customer Table")


# STEP 3 : TRANSFORMING AND CLEANING THE DATA SETS---

sales["OrderDate"] = pd.to_datetime(sales["OrderDate"])
sales["StockDate"] = pd.to_datetime(sales["StockDate"])
customer["BirthDate"] = pd.to_datetime(customer["BirthDate"])

customer["Gender"] = customer["Gender"].replace({"M":"Male" , "F":"Female"})
customer["MaritalStatus"] = customer["MaritalStatus"].replace({"M":"Married", "S":"Single"})

def calculate_age(birthdate):
    try:
        return 2017 - birthdate.year
    except Exception:
        return np.NaN

customer["Age"] = customer["BirthDate"].apply(lambda d: calculate_age(d))

customer["Prefix"] = customer["Prefix"].fillna("")
customer["Fullname"] = customer["Prefix"] + "" + customer["FirstName"] + "" + customer["LastName"]
customer["Fullname"] = customer["Fullname"].str.strip()           # Removes extra space 

df_merged = pd.merge(sales,product[["ProductKey","ProductName","ProductCost","ProductPrice"]],
                    on="ProductKey",
                    how="inner"
)

df_merged = pd.merge(
    df_merged,customer[["CustomerKey","Fullname", "Age", "Gender", "MaritalStatus", "AnnualIncome"]],
    on = "CustomerKey",
    how = "left"
)

df_merged = pd.merge(
    df_merged,territories[["SalesTerritoryKey", "Region", "Country"]],
    left_on = "TerritoryKey",
    right_on = "SalesTerritoryKey",
    how = "left"
)

df_merged["TotalRevenue"] = df_merged["OrderQuantity"] * df_merged["ProductPrice"]
df_merged["TotalCost"] = df_merged["OrderQuantity"] * df_merged["ProductCost"]
df_merged["GrossProfit"] = df_merged["TotalRevenue"] * df_merged["TotalCost"]

columns_to_drop = ["ProductKey", "CustomerKey", "TerritoryKey", "SalesTerritoryKey"]
df_final = df_merged.drop(columns=columns_to_drop)

print(df_final[["OrderDate", "Fullname", "Region", "TotalRevenue", "GrossProfit"]].head(5))
print(df_final[["Gender"]].head())


# LOADING THE DATA TO THE SALES FILE---

output_file = "C:/Users/karthik reddy/OneDrive/Desktop/AdventureWorks/AdventureWorks_Sales_2017.csv"

try:
    df_final.to_csv(output_file, index=False)
    print(f"SUCCESS: Curated dataset saved locally to '{output_file}'.")
except Exception as e:
    print(f"Error saving the file: {e}")



# LOADING THE CORRECTED DATA--

import matplotlib.pyplot as plt
print("Loading corrected dataset....")
df = pd.read_csv( "C:/Users/karthik reddy/OneDrive/Desktop/AdventureWorks/AdventureWorks_Sales_2017.csv")
df["OrderDate"] = pd.to_datetime(df["OrderDate"])


# QUESTION 1 : FINDING THE MONTHELY REVENUE TREND---

monthly_revenue = df.groupby(df["OrderDate"].dt.to_period("M"))["TotalRevenue"].sum()

plt.figure(figsize=(10, 5))
plt.plot(monthly_revenue.index.to_timestamp(), monthly_revenue.values, 
         marker='o', color='#2ca02c', linewidth=2.5)

plt.title("Monthly Revenue Trend (2017)", fontsize=14, fontweight="bold")
plt.xlabel("Month", fontsize=11)
plt.ylabel("Total Revenue ($)", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()



# QUESTION 2 : FINDING THE TOP 5 PRODUCTS BY GROSS PROFIT---

top_products = df.groupby("ProductName")["GrossProfit"].sum().sort_values(ascending=False).head(5)

plt.figure(figsize=(10, 5))
top_products.plot(kind="barh", color="#1f77b4", edgecolor="black")

plt.title("Top 5 Products by Gross Profit", fontsize=14, fontweight="bold")
plt.xlabel("Gross Profit ($)", fontsize=11)
plt.ylabel("Product Name", fontsize=11)
plt.gca().invert_yaxis() # Flips the chart so the #1 product is at the very top
plt.grid(axis="x", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()


# QUESTION 3 : FINDING TOTAL REVENUE BY COUNTRY---

country_revenue = df.groupby("Country")["TotalRevenue"].sum().sort_values(ascending=False)

plt.figure(figsize=(9, 5))
country_revenue.plot(kind="bar", color="#ff7f0e", edgecolor="black")

plt.title("Total Revenue by Country", fontsize=14, fontweight="bold")
plt.xlabel("Country", fontsize=11)
plt.ylabel("Total Revenue ($)", fontsize=11)
plt.xticks(rotation=45) # Tilts the country names so they don't overlap
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()


# QUESTION 4 : FINDING THE REVENUE BREAKDOWN BY CUSTOMER AGE GROUP---

bins = [18, 25, 35, 50, 100]
labels = ["18-25 (Gen Z)", "26-35 (Millennials)", "36-50 (Gen X)", "50+ (Boomers)"]


df["AgeGroup"] = pd.cut(df["Age"], bins=bins, labels=labels, right=True)


age_revenue = df.groupby("AgeGroup")["TotalRevenue"].sum()

plt.figure(figsize=(8, 8))

age_revenue.plot(
    kind="pie", 
    autopct="%1.1f%%",       # Shows percentage with one decimal
    startangle=140,          # Rotates the chart for better visual balance
    colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"], # Custom clean colors
    ylabel="",               # Hides the default y-axis label
)

plt.title("Revenue Breakdown by Customer Age Group", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.show()
