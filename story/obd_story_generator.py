import os
import json
import time
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import contextily as cx
from google import genai
from google.genai import types
from geopy.geocoders import GoogleV3

def reverse_geocode(lat: float, lon: float, api_key: str) -> str:
    """
    Reverse geocodes lat/lon using Google Maps API.
    """
    if not api_key:
        return f"Coordinates: {lat:.6f}, {lon:.6f}"
    
    try:
        # Rate limit safety
        time.sleep(0.5)
        geolocator = GoogleV3(api_key=api_key)
        location = geolocator.reverse((lat, lon), exactly_one=True)
        if location:
            return location.address
        return f"Coordinates: {lat:.6f}, {lon:.6f}"
    except Exception as e:
        print(f"[ERROR] Reverse geocoding failed: {e}")
        return f"Coordinates: {lat:.6f}, {lon:.6f}"

def analyze_obd_data(csv_path: str) -> dict:

    df = pd.read_csv(csv_path)
    # Parse timestamp
    df['datetime'] = pd.to_datetime(df['timestamp'], format='%d/%m/%y %H:%M', errors='coerce')
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # 1. Start & End
    start_row = df.iloc[0]
    end_row = df.iloc[-1]
    
    # 2. Max Speed
    speed_col = 'Ταχύτητα οχήματος'
    max_speed_idx = df[speed_col].idxmax()
    max_speed_row = df.loc[max_speed_idx]
    
    # 3. Max RPM
    rpm_col = 'Στροφές κινητήρα' if 'Στροφές κινητήρα' in df.columns else None
    if rpm_col and not df[rpm_col].dropna().empty:
        max_rpm_idx = df[rpm_col].idxmax()
        max_rpm_row = df.loc[max_rpm_idx]
    else:
        max_rpm_row = None
        
    # 4. Stops (defined as segments where OBD data is missing/null)
    obd_missing_mask = df[rpm_col].isnull() if rpm_col else df[speed_col].isnull()
    df['is_stopped'] = obd_missing_mask
    df['stop_id'] = (df['is_stopped'] != df['is_stopped'].shift()).cumsum()
    
    stops = []
    for name, group in df[df['is_stopped']].groupby('stop_id'):
        start_idx = group.index[0]
        end_idx = group.index[-1]
        
        start_row_stop = group.iloc[0]
        end_row_stop = group.iloc[-1]
        
        start_time = start_row_stop['datetime']
        end_time = end_row_stop['datetime']
        
        # True duration calculation considering the last known active timestamp before the stop
        actual_start_time = start_time
        if start_idx > 0:
            prev_row = df.loc[start_idx - 1]
            actual_start_time = prev_row['datetime']
            
        dur_mins = (end_time - actual_start_time).total_seconds() / 60.0
        
        if dur_mins >= 5.0:
            stops.append({
                'lat': start_row_stop['latitude'],
                'lon': start_row_stop['longitude'],
                'time_start': actual_start_time.strftime('%H:%M'),
                'time_end': end_time.strftime('%H:%M'),
                'duration_mins': dur_mins
            })
        
    # Stats
    bat_col = 'battery_vdc'
    coolant_col = 'Θερμοκρασία Ψυκτικού Υγρού Κινητήρα'
    sat_col = 'πλήθος δορυφόρων'
    alt_col = 'altitude'
    load_col = 'Φορτίο Κινητήρα'
    throttle_col = 'Θέση Πεταλούδας'
    intake_temp_col = 'Θερμοκρασία Αέρα Εισαγωγής'
    map_col = 'Απόλυτη Πίεση Εισαγωγής'
    advance_col = 'Αβάνς'
    
    battery_min = df[bat_col].min() / 1000.0 if bat_col in df.columns else None
    battery_max = df[bat_col].max() / 1000.0 if bat_col in df.columns else None
    coolant_min = df[coolant_col].min() if coolant_col in df.columns else None
    coolant_max = df[coolant_col].max() if coolant_col in df.columns else None
    
    sat_min = df[sat_col].min() if sat_col in df.columns else None
    sat_max = df[sat_col].max() if sat_col in df.columns else None
    sat_mean = df[sat_col].mean() if sat_col in df.columns else None
    
    alt_min = df[alt_col].min() if alt_col in df.columns else None
    alt_max = df[alt_col].max() if alt_col in df.columns else None
    alt_mean = df[alt_col].mean() if alt_col in df.columns else None
    
    load_min = df[load_col].min() if load_col in df.columns else None
    load_max = df[load_col].max() if load_col in df.columns else None
    load_mean = df[load_col].mean() if load_col in df.columns else None
    
    throttle_min = df[throttle_col].min() if throttle_col in df.columns else None
    throttle_max = df[throttle_col].max() if throttle_col in df.columns else None
    throttle_mean = df[throttle_col].mean() if throttle_col in df.columns else None
    
    intake_temp_min = df[intake_temp_col].min() if intake_temp_col in df.columns else None
    intake_temp_max = df[intake_temp_col].max() if intake_temp_col in df.columns else None
    
    map_min = df[map_col].min() if map_col in df.columns else None
    map_max = df[map_col].max() if map_col in df.columns else None
    
    advance_min = df[advance_col].min() if advance_col in df.columns else None
    advance_max = df[advance_col].max() if advance_col in df.columns else None
    
    return {
        'df': df,
        'start': {
            'lat': start_row['latitude'],
            'lon': start_row['longitude'],
            'time': start_row['timestamp'],
            'battery_v': start_row[bat_col] / 1000.0 if bat_col in df.columns else None,
            'coolant_c': start_row[coolant_col] if coolant_col in df.columns else None
        },
        'end': {
            'lat': end_row['latitude'],
            'lon': end_row['longitude'],
            'time': end_row['timestamp'],
            'battery_v': end_row[bat_col] / 1000.0 if bat_col in df.columns else None,
            'coolant_c': end_row[coolant_col] if coolant_col in df.columns else None
        },
        'max_speed': {
            'lat': max_speed_row['latitude'],
            'lon': max_speed_row['longitude'],
            'time': max_speed_row['timestamp'],
            'value': max_speed_row[speed_col],
            'rpm': max_speed_row[rpm_col] if rpm_col else None
        },
        'max_rpm': {
            'lat': max_rpm_row['latitude'],
            'lon': max_rpm_row['longitude'],
            'time': max_rpm_row['timestamp'],
            'value': max_rpm_row[rpm_col] if rpm_col else None,
            'speed': max_rpm_row[speed_col]
        } if max_rpm_row is not None else None,
        'stops': stops,
        'battery': {'min': battery_min, 'max': battery_max},
        'coolant': {'min': coolant_min, 'max': coolant_max},
        'satellites': {'min': sat_min, 'max': sat_max, 'mean': sat_mean},
        'altitude': {'min': alt_min, 'max': alt_max, 'mean': alt_mean},
        'load': {'min': load_min, 'max': load_max, 'mean': load_mean},
        'throttle': {'min': throttle_min, 'max': throttle_max, 'mean': throttle_mean},
        'intake_temp': {'min': intake_temp_min, 'max': intake_temp_max},
        'map_pressure': {'min': map_min, 'max': map_max},
        'advance': {'min': advance_min, 'max': advance_max}
    }

def generate_obd_story(gemini_api_key: str, google_api_key: str, csv_path: str) -> tuple:
    analysis = analyze_obd_data(csv_path)

    # Geocode critical events
    start_addr = reverse_geocode(analysis['start']['lat'], analysis['start']['lon'], google_api_key)
    end_addr = reverse_geocode(analysis['end']['lat'], analysis['end']['lon'], google_api_key)
    speed_addr = reverse_geocode(analysis['max_speed']['lat'], analysis['max_speed']['lon'], google_api_key)
    
    stop_addresses = []
    for i, stop in enumerate(analysis['stops']):
        addr = reverse_geocode(stop['lat'], stop['lon'], google_api_key)
        stop_addresses.append(addr)
        stop['address'] = addr
        
    analysis['start']['address'] = start_addr
    analysis['end']['address'] = end_addr
    analysis['max_speed']['address'] = speed_addr
    
    # Build prompt
    stops_prompt_str = ""
    for idx, stop in enumerate(analysis['stops']):
        stops_prompt_str += f"* **Στάση {idx+1}**: {stop['time_start']} - {stop['time_end']} (διάρκεια {stop['duration_mins']:.1f} λεπτά) στην περιοχή: {stop['address']}.\n"
        
    prompt = f"""
Είσαι ένας έμπειρος μηχανικός οχημάτων και αναλυτής δεδομένων τηλεμετρίας.
Θέλω να συντάξεις μια επίσημη τεχνική αναφορά (technical report) στα ελληνικά, με μέγιστο μέγεθος 500-600 λέξεις, σχετικά με τη διαδρομή, τη λήψη GPS και την κατάσταση του οχήματος.

Η αναφορά πρέπει να βασίζεται ΑΥΣΤΗΡΑ στα πραγματικά OBD, GPS και χωροχρονικά δεδομένα της διαδρομής:
- **Αφετηρία**: Εκκίνηση στις {analysis['start']['time']} από τη διεύθυνση/περιοχή: {start_addr}. Η τάση της μπαταρίας ήταν {analysis['start']['battery_v']:.2f}V και η θερμοκρασία του ψυκτικού υγρού ήταν {analysis['start']['coolant_c']:.1f}°C (κρύα εκκίνηση).
{stops_prompt_str}
- **Μέγιστη Ταχύτητα & Στροφές Κινητήρα**: Το όχημα ανέπτυξε μέγιστη ταχύτητα {analysis['max_speed']['value']:.1f} km/h με τις στροφές του κινητήρα να φτάνουν τις {analysis['max_speed']['rpm']:.0f} RPM στις {analysis['max_speed']['time']} στην περιοχή: {speed_addr}.
- **Τερματισμός**: Η διαδρομή ολοκληρώθηκε στις {analysis['end']['time']} στη διεύθυνση/περιοχή: {end_addr}.

Επιπλέον Telemetry Χαρακτηριστικά Οχήματος & GPS:
- **Μπαταρία**: Τάση από {analysis['battery']['min']:.2f}V έως {analysis['battery']['max']:.2f}V.
- **Ψυκτικό Υγρό**: Θερμοκρασία από {analysis['coolant']['min']:.1f}°C έως {analysis['coolant']['max']:.1f}°C.
- **Σήμα GPS / Δορυφόροι**: Πλήθος συνδεδεμένων δορυφόρων από {analysis['satellites']['min']:.0f} έως {analysis['satellites']['max']:.0f} (μέσος όρος: {analysis['satellites']['mean']:.1f} δορυφόροι).
- **Υψόμετρο (Elevation profile)**: Από {analysis['altitude']['min']:.1f}m έως {analysis['altitude']['max']:.1f}m (μέσος όρος: {analysis['altitude']['mean']:.1f}m).
- **Φορτίο Κινητήρα (Calculated Engine Load)**: Από {analysis['load']['min']:.1f}% έως {analysis['load']['max']:.1f}% (μέσος όρος: {analysis['load']['mean']:.1f}%).
- **Θέση Πεταλούδας (Throttle position)**: Από {analysis['throttle']['min']:.1f}% έως {analysis['throttle']['max']:.1f}% (μέσος όρος: {analysis['throttle']['mean']:.1f}%).
- **Θερμοκρασία Αέρα Εισαγωγής**: Από {analysis['intake_temp']['min']:.1f}°C έως {analysis['intake_temp']['max']:.1f}°C.
- **Απόλυτη Πίεση Εισαγωγής (MAP)**: Από {analysis['map_pressure']['min']:.1f} kPa έως {analysis['map_pressure']['max']:.1f} kPa.
- **Αβάνς (Ignition Advance)**: Από {analysis['advance']['min']:.1f} έως {analysis['advance']['max']:.1f}.

Στο τεχνικό report:
1. Χρησιμοποίησε επαγγελματική, τεχνική και αυστηρά ουδέτερη γλώσσα.
2. Χώρισε την αναφορά σε διακριτές ενότητες: 
   - "Σύνοψη Διαδρομής & Χρονολόγιο"
   - "Ανάλυση Οδικής Συμπεριφοράς & Φορτίου Κινητήρα"
   - "Κατάσταση, Τηλεμετρία & Ηλεκτρικά Συστήματα Οχήματος"
   - "Ανάλυση Συστημάτων Τηλεματικής & Λήψης GPS"
3. Στην ενότητα "Σύνοψη Διαδρομής & Χρονολόγιο", ΠΡΕΠΕΙ να αναφέρεις ΟΛΕΣ τις παραπάνω στάσεις σε μια λίστα με bullets (κουκκίδες με αστερίσκο *) ακολουθώντας ακριβώς τη μορφή:
   * **Στάση X**: Ώρα έναρξης - Ώρα λήξης (διάρκεια σε λεπτά) στην περιοχή: [Διεύθυνση/Περιοχή].
4. Σχολίασε:
   - Την ποιότητα λήψης του δέκτη GPS με βάση το πλήθος δορυφόρων.
   - Το υψομετρικό προφίλ της διαδρομής (μεταβολή υψομέτρου από {analysis['altitude']['min']:.1f}m έως {analysis['altitude']['max']:.1f}m).
   - Το φορτίο κινητήρα και τη θέση πεταλούδας κατά τη μέγιστη καταπόνηση ({analysis['max_speed']['rpm']:.0f} RPM, {analysis['max_speed']['value']:.1f} km/h).
   - Την κατάσταση της μπαταρίας, τη θερμοκρασία εισαγωγής αέρα και το advance/MAP.
"""

    client = genai.Client(api_key=gemini_api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7
        )
    )
    return response.text, analysis

def plot_obd_trajectory(analysis: dict, output_image_path: str, city: str = "Athens"):
    df = analysis['df']
    
    # Create GeoDataFrame for the trajectory path
    points = [Point(lon, lat) for lon, lat in zip(df.longitude, df.latitude)]
    gdf_trajectory = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=points)
    gdf_trajectory = gdf_trajectory.to_crs(epsg=3857)
    
    # Extract points for special events
    event_points = []
    event_names = []
    event_colors = []
    event_markers = []
    
    # 1. Start Point
    event_points.append(Point(analysis['start']['lon'], analysis['start']['lat']))
    event_names.append("Start (Αφετηρία)")
    event_colors.append("#2ecc71") 
    event_markers.append("o")
    
    # 2. Stops
    for idx, stop in enumerate(analysis['stops']):
        event_points.append(Point(stop['lon'], stop['lat']))
        event_names.append(f"Stop {idx+1} ({stop['duration_mins']:.0f} mins)")
        event_colors.append("#3498db") 
        event_markers.append("s") # Square
        
    # 3. Max Speed
    event_points.append(Point(analysis['max_speed']['lon'], analysis['max_speed']['lat']))
    event_names.append(f"Max Speed ({analysis['max_speed']['value']:.1f} km/h)")
    event_colors.append("#9b59b6") 
    event_markers.append("*") # Star
    
    # 4. End Point
    event_points.append(Point(analysis['end']['lon'], analysis['end']['lat']))
    event_names.append("End (Τερματισμός)")
    event_colors.append("#e74c3c") 
    event_markers.append("X") # X cross
    
    gdf_events = gpd.GeoDataFrame(
        {"Label": event_names, "Color": event_colors, "Marker": event_markers},
        geometry=event_points,
        crs="EPSG:4326"
    ).to_crs(epsg=3857)
    
    # Plotting
    fig, ax = plt.subplots(figsize=(12, 10), dpi=150)
    
    # Plot trajectory line
    if len(gdf_trajectory) >= 2:
        line_geom = LineString(gdf_trajectory.geometry.tolist())
        gdf_line = gpd.GeoDataFrame(geometry=[line_geom], crs="EPSG:3857")
        gdf_line.plot(ax=ax, color='#ff3366', linewidth=2.5, alpha=0.8, label='Route Path', zorder=2)
    else:
        gdf_trajectory.plot(ax=ax, color='#ff3366', markersize=10, alpha=0.5, label='Route Points', zorder=2)
        
    # Plot each event point type individually
    for idx, row in gdf_events.iterrows():
        gdf_single = gpd.GeoDataFrame(geometry=[row.geometry], crs="EPSG:3857")
        gdf_single.plot(
            ax=ax,
            marker=row['Marker'],
            color=row['Color'],
            edgecolor='white',
            markersize=280 if row['Marker'] == '*' else 160,
            label=row['Label'],
            zorder=5
        )
        
    # Stacking logic to prevent overlapping text labels on the map
    plotted_positions = []
    
    def get_non_overlapping_pos(x, y):
        offset_x = 120
        offset_y = 120
        attempts = 0
        while attempts < 15:
            overlap = False
            for px, py in plotted_positions:
                dist = ((x + offset_x - px) ** 2 + (y + offset_y - py) ** 2) ** 0.5
                if dist < 220:  # 220 meters threshold in EPSG:3857
                    overlap = True
                    break
            if not overlap:
                break
            # Adjust offset_y to stack labels vertically
            offset_y += 180  # Shift up by 180 meters
            attempts += 1
        plotted_positions.append((x + offset_x, y + offset_y))
        return x + offset_x, y + offset_y

    # Add text labels on the map next to the points
    # 1. Start Point (Index 0 in gdf_events)
    start_x, start_y = get_non_overlapping_pos(gdf_events.iloc[0].geometry.x, gdf_events.iloc[0].geometry.y)
    ax.text(
        start_x,
        start_y,
        "Αφετηρία",
        fontsize=9, weight='bold', color='black',
        bbox=dict(facecolor='white', alpha=0.85, edgecolor='#2ecc71', pad=2),
        zorder=6
    )
    
    # 2. Stops
    for idx, stop in enumerate(analysis['stops']):
        stop_geom = gdf_events.iloc[idx + 1].geometry
        stop_x, stop_y = get_non_overlapping_pos(stop_geom.x, stop_geom.y)
        ax.text(
            stop_x,
            stop_y,
            f"Στάση {idx+1}",
            fontsize=8, weight='bold', color='black',
            bbox=dict(facecolor='white', alpha=0.85, edgecolor='#3498db', pad=2),
            zorder=6
        )
        
    # 3. Max Speed
    speed_idx = 1 + len(analysis['stops'])
    speed_geom = gdf_events.iloc[speed_idx].geometry
    speed_x, speed_y = get_non_overlapping_pos(speed_geom.x, speed_geom.y)
    ax.text(
        speed_x,
        speed_y,
        f"Max Speed: {analysis['max_speed']['value']:.0f} km/h",
        fontsize=8, weight='bold', color='black',
        bbox=dict(facecolor='white', alpha=0.85, edgecolor='#9b59b6', pad=2),
        zorder=6
    )
    
    # 4. End Point
    end_idx = speed_idx + 1
    end_geom = gdf_events.iloc[end_idx].geometry
    end_x, end_y = get_non_overlapping_pos(end_geom.x, end_geom.y)
    ax.text(
        end_x,
        end_y,
        "Τερματισμός",
        fontsize=9, weight='bold', color='black',
        bbox=dict(facecolor='white', alpha=0.85, edgecolor='#e74c3c', pad=2),
        zorder=6
    )
        
    # Add Basemap using OpenStreetMap
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik)
    
    ax.set_axis_off()
    
    # Legend panel on the right side - clean list without address text strings
    legend_labels = []
    legend_labels.append("• Αφετηρία")
    for idx, stop in enumerate(analysis['stops']):
        legend_labels.append(f"• Στάση {idx+1} ({stop['duration_mins']:.0f} min)")
    legend_labels.append(f"• Μέγιστη Ταχύτητα ({analysis['max_speed']['value']:.1f} km/h)")
    legend_labels.append("• Τερματισμός")
    
    legend_text = "\n".join(legend_labels)
    props = dict(boxstyle='round', facecolor='white', alpha=0.92, edgecolor='#dddddd')
    ax.text(1.02, 0.98, f"Key Events:\n\n{legend_text}", transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
            
    plt.title(f"Vehicle Trajectory & OBD Events | {city}", fontsize=14, weight="bold", pad=15)
    plt.legend(loc='upper left', framealpha=0.9)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    plt.savefig(output_image_path, bbox_inches='tight', dpi=180)
    plt.close()
