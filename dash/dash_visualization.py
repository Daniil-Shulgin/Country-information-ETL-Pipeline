import pandas as pd
import sys
import logging
from dash import Dash, dash_table, html, Input, Output
from sqlalchemy import create_engine
from typing import List, Optional, Dict, Any
from dash.development.base_component import Component

# Logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dash.log", mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Connecting to the database
DB_URL = "postgresql://user:password@localhost:5432/countries_db"
engine = create_engine(DB_URL)

# Reading data
def get_data() -> pd.DataFrame:
    """
    Reading data from a database for display in a table
    """
    try:
        logging.info("Reading data from a database...")
        query = "SELECT * FROM countries"
        with engine.connect() as con:
            df = pd.read_sql(query, con)
            logging.info(f"Data loaded successfully. Rows: {len(df)}")
            return df
    except Exception as e:
        logging.error(f"Error reading from database: {e}")
        return pd.DataFrame()

df = get_data()

# Init dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Table of countries", style={'textAlign': 'center', 'fontFamily': 'sans-serif'}),
    
    html.Div([
        html.Div([
            dash_table.DataTable(
                id='datatable-interactivity',
                columns=[
                    {"name": i.replace('_', ' ').title(), "id": i} 
                    for i in df.columns if i != 'flag_url_png'
                ],
                data=df.to_dict('records'),
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                row_selectable="single",
                selected_rows=[0],
                page_action="native",
                page_current=0,
                page_size=17,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'fontFamily': 'sans-serif'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
            ),
        ], style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            html.H3("Flag of the selected country", style={'textAlign': 'center', 'fontFamily': 'sans-serif'}),
            html.Div(id='flag-container', style={'textAlign': 'center', 'marginTop': '30px'})
        ], style={'width': '25%', 'display': 'inline-block', 'marginLeft': '4%'})
    ], style={'display': 'flex', 'padding': '20px'})
])

@app.callback(
    Output('flag-container', 'children'),
    Input('datatable-interactivity', 'derived_virtual_data'),
    Input('datatable-interactivity', 'derived_virtual_selected_rows')
)
def update_flag(
    rows: Optional[List[Dict[str, Any]]], 
    selected_rows: Optional[List[int]]
) -> Component:
    """
    Updates the flag component when a new row is selected
    """
    if rows is None or selected_rows is None or len(selected_rows) == 0 or len(rows) == 0:
        return html.P("Select a country from the table")
    
    try:
        selected_row_data: Dict[str, Any] = rows[selected_rows[0]]
        flag_url: Optional[str] = selected_row_data.get('flag_url_png') 
        country_name: str = selected_row_data.get('common_name', 'Unknown')

        if not flag_url:
            message_not_flag = f"Flag for the country {country_name} is missing from the data."
            logging.warning(message_not_flag)
            return html.P(message_not_flag)

        return html.Div([
            html.Img(src=flag_url, style={'width': '100%', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)'}),
            html.P(f"Country: {country_name}", style={'marginTop': '15px', 'fontWeight': 'bold'})
        ])
    except Exception as e:
        message_error = f"Error updating flag: {e}"
        logging.error(message_error)
        return html.P(message_error)

if __name__ == '__main__':
    app.run(debug=True)