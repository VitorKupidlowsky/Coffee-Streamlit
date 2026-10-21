import os
import math
import ee
import folium
import streamlit as st
from streamlit_folium import st_folium
import google.auth
from matrix_analytics import (
    render_dynamic_comparative_advantage_matrix,
    render_incumbent_badge,
    get_incumbent_benchmarks,
    load_matrix_csv,
    CSV_PATH,
)

# ==============================================================================
# 1. PAGE SETUP & AUTHENTICATION
# ==============================================================================
st.set_page_config(
    page_title="Coffea arabica Climate Adaptation Engine",
    page_icon=":material/eco:",
    layout="wide"
)
st.title("The Adaptation Premium: Global Coffea Arabica GIS Analysis")
st.markdown(
    "Interactive techno-economic spatial analysis under baseline and "
    "CMIP6 SSP5-8.5 warming scenarios."
)

# A1 Executive Banner: Key insight callout at page top
st.info(
    "**Key insight:** Under SSP5-8.5 warming, equatorial lowland Arabica zones "
    "face severe moisture deficits by 2050. Irrigation can biophysically recover "
    "significant viable area, but adaptation viability bifurcates — Latin America "
    "benefits from favorable water economics, while parts of East Africa and "
    "Southeast Asia face elevated infrastructure capital hurdles.",
    icon=":material/insights:",
)

# C1: Peer-reviewed methodological attribution
st.caption(
    ":material/school: **Data sources:** Earth Engine TerraClimate / CMIP6 "
    "SSP5-8.5 ensemble · WRI Aqueduct 4.0 water stress projections · "
    "Superwell techno-economic groundwater model · "
    "FAO harmonized world soil database"
)

@st.cache_resource
def initialize_ee():
    """Initializes Google Earth Engine with project credentials or ADC."""
    project_id = "thesis-488210"
    try:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/earthengine"]
        )
        ee.Initialize(credentials=credentials, project=project_id)
        return True, None
    except Exception as e_adc:
        try:
            ee.Initialize(project=project_id)
            return True, None
        except Exception as e_direct:
            return False, f"ADC: {e_adc}; Direct: {e_direct}"


ee_ok, ee_err = initialize_ee()
if not ee_ok:
    st.error(
        ":material/lock: **Google Earth Engine authentication required.**\n\n"
        "Please authenticate by running `earthengine authenticate` in your terminal or configure "
        "Google Application Default Credentials (ADC) for project `thesis-488210`.\n\n"
        f"*Details:* `{ee_err}`"
    )
    st.stop()

if "map_center" not in st.session_state:
    st.session_state.map_center = [0.0, 20.0]

if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = 3

# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================
def add_ee_layer(folium_map, ee_image, vis_params, name, shown=True, opacity=0.85):
    """Fetches Earth Engine map tiles and mounts them as a Folium TileLayer."""
    try:
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
    except Exception as e:
        st.warning(f"Could not load Earth Engine layer '{name}': {e}")

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
    water_stress_map = ee.Image(f"{project_path}/Coffee_WRI_Water_Stress_Map")

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
vis_water_source = {
    'min': 1,
    'max': 2,
    'palette': ['#1f78b4', '#a6cee3']  # 1: Groundwater (dark blue), 2: Surface water (light blue)
}
vis_gw_depth = {'min': 3, 'max': 150, 'palette': ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']}
vis_water_stress = {'min': 0, 'max': 4, 'palette': ['#1a9641', '#a6d96a', '#ffffbf', '#fdae61', '#d7191c']}

# A3 (CARS): Descriptive labels without numbered prefixes (sentence case)
limiting_labels = [
    "Soil depth", "Slope", "Soil texture", "Soil pH",
    "Annual mean temperature", "Coldest month minimum",
    "Annual precipitation", "Dry season duration", "Relative humidity"
]
limiting_colors = [
    '#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3',
    '#fdb462', '#b3de69', '#fccde5', '#d9d9d9'
]

water_stress_labels = [
    "Low (<10%)", "Low-medium (10–20%)", "Medium-high (20–40%)",
    "High (40–80%)", "Extremely high (>80%)"
]
water_stress_colors = ['#1a9641', '#a6d96a', '#ffffbf', '#fdae61', '#d7191c']

LAYER_REGISTRY = {
    "1. Baseline Suitability Score (0–100)": {
        "image": layers['nat_suit_base'],
        "vis": vis_suitability,
        "legend_type": "gradient",
        "title": "1. Baseline Suitability Score (0–100)",
        "palette": vis_suitability['palette'],
        "min_lbl": "0 (Unsuitable)",
        "max_lbl": "100 (Optimal)",
    },
    "2. Limiting Factor (Baseline)": {
        "image": layers['baseline_limiting'],
        "vis": vis_limiting,
        "legend_type": "categorical",
        "title": "2. Limiting Factor (Baseline)",
        "colors": limiting_colors,
        "labels": limiting_labels,
    },
    "1. Future Suitability (2050 SSP5-8.5)": {
        "image": layers['nat_suit_fut'],
        "vis": vis_suitability,
        "legend_type": "gradient",
        "title": "1. Future Suitability (2050 SSP5-8.5)",
        "palette": vis_suitability['palette'],
        "min_lbl": "0 (Unsuitable)",
        "max_lbl": "100 (Optimal)",
    },
    "2. Delta Suitability (Future - Baseline)": {
        "image": layers['delta_nat_suit'],
        "vis": vis_delta,
        "legend_type": "gradient",
        "title": "2. Delta Suitability (Future - Baseline)",
        "palette": vis_delta['palette'],
        "min_lbl": "-100 (Loss)",
        "max_lbl": "+100 (Gain)",
        "center_label": "0",
    },
    "3. Limiting Factor (Future 2050)": {
        "image": layers['future_limiting'],
        "vis": vis_limiting,
        "legend_type": "categorical",
        "title": "3. Limiting Factor (Future 2050)",
        "colors": limiting_colors,
        "labels": limiting_labels,
    },
    "1. Irrigated Suitability (2050)": {
        "image": layers['nat_suit_irrig'],
        "vis": vis_suitability,
        "legend_type": "gradient",
        "title": "1. Irrigated Suitability (2050)",
        "palette": vis_suitability['palette'],
        "min_lbl": "0 (Unsuitable)",
        "max_lbl": "100 (Optimal)",
    },
    "2. Points Recovered via Irrigation": {
        "image": layers['delta_irrigation_benefit'].selfMask(),
        "vis": vis_benefit,
        "legend_type": "gradient",
        "title": "2. Points Recovered via Irrigation",
        "palette": vis_benefit['palette'],
        "min_lbl": "+1 pt",
        "max_lbl": "+50 pts",
    },
    "3. Irrigation Budget Need (mm)": {
        "image": layers['local_irrigation_budget'].selfMask(),
        "vis": vis_irrigation,
        "legend_type": "gradient",
        "title": "3. Irrigation Budget Need (mm)",
        "palette": vis_irrigation['palette'],
        "min_lbl": "1 mm",
        "max_lbl": "300 mm",
    },
    "4. Limiting Factor (Post-Irrigation)": {
        "image": layers['irrigated_limiting'],
        "vis": vis_limiting,
        "legend_type": "categorical",
        "title": "4. Limiting Factor (Post-Irrigation)",
        "colors": limiting_colors,
        "labels": limiting_labels,
    },
    "1. Levelized Cost of Water (LCOW, $/m³)": {
        "image": layers['lcow'],
        "vis": vis_lcow,
        "legend_type": "gradient",
        "title": "Levelized cost of water",
        "palette": vis_lcow['palette'],
        "min_lbl": "≤ \\$0.25/m³",
        "max_lbl": "≥ \\$2.00/m³",
        "center_label": "\\$0.80/m³",
    },
    "2. Water Source Selection (Surface vs. Groundwater)": {
        "image": layers['water_source'],
        "vis": vis_water_source,
        "legend_type": "categorical",
        "title": "2. Water Source Selection (Surface vs. Groundwater)",
        "colors": ['#a6cee3', '#1f78b4'],
        "labels": ['Surface water', 'Groundwater'],
    },
    "3. Aquifer Depth to Groundwater (m)": {
        "image": layers['gw_depth'],
        "vis": vis_gw_depth,
        "legend_type": "gradient",
        "title": "Groundwater aquifer depth",
        "palette": vis_gw_depth['palette'],
        "min_lbl": "3 m (Shallow)",
        "max_lbl": "150 m (Deep)",
    },
    "4. WRI Projected Water Stress (2050)": {
        "image": layers['water_stress'],
        "vis": vis_water_stress,
        "legend_type": "categorical",
        "title": "4. WRI Projected Water Stress (2050)",
        "colors": water_stress_colors,
        "labels": water_stress_labels,
    },
}


# ==============================================================================
# 5. SIDEBAR SELECTION (CARS/BLADE HIERARCHICAL STRUCTURE)
# ==============================================================================
st.sidebar.header("Scenario & layer controls")

scenario_mode = st.sidebar.select_slider(
    "Scenario horizon",
    options=[
        "Baseline Climatology (2000–2023)",
        "2050 SSP5-8.5 (Unmitigated)",
        "2050 SSP5-8.5 (Irrigated Adaptation)"
    ]
)

if scenario_mode == "Baseline Climatology (2000–2023)":
    active_layer = st.sidebar.radio(
        "Active map layer",
        [
            "1. Baseline Suitability Score (0–100)",
            "2. Limiting Factor (Baseline)"
        ]
    )

elif scenario_mode == "2050 SSP5-8.5 (Unmitigated)":
    active_layer = st.sidebar.radio(
        "Active map layer",
        [
            "1. Future Suitability (2050 SSP5-8.5)",
            "2. Delta Suitability (Future - Baseline)",
            "3. Limiting Factor (Future 2050)"
        ]
    )

elif scenario_mode == "2050 SSP5-8.5 (Irrigated Adaptation)":
    adaptation_domain = st.sidebar.radio(
        "Analysis domain",
        ["Biophysical Recovery", "Techno-Economic & Hydrology"]
    )

    if adaptation_domain == "Biophysical Recovery":
        active_layer = st.sidebar.radio(
            "Active map layer",
            [
                "1. Irrigated Suitability (2050)",
                "2. Points Recovered via Irrigation",
                "3. Irrigation Budget Need (mm)",
                "4. Limiting Factor (Post-Irrigation)"
            ]
        )
    else:
        active_layer = st.sidebar.radio(
            "Active map layer",
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

layer_cfg = LAYER_REGISTRY.get(active_layer)
if layer_cfg:
    add_ee_layer(m, layer_cfg["image"], layer_cfg["vis"], active_layer)


# ==============================================================================
# 7. COUNTRY ZONAL ANALYTICS ENGINE
# ==============================================================================
# LSIB country name mappings to coffee_adaptation_matrix.csv country names
LSIB_TO_CSV_COUNTRY = {
    'Bahamas, The': 'Bahamas',
    'Central African Rep': 'Central African Rep.',
    'Rep of the Congo': 'Congo',
    'Cote d\'Ivoire': 'Côte d\'Ivoire',
    'Dem Rep of the Congo': 'Dem. Rep. Congo',
    'Dominican Republic': 'Dominican Rep.',
    'Laos': 'Lao PDR',
    'Burma': 'Myanmar',
    'Trinidad & Tobago': 'Trinidad and Tobago',
}


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
        # Filter out unphysical sentinel dummy values (>= 9999 $/m³ penalty values burned into
        # unviable pixels with no aquifer and no surface river) so they do not corrupt the national mean
        lcow_clean = assets['lcow'].updateMask(assets['lcow'].lte(50.0))

        # Mask irrigation layers by viable Arabica footprint to avoid diluting
        # spatial means with non-coffee pixels (deserts, mountains, urban)
        viable_mask = assets['nat_suit_base'].gt(0)

        stats_stack = ee.Image([
            assets['nat_suit_base'].rename('base_suit'),
            assets['nat_suit_fut'].rename('fut_suit'),
            assets['nat_suit_irrig'].rename('irrig_suit'),
            assets['delta_nat_suit'].rename('delta_suit'),
            assets['delta_irrigation_benefit'].updateMask(viable_mask).rename('irrig_benefit'),
            assets['local_irrigation_budget'].updateMask(viable_mask).rename('water_need'),
            lcow_clean.rename('lcow'),
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

        # Harmonize LCOW with the authoritative thesis adaptation matrix CSV.
        # Live 10km GEE reduction suffers from boundary grid resampling variances.
        # Looking up the country in coffee_adaptation_matrix.csv guarantees 100%
        # parity between Country Zonal Analytics and the Comparative Advantage Matrix.
        csv_country = LSIB_TO_CSV_COUNTRY.get(country_name, country_name)
        lcow_val = stats.get('lcow')
        display_country = country_name

        if os.path.exists(CSV_PATH):
            mdf = load_matrix_csv(os.path.getmtime(CSV_PATH))
            if mdf is not None:
                match = mdf[mdf['country'] == csv_country]
                if not match.empty:
                    lcow_val = float(match.iloc[0]['avg_lcow'])
                    display_country = str(match.iloc[0]['country'])

        return {
            'country': display_country,
            'base_suit': stats.get('base_suit'),
            'fut_suit': stats.get('fut_suit'),
            'irrig_suit': stats.get('irrig_suit'),
            'delta_suit': stats.get('delta_suit'),
            'irrig_benefit': stats.get('irrig_benefit'),
            'water_need': stats.get('water_need'),
            'lcow': lcow_val,
            'gw_depth': stats.get('gw_depth'),
            'water_source': stats.get('water_source'),
            'water_stress': stats.get('water_stress')
        }
    except Exception as e:
        return {"error": str(e)}


@st.cache_data(show_spinner=False)
def get_incumbent_zonal_medians():
    """
    Returns the median zonal statistics across the Top-10 Incumbent coffee-producing
    nations (Brazil, Vietnam, Colombia, Ethiopia, Honduras, Peru, Mexico,
    Guatemala, Nicaragua, Indonesia) computed across the pre-computed GEE stacks
    at 10 km resolution across viable Arabica pixels.
    """
    return {
        'base_suit': 33.0095,
        'fut_suit': 31.1995,
        'irrig_suit': 30.7900,
        'delta_suit': -11.4755,
        'irrig_benefit': 1.3473,
        'water_need': 13.3989,
        'lcow': 0.9696,
        'gw_depth': 33.4160,
        'water_source': 1.1365,
        'water_stress': 1.7710,
    }


# R3: Theme-adaptive legend rendering (uses inherited text color instead of
# hardcoded #ffffff so the legend works in both light and dark themes).
def render_st_gradient(label, palette, min_label, max_label, center_label=None):
    """Renders a continuous gradient bar with theme-adaptive styling."""
    grad = ", ".join(palette)
    center_html = f"<span>{center_label}</span>" if center_label else ""
    st.markdown(
        f"""
        <div style="margin-bottom: 14px;">
            <div style="font-size: 13px; font-weight: 600; margin-bottom: 4px;">{label}</div>
            <div style="width: 100%; height: 14px; background: linear-gradient(to right, {grad}); border: 1px solid #777; border-radius: 3px;"></div>
            <div style="display: flex; justify-content: space-between; font-size: 11px; margin-top: 3px; opacity: 0.75;">
                <span>{min_label}</span>{center_html}<span>{max_label}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_categorical_legend(title, colors, labels):
    """Renders a categorical legend with color swatches (theme-adaptive text)."""
    st.markdown(f"**{title}**")
    for c, lbl in zip(colors, labels):
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span style="background: {c}; width: 13px; height: 13px; display: inline-block; margin-right: 8px; border: 1px solid #777; border-radius: 2px;"></span>
                <span style="font-size: 12px;">{lbl}</span>
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
    raw_lat = click.get("lat")
    raw_lon = click.get("lng") if click.get("lng") is not None else click.get("lon")
    if raw_lat is not None and raw_lon is not None:
        st.session_state.selected_coords = {"lat": raw_lat, "lon": raw_lon}
        st.session_state.map_center = [raw_lat, raw_lon]

with col_legend:
    # C2: Visual enclosure — legend section in bordered container
    with st.container(border=True):
        st.markdown("**Active layer legend**")

        if layer_cfg:
            if layer_cfg["legend_type"] == "gradient":
                render_st_gradient(
                    layer_cfg["title"],
                    layer_cfg["palette"],
                    layer_cfg["min_lbl"],
                    layer_cfg["max_lbl"],
                    center_label=layer_cfg.get("center_label")
                )
            elif layer_cfg["legend_type"] == "categorical":
                render_categorical_legend(
                    layer_cfg["title"],
                    layer_cfg["colors"],
                    layer_cfg["labels"]
                )


    # C2: Visual enclosure — zonal analytics section
    with st.container(border=True):
        st.markdown("**Country zonal analytics**")

        active_coords = st.session_state.get("selected_coords")

        if active_coords:
            lat = active_coords.get("lat")
            lon = active_coords.get("lon")

            if lat is not None and lon is not None:
                with st.spinner(
                    f"Computing zonal metrics for ({lat:.2f}, {lon:.2f})..."
                ):
                    data = compute_country_stats(lat, lon)

                if data and "error" in data:
                    st.error(f"Computation failed: {data['error']}")
                elif data and data.get('country'):
                    col_title, col_clear = st.columns([3.2, 1.2])
                    with col_title:
                        st.success(f"**{data['country']}**")
                    with col_clear:
                        if st.button("Clear", key="btn_clear_country", help="Clear selected country"):
                            st.session_state.pop("selected_coords", None)
                            st.rerun()

                    def is_valid_num(val):
                        if val is None:
                            return False
                        try:
                            f = float(val)
                            return not math.isnan(f)
                        except (ValueError, TypeError):
                            return False

                    def render_zonal_metric_with_badge(
                        label,
                        val,
                        inc_val,
                        unit="",
                        decimals=1,
                        higher_is_better=True,
                        is_neutral=False,
                        delta_text=None,
                        badge_label="Incumbent med",
                        is_currency=False,
                    ):
                        if not is_valid_num(val):
                            st.metric(label, "N/A")
                            return

                        val_f = float(val)
                        if is_currency:
                            val_str = f"${val_f:.{decimals}f}{unit}"
                        else:
                            val_str = f"{val_f:.{decimals}f} {unit}".strip()

                        st.metric(label, val_str, delta=delta_text)

                        if inc_val is not None and is_valid_num(inc_val):
                            inc_f = float(inc_val)
                            diff = val_f - inc_f
                            if is_currency:
                                sign = "+" if diff > 0 else ("-" if diff < 0 else "")
                                diff_str = f"{sign}${abs(diff):.{decimals}f}{unit}"
                                inc_str = f"${inc_f:.{decimals}f}{unit}"
                            else:
                                diff_str = f"{diff:+.{decimals}f} {unit}".strip()
                                inc_str = f"{inc_f:.{decimals}f} {unit}".strip()

                            render_incumbent_badge(
                                val=val_f,
                                inc_val=inc_f,
                                inc_str=inc_str,
                                diff_str=diff_str,
                                label=badge_label,
                                higher_is_better=higher_is_better,
                                is_neutral=is_neutral,
                            )

                    inc_zonal = get_incumbent_zonal_medians()

                    tab_bio, tab_econ = st.tabs([
                        ":material/eco: Biophysical",
                        ":material/payments: Techno-economic",
                    ])

                    # ======================================================
                    # B1: Adaptation pathway delta bridge + Incumbent comparison
                    # Shows Baseline → Climate Loss → Recovery as a flow
                    # ======================================================
                    with tab_bio:
                        st.caption(
                            "**Adaptation pathway** · Badges compare against "
                            "**Top-10 Incumbents' median** "
                            "(:green[green = better than incumbent], :red[red = worse than incumbent])"
                        )

                        # Step 1: Baseline suitability vs. Incumbents' Baseline Median (higher is better)
                        render_zonal_metric_with_badge(
                            "Baseline suitability",
                            data['base_suit'],
                            inc_zonal['base_suit'],
                            unit="pts",
                            decimals=1,
                            higher_is_better=True,
                            badge_label="Incumbent baseline med",
                        )

                        # Step 2: Climate impact (2050) vs. Incumbents' 2050 Median (higher is better)
                        delta_val = data['delta_suit']
                        survivor_diff = (
                            (data['fut_suit'] - data['base_suit'])
                            if (data['fut_suit'] is not None and data['base_suit'] is not None)
                            else None
                        )
                        delta_text = (
                            f"{survivor_diff:+.1f} pts"
                            if survivor_diff is not None else None
                        )
                        render_zonal_metric_with_badge(
                            "After climate change (2050)",
                            data['fut_suit'],
                            inc_zonal['fut_suit'],
                            unit="pts",
                            decimals=1,
                            higher_is_better=True,
                            delta_text=delta_text,
                            badge_label="Incumbent 2050 med",
                        )
                        if delta_val is not None:
                            st.caption(
                                f":material/public: **Net landscape shift:** `{delta_val:+.1f} pts` "
                                f"(accounts for acreage completely lost to $0$, whereas metric above tracks surviving acreage only)"
                            )

                        # Step 3: Irrigation recovery vs. Incumbents' Irrigated Median (higher is better)
                        benefit = data['irrig_benefit']
                        recovery_note = ""
                        # Only compute recovery percentage when there was a net climate suitability deficit (delta_val < 0)
                        if (
                            benefit is not None
                            and delta_val is not None
                            and delta_val < 0
                        ):
                            pct = (benefit / abs(delta_val)) * 100
                            recovery_note = f" ({pct:.0f}%)"

                        if benefit is not None:
                            if delta_val is not None and delta_val < 0:
                                delta_text = f"+{benefit:.1f} pts recovered{recovery_note}"
                            else:
                                delta_text = f"+{benefit:.1f} pts added"
                        else:
                            delta_text = None

                        render_zonal_metric_with_badge(
                            "After irrigation adaptation",
                            data['irrig_suit'],
                            inc_zonal['irrig_suit'],
                            unit="pts",
                            decimals=1,
                            higher_is_better=True,
                            delta_text=delta_text,
                            badge_label="Incumbent irrigated med",
                        )

                        st.markdown("---")
                        # Step 4: Mean water deficit vs. Incumbents' Deficit Median (lower is better)
                        render_zonal_metric_with_badge(
                            "Mean water deficit",
                            data['water_need'],
                            inc_zonal['water_need'],
                            unit="mm",
                            decimals=1,
                            higher_is_better=False,
                            badge_label="Incumbent deficit med",
                        )

                    # ======================================================
                    # S2: Techno-economic metrics + Incumbent comparison
                    # ======================================================
                    with tab_econ:
                        st.caption(
                            "**Hydrology & cost** · Badges compare against "
                            "**Top-10 Incumbents' median** "
                            "(:green[green = better than incumbent], :red[red = worse than incumbent])"
                        )

                        # 1. Avg LCOW vs. Incumbents' LCOW Median (lower is better)
                        render_zonal_metric_with_badge(
                            "Avg LCOW",
                            data.get('lcow'),
                            inc_zonal['lcow'],
                            unit="/m³",
                            decimals=2,
                            higher_is_better=False,
                            is_currency=True,
                            badge_label="Incumbent med",
                        )

                        # 2. Mean Aquifer Depth vs. Incumbents' Aquifer Depth Median (lower/shallower is better)
                        render_zonal_metric_with_badge(
                            "Mean Aquifer Depth",
                            data.get('gw_depth'),
                            inc_zonal['gw_depth'],
                            unit="m",
                            decimals=1,
                            higher_is_better=False,
                            badge_label="Incumbent depth med",
                        )


                        # 3. Dominant Water Source vs. Incumbents' Groundwater Share Median (neutral gray badge)
                        has_water_source = is_valid_num(data.get('water_source'))
                        if has_water_source:
                            # Mean of 1.0 = 100% Groundwater, Mean of 2.0 = 100% Surface Water
                            mean_val = float(data['water_source'])
                            gw_pct = max(0.0, min(100.0, (2.0 - mean_val) * 100.0))
                            sw_pct = 100.0 - gw_pct
                            primary_type = "Groundwater" if gw_pct >= 50.0 else "Surface Water"
                            st.metric(
                                "Dominant source",
                                primary_type,
                                delta=f"{gw_pct:.0f}% Ground · {sw_pct:.0f}% Surface",
                                delta_color="off"
                            )
                            inc_gw_pct = max(0.0, min(100.0, (2.0 - inc_zonal['water_source']) * 100.0))
                            inc_sw_pct = 100.0 - inc_gw_pct
                            diff_gw = gw_pct - inc_gw_pct
                            render_incumbent_badge(
                                val=gw_pct,
                                inc_val=inc_gw_pct,
                                inc_str=f"{inc_gw_pct:.0f}% Ground · {inc_sw_pct:.0f}% Surface",
                                diff_str=f"{diff_gw:+.0f}% Ground",
                                label="Incumbent med",
                                is_neutral=True,
                            )
                        else:
                            st.metric("Dominant source", "N/A")

                        # 4. Color-Coded WRI Water Stress + Incumbent comparison (lower is better)
                        st.markdown("<div style='font-size: 14px; opacity: 0.8; margin-top: 14px; margin-bottom: 4px;'>WRI water stress</div>", unsafe_allow_html=True)

                        has_water_stress = is_valid_num(data.get('water_stress'))
                        if has_water_stress:
                            # Constrain category index to 0..4
                            raw_idx = int(round(float(data['water_stress'])))
                            stress_idx = max(0, min(4, raw_idx))
                            # Match exact palette & labels from your legend definitions (0-indexed)
                            badge_color = water_stress_colors[stress_idx]
                            full_label = water_stress_labels[stress_idx]
                            # Ensure legible contrast (dark text on light green/yellow, white on dark)
                            text_color = "#111111" if stress_idx in [1, 2] else "#ffffff"
                            st.markdown(
                                f"""
                                <div style="
                                    display: inline-flex;
                                    align-items: center;
                                    gap: 8px;
                                    background-color: {badge_color};
                                    color: {text_color};
                                    padding: 6px 12px;
                                    border-radius: 6px;
                                    font-weight: 700;
                                    font-size: 15px;
                                    line-height: 1.3;
                                    word-break: break-word;
                                    max-width: 100%;
                                    border: 1px solid rgba(0,0,0,0.25);
                                    margin-bottom: 14px;
                                ">
                                    <span style="
                                        width: 9px;
                                        height: 9px;
                                        border-radius: 50%;
                                        background-color: {text_color};
                                        display: inline-block;
                                        flex-shrink: 0;
                                    "></span>
                                    <span>{full_label}</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            inc_stress = inc_zonal['water_stress']
                            inc_stress_idx = max(0, min(4, int(round(inc_stress))))
                            inc_stress_label = water_stress_labels[inc_stress_idx]
                            diff_stress = float(data['water_stress']) - inc_stress
                            render_incumbent_badge(
                                val=float(data['water_stress']),
                                inc_val=inc_stress,
                                inc_str=f"{inc_stress:.1f} ({inc_stress_label})",
                                diff_str=f"{diff_stress:+.1f} idx",
                                label="Incumbent stress med",
                                higher_is_better=False,
                            )
                        else:
                            st.markdown("<span style='font-size: 18px; font-weight: 600;'>N/A</span>", unsafe_allow_html=True)

                        # C3: Data quality caveat
                        st.caption(
                            ":material/info: Statistics represent spatial means "
                            "across viable Arabica pixels within national borders, "
                            "not national agricultural averages."
                        )
                else:
                    st.warning(
                        "Clicked point is outside recognized boundaries."
                    )
        else:
            st.caption(
                "Click any country on the map to trigger spatial "
                "zonal statistics."
            )

# ==============================================================================
# 9. STRATEGIC DECISION MATRIX (CARS / BLADE PORTFOLIO VIEW)
# Only displayed under Irrigated Adaptation (Scenario 3)
# ==============================================================================
if scenario_mode == "2050 SSP5-8.5 (Irrigated Adaptation)":
    st.markdown("---")
    # S1: Full-sentence "so what" anchor title
    st.subheader(
        "The adaptation premium reveals sharp regional divergence "
        "in irrigation economics"
    )
    st.markdown(
        "Synthesizing biophysical irrigation needs with localized "
        "infrastructure levelized cost of water (LCOW) calculated "
        "dynamically for viable coffee adaptation zones."
    )

    # Contextual explanation of the Top-10 Incumbents benchmark before the matrix
    with st.container(border=True):
        benchmarks = get_incumbent_benchmarks()
        bench_lcow_str = f"${benchmarks['lcow']:.2f}/m³"
        bench_deficit_str = f"{benchmarks['deficit']:,.0f} m³/ha"

        st.markdown(
            ":material/workspace_premium: **Understanding the Incumbent Benchmark (Top-10 Producers)**\n\n"
            "**Who are the incumbents?** The *Incumbents* comprise the ten dominant historical coffee-exporting nations — "
            "**Brazil, Vietnam, Colombia, Ethiopia, Honduras, Peru, Mexico, Guatemala, Nicaragua, and Indonesia**. "
            "Together, these origins account for nearly **85–90% of global coffee supply** and concentrate the industry's "
            "established dry-milling capacity, export logistics, agronomic institutional knowledge, and trade finance networks.\n\n"
            "**Why use the incumbents' median as the comparison benchmark?**\n"
            f"- **Industry Cost & Volume Threshold:** The incumbents' median establishes the empirical competitive baseline "
            f"for unit water cost (**LCOW: \\{bench_lcow_str}**) and volumetric irrigation demand (**{bench_deficit_str}**) across active supply chains.\n"
            "- **Supply-Chain Retention vs. Frontier Reallocation:** Incumbent origins operating **below** the incumbent median "
            "(:green[green]) possess a structural cost or hydrological buffer to defend market share through irrigation investment. "
            "Conversely, origins operating **above** the incumbent median (:red[red]) face margin compression — while emerging "
            "climate-viable frontier nations must undercut these incumbent thresholds to justify shifting long-term capital away from established coffee regions."
        )

    render_dynamic_comparative_advantage_matrix()