import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import random
import os

CSV_FILE = 'traffic_counts.csv'
RECORDS_PER_ANALYSIS = 24
AUTO_INTERVAL_SECONDS = 10  # Auto-generation interval in seconds
HIGH_TRAFFIC_THRESHOLD = 50

# Load or create CSV file
def load_data():
    try:
        df = pd.read_csv(CSV_FILE)
        df['Time'] = pd.to_datetime(df['Time'])
        return df
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Date', 'Time', 'Cars', 'Bicycles', 'Pedestrians'])
        df.to_csv(CSV_FILE, index=False)
        return df

# Add new entry to CSV
def add_entry(cars, bicycles, pedestrians):
    df = load_data()
    new_entry = pd.DataFrame({
        'Date': [datetime.now().strftime('%Y-%m-%d')],
        'Time': [datetime.now()],
        'Cars': [cars],
        'Bicycles': [bicycles],
        'Pedestrians': [pedestrians]
    })
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# Clear all data by deleting the CSV file
def clear_data():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
        st.success("All previous traffic data has been cleared!")
    else:
        st.info("No data file found to delete.")

# Analyze data after enough records
def analyze_data(df):
    df['Total'] = df['Cars'] + df['Bicycles'] + df['Pedestrians']
    df['Hour'] = df['Time'].dt.hour
    traffic_by_hour = df.groupby('Hour')['Total'].sum()
    peak_hour = traffic_by_hour.idxmax()
    peak_traffic = traffic_by_hour.max()
    return traffic_by_hour, peak_hour, peak_traffic

# Random auto generation of data
def auto_generate_data():
    cars = random.randint(0, 20)
    bicycles = random.randint(0, 15)
    pedestrians = random.randint(0, 30)
    add_entry(cars, bicycles, pedestrians)
    st.info(f"Auto-generated data - Cars: {cars}, Bicycles: {bicycles}, Pedestrians: {pedestrians}")

def main():
    st.title("Traffic Count Study App with Auto and Manual Data")

    # Manual entry
    st.header("Manual Entry of Traffic Counts")
    cars = st.number_input('Number of Cars', min_value=0, value=0, step=1)
    bicycles = st.number_input('Number of Bicycles', min_value=0, value=0, step=1)
    pedestrians = st.number_input('Number of Pedestrians', min_value=0, value=0, step=1)

    total_manual = cars + bicycles + pedestrians
    if total_manual > HIGH_TRAFFIC_THRESHOLD:
        st.error(f"⚠️ High traffic alert! Total manual vehicles: {total_manual}")

    if st.button("Record Manual Data"):
        add_entry(cars, bicycles, pedestrians)
        st.success(f"Manual data recorded - Cars: {cars}, Bicycles: {bicycles}, Pedestrians: {pedestrians}")

    # Clear all data button
    if st.button("Clear All Previous Data"):
        clear_data()

    # Auto data generation every AUTO_INTERVAL_SECONDS
    if 'last_auto_time' not in st.session_state:
        st.session_state.last_auto_time = datetime.now()

    time_diff = (datetime.now() - st.session_state.last_auto_time).total_seconds()
    if time_diff > AUTO_INTERVAL_SECONDS:
        auto_generate_data()
        st.session_state.last_auto_time = datetime.now()

    df = load_data()
    st.header("Recorded Traffic Data")
    if df.empty:
        st.info("No data recorded yet.")
        return
    else:
        st.write(df)

    # Always draw line chart showing counts over time immediately
    df_sorted = df.sort_values('Time')
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    df_sorted.set_index('Time')[['Cars', 'Bicycles', 'Pedestrians']].plot(ax=ax2)
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Count')
    ax2.set_title('Traffic Counts Over Time')
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    # After every 24 records, do the hour-wise traffic analysis with bar chart and alert
    if len(df) >= RECORDS_PER_ANALYSIS and len(df) % RECORDS_PER_ANALYSIS == 0:
        traffic_by_hour, peak_hour, peak_traffic = analyze_data(df)
        st.header("Traffic Analysis")
        st.subheader(f"Peak traffic hour: {peak_hour}:00 - {peak_traffic} total vehicles")

        fig1, ax1 = plt.subplots()
        traffic_by_hour.plot(kind='bar', ax=ax1)
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Total Traffic')
        ax1.set_title('Traffic Volume by Hour')
        st.pyplot(fig1)

if __name__ == "__main__":
    main()
