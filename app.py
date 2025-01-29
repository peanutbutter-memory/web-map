"""Dash geo-spatial web application


## Notes:
- Must remove geometry column from geodataframe to allow display in dash_table

"""

# TODO: Add hover tips for bbox information
# TODO: Add start page
# TODO: Add site selection
# TODO: Add model selection
# TODO: Select bbox
# TODO: Use selected bbox to load image for preview
# TODO: Use selected bbox to run high res model
# TODO: Display results of high res model onto map


import os
import sys
from datetime import date
from dash import Dash, html, dcc, callback, Output, Input, dash_table, State, no_update
import plotly.express as px
import dash_bootstrap_components as dbc

import pandas as pd
import geopandas as gpd
import dash_leaflet as dl
import json
from dash_extensions.javascript import arrow_function


CONTACT_EMAIL = os.environ["CONTACT_EMAIL"]
DEPLOY_STATUS = os.environ["DEPLOY_STATUS"]
print(f"Deploy status is {DEPLOY_STATUS}")
PORT = os.environ["PORT"]
DEBUG_STATUS = os.environ["DEBUG_STATUS"]

external_stylesheets = [dbc.themes.CERULEAN, dbc.icons.BOOTSTRAP]

if DEPLOY_STATUS == "Production":
    app = Dash(__name__,
                requests_pathname_prefix="/app/WEB/",
                routes_pathname_prefix="/app/WEB/",
                external_stylesheets=external_stylesheets)
    
    # TODO: Parameterize this + add to callback to update individual tilemaps for images
    tilemap_path = "/blob/assets/sites/west-coast-high-resolution/burrand_inlet/tiles/{z}/{x}/{y}.png" #app.get_asset_url("sites/west-coast-high-resolution/burrand_inlet/tiles/{z}/{x}/{y}.png")
    print(f"Tilemap being used is {tilemap_path}")

    high_resolution_metadata = "/blob/assets/sites/west-coast-high-resolution/sites.geojson"
    print(f"High resolution metadata being used is {high_resolution_metadata}")

elif DEPLOY_STATUS == "Development":
    print("Running in development mode")
    app = Dash(__name__, external_stylesheets=external_stylesheets)

    # TODO: Parameterize this + add to callback to update individual tilemaps for images
    tilemap_path = "./assets/sites/west-coast-high-resolution/burrand_inlet/tiles/{z}/{x}/{y}.png"
    print(f"Tilemap being used is {tilemap_path}")

    high_resolution_metadata = "./assets/sites/west-coast-high-resolution/sites.geojson"
    print(f"High resolution metadata being used is {high_resolution_metadata}")

else:
    raise ValueError("Invalid value for DEPLOY_STATUS. Must be either 'Production' or 'Development'")
    sys.exit(1)


gdf = gpd.read_file(high_resolution_metadata)
# Provide data in dict format that is compatible with dash_leaflet
geojson_bboxes = gdf.__geo_interface__

# ==========

# == navigiation bar ==
navbar = dbc.NavbarSimple(
    brand="Phase - Initial User Testing",
    brand_href="/",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dcc.Link("Home", href="/", className="nav-link")),
        dbc.Button("Contact Us", color="info", className="me-2", size="md", href=f"mailto:{CONTACT_EMAIL}"),
    ]
)
# =====


# == landing page content ==
landing_page_content_introduction = dcc.Markdown("""
# Welcome to our application
                                    
`Showing placeholder content for now. This will be updated shortly`

Suspendisse cursus tellus neque, at accumsan tortor imperdiet non. Donec porta mollis eros. Vestibulum dictum gravida sapien, eu ornare magna laoreet nec. Fusce eget interdum nibh, id placerat massa. Duis id purus ante. Etiam lobortis nec lectus id tincidunt. Sed consequat sit amet sem vitae rhoncus. Vivamus imperdiet nunc tincidunt lectus vestibulum sodales in eget leo. Nam congue efficitur facilisis. Maecenas quis mattis erat, eget ullamcorper arcu. Aliquam tincidunt commodo ex vel porttitor. Nunc elementum imperdiet vulputate. Suspendisse accumsan sodales nunc, eu pellentesque justo posuere ut.

""")

landing_page_content_high_res_detection = dcc.Markdown("""
## High Resolution Object Detection

"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

""")                                    

landing_page_content_coastal_scanning = dcc.Markdown("""
## Coastal Scanning with Sentinel-2                                 

Nullam nisi sapien, gravida eu mauris sed, mollis condimentum neque. Proin turpis nisl, varius at interdum sit amet, maximus id nibh. Cras pretium volutpat fringilla. Suspendisse dapibus, lectus quis suscipit sagittis, dolor est elementum sem, vel vestibulum turpis nisi at augue. Phasellus quis sollicitudin nisi. Cras hendrerit tortor varius justo tincidunt, sed varius felis vestibulum. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam mattis consectetur lectus, non blandit odio ullamcorper in. Nunc ornare augue lorem, et pulvinar enim scelerisque in. Nam vitae est tortor. Pellentesque varius tellus felis, sit amet egestas risus consequat sed. Donec aliquam ante eget arcu efficitur viverra. Donec quis ullamcorper tellus.

""")

landing_page_content_change_detection = dcc.Markdown("""
## Change Dectection with Sentinel-2                                 

Nullam nisi sapien, gravida eu mauris sed, mollis condimentum neque. Proin turpis nisl, varius at interdum sit amet, maximus id nibh. Cras pretium volutpat fringilla. Suspendisse dapibus, lectus quis suscipit sagittis, dolor est elementum sem, vel vestibulum turpis nisi at augue. Phasellus quis sollicitudin nisi. Cras hendrerit tortor varius justo tincidunt, sed varius felis vestibulum. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam mattis consectetur lectus, non blandit odio ullamcorper in. Nunc ornare augue lorem, et pulvinar enim scelerisque in. Nam vitae est tortor. Pellentesque varius tellus felis, sit amet egestas risus consequat sed. Donec aliquam ante eget arcu efficitur viverra. Donec quis ullamcorper tellus.

""")

# =====

# == landing page ==
landing_page = dbc.Container([
    html.Div([
    landing_page_content_introduction,
    html.Br(), html.Br(),
    landing_page_content_high_res_detection,
    dcc.Link(html.Button('Go to Map'), href='/map'),
    html.Br(), html.Br(),
    landing_page_content_coastal_scanning,
    dcc.Link(html.Button('Go to Map'), href='/map'),
    html.Br(), html.Br(),
    landing_page_content_change_detection,
    dcc.Link(html.Button('Go to Map'), href='/map'),
], style={'textAlign': 'left', 'padding': '50px'})
], fluid=True)

# =====

# == options
# ==== allow user to turn on/off imagery bboxes
display_state_of_imagery_bboxes = dbc.Col(html.Div([dcc.Dropdown(
            id="display-imagery-bboxes",
            options=[
                {"label": "Show Imagery Bboxes", "value": "display-bboxes"},
                {"label": "Turn off Imagery BBoxes", "value": "disable-bboxes"},
            ],
            value="display-bboxes",
            clearable=False)]))

# == map page ==
map_page = dbc.Container([
    dbc.Row(html.Br()),
    dbc.Row([
        dbc.Col(html.Div([dcc.Dropdown(
            id="basemap-dropdown",
            options=[
                {"label": "Open Street Map", "value": "osm"},
                {"label": "ESRI World Imagery", "value": "esri-world-imagery"},
            ],
            value="osm",
            clearable=False)])),

        dbc.Col(html.Div([display_state_of_imagery_bboxes])),

        dbc.Col(html.Div([dbc.Button("Run detection", id="run-object-detection", color="primary")])),

        dbc.Col(html.Div([dbc.Button("Clear detection results", id="clear-object-detection-results", color="primary")]))
            
        ]),

    dbc.Row(html.Br()),

    dbc.Row(html.Br()),


    # == web map
    dbc.Row(dl.Map(center=[48.57, -123.95], zoom=8, 
                   children=[
                       # Base map
                       dl.TileLayer(id="map-tile-layer"),
                       # High resolution tilemaps
                       dl.TileLayer(id="tilemap-layer", url=tilemap_path),
                             dl.EasyButton(icon="bi bi-house", id="reset-map-location-zoom", title="Reset map location and zoom"),
                            dl.GeoJSON(data=geojson_bboxes, id="imagery-bbox-polygons",
                                       zoomToBounds=True,
                                       zoomToBoundsOnClick=True,
                                       hoverStyle=arrow_function(dict(weight=5, color="#666", dashArray=""))),
                            ], id="web-map", style={"height": "75vh"})),
    
    html.Div("Selected Polygon ID: ", id="user-selected-bbox-polygon", style={"marginTop": "20px"}),
    
    html.Div("Hover over a polygon to see details here.", id="hover-geojson-tooltip", style={"marginTop": "20px"}),

    html.Div(id='output-container-date-picker-range')

], fluid=True)

# =====

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

# == handle page routing ==
@callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/map':
        return map_page
    else:
        return landing_page


# == show or disable imagery bboxes
@callback(
    Output("imagery-bbox-polygons", "data"),
    Input("display-imagery-bboxes", "value"),
)
def display_imagery_bboxes(selection_value):
    """Enable or turn off imagery bboxes

    Turning off targets geojson data with an empty feature.
    """

    if selection_value == "display-bboxes":
        return geojson_bboxes
    elif selection_value == "disable-bboxes":
        return {"type": "FeatureCollection", "features": []}


# == change basemap tile provider
@callback(
    Output("map-tile-layer", "url"),
    Output("map-tile-layer", "attribution"),
    Input("basemap-dropdown","value")
)
def update_basemap(basemap):
    """Change base map tile provider"""

    if basemap == "osm":
        tile_url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution = "(C) OpenStreetMap contributors"
    elif basemap == "esri-world-imagery":
        tile_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png"
        attribution = "Tiles (C) Esri -- Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"

    return tile_url, attribution

# == reset map view to data bbox bounds after zooming in
@callback(
    Output("web-map", "center"),
    Output("web-map", "zoom"),
    Input("reset-map-location-zoom", "n_clicks")
)
def reset_map(n_clicks):
    return [48.57, -123.95], 8

# == get feature data when user clicks on a geojson bbox
@callback(
    Output("user-selected-bbox-polygon", "children"),
    Input("imagery-bbox-polygons", "clickData"),
    Input("imagery-bbox-polygons", "n_clicks")
)
def get_id_of_imagery_bbox_selected(feature, n_clicks):
    print(feature)
    if feature is not None:
        polygon_id = feature["id"]
        print(f"Feature clicked: {polygon_id}")  # Debugging log
        return polygon_id
    else:
        print("No feature clicked")
        return "Selected Polygon ID: None"

# == show hover tip data when user hovers over a geojson bbox
@callback(
    Output("hover-geojson-tooltip", "children"),
    Input("imagery-bbox-polygons", "hoverData")
)
def display_bbox_hover_data(feature):
    if feature is not None:
        print(feature)
        return f"Hovering over: {feature['properties']}"
    else:
        return []


# # == generate date slider data for
# @callback(
#     Output("date-filtering-imagery-bboxes", "children"),
# )
#
# # == date selection filter
# @callback(
#     Output("output-container-date-picker-range", "children"),
#     Input("date-filtering-imagery-bboxes", "start_date"),
#     Input("date-filtering-imagery-bboxes", "end_date"))
# def update_output(start_date, end_date):
#     string_prefix = 'You have selected: '
#     if start_date is not None:
#         start_date_object = date.fromisoformat(start_date)
#         start_date_string = start_date_object.strftime('%B %d, %Y')
#         string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
#     if end_date is not None:
#         end_date_object = date.fromisoformat(end_date)
#         end_date_string = end_date_object.strftime('%B %d, %Y')
#         string_prefix = string_prefix + 'End Date: ' + end_date_string
#     if len(string_prefix) == len('You have selected: '):
#         return 'Select a date to see it displayed here'
#     else:
#         return string_prefix


if __name__ == '__main__':
    app.run_server(debug=DEBUG_STATUS, host='0.0.0.0', port=PORT)

