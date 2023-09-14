import pandas as pd
from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

# get live AD.model.csv from adkp/data-models repo
url = "https://raw.githubusercontent.com/adknowledgeportal/data-models/main/AD.model.csv"
model = pd.read_csv(url)

# drop a few columns
model = model.drop(['DependsOn Component', 'Properties', 'Required'], axis = 1)


app_ui = ui.page_fluid(
    ui.input_select(
        "selection_mode",
        "Selection mode",
        {"none": "(None)", "single": "Single", "multiple": "Multiple"},
        selected="multiple",
    ),
    ui.input_switch("fullwidth", "Take full width", True),
    ui.input_switch("fixedheight", "Fixed height", True),
    ui.input_switch("filters", "Filters", True),
    ui.output_data_frame("grid"),
    ui.panel_fixed(
        ui.output_text_verbatim("detail"),
        right="10px",
        bottom="10px",
    ),
    class_="p-3",
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.data_frame
    def grid():
        height = 350 if input.fixedheight() else None
        width = "100%" if input.fullwidth() else "fit-content"
        return render.DataTable(
            model,
            row_selection_mode=input.selection_mode(),
            height=height,
            width=width,
            filters=input.filters(),
        )

    @output
    @render.text
    def detail():
        if (
            input.grid_selected_rows() is not None
            and len(input.grid_selected_rows()) > 0
        ):
            # "split", "records", "index", "columns", "values", "table"
            return model.iloc[list(input.grid_selected_rows())]


app = App(app_ui, server)
