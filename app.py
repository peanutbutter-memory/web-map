"""Dash geo-spatial web application

"""


import ast
import os
import sys
from datetime import date
import subprocess
import diskcache

from dash import Dash, html, dcc, callback, Output, Input, dash_table, no_update
from dash.long_callback import DiskcacheLongCallbackManager
import plotly.express as px
import dash_bootstrap_components as dbc

import pandas as pd
import geopandas as gpd
import dash_leaflet as dl
import json
from dash_extensions.javascript import arrow_function

from flask import Flask, render_template, send_from_directory

CONTACT_EMAIL = os.environ["CONTACT_EMAIL"]
DEPLOY_STATUS = os.environ["DEPLOY_STATUS"]
print(f"Deploy status is {DEPLOY_STATUS}")
PORT = os.environ["PORT"]
DEBUG_STATUS = os.environ["DEBUG_STATUS"]
ML_MODEL_PATH = os.environ["ML_MODEL_PATH"]
CHANGE_DETECTION_SCRIPT = os.environ["CHANGE_DETECTION_SCRIPT"]
ML_RESULTS_PATH = os.environ["ML_RESULTS_PATH"]

# Diskcache for long callbacks
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

external_stylesheets = [dbc.themes.CERULEAN, dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME]

server = Flask(__name__)


app = Dash(__name__,
            requests_pathname_prefix="/app/WEB/",
            routes_pathname_prefix="/app/WEB/",
            external_stylesheets=external_stylesheets,
            server=server)

ASSETS_DIRECTORY = "/blob"

sites_metadata = "/blob/assets/sites/sites.geojson"
print(f"Site metadata being used is {sites_metadata}")

@server.route("/app/WEB/maptiles/<path:location>/<z>/<x>/<y>.png")
def serve_tiles(location, z, x, y):
    """Serve tilemaps for dash_leaflet map component
    """

    url = f"{location}/tiles/{z}/{x}/{y}.png"

    return send_from_directory(ASSETS_DIRECTORY, url)


imagery_metadata = gpd.read_file(sites_metadata)
# do not convert datetime into datetime objects; retain as strings. avoids hanlding timestamps
imagery_metadata["DATETIME"] = imagery_metadata["DATETIME"].astype(str)
imagery_metadata.columns = imagery_metadata.columns.str.lower()
# convert "webmap_centre" from string to list
imagery_metadata["webmap_center"] = imagery_metadata["webmap_center"].apply(ast.literal_eval)

# provide data in dict format that is compatible with dash_leaflet
geojson_bboxes = imagery_metadata.__geo_interface__
print(f"Imagery metadata: {imagery_metadata}")

# generate df for dash_table; gdf not compatible with dash_table
imagery_metadata_dashtable = imagery_metadata.drop(columns=["geometry", "geotiff_path", "tilemaps_path", "webmap_center", "webmap_zoom", "crs", "notes"])
imagery_metadata_dashtable.columns = imagery_metadata_dashtable.columns.str.title()

# ==========

initial_map_center_mapload = [59.4604, -104.45483]
available_algorithms = imagery_metadata["algorithm"].unique()

# == home page content ==
home_page_content_introduction = dcc.Markdown("""
# Welcome to our application
                                    
`Showing placeholder content for now. This will be updated shortly`

Suspendisse cursus tellus neque, at accumsan tortor imperdiet non. Donec porta mollis eros. Vestibulum dictum gravida sapien, eu ornare magna laoreet nec. Fusce eget interdum nibh, id placerat massa. Duis id purus ante. Etiam lobortis nec lectus id tincidunt. Sed consequat sit amet sem vitae rhoncus. Vivamus imperdiet nunc tincidunt lectus vestibulum sodales in eget leo. Nam congue efficitur facilisis. Maecenas quis mattis erat, eget ullamcorper arcu. Aliquam tincidunt commodo ex vel porttitor. Nunc elementum imperdiet vulputate. Suspendisse accumsan sodales nunc, eu pellentesque justo posuere ut.

""")

home_page_content_high_res_detection = dcc.Markdown("""
## High Resolution Object Detection

"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

""")                                    

home_page_content_coastal_scanning = dcc.Markdown("""
## Coastal Scanning with Sentinel-2                                 

Nullam nisi sapien, gravida eu mauris sed, mollis condimentum neque. Proin turpis nisl, varius at interdum sit amet, maximus id nibh. Cras pretium volutpat fringilla. Suspendisse dapibus, lectus quis suscipit sagittis, dolor est elementum sem, vel vestibulum turpis nisi at augue. Phasellus quis sollicitudin nisi. Cras hendrerit tortor varius justo tincidunt, sed varius felis vestibulum. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam mattis consectetur lectus, non blandit odio ullamcorper in. Nunc ornare augue lorem, et pulvinar enim scelerisque in. Nam vitae est tortor. Pellentesque varius tellus felis, sit amet egestas risus consequat sed. Donec aliquam ante eget arcu efficitur viverra. Donec quis ullamcorper tellus.

""")

# =====

# == landing page ==
home_page = dbc.Container([
    html.Div([
    home_page_content_introduction,
    html.Br(), html.Br(),
    home_page_content_high_res_detection,
    html.Br(), html.Br(),
    home_page_content_coastal_scanning,
    html.Br(), html.Br(),
], style={'textAlign': 'left', 'padding': '50px'})
], fluid=False)

# =====

# == control to run ml algorithm 
ml_algorithm_initiation = html.Div(
    [   
        html.Div([html.P(id="id-start-ml-algorithm", children=["Button not clicked"])]),
        dbc.Button("Execute ML algorithm", id="id-run-selected-algorithm", n_clicks=0, disabled=False),
    ]
)

# drives navigation
# auto hides
sidebar_page = html.Div(
    [
        html.Div(
            [
                html.H3("TC NAST", style={"color": "blue"}),
            ],
            className="sidebar-header",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    [html.I(className="fas fa-home me-2"), html.Span("Home")],
                    href="/home",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-solid fa-map me-2"),
                        html.Span("Map"),
                    ],
                    href="/map",
                    active="exact",
                ),

                dbc.NavLink(
                    [
                        html.I(className="fas fa-solid fa-database me-2"),
                        html.Span("Data"),
                    ],
                    href="/data",
                    active="exact",
                ),

                dbc.NavLink(
                    [
                        html.I(className="fas fa-envelope-open-text me-2"),
                        html.Span("Contact Us"),
                    ],
                    href=f"mailto:{CONTACT_EMAIL}",
                    active="exact",
                ),

                dbc.NavLink(
                    [
                        html.I(className="fas fa-solid fa-info me-2"),
                        html.Span("Help"),
                    ],
                    href="/help",
                    active="exact",
                ),

            ],
            vertical=True,
            pills=True,
        ),
    ],
    className="sidebar",
)

help_page_content = dcc.Markdown("""
## Help

"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

""")   

help_page = dbc.Container([
    html.Div([
    help_page_content,
    html.Br(), html.Br(),
], style={'textAlign': 'left', 'padding': '50px'})
], fluid=False)


# == Map page ==
map_page = dbc.Container([
    sidebar_page,
    dbc.Row(html.Br()),

    dbc.Row([
            dcc.Dropdown(
                id="id-algorithm-dropdown",
                clearable=False,
                options=[{"label": algorithm, "value": algorithm} for algorithm in available_algorithms],
                placeholder="Select an algorithm to begin...."
            ),
            dcc.Dropdown(
                id="id-location-dropdown",
                clearable=False,
                placeholder="Select a site location..."),

 ]),

    dbc.Row(
        [dbc.Col(dcc.Dropdown(
                id="id-change-selection-startdate",
                clearable=True,
                placeholder="Select start date for algorithm")),
        
        dbc.Col(dcc.Dropdown(
                id="id-change-selection-enddate",
                clearable=True,
                placeholder="Select end date for algorithm"))

        ], id="id-row-algorithm-dropdown-for-date-selection"),
    
    dbc.Row([
        dbc.Col(ml_algorithm_initiation),
        dbc.Col(dcc.Dropdown(id="id-datetime-for-imagery_tilemap", clearable=False, placeholder="Select date for imagery tilemap")),
            ]),

    # == web map
    dbc.Row(dl.Map(center=initial_map_center_mapload, zoom=4, 
                   children=[
            # Group tilemaps and overlays into single control present on the map
            dl.LayersControl(
                position="topright", 
                id="id-map-layers-control",
                collapsed=False,
                children=[
                    # Default base map with OSM tiles
                    dl.BaseLayer(
                        dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", attribution="(C) OpenStreetMap contributors"),
                        name="Open Street Map",
                        # Visible by default
                        checked=True
                    ),
                    # ESRI World Imagery tiles for user to select
                    dl.BaseLayer(
                        dl.TileLayer(url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png", attribution="Tiles (C) Esri -- Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"),
                        name="ESRI World Imagery",
                        # Visible by default
                        checked=False
                    ),
                    
                    # Generated imagery tilemaps
                    dl.Overlay(
                        dl.TileLayer(id="id-satellite-tilemap-layer"),
                        name="Show Satellite Imagery Tiles",
                        checked=True),
                    
                    # ML model results
                    dl.Overlay(
                        dl.GeoJSON(id="id-ml-model-results-polygons"),
                        name="Show ML Model Results",
                        checked=True),

                    # Imagery bboxes
                    dl.Overlay(
                        dl.GeoJSON(data=geojson_bboxes, id="id-imagery-bbox-polygons",
                            zoomToBounds=False,
                            zoomToBoundsOnClick=True,
                            hoverStyle=arrow_function(dict(weight=5, color="#666", dashArray=""))),
                        name="Imagery Bounding Boxes",
                        checked=False),
                                                
                            ]
                        )
                                    
                        ], id="id-web-map", style={"height": "75vh"})),
    
    
], fluid=False)

# == data page ==
data_page_content = dcc.Markdown("""
## Data
                                 
Add content and descriptions here.......
""")

data_page = dbc.Container([
    html.Div([
    data_page_content,
    html.Br(), html.Br(),
    dbc.Row([
    dash_table.DataTable(imagery_metadata_dashtable.to_dict("records"),              
                             id="id-imagery-metadata-table", fixed_rows={"headers": True}, #style_table={"height": "200px", "overflowY": "auto"},
                             style_cell={"textAlign": "left"}),
    ]),

], style={'textAlign': 'left', 'padding': '50px'})
], fluid=False)


# =====
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar_page,
    html.Div(id='page-content')
])

# == handle which page to route too
@callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/map':
        return map_page
    elif pathname == '/home':
        return home_page
    elif pathname == '/help':
        return help_page
    elif pathname == '/data':
        return data_page
    else:
        return no_update

# == get feature data when user clicks on a geojson bbox
@callback(
    Output("id-user-selected-bbox-polygon", "children"),
    Input("id-imagery-bbox-polygons", "clickData"),
    Input("id-imagery-bbox-polygons", "n_clicks"),
    prevent_initial_call=True
)
def get_id_of_imagery_bbox_selected(feature, n_clicks):
    print(feature)
    if feature is not None:
        polygon_id = feature["id"]
        
        if DEBUG_STATUS: print(f"Feature clicked: {polygon_id}")
        return polygon_id
    else:
        if DEBUG_STATUS: print("No feature clicked")
        return "Selected Polygon ID: None"

# == show hover tip data when user hovers over a geojson bbox
@callback(
    Output("hover-geojson-tooltip", "children"),
    Input("id-imagery-bbox-polygons", "hoverData"),
    prevent_initial_call=True
)
def display_bbox_hover_data(feature):
    if feature is not None:
        if DEBUG_STATUS: return f"Hovering over: {feature['properties']}"
    else:
        return []

# == Select site location dropdown
@callback(
    Output("id-location-dropdown", "options"),
    Output("id-location-dropdown", "value"),
    Input("id-algorithm-dropdown", "value"),
    prevent_initial_call=True
)
def update_site_locations_dropdown(selected_algorithm):
    if selected_algorithm:    
        sites = imagery_metadata[imagery_metadata["algorithm"] == selected_algorithm]["sitename"].unique()
        
        site_options = [{'label': site, 'value': site} for site in sites]

        if DEBUG_STATUS: print(f"Site options: {site_options}")
        
        # None will forces the user to select a site location
        return site_options, None
    else:
        return no_update, no_update


@callback(
    Output("id-datetime-for-imagery_tilemap", "options"),
    Output("id-datetime-for-imagery_tilemap", "value"),
    Output("id-change-selection-startdate", "multi"),
    Output("id-change-selection-startdate", "options"),
    Output("id-change-selection-startdate", "value"),
    Output("id-change-selection-enddate", "multi"),
    Output("id-change-selection-enddate", "options"),
    Output("id-change-selection-enddate", "value"),
    Input("id-algorithm-dropdown", "value"),
    Input("id-location-dropdown", "value"),
    prevent_initial_call=True)
def set_imagery_dates_available_change_detection(selected_algorithm, selected_location):
    """Update dates for change detection and object detecton date dropdown controls with available imagery dates 

    Change detection provides start and end dates for change detection
    Object detection provides a single date for object detection in the 'start date' only.

    `value` is the UUID of the image
    """
    
    if DEBUG_STATUS: print(f"INFO -- Entered set_imagery_dates_available_change_detection(): {selected_algorithm}, {selected_location}")

    if selected_algorithm == "Change" and selected_location: 
        site_metadata = imagery_metadata[
            (imagery_metadata["sitename"] == selected_location) & 
            (imagery_metadata["algorithm"] == selected_algorithm)
        ]
        
        if DEBUG_STATUS: print(f"Imagery metadata found -- {type(site_metadata)}")

        imagery_dates = site_metadata["datetime"].astype(str).tolist()
        imagery_uuids = site_metadata["uuid"].tolist()

        print(f"Imagery dates: {type(imagery_dates)}")
        print(f"Imagery uuids: {type(imagery_uuids)}")

        results = zip(imagery_uuids, imagery_dates)
        drop_drown_label_values = [{"label": date, "value": uuid} for uuid, date in results]

        if DEBUG_STATUS: print(f"INFO -- Leaving set_imagery_dates_available_change_detection(): updated 'change detection' returned {drop_drown_label_values}")

        return drop_drown_label_values, None, True, drop_drown_label_values, None, True, drop_drown_label_values, None

    if selected_algorithm == "Detection" and selected_location:
        site_metadata = imagery_metadata[
            (imagery_metadata["sitename"] == selected_location) & 
            (imagery_metadata["algorithm"] == selected_algorithm)
        ]
        
        if DEBUG_STATUS: print(f"Imagery metadata found -- {type(site_metadata)}")

        imagery_dates = site_metadata["datetime"].astype(str).tolist()
        imagery_uuids = site_metadata["uuid"].tolist()

        print(f"Imagery dates: {type(imagery_dates)}")
        print(f"Imagery uuids: {type(imagery_uuids)}")

        results = zip(imagery_uuids, imagery_dates)
        drop_drown_label_values = [{"label": date, "value": uuid} for uuid, date in results]

        if DEBUG_STATUS: print(f"INFO -- Leaving set_imagery_dates_available_change_detection(): updated 'change detection' returned {drop_drown_label_values}")

        return drop_drown_label_values, None, True, drop_drown_label_values, None, False, no_update, None


    else:
        return no_update, None, False, no_update, None, False, no_update, None


# == Run ml execution via button press
@app.long_callback(
    Output("id-ml-model-results-polygons", "url"),
    Output("id-start-ml-algorithm", "children"),
    Input("id-run-selected-algorithm", "n_clicks"),
    Input("id-algorithm-dropdown", "value"),
    Input("id-location-dropdown", "value"),
    Input("id-change-selection-startdate", "value"),
    Input("id-change-selection-enddate", "value"),
    manager=long_callback_manager
)
def start_ml_algorithm(run, selected_algorithm, selected_location, start_date_uuid, end_date_uuid):
    """Enable button to call algorithm for selected location
    
    Passed 'value' is the uuid of the image
    
    """

    print(f"INFO -- Entered start_ml_algorithm(): {run}, {selected_algorithm}, {selected_location}, {start_date_uuid}, {end_date_uuid}")

    # Check if the callback was triggered by clicking the run button
    if not run:
        return "Waiting for input to run the algorithm."

    # Default values if inputs might be missing
    start_date_uuid = start_date_uuid if start_date_uuid is not None else "Default Start Date"
    end_date_uuid = end_date_uuid if end_date_uuid is not None else "Default End Date"

    # Ensure other critical inputs are provided
    if selected_algorithm is None or selected_location is None:
        return "Please select an algorithm and location."

    # Simulate a long-running task
    # Here you would typically start your machine learning algorithm
        
    # TODO: Show a progress bar to user when algorithm is running --> see https://dash.plotly.com/long-callbacks

    if selected_algorithm == "Change":
        if selected_location and start_date_uuid and end_date_uuid:
            
            if DEBUG_STATUS: print(f"INFO -- Running change detection algorithm for {selected_location} from {start_date_uuid} to {end_date_uuid}")

            print(f"{imagery_metadata}")

            # FIXME: Only allowing single date for before and after image
            if len(start_date_uuid) == 1:
                start_date_uuid = start_date_uuid[0]
                before_image_metadata = imagery_metadata[imagery_metadata["uuid"] == start_date_uuid]
                print(f"before_image_metadata: {before_image_metadata}")
                before_image_path = os.path.join(ASSETS_DIRECTORY, before_image_metadata["geotiff_path"].tolist()[0])
                print(f"before_image_path: {before_image_path}")
            
            if len(end_date_uuid) == 1:
                end_date_uuid = end_date_uuid[0]
                after_image_metadata = imagery_metadata[imagery_metadata["uuid"] == end_date_uuid]
                print(f"after_image_metadata: {after_image_metadata}")
                after_image_path = os.path.join(ASSETS_DIRECTORY, after_image_metadata["geotiff_path"].tolist()[0])
                print(f"after_image_path: {after_image_path}")
            
            ml_model_path = os.path.join(ASSETS_DIRECTORY, ML_MODEL_PATH)
            print(f"ml_model_path: {ml_model_path}")
            
            # FIXME: Prepend date ran to filename. Should a uuid be added? 
            # QUESTION: Should metadata be injected into geojson file etc. dated used, location, algotithm etc.
            ml_results_filename = f"{selected_algorithm}_{selected_location}_{start_date_uuid}_{end_date_uuid}.geojson"
            ml_output_path = os.path.join(ASSETS_DIRECTORY, ml_results_filename)
            print(f"ml_output_path: {ml_output_path}")

            change_detection_path = os.path.join(ASSETS_DIRECTORY, CHANGE_DETECTION_SCRIPT)
            print(f"change_detection_path: {change_detection_path}")


            run = subprocess.run(["python", change_detection_path, before_image_path, after_image_path, ml_model_path, ml_output_path, "--verbose"], capture_output=True)

            if run.returncode == 0:
                # TODO: Show as banner on UI
                print("ML algorithm completed successfully")
                return ml_output_path, f"Running {selected_algorithm} for location {selected_location}," f"from {start_date_uuid} to {end_date_uuid}."
            else:
                # TODO: Show as banner on UI
                print("ML algorithm failed")
                return no_update, f"ML algorithm failed to run for location {selected_location}," f"from {start_date_uuid} to {end_date_uuid}."
    
    else:
        # TODO: Implement detection


        # For demonstration, we'll just return a message
        return (
            f"Running {selected_algorithm} for location {selected_location},"
            f"from {start_date_uuid} to {end_date_uuid}."
        )


# == Show single date maptiles for imagery
@callback(
        Output("id-satellite-tilemap-layer", "url"),
        Input("id-datetime-for-imagery_tilemap", "value"),
        prevent_initial_call=True
)
def set_url_tilemap_for_single_selected_datetime(selected_tile_uuid):
    """Set tilemap url based on user selected datetime
    
    Single input datetime and single url output

    Input is the tilemaps path
    """

    if selected_tile_uuid:
        image_metadata = imagery_metadata[imagery_metadata["uuid"] == selected_tile_uuid]
        path = image_metadata["tilemaps_path"].tolist()[0]
        if DEBUG_STATUS: print(f"set_url_tilemap_for_user_selected_datetime - selected tilemap url: {path}")
    
        return path
    else:
        return no_update

# == set map center and zoom level based on selected location
@callback(
        Output("id-web-map", "center"),
        Output("id-web-map", "zoom"),
        Input("id-location-dropdown", "value"),
        prevent_initial_call=True
)
def zoom_map_to_site_location(selected_location):
        
    if selected_location:
        selected_location = imagery_metadata[imagery_metadata["sitename"] == selected_location]
    
        if DEBUG_STATUS: print(f"Selected location: {selected_location}")

        coordinates = selected_location["webmap_center"].tolist()[0]
        zoom_level = selected_location["webmap_zoom"].tolist()[0]

        if DEBUG_STATUS: print(f"returned: coordinates: {coordinates}, Zoom level: {zoom_level}")

        return coordinates, zoom_level
    else:
        return no_update, no_update



if __name__ == "__main__":
    app.run_server(debug=DEBUG_STATUS, host='0.0.0.0', port=PORT)

