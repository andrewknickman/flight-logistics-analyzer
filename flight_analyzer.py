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
        fig_height = max(5, len(avg) * 0.6)
        fig, ax = plt.subplots(figsize=(10, fig_height))
        colors = sns.color_palette("coolwarm", len(avg))
        bars = sns.barplot(x=avg.values, y=avg.index, ax=ax, palette=colors)

        ax.set_title(title, fontsize=16, pad=15)
        ax.set_xlabel("Avg Delay (min)", fontsize=12)
        ax.set_ylabel(xlabel, fontsize=12)
        ax.grid(axis='x', linestyle='--', alpha=0.7)

        #annotate bars
        max_val = max(avg.values)
        ax.set_xlim(0, max_val * 1.15)

        for i, v in enumerate(avg.values):
            ax.text(v + (max_val * 0.01), i, f"{v:.1f}", va='center', fontsize=10)

        fig.tight_layout()
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
    fig1 = plot_bar_avg(filtered, "Carrier", "Average Delay by Carrier", "Carrier")
    if fig1: st.pyplot(fig1)

    fig2 = plot_bar_avg(filtered, "DelayReason", "Average Delay by Reason", "Reason")
    if fig2: st.pyplot(fig2)

    fig3 = plot_bar_avg(filtered, "DepartureTime", "Average Delay by Time of Day", "Time of Day")
    if fig3: st.pyplot(fig3)

    #summary
    show_summary_stats(filtered)
