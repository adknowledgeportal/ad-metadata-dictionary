import pandas as pd
from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

# get live AD.model.csv from adkp/data-models repo
#url = "https://raw.githubusercontent.com/adknowledgeportal/data-models/main/AD.model.csv"
model_df = pd.read_csv("AD.model.csv")

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

merged_df = merged_df[["Key", 
                      "Key Type",
                      "Key Description",
                      "Value",
                      "Value Description",
                      "Source"]]

# sort alphabetically
sorted_df = merged_df.sort_values(by = ["Key", "Value"], 
                                  kind = "mergesort",
                                  ascending = True,
                                  key = lambda col: col.str.lower())

# make clickable urls in source column

# wrap urls in source column (27 is length of purl obo)
#sorted_df["Source"] = sorted_df["Source"].str.wrap(width = 27, break_long_words=True, drop_whitespace=False)

# app ui
app_ui = ui.page_fluid(
    ui.h1("Search the AD Knowledge Portal Data Model Dictionary"),
    ui.row(
        ui.column(11, ui.output_data_frame("grid"))
    ),
    class_="p-4"
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.data_frame
    def grid():
       return render.DataGrid(
            sorted_df,
            height=600,
            width="fit-to-content",
            filters=True,
            summary=True
        )


app = App(app_ui, server)
