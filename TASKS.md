# Engineering Audit & Agent Task Registry

This registry tracks identified bugs, edge cases, and code-leaner refactoring opportunities across the **Coffee-Streamlit** codebase (`coffee_app.py` and `matrix_analytics.py`).

Tasks are formatted for direct execution by an autonomous coding agent. Each task contains the root cause, target files with line links, step-by-step resolution plan, and acceptance criteria.

---

## Task Summary Dashboard

### Bugs & Edge Cases (Reliability & Correctness)
- [ ] **[BUG-01]** Graceful handling of Earth Engine authentication failures ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L79-L91) · [#2](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/2))
- [ ] **[BUG-02]** Earth Engine tile fetcher error handling in `add_ee_layer` ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L102-L114) · [#3](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/3))
- [ ] **[BUG-03]** Fix non-viable pixel dilution from `.unmask(0)` in zonal reduction ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L363-L364) · [#4](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/4))
- [ ] **[BUG-04]** Preserve selected country zonal statistics across map layer switches ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L475-L487) · [#5](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/5))
- [ ] **[BUG-05]** Fix Prime Meridian `lon=0.0` truthiness check in click coordinates ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L550) · [#6](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/6))
- [ ] **[BUG-06]** Fix false recovery percentage when climate change yields positive delta ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L640-L646) · [#7](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/7))
- [ ] **[BUG-07]** Guard against NaN in `lcow` preventing `$nan/m³` display and invalid badge diffs ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L698-L707) · [#8](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/8))
- [ ] **[BUG-08]** Guard against NaN in `water_source` preventing `nan%` calculations ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L733-L736) · [#9](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/9))
- [ ] **[BUG-09]** Prevent `ValueError` crash on `int(round(nan))` when `water_stress` is NaN ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L762-L763) · [#10](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/10))
- [ ] **[BUG-10]** Robust fallback for incumbent medians when CSV columns contain NaN or missing countries ([matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L331-L335) · [#11](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/11))
- [ ] **[BUG-11]** Fix pandas Series `.get()` returning NaN instead of default fallback ([matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L403-L407) · [#12](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/12))
- [ ] **[BUG-12]** Prevent Plotly annotation overlap between reference lines and quadrant archetype labels ([matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L460-L519) · [#13](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/13))

### Code Leaner & Refactoring (Simplification & Maintainability)
- [ ] **[LEAN-01]** Purge unused imports (`Element`, `get_global_medians`, `DEFAULT_COUNTRIES`, `statistics`) ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L4), [matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L6) · [#14](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/14))
- [ ] **[LEAN-02]** Replace brittle DOM test-id CSS injection with native layout configs ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L25-L54) · [#15](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/15))
- [ ] **[LEAN-03]** Consolidate 12-branch map layer and 9-branch legend dispatch into declarative `LAYER_REGISTRY` ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L289-L317) · [#16](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/16))
- [ ] **[LEAN-04]** Unify repetitive metric card + incumbent badge boilerplate into reusable helper ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L588-L683) · [#17](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/17))
- [ ] **[LEAN-05]** Eliminate hardcoded incumbent values in prose and harmonize with CSV constants ([coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L851-L863) · [#18](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/18))
- [ ] **[LEAN-06]** Eliminate dead function `get_global_medians` ([matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L68-L94) · [#19](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/19))
- [ ] **[LEAN-07]** Consolidate 6 duplicate magnitude formatting functions into one compact utility ([matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L97-L174) · [#20](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/20))
- [ ] **[LEAN-08]** Make Plotly matrix theme-adaptive or transparent to avoid light mode visual clash ([matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L557-L570) · [#21](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/21))
- [ ] **[LEAN-09]** Streamline expander drill-down cards with data-driven loop ([matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L617-L688) · [#22](https://github.com/VitorKupidlowsky/Coffee-Streamlit/issues/22))

---

## Detailed Task Specifications

### [BUG-01] Graceful handling of Earth Engine authentication failures
- **Priority**: High
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L79-L91)
- **Problem**: Calling `ee.Initialize()` directly at module import causes an unhandled exception that crashes the entire Streamlit application if Google Application Default Credentials (ADC) are not set or expired.
- **Remediation**:
  Wrap `initialize_ee()` in a graceful check. If initialization fails, display `st.error("Earth Engine authentication required.")` with instructions (`earthengine authenticate`) and stop further execution (`st.stop()`) instead of dumping an unhandled stack trace.
- **Acceptance Criteria**: App displays a clear user-facing error message with remediation steps instead of an uncaught traceback when credentials are missing.

---

### [BUG-02] Earth Engine tile fetcher error handling in `add_ee_layer`
- **Priority**: Medium
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L102-L114)
- **Problem**: `ee.Image(ee_image).getMapId(vis_params)` can fail due to network interruptions, Google API quota limits, or invalid visualization parameters. This halts execution during Folium map generation.
- **Remediation**:
  Wrap `getMapId` and `folium.TileLayer` in a `try...except Exception as e:` block. Log or display an `st.warning(f"Could not load layer '{name}': {e}")` and allow the base map to render.
- **Acceptance Criteria**: Map loads with available layers even if an individual Earth Engine layer tile request fails.

---

### [BUG-03] Fix non-viable pixel dilution from `.unmask(0)` in zonal reduction
- **Priority**: High
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L363-L364)
- **Problem**:
  In `compute_country_stats`:
  ```python
  assets['delta_irrigation_benefit'].unmask(0).rename('irrig_benefit'),
  assets['local_irrigation_budget'].unmask(0).rename('water_need'),
  ```
  Calling `.unmask(0)` unmasks all pixels in the entire national bounding geometry (including deserts, cities, and non-viable land) with value `0`. When `ee.Reducer.mean()` executes over `country_geom`, all zero-value non-coffee pixels are factored into the average, artificially diluting the country's mean water deficit from ~100 mm to ~7.5 mm.
  Note that line 816 claims: *"Statistics represent spatial means across viable Arabica pixels within national borders"*.
- **Remediation**:
  Mask the image with the viable coffee mask before computing the mean, or unmask only within the viable coffee footprint mask rather than across the whole national polygon.
- **Acceptance Criteria**: `water_need` and `irrig_benefit` represent true spatial means across viable coffee acreage, harmonizing with thesis numbers (~1,004 m³/ha = ~100.4 mm).

---

### [BUG-04] Preserve selected country zonal statistics across map layer switches
- **Priority**: High (UX / Usability)
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L475-L487)
- **Problem**:
  The Folium map uses `key=f"coffee_map_{active_layer}"`. Whenever the user selects a new layer or scenario, the key changes. Streamlit unmounts the previous iframe and mounts a new one, resetting `map_output["last_clicked"]` to `None`. This wipes out the country zonal analytics panel, resetting it to `"Click any country on the map to trigger spatial zonal statistics."` and forcing the user to re-click the country.
- **Remediation**:
  Store the selected country information or `(lat, lon)` in `st.session_state["selected_coords"]` and/or `st.session_state["selected_country_stats"]`. When `active_layer` changes, read from session state so the zonal panel persists while switching between map layers.
- **Acceptance Criteria**: A user can click a country (e.g. Colombia), view its stats, and switch layers (e.g. from Suitability to LCOW) without losing the country stats display.

---

### [BUG-05] Fix Prime Meridian `lon=0.0` truthiness check in click coordinates
- **Priority**: Low / Edge Case
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L550)
- **Problem**:
  ```python
  lon = click_data.get("lng") or click_data.get("lon")
  ```
  In Python, `0.0 or None` evaluates to `None`. If a user clicks at `lon=0.0` (Prime Meridian, e.g. Ghana, UK, Togo, Burkina Faso), `click_data.get("lng")` is `0.0`. The `or` expression skips `0.0` and falls back to `click_data.get("lon")`. If `lon` is also absent, it evaluates to `None`, causing clicks along longitude 0 to fail.
- **Remediation**:
  Use explicit `None` checks:
  ```python
  lon = click_data.get("lng") if click_data.get("lng") is not None else click_data.get("lon")
  ```
- **Acceptance Criteria**: Clicking on countries intersecting `lon=0.0` reliably triggers zonal computation.

---

### [BUG-06] Fix false recovery percentage when climate change yields positive delta
- **Priority**: Medium
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L640-L646)
- **Problem**:
  ```python
  if benefit is not None and delta_val is not None and delta_val != 0:
      pct = abs(benefit / delta_val) * 100
      recovery_note = f" ({pct:.0f}%)"
  ```
  If `delta_val > 0` (warming actually increased climate suitability in cooler high-elevation zones), dividing `benefit / delta_val` and labeling it as "recovered %" is invalid because no suitability was lost.
- **Remediation**:
  Only calculate `recovery_note` when `delta_val < 0`:
  ```python
  if benefit is not None and delta_val is not None and delta_val < 0:
      pct = (benefit / abs(delta_val)) * 100
      recovery_note = f" ({pct:.0f}%)"
  ```
- **Acceptance Criteria**: Recovery percentage is only displayed when a country suffers a climate suitability deficit.

---

### [BUG-07] Guard against NaN in `lcow` preventing `$nan/m³` display and invalid badge diffs
- **Priority**: Medium
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L698-L707)
- **Problem**:
  If `data['lcow']` is `NaN`, `data['lcow'] is not None` is `True`. The metric formats as `"$nan/m³"`. The difference `diff_lcow` evaluates to `NaN`, causing `lcow_diff_str` to format as `"$nan/m³"`.
- **Remediation**:
  Use `pd.notna(data['lcow'])` instead of `data['lcow'] is not None`:
  ```python
  has_lcow = data['lcow'] is not None and pd.notna(data['lcow'])
  st.metric("Avg LCOW", f"${data['lcow']:.2f}/m³" if has_lcow else "N/A")
  ```
- **Acceptance Criteria**: Missing or uncalculated LCOW values display as `"N/A"` without any `$nan` artifacts.

---

### [BUG-08] Guard against NaN in `water_source` preventing `nan%` calculations
- **Priority**: Medium
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L733-L736)
- **Problem**:
  If `data['water_source']` is `NaN`, Python's `min(100.0, max(0.0, (2.0 - mean_val) * 100.0))` returns `NaN`. Formatting `f"{gw_pct:.0f}%"` outputs `"nan% Ground · nan% Surface"`.
- **Remediation**:
  Check `pd.notna(data['water_source'])` before computing groundwater/surface water proportions. If NaN, render `"N/A"`.
- **Acceptance Criteria**: Countries with no water source raster data display `"N/A"` cleanly.

---

### [BUG-09] Prevent `ValueError` crash on `int(round(nan))` when `water_stress` is NaN
- **Priority**: High
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L762-L763)
- **Problem**:
  ```python
  if data['water_stress'] is not None:
      raw_idx = int(round(data['water_stress']))
  ```
  If `data['water_stress']` is `float('nan')`, `data['water_stress'] is not None` evaluates to `True`. Calling `round(float('nan'))` returns `NaN`. Calling `int(NaN)` raises `ValueError: cannot convert float NaN to integer`, crashing the entire application.
- **Remediation**:
  Check `if data['water_stress'] is not None and pd.notna(data['water_stress']):`.
- **Acceptance Criteria**: Clicking on any region with missing water stress data renders `"N/A"` instead of throwing a `ValueError`.

---

### [BUG-10] Robust fallback for incumbent medians when CSV columns contain NaN or missing countries
- **Priority**: High
- **Files**: [matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L331-L335), [L580-L582](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L580-L582)
- **Problem**:
  `incumbent_df` calculates medians across `total_exposure`, `total_viable_ha`, and `total_m3` without verifying that these columns exist or that `incumbent_df` contains non-empty rows. If any column is missing or all rows are NaN, `median()` returns `NaN`, causing `float(np.nan)` to propagate `NaN` into Plotly reference lines (`add_vline(x=nan)`) and badge diffs.
- **Remediation**:
  Add defensive checks with known thesis fallback constants if `incumbent_df.empty` or columns are NaN:
  - `incumbent_lcow`: fallback `0.9696`
  - `incumbent_deficit`: fallback `1004.0`
  - `inc_exposure`: fallback `3384322371.0`
  - `inc_viable_ha`: fallback `11878955.0`
  - `inc_total_m3`: fallback `10016459944.0`
- **Acceptance Criteria**: The matrix renders without error even if the CSV dataset has missing incumbent rows or columns.

---

### [BUG-11] Fix pandas Series `.get()` returning NaN instead of default fallback
- **Priority**: Medium
- **Files**: [matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L403-L407), [L610-L612](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L610-L612)
- **Problem**:
  In pandas, `row.get('col', default)` returns the cell value if `'col'` is present in `df.columns`. If the cell value is `NaN`, `.get()` returns `NaN`, NOT the default value! Subsequent string formatting like `f"{area_display}M ha"` or `float(row.get('total_exposure', 0))` produces `NaN` or crashes.
- **Remediation**:
  Use `pd.notna()`:
  ```python
  val = row.get('total_exposure')
  exposure = float(val) if pd.notna(val) else 0.0
  ```
- **Acceptance Criteria**: Drill-down cards and hover templates never display `NaN` when an individual cell is blank.

---

### [BUG-12] Prevent Plotly annotation overlap between reference lines and quadrant archetype labels
- **Priority**: Medium / Visual Polish
- **Files**: [matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L460-L519)
- **Problem**:
  Quadrant archetype labels are anchored in paper coordinates at the four corners: `(0.02, 0.02)`, `(0.02, 0.98)`, `(0.98, 0.02)`, `(0.98, 0.98)`.
  Reference line annotations are placed at `x=0.02, xref="paper", y=incumbent_deficit` and `x=0.98, xref="paper", y=y_mid`. If `incumbent_deficit` or `y_mid` falls near the bottom or top of the chart range, these annotations overlap directly with the quadrant labels.
- **Remediation**:
  Shift reference line badges inward along the lines (e.g. `x=0.15` and `x=0.85`), or anchor annotations directly onto the dashed lines using Plotly's native line annotation features.
- **Acceptance Criteria**: Reference line labels and quadrant labels never collide or overlap at any axis zoom level.

---

### [LEAN-01] Purge unused imports
- **Priority**: Low / Code Cleanliness
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L4), [L11-L12](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L11-L12); [matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L6)
- **Problem**:
  `coffee_app.py` imports `from branca.element import Element`, `DEFAULT_COUNTRIES`, and `get_global_medians` but never uses them. `matrix_analytics.py` imports `statistics` but never uses it.
- **Remediation**: Remove unused imports.
- **Acceptance Criteria**: No dead imports in either file; `flake8` / `pyflakes` runs clean on imports.

---

### [LEAN-02] Replace brittle DOM test-id CSS injection with native layout configs
- **Priority**: Medium
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L25-L54)
- **Problem**:
  The app injects custom CSS targeting `[data-testid="stMetricValue"]` and `[data-testid="stSliderTickBar"]` with `!important` absolute positioning. Streamlit DOM test IDs change across minor versions, risking broken layouts.
- **Remediation**:
  Per Streamlit guidelines, rely on native styling and `.streamlit/config.toml` where possible, or replace fragile selectors with scoped styling.
- **Acceptance Criteria**: App maintains clean sidebar and slider spacing without brittle test ID hacks.

---

### [LEAN-03] Consolidate 12-branch map layer and 9-branch legend dispatch into declarative `LAYER_REGISTRY`
- **Priority**: High / Architecture
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L289-L317), [L494-L540](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L494-L540)
- **Problem**:
  Both the map layer addition and legend rendering rely on large `if/elif` chains matching substrings like `"Baseline Suitability" in active_layer`. This is duplicate logic (~75 lines), error-prone, and hard to maintain.
- **Remediation**:
  Create a single dictionary mapping layer names to their configuration:
  ```python
  LAYER_CONFIG = {
      "1. Baseline Suitability Score (0–100)": {
          "layer": layers['nat_suit_base'],
          "vis": vis_suitability,
          "legend_type": "gradient",
          "min_lbl": "0 (Unsuitable)", "max_lbl": "100 (Optimal)"
      },
      ...
  }
  ```
  Map layer addition and legend rendering then become clean 5-line lookups.
- **Acceptance Criteria**: Adding or modifying a layer requires updating only one configuration dictionary.

---

### [LEAN-04] Unify repetitive metric card + incumbent badge boilerplate into reusable helper
- **Priority**: High / DRY
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L588-L683), [L696-L813](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L696-L813)
- **Problem**:
  The pattern of computing a metric, checking for None/NaN, calculating difference against incumbent median, formatting signed delta, and calling `render_incumbent_badge()` is repeated 8 times in `coffee_app.py` (~120 lines of repetitive code).
- **Remediation**:
  Create a unified helper:
  ```python
  def render_zonal_metric_with_badge(label, val, inc_val, unit="", decimals=1, higher_is_better=True, is_neutral=False, delta_text=None):
      ...
  ```
- **Acceptance Criteria**: Eliminates >80 lines of duplicate boilerplate; all badges render consistently.

---

### [LEAN-05] Eliminate hardcoded incumbent values in prose and harmonize with CSV constants
- **Priority**: Medium
- **Files**: [coffee_app.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/coffee_app.py#L851-L863)
- **Problem**:
  The explanatory container in `coffee_app.py` hardcodes: `LCOW: $0.97/m³` and `1,004 m³/ha`. If the matrix CSV is regenerated with updated model runs, this text will become out of sync with the chart.
- **Remediation**:
  Reference the incumbent medians dynamically in the markdown string via f-string or template variable.
- **Acceptance Criteria**: Benchmark description updates automatically if the underlying matrix dataset changes.

---

### [LEAN-06] Eliminate dead function `get_global_medians`
- **Priority**: Low / Dead Code
- **Files**: [matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L68-L94)
- **Problem**:
  `get_global_medians(modified_at)` is 27 lines of cached code that is never invoked anywhere in the codebase.
- **Remediation**: Remove the function or integrate it if needed.
- **Acceptance Criteria**: Dead function removed, reducing file size and cognitive overhead.

---

### [LEAN-07] Consolidate 6 duplicate magnitude formatting functions into one compact utility
- **Priority**: High / DRY
- **Files**: [matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L97-L174)
- **Problem**:
  `_format_exposure`, `_format_signed_exposure`, `_format_area`, `_format_signed_area`, `_format_water`, and `_format_signed_water` are 6 separate functions (~75 lines) that perform identical magnitude thresholding (`T`, `B`, `M`, `k`).
- **Remediation**:
  Replace all 6 with a single general-purpose formatter:
  ```python
  def format_magnitude(val, unit="", is_currency=False, signed=False, decimals=1):
      ...
  ```
- **Acceptance Criteria**: Reduces ~60 lines of code; all unit string formats (`$1.2B`, `+500k ha`, `10M m³`) are handled through one well-tested function.

---

### [LEAN-08] Make Plotly matrix theme-adaptive or transparent to avoid light mode visual clash
- **Priority**: Medium
- **Files**: [matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L557-L570)
- **Problem**:
  The Plotly figure layout hardcodes `plot_bgcolor="#18191c"` and `paper_bgcolor="#0e1117"`. If the user has Streamlit configured in light mode, the chart renders as a dark box inside a light page.
- **Remediation**:
  Use `paper_bgcolor="rgba(0,0,0,0)"` and `plot_bgcolor="rgba(0,0,0,0)"`, or check `st.context.theme` to adapt text and background colors dynamically.
- **Acceptance Criteria**: The chart seamlessly integrates into both dark and light Streamlit themes.

---

### [LEAN-09] Streamline expander drill-down cards with data-driven loop
- **Priority**: Medium / DRY
- **Files**: [matrix_analytics.py](file:///Users/vitorkupidlowsky/Documents/GitHub/Coffee-Streamlit/matrix_analytics.py#L617-L688)
- **Problem**:
  The drill-down expander repeats `st.metric()` and `render_incumbent_badge()` across 5 separate metrics in 70 lines of verbose code.
- **Remediation**:
  Iterate over a declarative list of metric specifications:
  ```python
  metrics_to_render = [
      ("National adaptation exposure", exposure, inc_exposure, True, False),
      ("Total viable footprint", viable_ha, inc_viable_ha, False, True),
      ...
  ]
  ```
- **Acceptance Criteria**: Expander card logic is concise, readable, and easy to extend.

---

## Instructions for Agents
When an agent is assigned to resolve any of these tasks:
1. Search the codebase for the corresponding `# TODO(agent-task: <TASK-ID>)` tag.
2. Implement the changes following the specifications in this file.
3. Test the application with `./.venv/bin/streamlit run coffee_app.py` or unit tests.
4. Mark the task as completed in the checklist above (`- [x] **[TASK-ID]**`).
