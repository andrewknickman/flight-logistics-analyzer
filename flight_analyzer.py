import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#generate mock data
@st.cache_data
def load_mock_data():
    try:
        np.random.seed(42)
        num = 200
        data = {
            'FlightID': ['FL' + str(1000 + i) for i in range(num)],
            'Carrier': np.random.choice(['Delta', 'United', 'American', 'Southwest'], num),
            'Origin': np.random.choice(['JFK', 'LAX', 'ORD', 'ATL', 'DFW'], num),
            'Destination': np.random.choice(['JFK', 'LAX', 'ORD', 'ATL', 'DFW'], num),
            'DepartureTime': np.random.choice(['Morning', 'Afternoon', 'Evening', 'Night'], num),
            'DelayReason': np.random.choice(['Weather', 'Crew', 'Technical', 'Air Traffic', 'Security'], num),
            'DelayMinutes': np.random.exponential(scale=20, size=num).astype(int)
        }
        return pd.DataFrame(data)
    except Exception as e:
        st.error("Failed to generate mock data.")
        st.stop()

#plot helpers
def plot_bar_avg(df, group_col, title, xlabel):
    try:
        avg = df.groupby(group_col)["DelayMinutes"].mean().sort_values()
        fig, ax = plt.subplots()
        sns.barplot(x=avg.index, y=avg.values, ax=ax)
        ax.set_title(title)
        ax.set_ylabel("Avg Delay (min)")
        ax.set_xlabel(xlabel)
        return fig
    except Exception as e:
        st.warning(f"Could not render plot: {e}")
        return None

#show stats
def show_summary_stats(df):
    try:
        st.markdown("### Data Summary")
        st.write(f"**Total flights:** {len(df)}")
        st.write(f"**Average delay:** {df['DelayMinutes'].mean():.1f} min")
        st.write(f"**Maximum delay:** {df['DelayMinutes'].max()} min")

        if len(df) > 0:
            worst_carrier = df.groupby("Carrier")["DelayMinutes"].mean().idxmax()
            worst_time = df.groupby("DepartureTime")["DelayMinutes"].mean().idxmax()
            common_reason = df["DelayReason"].value_counts().idxmax()

            st.markdown("### Strategy Suggestions")
            st.write(f"- `{worst_carrier}` has the worst average delays.")
            st.write(f"- Watch out for delays during the **{worst_time}**.")
            st.write(f"- Most frequent issue: **{common_reason}** delays.")
    except Exception as e:
        st.warning(f"Error during summary: {e}")

#main
st.title("Flight Logistics Analyzer")
st.write("Filter and analyze delay patterns using simulated flight data.")

#load mock data
df = load_mock_data()

#sidebar
st.sidebar.header("Filter Options")
selected_carriers = st.sidebar.multiselect("Select Carriers", df["Carrier"].unique(), default=list(df["Carrier"].unique()))
selected_reasons = st.sidebar.multiselect("Select Delay Reasons", df["DelayReason"].unique(), default=list(df["DelayReason"].unique()))
selected_times = st.sidebar.multiselect("Select Time of Day", df["DepartureTime"].unique(), default=list(df["DepartureTime"].unique()))

#filters
filtered = df[
    df["Carrier"].isin(selected_carriers) &
    df["DelayReason"].isin(selected_reasons) &
    df["DepartureTime"].isin(selected_times)
]

#preview
st.write("### Filtered Flight Data")
if len(filtered) > 0:
    st.dataframe(filtered)
else:
    st.warning("No data matches the current filter settings.")

#plots
if len(filtered) > 0:
    fig1 = plot_bar_avg(filtered, "Carrier", "Avg Delay by Carrier", "Carrier")
    if fig1: st.pyplot(fig1)

    fig2 = plot_bar_avg(filtered, "DelayReason", "Avg Delay by Reason", "Reason")
    if fig2: st.pyplot(fig2)

    fig3 = plot_bar_avg(filtered, "DepartureTime", "Avg Delay by Time", "Time of Day")
    if fig3: st.pyplot(fig3)

    #summary
    show_summary_stats(filtered)
