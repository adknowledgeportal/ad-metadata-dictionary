import pandas as pd
from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

# get live AD.model.csv from adkp/data-models repo
url = "https://raw.githubusercontent.com/adknowledgeportal/data-models/main/AD.model.csv"
model_df = pd.read_csv(url)

# remove template rows
model_df = model_df.loc[model_df["Parent"] != "DataType"]

# pull out "key" attributes
keys_df = model_df.loc[model_df["Parent"] == "DataProperty"]

#rename key columns
keys_df = keys_df.rename(columns = {"Attribute" : "Key",
                          "Description" : "Key Description",
                          "columnType" : "Key Type"})
keys_df = keys_df[["Key", "Key Description", "Key Type"]]

# pull out "value" attributes
values_df = model_df.loc[model_df["Parent"].isin(keys_df["Key"])]

# rename columns
values_df = values_df.rename(columns = {"Attribute" : "Value",
                          "Description" : "Value Description"})
values_df = values_df[["Value", "Value Description", "Source", "Parent"]]

# join keys and values
merged_df = values_df.merge(
    keys_df,
    how = "left", 
    left_on = "Parent", 
    right_on = "Key")

merged_df =merged_df[["Key",
           "Key Description",
           "Value",
           "Value Description",
           "Source",
           "Key Type"]]

# sort alphabetically
sorted_df = merged_df.sort_values(by = ["Key", "Value"], 
                                  kind = "mergesort",
                                  ascending = True,
                                  key = lambda col: col.str.lower())


# app ui
app_ui = ui.page_fluid(
    ui.h1("Search the AD Knowledge Portal Data Model Dictionary"),
    ui.output_data_frame("grid"),
    class_="p-3"
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.data_frame
    def grid():
       return render.DataGrid(
            sorted_df,
            height=500,
            width="100%",
            filters=True,
            summary=True
        )


app = App(app_ui, server)
