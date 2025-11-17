import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import os
import pytz


pk_tz = pytz.timezone("Asia/Karachi")

# Set page config
st.set_page_config(
    page_title="Agri Sensor Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2e7d32;
        text-align: center;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #1b5e20;
    }
    .card {
        border-radius: 50px;
        background-color: #f1f8e9;
        padding: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .stProgress > div > div > div > div {
        background-color: #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# Constants
JSON_FILE = "sensor_data.json"
REFRESH_INTERVAL = 5  # seconds

# Helper functions
def load_data():
    @st.cache_data(show_spinner=False)
    def _load():
        try:
            df = pd.read_json(JSON_FILE)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df = df.sort_values('timestamp')
            return df
        except FileNotFoundError:
            st.error("Sensor data file not found. Please ensure the MQTT listener is running.")
            return None
        except ValueError:
            st.warning("Sensor data file is empty or invalid. Please wait for data to be collected.")
            return None
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return None
    return _load()

def get_optimal_ranges():
    # Define optimal ranges for each parameter
    return {
        "soil_moisture": (30, 70),
        "soil_nitrogen": (5, 15),
        "soil_phosphorus": (5, 15),
        "soil_potassium": (15, 30),
        "soil_temperature": (20, 30),
        "soil_conductivity": (50, 80),
        "soil_ph": (6.0, 7.5),
        "air_temperature": (20, 35),
        "air_humidity": (50, 85)
    }

def create_gauge(value, title, min_val, max_val, optimal_min, optimal_max):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [min_val, optimal_min], 'color': "lightcoral"},
                {'range': [optimal_min, optimal_max], 'color': "lightgreen"},
                {'range': [optimal_max, max_val], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
    return fig

def generate_insights(df):
    if df is None or len(df) < 10:
        return "Not enough data to generate insights."
    
    insights = []
    optimal_ranges = get_optimal_ranges()
    
    # Get the most recent entry
    latest = df.iloc[-1]
    
    for param, (min_val, max_val) in optimal_ranges.items():
        current_value = latest[param]
        if current_value < min_val:
            insights.append(f"⚠️ {param.replace('_', ' ').title()} is too low ({current_value}). Optimal range: {min_val}-{max_val}.")
        elif current_value > max_val:
            insights.append(f"⚠️ {param.replace('_', ' ').title()} is too high ({current_value}). Optimal range: {min_val}-{max_val}.")
    
    # Analyze trends
    if len(df) >= 10:
        recent_df = df.tail(10)
        for param in optimal_ranges.keys():
            slope = np.polyfit(range(10), recent_df[param], 1)[0]
            if abs(slope) > 0.5:  # Significant change
                direction = "increasing" if slope > 0 else "decreasing"
                insights.append(f"📈 {param.replace('_', ' ').title()} is {direction} significantly.")
    
    # Correlation insights
    if len(df) >= 20:
        corr = df[list(optimal_ranges.keys())].corr()
        high_corrs = []
        for i, row in corr.iterrows():
            for j, val in row.items():
                if i != j and abs(val) > 0.7:  # Strong correlation
                    high_corrs.append(f"🔗 Strong correlation ({val:.2f}) between {i.replace('_', ' ').title()} and {j.replace('_', ' ').title()}.")
        insights.extend(high_corrs[:3])  # Show top 3 correlations
    
    return insights if insights else "All parameters are within optimal ranges."

# Sidebar
# st.sidebar.markdown('<h1 class="main-header" style="text-align: center;">🌱 Agri Sensor Dashboard</h1>', unsafe_allow_html=True)
st.sidebar.image("https://namal.edu.pk/uploads/logo22869383.png", width=100) # Adjust the width as needed
# st.sidebar.image("agri_img.jpg") # Adjust the width as needed

# Navigation
page = st.sidebar.radio("Navigation", ["Dashboard", "Detailed Analysis", "Historical Data", "About"])

# Auto-refresh option
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=False)
if auto_refresh:
    refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 5, 60, REFRESH_INTERVAL)
    st.sidebar.write(f"Refreshing every {refresh_interval} seconds")

# Data timeframe

# Crop number filter
crop_number = st.sidebar.selectbox(
    "Crop Number (filter)",
    ["All"] + sorted(set(pd.read_json(JSON_FILE)["crop_number"]))
)

# Sensor type filter
sensor_type = st.sidebar.selectbox(
    "Sensor Type (filter)",
    ["All", "soil_moisture", "soil_nitrogen", "soil_phosphorus", "soil_potassium", "soil_temperature", "soil_conductivity", "soil_ph", "air_temperature", "air_humidity"]
)

st.sidebar.subheader("Data Timeframe")
timeframe = st.sidebar.selectbox(
    "Select timeframe", 
    ["Last 6 hours", "Last day", "Last week", "Last month", "Last quarter", "Last 6 months", "Last year","All data"]
)

# Load data
df = load_data()

# Filter data based on selected timeframe
if df is not None and len(df) > 0:
    now = datetime.now(pk_tz)
    if df['timestamp'].dtype == 'datetime64[ns]':
        df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(pk_tz)
    else:
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert(pk_tz)

    # Timeframe filter
    if timeframe == "Last hour":
        df = df[df['timestamp'] > (now - timedelta(hours=1))]
    elif timeframe == "Last 6 hours":
        df = df[df['timestamp'] > (now - timedelta(hours=6))]
    elif timeframe == "Last day":
        df = df[df['timestamp'] > (now - timedelta(days=1))]
    elif timeframe == "Last week":
        df = df[df['timestamp'] > (now - timedelta(weeks=1))]
    elif timeframe == "Last month":
        df = df[df['timestamp'] > (now - timedelta(days=30))]
    elif timeframe == "Last quarter":
        df = df[df['timestamp'] > (now - timedelta(days=90))]
    elif timeframe == "Last 6 months":
        df = df[df['timestamp'] > (now - timedelta(days=182))]
    elif timeframe == "Last year":
        df = df[df['timestamp'] > (now - timedelta(days=365))]

    # Crop number filter
    if crop_number != "All":
        df = df[df["crop_number"] == int(crop_number)]

    # Sensor type filter
    if sensor_type != "All":
        df = df[["timestamp", sensor_type]]

# Dashboard Page
if page == "Dashboard":
    st.markdown(
    """
    <div style="display: flex; flex-direction: column; align-items: center;">
        <h1 class="main-header">🌱 Namal Agricultural Dashboard</h1>
        <p style="font-size: 14px; color: #777;">Powered by Electrical Engineering Department</p>
    </div>
    """,
    unsafe_allow_html=True,
    )
    
    if df is not None and len(df) > 0:
        # Top metrics section
        latest = df.iloc[-1]
        timestamp = latest['timestamp']

        if isinstance(timestamp, (float, int)):
            utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
        elif isinstance(timestamp, datetime):
            if timestamp.tzinfo is None:
                utc_dt = timestamp.replace(tzinfo=pytz.utc)
            else:
                utc_dt = timestamp.astimezone(pytz.utc)
        else:
            try:
                # If it's a pandas Timestamp without tzinfo
                utc_dt = timestamp.tz_localize('UTC')
            except:
                utc_dt = datetime.utcnow().replace(tzinfo=pytz.utc)

        # Convert to Pakistan Time
        pkt = pytz.timezone("Asia/Karachi")
        last_update = utc_dt.astimezone(pkt).strftime("%Y-%m-%d %H:%M:%S")

        st.write(f"🕒 Last updated (PKT): {last_update}")


        # latest = df.iloc[-1]
        # last_update = latest['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        # st.write(f"Last updated: {last_update}")
        
        # Key metrics in 3 columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Soil Moisture")
            st.plotly_chart(create_gauge(
                latest['soil_moisture'], "Moisture %", 0, 100, 30, 70
            ), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            # st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Soil pH")
            st.plotly_chart(create_gauge(
                latest['soil_ph'], "pH Level", 4, 9, 6.0, 7.5
            ), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col3:
            # st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Air Temperature")
            st.plotly_chart(create_gauge(
                latest['air_temperature'], "°C", 0, 50, 20, 35
            ), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Second row of metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # st.markdown('<div class="card">', unsafe_allow_html=True)
            st.metric("Soil Nitrogen", f"{latest['soil_nitrogen']} mg/kg")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            # st.markdown('<div class="card">', unsafe_allow_html=True)
            st.metric("Soil Phosphorus", f"{latest['soil_phosphorus']} mg/kg")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col3:
            # st.markdown('<div class="card">', unsafe_allow_html=True)
            st.metric("Soil Potassium", f"{latest['soil_potassium']} mg/kg")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col4:
            # st.markdown('<div class="card">', unsafe_allow_html=True)
            st.metric("Air Humidity", f"{latest['air_humidity']}%")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Main visualizations
        st.markdown('<h2 class="sub-header">Sensor Data Trends</h2>', unsafe_allow_html=True)
        
        # Soil Moisture
        fig = make_subplots(rows=9, cols=1, 
                   subplot_titles=("Soil Moisture", 
                          "Soil Temperature", 
                          "Soil Conductivity",
                          "Soil Nitrogen",
                          "Soil Phosphorus",
                          "Soil Potassium",
                          "Soil pH",
                          "Air Temperature",
                          "Air Humidity"),
                   vertical_spacing=0.02,
                   shared_xaxes=True)
        
        # Soil Moisture
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['soil_moisture'],
            name="Soil Moisture", line=dict(color="blue")
        ), row=1, col=1)
        
        # Soil Temperature
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['soil_temperature'],
            name="Soil Temperature", line=dict(color="red")
        ), row=2, col=1)
        
        # Soil Humidity
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['soil_conductivity'],
            name="Soil Conductivity", line=dict(color="purple")
        ), row=3, col=1)
        
        # Soil Nitrogen
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['soil_nitrogen'],
            name="Nitrogen", line=dict(color="green")
        ), row=4, col=1)
        
        # Soil Phosphorus
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['soil_phosphorus'],
            name="Phosphorus", line=dict(color="orange")
        ), row=5, col=1)
        
        # Soil Potassium
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['soil_potassium'],
            name="Potassium", line=dict(color="brown")
        ), row=6, col=1)
        
        # Soil pH
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['soil_ph'],
            name="Soil pH", line=dict(color="darkgreen")
        ), row=7, col=1)
        
        # Air Temperature
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['air_temperature'],
            name="Air Temperature", line=dict(color="crimson")
        ), row=8, col=1)
        
        # Air Humidity
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['air_humidity'],
            name="Air Humidity", line=dict(color="skyblue")
        ), row=9, col=1)
        
        fig.update_layout(height=1800, showlegend=True, 
                 legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)
        
        # Insights section
        st.markdown('<h2 class="sub-header">Insights</h2>', unsafe_allow_html=True)
        insights = generate_insights(df)
        if isinstance(insights, list):
            for insight in insights:
                st.write(insight)
            else:
                st.write(insights)
    else:
        st.warning("No data available to display. Please check if the MQTT listener is running.")
        
# Detailed Analysis Page
elif page == "Detailed Analysis":
    st.markdown('<h1 class="main-header">Detailed Sensor Analysis</h1>', unsafe_allow_html=True)
    
    if df is not None and len(df) > 0:
        # Parameter selection for detailed analysis
        st.sidebar.subheader("Parameter Analysis")
        selected_param = st.sidebar.selectbox(
            "Select parameter to analyze",
            ["soil_moisture", "soil_nitrogen", "soil_phosphorus", "soil_potassium", 
             "soil_temperature", "soil_conductivity", "soil_ph", "air_temperature", "air_humidity"]
        )
        
        # Statistical summary
        st.subheader(f"Statistical Summary of {selected_param.replace('_', ' ').title()}")
        
        col1, col2, col3, col4 = st.columns(4)
        stats = df[selected_param].describe()
        
        with col1:
            st.metric("Mean", f"{stats['mean']:.2f}")
        with col2:
            st.metric("Min", f"{stats['min']:.2f}")
        with col3:
            st.metric("Max", f"{stats['max']:.2f}")
        with col4:
            st.metric("Standard Dev", f"{stats['std']:.2f}")
        
        # Time series with moving average
        st.subheader("Time Series Analysis")
        
        window_size = st.slider("Moving average window size", 1, 20, 5)
        
        # Calculate moving average
        df['moving_avg'] = df[selected_param].rolling(window=window_size).mean()
        
        # Plot time series with moving average
        fig = px.line(df, x='timestamp', y=[selected_param, 'moving_avg'],
                     labels={selected_param: selected_param.replace('_', ' ').title(),
                             'moving_avg': f'{window_size}-point Moving Average',
                             'timestamp': 'Time'},
                     title=f"{selected_param.replace('_', ' ').title()} Over Time with Moving Average")
        
        fig.update_layout(legend_title_text='', height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Correlation heatmap
        st.subheader("Parameter Correlations")
        
        numeric_df = df.drop(columns=['timestamp']).select_dtypes(include='number')

        # Calculate the correlation matrix
        corr = numeric_df.corr()

        # Plot the correlation matrix
        fig = px.imshow(corr, text_auto=True, aspect="auto",
                        labels=dict(x="Parameters", y="Parameters", color="Correlation"),
                        x=corr.columns, y=corr.columns)
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribution analysis
        st.subheader(f"Distribution Analysis of {selected_param.replace('_', ' ').title()}")
        
        fig = px.histogram(df, x=selected_param, nbins=20, 
                          marginal="box",
                          title=f"Distribution of {selected_param.replace('_', ' ').title()}")
        st.plotly_chart(fig, use_container_width=True)
        
        # Scatter plot matrix
        st.subheader("Scatter Plot Matrix")
        
        selected_params = st.multiselect(
            "Select parameters for scatter plot matrix",
            df.columns.drop('timestamp').tolist(),
            # default=[selected_param, 'soil_moisture', 'air_temperature']
        )
        
        if len(selected_params) >= 2:
            fig = px.scatter_matrix(
                df[selected_params],
                dimensions=selected_params,
                title="Scatter Plot Matrix"
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select at least 2 parameters for the scatter plot matrix.")
    else:
        st.warning("No data available for analysis. Please check if the MQTT listener is running.")

# Historical Data Page
elif page == "Historical Data":
    st.markdown('<h1 class="main-header">Historical Data</h1>', unsafe_allow_html=True)
    
    if df is not None and len(df) > 0:
        # Date range picker
        min_date = df['timestamp'].min().date()
        max_date = df['timestamp'].max().date()
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start date", min_date)
        with col2:
            end_date = st.date_input("End date", max_date)
        
        # Filter by date range
        mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
        filtered_df = df.loc[mask]
        
        if len(filtered_df) > 0:
            st.write(f"Showing data from {start_date} to {end_date} ({len(filtered_df)} records)")
            
            # Parameter comparison
            st.subheader("Parameter Comparison")
            params_to_compare = st.multiselect(
                "Select parameters to compare",
                df.columns.drop('timestamp').tolist(),
                default=['soil_moisture', 'soil_temperature']
            )
            
            if params_to_compare:
                fig = px.line(filtered_df, x='timestamp', y=params_to_compare,
                             title="Parameter Comparison Over Time")
                st.plotly_chart(fig, use_container_width=True)
            
            # Data aggregation options
            st.subheader("Data Aggregation")
            aggregation = st.selectbox(
                "Aggregate data by",
                ["None", "Hour", "Day", "Week"]
            )
            
            if aggregation != "None":
                if aggregation == "Hour":
                    grouped_df = filtered_df.set_index('timestamp').resample('H').mean().reset_index()
                elif aggregation == "Day":
                    grouped_df = filtered_df.set_index('timestamp').resample('D').mean().reset_index()
                else:  # Week
                    grouped_df = filtered_df.set_index('timestamp').resample('W').mean().reset_index()
                
                # Plot aggregated data
                if len(grouped_df) > 0:
                    st.write(f"Data aggregated by {aggregation.lower()} ({len(grouped_df)} data points)")
                    
                    param = st.selectbox("Select parameter to visualize", filtered_df.columns.drop('timestamp').tolist())
                    
                    fig = px.line(grouped_df, x='timestamp', y=param,
                                 title=f"{param.replace('_', ' ').title()} Aggregated by {aggregation}")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Not enough data for the selected aggregation level.")
            
            # Export options
            st.subheader("Export Data")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Export to CSV"):
                    csv = filtered_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"sensor_data_{start_date}_{end_date}.csv",
                        mime='text/csv',
                    )
            
            with col2:
                if st.button("Export to JSON"):
                    json_string = filtered_df.to_json(orient='records', date_format='iso')
                    st.download_button(
                        label="Download JSON",
                        data=json_string,
                        file_name=f"sensor_data_{start_date}_{end_date}.json",
                        mime='application/json',
                    )
            
            # Raw data table with pagination
            st.subheader("Raw Data")
            page_size = 20
            total_pages = max(1, (len(filtered_df) + page_size - 1) // page_size)
            page_number = st.number_input("Page", 1, total_pages, 1)
            
            start_idx = (page_number - 1) * page_size
            end_idx = min(start_idx + page_size, len(filtered_df))
            
            st.write(f"Showing records {start_idx+1} to {end_idx} of {len(filtered_df)}")
            st.dataframe(filtered_df.iloc[start_idx:end_idx].reset_index(drop=True))
        else:
            st.warning("No data available for the selected date range.")
    else:
        st.warning("No historical data available. Please check if the MQTT listener is running.")

# About Page
else:
    st.markdown('<h1 class="main-header">About This Dashboard</h1>', unsafe_allow_html=True)
    
    st.write("""
    This agricultural sensor monitoring dashboard provides real-time and historical data visualization for various 
    soil and air parameters measured by IoT sensors in the field.
    
    ### Parameters Monitored
    
    #### Soil Parameters
    - **Soil Moisture**: Indicates the water content of the soil (%)
    - **Soil Nitrogen**: Amount of nitrogen in the soil (mg/kg)
    - **Soil Phosphorus**: Amount of phosphorus in the soil (mg/kg)
    - **Soil Potassium**: Amount of potassium in the soil (mg/kg)
    - **Soil Temperature**: Temperature of the soil (°C)
    - **Soil Conductivity**: Conductivity level of the soil (%)
    - **Soil pH**: Acidity/alkalinity of the soil
    
    #### Air Parameters
    - **Air Temperature**: Ambient temperature (°C)
    - **Air Humidity**: Humidity level in the air (%)
    
    ### Data Collection
    
    Data is collected through MQTT protocol from sensors deployed in the field. 
    The MQTT listener continuously receives and logs the data to a CSV file.
    
    ### About the System
    
    This system is designed to help farmers and agricultural experts monitor field conditions in real-time
    and make data-driven decisions to optimize crop growth and resource usage.
    """)
    
    st.subheader("Technologies Used")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Frontend")
        st.markdown("- Streamlit")
        st.markdown("- Plotly")
        
    with col2:
        st.markdown("### Backend")
        st.markdown("- Python")
        st.markdown("- MQTT")
        st.markdown("- Pandas")
        
    with col3:
        st.markdown("### Deployment")
        st.markdown("- Self-hosted")
        st.markdown("- Docker (optional)")

st.markdown(
    """
    <div style='text-align: center; margin-top: 20px; padding-top: 10px; border-top: 1px solid #eee;'>
        <p style='color: #777; font-size: 0.8em;'>
            Copyright © 2025 Qureshi. All Rights Reserved. | Namal University, Mianwali, Pakistan. | Developed by Electrical Engineering Department.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
# Auto refresh the page
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
