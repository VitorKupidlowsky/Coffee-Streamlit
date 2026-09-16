import os
import ee
import folium
from branca.element import Element
import streamlit as st
from streamlit_folium import st_folium
import google.auth

# ==============================================================================
# 1. PAGE SETUP & AUTHENTICATION
# ==============================================================================
st.set_page_config(
    page_title="Coffea arabica Climate Adaptation Engine",
    page_icon="☕",
    layout="wide"
)

st.title("The Adaptation Premium: Global Coffea Arabica GIS Analysis")
st.markdown("Interactive techno-economic spatial analysis under baseline and CMIP6 SSP5-8.5 warming scenarios.")

@st.cache_resource
def initialize_ee():
    """Initializes Google Earth Engine with project credentials or ADC."""
    project_id = "thesis-488210"
    try:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/earthengine"]
        )
        ee.Initialize(credentials=credentials, project=project_id)
    except Exception:
        ee.Initialize(project=project_id)

initialize_ee()

if "map_center" not in st.session_state:
    st.session_state.map_center = [0.0, 20.0]

if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = 3

# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================
def add_ee_layer(folium_map, ee_image, vis_params, name, shown=True, opacity=0.8):
    """Fetches Earth Engine map tiles and mounts them as a Folium TileLayer."""
    map_id_dict = ee.Image(ee_image).getMapId(vis_params)
    folium.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr="Google Earth Engine",
        name=name,
        overlay=True,
        control=True,
        show=shown,
        opacity=opacity
    ).add_to(folium_map)

def get_suitability(image, min_val, op_min, op_max, max_val):
    """Piecewise linear suitability score function (EcoCrop response logic)."""
    expression_str = (
        "(i <= min || i >= max) ? 0 :"
        "(i >= opMin && i <= opMax) ? 100 :"
        "(i > min && i < opMin) ? ((i - min) / (opMin - min)) * 100 :"
        "(i > opMax && i < max) ? ((max - i) / (max - opMax)) * 100 : 0"
    )
    return image.expression(
        expression_str,
        {'i': image, 'min': min_val, 'opMin': op_min, 'opMax': op_max, 'max': max_val}
    ).toFloat()

def get_limiting_factor(stack):
    """Determines the index of the lowest score (most limiting factor)."""
    return stack.multiply(-1).toArray().arrayArgmax().arrayGet([0]).add(1).rename('limiting_factor_index')

# ==============================================================================
# 3. PRE-COMPUTED ASSET LOADER (Mapped to Asset Band Indices)
# ==============================================================================
@st.cache_resource
def load_precomputed_assets():
    """
    Loads pre-computed multi-band GeoTIFF assets using the automatic 
    indexed band names (b1, b2, ...) assigned during GEE asset ingestion.
    """
    project_path = "projects/thesis-488210/assets"

    # Multi-band Image Stacks
    base_stack = ee.Image(f"{project_path}/Coffee_Baseline_Complete_Stack")
    fut_stack = ee.Image(f"{project_path}/Coffee_Future_Complete_Stack")
    delta_stack = ee.Image(f"{project_path}/Coffee_Deltas_Complete_Stack")
    irrig_stack = ee.Image(f"{project_path}/Coffee_Future_IRRIGATED_Complete_Stack")
    benefit_stack = ee.Image(f"{project_path}/Coffee_Irrigation_Benefit_Delta")

    # Limiting Factor Single-Band Images (Mask out 0 ocean pixels)
    base_limit = ee.Image(f"{project_path}/Coffee_Baseline_Limiting_Factor").selfMask()
    fut_limit = ee.Image(f"{project_path}/Coffee_Future_Limiting_Factor").selfMask()
    irrig_limit = ee.Image(f"{project_path}/Coffee_Irrigated_Limiting_Factor").selfMask()

    return {
        # Overall Suitability Scores (Band 1 of each complete stack)
        'nat_suit_base': base_stack.select(['b1']),
        'nat_suit_fut': fut_stack.select(['b1']),
        'nat_suit_irrig': irrig_stack.select(['b1']),

        # Deltas & Benefits
        # In Coffee_Deltas_Complete_Stack: b1=viability_shift, b2=delta_suitability, b3=irrigation_need
        'delta_nat_suit': delta_stack.select(['b2']),
        'local_irrigation_budget': delta_stack.select(['b3']),

        # In Coffee_Irrigation_Benefit_Delta: b1=delta_irrigation_benefit_points
        'delta_irrigation_benefit': benefit_stack.select(['b1']),

        # Limiting Factor rasters (Single band, select b1)
        'baseline_limiting': base_limit.select(['b1']),
        'future_limiting': fut_limit.select(['b1']),
        'irrigated_limiting': irrig_limit.select(['b1'])
    }

layers = load_precomputed_assets()

# ==============================================================================
# 4. PALETTES & SIDEBAR CONTROLS
# ==============================================================================
vis_suitability = {'min': 0, 'max': 100, 'palette': ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']}
vis_delta = {'min': -100, 'max': 100, 'palette': ['#ca0020', '#f4a582', '#f7f7f7', '#92c5de', '#0571b0']}
vis_irrigation = {'min': 1, 'max': 300, 'palette': ['#ffffcc', '#a1dab4', '#41b6c4', '#2c7fb8', '#253494']}
vis_benefit = {'min': 1, 'max': 50, 'palette': ['#f7fcf0', '#e0f3db', '#ccebc5', '#a8ddb5', '#7bccc4', '#4eb3d3', '#2b8cbe', '#08589e']}
vis_limiting = {
    'min': 1, 'max': 9,
    'palette': ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462', '#b3de69', '#fccde5', '#d9d9d9']
}

st.sidebar.header("Scenario & Layer Selection")

# 1. Primary Scenario Selector
scenario_mode = st.sidebar.radio(
    "Scenario Horizon",
    (
        "Baseline Climatology (2000–2023)",
        "2050 SSP5-8.5 (Unmitigated)",
        "2050 SSP5-8.5 (Irrigated Adaptation)"
    )
)

# 2. Dynamic Single-Choice Layer Options based on Scenario
if scenario_mode == "Baseline Climatology (2000–2023)":
    layer_options = [
        "1. Baseline Suitability Score (0–100)",
        "2. Limiting Factor (Baseline)"
    ]
elif scenario_mode == "2050 SSP5-8.5 (Unmitigated)":
    layer_options = [
        "1. Future Suitability (2050 SSP5-8.5)",
        "2. Delta Suitability (Future - Baseline)",
        "3. Limiting Factor (Future 2050)"
    ]
elif scenario_mode == "2050 SSP5-8.5 (Irrigated Adaptation)":
    layer_options = [
        "1. Irrigated Suitability (2050)",
        "2. Points Recovered via Irrigation",
        "3. Irrigation Budget Need (mm)",
        "4. Limiting Factor (Post-Irrigation)"
    ]

# Mutually exclusive layer selector
active_layer = st.sidebar.radio("Active Map Layer", layer_options)

# ==============================================================================
# 4.5. LEGEND INJECTOR HELPERS
# ==============================================================================
limiting_labels = [
    "1. Soil Depth", "2. Slope", "3. Texture", "4. pH",
    "5. Annual Mean Temp", "6. Min Temp Coldest Month",
    "7. Annual Precip", "8. Dry Season Duration", "9. Relative Humidity"
]
limiting_colors = [
    '#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3',
    '#fdb462', '#b3de69', '#fccde5', '#d9d9d9'
]

def add_categorical_legend(folium_map, title, colors, labels):
    """Injects a floating HTML categorical legend into a Folium map."""
    items_html = "".join([
        f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <span style="background: {c}; width: 14px; height: 14px; display: inline-block; margin-right: 8px; border: 1px solid #444; border-radius: 2px;"></span>
            <span style="font-size: 11px; color: #c9c7c7;">{lbl}</span>
        </div>
        """
        for c, lbl in zip(colors, labels)
    ])

    legend_html = f"""
    {{% macro html(this, kwargs) %}}
    <div style="
        position: fixed; 
        bottom: 30px; 
        right: 20px; 
        z-index: 99999; 
        background: rgba(255, 255, 255, 0.95); 
        padding: 10px 14px; 
        border: 2px solid #999; 
        border-radius: 5px; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        font-family: Arial, sans-serif;
        max-height: 260px;
        overflow-y: auto;
    ">
        <div style="font-weight: bold; font-size: 12px; margin-bottom: 6px; color: #000;">{title}</div>
        {items_html}
    </div>
    {{% endmacro %}}
    """
    macro = Element(legend_html)
    folium_map.get_root().add_child(macro)

def add_continuous_legend(folium_map, title, palette, min_val, max_val, unit=""):
    """Injects a horizontal gradient bar legend onto the map."""
    gradient_str = ", ".join(palette)
    legend_html = f"""
    {{% macro html(this, kwargs) %}}
    <div style="
        position: fixed; 
        bottom: 30px; 
        left: 20px; 
        z-index: 99999; 
        background: rgba(255, 255, 255, 0.95); 
        padding: 8px 12px; 
        border: 2px solid #999; 
        border-radius: 5px; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        font-family: Arial, sans-serif;
        min-width: 200px;
    ">
        <div style="font-weight: bold; font-size: 11px; margin-bottom: 4px; color: #000;">{title}</div>
        <div style="
            width: 100%; 
            height: 12px; 
            background: linear-gradient(to right, {gradient_str}); 
            border: 1px solid #555;
            border-radius: 2px;
        "></div>
        <div style="display: flex; justify-content: space-between; font-size: 10px; margin-top: 3px; color: #c9c7c7;">
            <span>{min_val} {unit}</span>
            <span>{max_val} {unit}</span>
        </div>
    </div>
    {{% endmacro %}}
    """
    macro = Element(legend_html)
    folium_map.get_root().add_child(macro)

# ==============================================================================
# 5. FOLIUM MAP ASSEMBLY
# ==============================================================================

# 1. Sync viewport coordinates from the previous render BEFORE building folium.Map
for k in st.session_state:
    if k.startswith("map_") and isinstance(st.session_state[k], dict):
        last_center = st.session_state[k].get("center")
        last_zoom = st.session_state[k].get("zoom")
        if last_center and isinstance(last_center, dict):
            c_lat = last_center.get("lat")
            c_lng = last_center.get("lng")
            if c_lat is not None and c_lng is not None:
                st.session_state.map_center = [c_lat, c_lng]
        if last_zoom is not None:
            st.session_state.map_zoom = last_zoom

# 2. Build the map using the updated viewport
m = folium.Map(
    location=st.session_state.map_center,
    zoom_start=st.session_state.map_zoom,
    tiles="https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png",
    attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
)

# 3. Add the active layer based on the radio selection
if "Baseline Suitability" in active_layer:
    add_ee_layer(m, layers['nat_suit_base'], vis_suitability, active_layer)
elif "Limiting Factor (Baseline)" in active_layer:
    add_ee_layer(m, layers['baseline_limiting'], vis_limiting, active_layer)
elif "Future Suitability" in active_layer:
    add_ee_layer(m, layers['nat_suit_fut'], vis_suitability, active_layer)
elif "Delta Suitability" in active_layer:
    add_ee_layer(m, layers['delta_nat_suit'], vis_delta, active_layer)
elif "Limiting Factor (Future 2050)" in active_layer:
    add_ee_layer(m, layers['future_limiting'], vis_limiting, active_layer)
elif "Irrigated Suitability" in active_layer:
    add_ee_layer(m, layers['nat_suit_irrig'], vis_suitability, active_layer)
elif "Points Recovered" in active_layer:
    add_ee_layer(m, layers['delta_irrigation_benefit'].selfMask(), vis_benefit, active_layer)
elif "Irrigation Budget" in active_layer:
    add_ee_layer(m, layers['local_irrigation_budget'].selfMask(), vis_irrigation, active_layer)
elif "Limiting Factor (Post-Irrigation)" in active_layer:
    add_ee_layer(m, layers['irrigated_limiting'], vis_limiting, active_layer)

    
def render_st_gradient(label, palette, min_label, max_label, center_label=None):
    """Renders a continuous gradient bar with theme-adaptive white/light text."""
    grad = ", ".join(palette)
    center_html = f"<span>{center_label}</span>" if center_label else ""
    st.markdown(
        f"""
        <div style="margin-bottom: 14px;">
            <div style="font-size: 13px; font-weight: 600; margin-bottom: 4px; color: #ffffff;">{label}</div>
            <div style="width: 100%; height: 14px; background: linear-gradient(to right, {grad}); border: 1px solid #777; border-radius: 3px;"></div>
            <div style="display: flex; justify-content: space-between; font-size: 11px; margin-top: 3px; color: #d0d4dc;">
                <span>{min_label}</span>{center_html}<span>{max_label}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
# ==============================================================================
# 5.5. Helper country zone
# ==============================================================================
@st.cache_data(show_spinner=False)
def compute_country_stats(lat, lon):
    try:
        point = ee.Geometry.Point([lon, lat])
        countries = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017")
        selected_country = countries.filterBounds(point).first()
        
        info = selected_country.getInfo()
        if not info or 'properties' not in info:
            return None

        country_name = info['properties'].get('country_na', 'Unknown Country')
        country_geom = selected_country.geometry()

        # Connect directly to the cached assets
        assets = load_precomputed_assets()
        stats_stack = ee.Image([
            assets['nat_suit_base'].rename('base_suit'),
            assets['nat_suit_fut'].rename('fut_suit'),
            assets['nat_suit_irrig'].rename('irrig_suit'),
            assets['delta_nat_suit'].rename('delta_suit'),
            assets['delta_irrigation_benefit'].unmask(0).rename('irrig_benefit'),
            assets['local_irrigation_budget'].unmask(0).rename('water_need')
        ])

        stats = stats_stack.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=country_geom,
            scale=10000,
            maxPixels=1e10,
            tileScale=8,
            bestEffort=True
        ).getInfo()

        return {
            'country': country_name,
            'base_suit': stats.get('base_suit'),
            'fut_suit': stats.get('fut_suit'),
            'irrig_suit': stats.get('irrig_suit'),
            'delta_suit': stats.get('delta_suit'),
            'irrig_benefit': stats.get('irrig_benefit'),
            'water_need': stats.get('water_need')
        }
    except Exception as e:
        return {"error": str(e)}
# ==============================================================================
# 6. STREAMLIT DISPLAY WITH MULTI-PANEL LAYOUT
# ==============================================================================
col_map, col_legend = st.columns([3.8, 1.4])

with col_map:
    map_output = st_folium(
        m,
        key=f"map_{active_layer}",
        width="100%",
        height=720,
        returned_objects=["last_clicked", "center", "zoom"]
    )

# If the user panned or zoomed, update the session state for the next render
    if map_output:
        # Check that center exists and actually has lat/lng
        curr_center = map_output.get("center")
        if curr_center and isinstance(curr_center, dict):
            lat = curr_center.get("lat")
            lng = curr_center.get("lng")
            if lat is not None and lng is not None:
                st.session_state.map_center = [lat, lng]

        # Check zoom
        curr_zoom = map_output.get("zoom")
        if curr_zoom is not None:
            st.session_state.map_zoom = curr_zoom

with col_legend:
    st.subheader("Active Layer Legend")

    # Render dynamic legends
    if "Suitability" in active_layer:
        render_st_gradient(active_layer, vis_suitability['palette'], "0 (Unsuitable)", "100 (Optimal)")
    elif "Delta Suitability" in active_layer:
        render_st_gradient(active_layer, vis_delta['palette'], "-100 (Loss)", "+100 (Gain)", center_label="0")
    elif "Points Recovered" in active_layer:
        render_st_gradient(active_layer, vis_benefit['palette'], "+1 pt", "+50 pts")
    elif "Irrigation Budget" in active_layer:
        render_st_gradient(active_layer, vis_irrigation['palette'], "1 mm", "300 mm")
    elif "Limiting Factor" in active_layer:
        st.markdown(f"**{active_layer}**")
        for c, lbl in zip(limiting_colors, limiting_labels):
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <span style="background: {c}; width: 13px; height: 13px; display: inline-block; margin-right: 8px; border: 1px solid #777; border-radius: 2px;"></span>
                    <span style="font-size: 12px; color: #ffffff;">{lbl}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.subheader("Country Zonal Analytics")

    # Check for click coordinates safely
    click_data = map_output.get("last_clicked") if map_output else None

    if click_data:
        lat = click_data.get("lat")
        lon = click_data.get("lng") or click_data.get("lon")

        if lat is not None and lon is not None:
            with st.spinner(f"Computing stats for coordinates ({lat:.2f}, {lon:.2f})..."):
                data = compute_country_stats(lat, lon)

            if data and "error" in data:
                st.error(f"Computation failed: {data['error']}")
            elif data and data.get('country'):
                st.success(f"**{data['country']}**")
                
                def fmt(val, unit=""): 
                    return f"{val:.1f} {unit}" if val is not None else "N/A"

                st.metric("Baseline Suitability", fmt(data['base_suit'], "pts"))
                st.metric(
                    "2050 Future Suitability", 
                    fmt(data['fut_suit'], "pts"), 
                    delta=f"{data['delta_suit']:.1f} pts" if data['delta_suit'] is not None else None
                )
                st.metric("Irrigated Suitability", fmt(data['irrig_suit'], "pts"))
                st.metric("Mean Water Deficit Need", fmt(data['water_need'], "mm"))
                st.metric("Irrigation Recovery Benefit", fmt(data['irrig_benefit'], "pts"))
            else:
                st.warning("Clicked point is outside recognized boundaries.")
    else:
        st.caption("Click any country on the map to trigger spatial zonal statistics.")
# ==============================================================================
# 7. Helper country zone
# ==============================================================================
@st.cache_data(show_spinner=False)
def compute_country_stats(lat, lon):
    """
    Identifies the clicked country and calculates zonal mean statistics.
    Uses an optimized tile scale and scale resolution to prevent GEE timeouts.
    """
    try:
        point = ee.Geometry.Point([lon, lat])
        
        # 1. Identify Country via LSIB Global Boundaries
        countries = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017")
        selected_country = countries.filterBounds(point).first()
        
        # Check if click landed on valid land/country
        info = selected_country.getInfo()
        if not info or 'properties' not in info:
            return None

        country_name = info['properties'].get('country_na', 'Unknown Country')
        country_geom = selected_country.geometry()

        # 2. Build multi-band metric stack
        pipeline = load_precomputed_assets()
        stats_stack = ee.Image([
            pipeline['nat_suit_base'].rename('base_suit'),
            pipeline['nat_suit_fut'].rename('fut_suit'),
            pipeline['nat_suit_irrig'].rename('irrig_suit'),
            pipeline['delta_nat_suit'].rename('delta_suit'),
            pipeline['delta_irrigation_benefit'].unmask(0).rename('irrig_benefit'),
            pipeline['local_irrigation_budget'].unmask(0).rename('water_need')
        ])

        # 3. Fast Zonal Reduction (Using scale=10000 to keep responses under 2 seconds)
        stats = stats_stack.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=country_geom,
            scale=10000,
            maxPixels=1e10,
            tileScale=8,
            bestEffort=True
        ).getInfo()

        return {
            'country': country_name,
            'base_suit': stats.get('base_suit'),
            'fut_suit': stats.get('fut_suit'),
            'irrig_suit': stats.get('irrig_suit'),
            'delta_suit': stats.get('delta_suit'),
            'irrig_benefit': stats.get('irrig_benefit'),
            'water_need': stats.get('water_need')
        }
    except Exception as e:
        return {"error": str(e)}