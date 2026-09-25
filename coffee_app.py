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
def add_ee_layer(folium_map, ee_image, vis_params, name, shown=True, opacity=0.85):
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

# ==============================================================================
# 3. PRE-COMPUTED ASSET LOADER
# ==============================================================================
@st.cache_resource
def load_precomputed_assets():
    """
    Loads pre-computed multi-band and single-band GeoTIFF assets from GEE.
    """
    project_path = "projects/thesis-488210/assets"

    # Multi-band Image Stacks
    base_stack = ee.Image(f"{project_path}/Coffee_Baseline_Complete_Stack")
    fut_stack = ee.Image(f"{project_path}/Coffee_Future_Complete_Stack")
    delta_stack = ee.Image(f"{project_path}/Coffee_Deltas_Complete_Stack")
    irrig_stack = ee.Image(f"{project_path}/Coffee_Future_IRRIGATED_Complete_Stack")
    benefit_stack = ee.Image(f"{project_path}/Coffee_Irrigation_Benefit_Delta")

    # Limiting Factor Single-Band Images (Mask out 0 non-viable pixels)
    base_limit = ee.Image(f"{project_path}/Coffee_Baseline_Limiting_Factor").selfMask()
    fut_limit = ee.Image(f"{project_path}/Coffee_Future_Limiting_Factor").selfMask()
    irrig_limit = ee.Image(f"{project_path}/Coffee_Irrigated_Limiting_Factor").selfMask()

    # Hydrology & Techno-Economic Single-Band Images
    lcow_map = ee.Image(f"{project_path}/Coffee_Optimal_LCOW_Map").selfMask()
    water_source_map = ee.Image(f"{project_path}/Coffee_Water_Source_Map").selfMask()
    gw_depth_map = ee.Image(f"{project_path}/Coffee_Groundwater_Depth_Map").selfMask()
    water_stress_map = ee.Image(f"{project_path}/Coffee_WRI_Water_Stress_Map").selfMask()

    return {
        # Overall Suitability Scores
        'nat_suit_base': base_stack.select(['b1']),
        'nat_suit_fut': fut_stack.select(['b1']),
        'nat_suit_irrig': irrig_stack.select(['b1']),

        # Deltas & Benefits
        'delta_nat_suit': delta_stack.select(['b2']),
        'local_irrigation_budget': delta_stack.select(['b3']),
        'delta_irrigation_benefit': benefit_stack.select(['b1']),

        # Limiting Factor Rasters
        'baseline_limiting': base_limit.select(['b1']),
        'future_limiting': fut_limit.select(['b1']),
        'irrigated_limiting': irrig_limit.select(['b1']),

        # Techno-Economic & Hydrology Rasters
        'lcow': lcow_map.select(['b1']),
        'water_source': water_source_map.select(['b1']),
        'gw_depth': gw_depth_map.select(['b1']),
        'water_stress': water_stress_map.select(['b1'])
    }

layers = load_precomputed_assets()

# ==============================================================================
# 4. PALETTES & VISUALIZATION PARAMETERS
# ==============================================================================
vis_suitability = {'min': 0, 'max': 100, 'palette': ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']}
vis_delta = {'min': -100, 'max': 100, 'palette': ['#ca0020', '#f4a582', '#f7f7f7', '#92c5de', '#0571b0']}
vis_irrigation = {'min': 1, 'max': 300, 'palette': ['#ffffcc', '#a1dab4', '#41b6c4', '#2c7fb8', '#253494']}
vis_benefit = {'min': 1, 'max': 50, 'palette': ['#f7fcf0', '#e0f3db', '#ccebc5', '#a8ddb5', '#7bccc4', '#4eb3d3', '#2b8cbe', '#08589e']}
vis_limiting = {
    'min': 1, 'max': 9,
    'palette': ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462', '#b3de69', '#fccde5', '#d9d9d9']
}

# Economic & Hydrological Vis Params
vis_lcow = {'min': 0.1, 'max': 2.0, 'palette': ['#2b83ba', '#abdda4', '#ffffbf', '#fdae61', '#d7191c']}
vis_water_source = {'min': 0, 'max': 1, 'palette': ['#a6cee3', '#1f78b4']}  # 0: Surface, 1: Groundwater
vis_gw_depth = {'min': 3, 'max': 150, 'palette': ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']}
vis_water_stress = {'min': 1, 'max': 5, 'palette': ['#1a9641', '#a6d96a', '#ffffbf', '#fdae61', '#d7191c']}

limiting_labels = [
    "1. Soil Depth", "2. Slope", "3. Texture", "4. pH",
    "5. Annual Mean Temp", "6. Min Temp Coldest Month",
    "7. Annual Precip", "8. Dry Season Duration", "9. Relative Humidity"
]
limiting_colors = [
    '#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3',
    '#fdb462', '#b3de69', '#fccde5', '#d9d9d9'
]

water_stress_labels = [
    "1. Low (<10%)", "2. Low-Medium (10–20%)", "3. Medium-High (20–40%)",
    "4. High (40–80%)", "5. Extremely High (>80%)"
]
water_stress_colors = ['#1a9641', '#a6d96a', '#ffffbf', '#fdae61', '#d7191c']

# ==============================================================================
# 5. SIDEBAR SELECTION (CARS/BLADE HIERARCHICAL STRUCTURE)
# ==============================================================================
st.sidebar.header("Scenario & Layer Controls")

scenario_mode = st.sidebar.select_slider(
    "Scenario Horizon",
    options=[
        "Baseline Climatology (2000–2023)",
        "2050 SSP5-8.5 (Unmitigated)",
        "2050 SSP5-8.5 (Irrigated Adaptation)"
    ]
)

if scenario_mode == "Baseline Climatology (2000–2023)":
    active_layer = st.sidebar.radio(
        "Active Map Layer",
        [
            "1. Baseline Suitability Score (0–100)",
            "2. Limiting Factor (Baseline)"
        ]
    )

elif scenario_mode == "2050 SSP5-8.5 (Unmitigated)":
    active_layer = st.sidebar.radio(
        "Active Map Layer",
        [
            "1. Future Suitability (2050 SSP5-8.5)",
            "2. Delta Suitability (Future - Baseline)",
            "3. Limiting Factor (Future 2050)"
        ]
    )

elif scenario_mode == "2050 SSP5-8.5 (Irrigated Adaptation)":
    adaptation_domain = st.sidebar.radio(
        "Analysis Domain",
        ["Biophysical Recovery", "Techno-Economic & Hydrology"]
    )

    if adaptation_domain == "Biophysical Recovery":
        active_layer = st.sidebar.radio(
            "Active Map Layer",
            [
                "1. Irrigated Suitability (2050)",
                "2. Points Recovered via Irrigation",
                "3. Irrigation Budget Need (mm)",
                "4. Limiting Factor (Post-Irrigation)"
            ]
        )
    else:
        active_layer = st.sidebar.radio(
            "Active Map Layer",
            [
                "1. Levelized Cost of Water (LCOW, $/m³)",
                "2. Water Source Selection (Surface vs. Groundwater)",
                "3. Aquifer Depth to Groundwater (m)",
                "4. WRI Projected Water Stress (2050)"
            ]
        )

# ==============================================================================
# 6. FOLIUM MAP COMPOSITION
# ==============================================================================
if "coffee_map" in st.session_state and isinstance(st.session_state["coffee_map"], dict):
    last_center = st.session_state["coffee_map"].get("center")
    last_zoom = st.session_state["coffee_map"].get("zoom")
    if last_center and isinstance(last_center, dict):
        c_lat = last_center.get("lat")
        c_lng = last_center.get("lng")
        if c_lat is not None and c_lng is not None:
            st.session_state.map_center = [c_lat, c_lng]
    if last_zoom is not None:
        st.session_state.map_zoom = last_zoom

m = folium.Map(
    location=st.session_state.map_center,
    zoom_start=st.session_state.map_zoom,
    tiles="https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png",
    attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
)

# Biophysical Layers
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

# Techno-Economic & Hydrological Layers
elif "LCOW" in active_layer:
    add_ee_layer(m, layers['lcow'], vis_lcow, active_layer)
elif "Water Source Selection" in active_layer:
    add_ee_layer(m, layers['water_source'], vis_water_source, active_layer)
elif "Aquifer Depth" in active_layer:
    add_ee_layer(m, layers['gw_depth'], vis_gw_depth, active_layer)
elif "WRI Projected Water Stress" in active_layer:
    add_ee_layer(m, layers['water_stress'], vis_water_stress, active_layer)

# ==============================================================================
# 7. COUNTRY ZONAL ANALYTICS ENGINE
# ==============================================================================
@st.cache_data(show_spinner=False)
def compute_country_stats(lat, lon):
    """
    Identifies the clicked country and calculates zonal statistics across biophysical
    and techno-economic layers using optimized sampling.
    """
    try:
        point = ee.Geometry.Point([lon, lat])
        countries = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017")
        selected_country = countries.filterBounds(point).first()

        info = selected_country.getInfo()
        if not info or 'properties' not in info:
            return None

        country_name = info['properties'].get('country_na', 'Unknown Country')
        country_geom = selected_country.geometry()

        assets = load_precomputed_assets()
        stats_stack = ee.Image([
            assets['nat_suit_base'].rename('base_suit'),
            assets['nat_suit_fut'].rename('fut_suit'),
            assets['nat_suit_irrig'].rename('irrig_suit'),
            assets['delta_nat_suit'].rename('delta_suit'),
            assets['delta_irrigation_benefit'].unmask(0).rename('irrig_benefit'),
            assets['local_irrigation_budget'].unmask(0).rename('water_need'),
            assets['lcow'].rename('lcow'),
            assets['gw_depth'].rename('gw_depth'),
            assets['water_source'].rename('water_source'),
            assets['water_stress'].rename('water_stress')
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
            'water_need': stats.get('water_need'),
            'lcow': stats.get('lcow'),
            'gw_depth': stats.get('gw_depth'),
            'water_source': stats.get('water_source'),
            'water_stress': stats.get('water_stress')
        }
    except Exception as e:
        return {"error": str(e)}

def render_st_gradient(label, palette, min_label, max_label, center_label=None):
    """Renders a continuous gradient bar with theme-adaptive styling."""
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
# 8. STREAMLIT DISPLAY WITH MULTI-PANEL LAYOUT
# ==============================================================================
col_map, col_legend = st.columns([3.8, 1.4])

with col_map:
    map_output = st_folium(
        m,
        key=f"coffee_map_{active_layer}",
        width="100%",
        height=720,
        returned_objects=["last_clicked", "last_object_clicked"]
    )

if map_output and map_output.get("last_clicked"):
    click = map_output["last_clicked"]
    if click.get("lat") is not None and click.get("lng") is not None:
        st.session_state.map_center = [click["lat"], click["lng"]]

with col_legend:
    st.subheader("Active Layer Legend")

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
    elif "LCOW" in active_layer:
        render_st_gradient("Levelized Cost of Water", vis_lcow['palette'], "≤ $0.25/m³", "≥ $2.00/m³", center_label="$0.80/m³")
    elif "Water Source Selection" in active_layer:
        st.markdown(f"**{active_layer}**")
        st.markdown(
            """
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span style="background: #a6cee3; width: 13px; height: 13px; display: inline-block; margin-right: 8px; border: 1px solid #777; border-radius: 2px;"></span>
                <span style="font-size: 12px; color: #ffffff;">Surface Water</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span style="background: #1f78b4; width: 13px; height: 13px; display: inline-block; margin-right: 8px; border: 1px solid #777; border-radius: 2px;"></span>
                <span style="font-size: 12px; color: #ffffff;">Groundwater</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif "Aquifer Depth" in active_layer:
        render_st_gradient("Groundwater Aquifer Depth", vis_gw_depth['palette'], "3 m (Shallow)", "150 m (Deep)")
    elif "WRI Projected Water Stress" in active_layer:
        st.markdown(f"**{active_layer}**")
        for c, lbl in zip(water_stress_colors, water_stress_labels):
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

    click_data = map_output.get("last_clicked") if map_output else None

    if click_data:
        lat = click_data.get("lat")
        lon = click_data.get("lng") or click_data.get("lon")

        if lat is not None and lon is not None:
            with st.spinner(f"Computing zonal metrics for ({lat:.2f}, {lon:.2f})..."):
                data = compute_country_stats(lat, lon)

            if data and "error" in data:
                st.error(f"Computation failed: {data['error']}")
            elif data and data.get('country'):
                st.success(f"**{data['country']}**")

                def fmt(val, unit="", decimals=1):
                    return f"{val:.{decimals}f} {unit}" if val is not None else "N/A"

                tab_bio, tab_econ = st.tabs(["Biophysical", "Techno-Economic"])

                with tab_bio:
                    st.metric("Baseline Suitability", fmt(data['base_suit'], "pts"))
                    st.metric(
                        "2050 Future Suitability",
                        fmt(data['fut_suit'], "pts"),
                        delta=f"{data['delta_suit']:.1f} pts" if data['delta_suit'] is not None else None
                    )
                    st.metric("Irrigated Suitability", fmt(data['irrig_suit'], "pts"))
                    st.metric("Mean Water Deficit", fmt(data['water_need'], "mm"))
                    st.metric("Irrigation Recovery", fmt(data['irrig_benefit'], "pts"))

                with tab_econ:
                    st.metric("Mean LCOW", fmt(data['lcow'], "$/m³", decimals=2))
                    st.metric("Mean Aquifer Depth", fmt(data['gw_depth'], "m"))

                    # Format Water Source ratio if available
                    if data['water_source'] is not None:
                        gw_pct = data['water_source'] * 100
                        st.metric("Dominant Source", f"{gw_pct:.0f}% Ground / {100-gw_pct:.0f}% Surface")
                    else:
                        st.metric("Dominant Source", "N/A")

                    # Format Water Stress index
                    if data['water_stress'] is not None:
                        stress_idx = int(round(data['water_stress']))
                        stress_idx = max(1, min(5, stress_idx))
                        st.metric("WRI Water Stress", water_stress_labels[stress_idx - 1])
                    else:
                        st.metric("WRI Water Stress", "N/A")
            else:
                st.warning("Clicked point is outside recognized boundaries.")
    else:
        st.caption("Click any country on the map to trigger spatial zonal statistics.")