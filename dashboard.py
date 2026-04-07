import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config for a premium look
st.set_page_config(
    page_title="Options Backtest Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium feel
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetricValue"] {
        color: #00d4ff;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1e2130;
        border-radius: 5px 5px 0px 0px;
        color: white;
        padding-left: 20px;
        padding-right: 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00d4ff !important;
        color: #0e1117 !important;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("backtest_results.csv")
        df['date'] = pd.to_datetime(df['date'])
        # Ensure PnL is numeric
        df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce')
        df = df.dropna(subset=['pnl'])
        return df
    except Exception as e:
        st.error(f"Error loading backtest_results.csv: {e}")
        return None

df = load_data()

if df is not None:
    # Sidebar
    st.sidebar.header("📊 Backtest Filters")
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Trading Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
        filtered_df = df.loc[mask].copy()
    else:
        filtered_df = df.copy()

    # Calculations
    filtered_df = filtered_df.sort_values('date')
    filtered_df['cumulative_pnl'] = filtered_df['pnl'].cumsum()
    
    total_pnl = filtered_df['pnl'].sum()
    total_trades = len(filtered_df)
    win_trades = len(filtered_df[filtered_df['pnl'] > 0])
    loss_trades = len(filtered_df[filtered_df['pnl'] <= 0])
    win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Risk Metrics
    avg_trade = filtered_df['pnl'].mean() if total_trades > 0 else 0
    rolled_max = filtered_df['cumulative_pnl'].cummax()
    drawdowns = filtered_df['cumulative_pnl'] - rolled_max
    max_dd = drawdowns.min()
    
    # Header Section
    st.title("📈 Options Backtest Analytics")
    st.markdown("---")

    # Metrics Layout
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total PnL", f"{total_pnl:,.2f}")
    m2.metric("Win Rate", f"{win_rate:.1f}%")
    m3.metric("Avg Trade", f"{avg_trade:,.2f}")
    m4.metric("Max Drawdown", f"{max_dd:,.2f}")
    m5.metric("Total Trades", total_trades)

    st.markdown("---")

    # Charts
    tab1, tab2, tab3 = st.tabs(["🚀 Equity Curve", "📊 Distribution", "📉 Drawdown Analysis"])

    with tab1:
        fig_equity = px.area(
            filtered_df, 
            x='date', 
            y='cumulative_pnl',
            title="Performance Over Time (Cumulative PnL)",
            labels={'cumulative_pnl': 'PnL Points', 'date': 'Trade Date'},
            template="plotly_dark",
            color_discrete_sequence=['#00d4ff']
        )
        fig_equity.update_layout(
            hovermode="x unified",
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_equity, use_container_width=True)

    with tab2:
        fig_dist = px.histogram(
            filtered_df, 
            x='pnl',
            nbins=50,
            title="PnL Frequency Distribution",
            labels={'pnl': 'Profit/Loss', 'count': 'Frequency'},
            template="plotly_dark",
            color_discrete_sequence=['#ff4b4b']
        )
        # Add a vertical line at 0
        fig_dist.add_vline(x=0, line_dash="dash", line_color="white")
        st.plotly_chart(fig_dist, use_container_width=True)

    with tab3:
        fig_dd = px.area(
            filtered_df, 
            x='date', 
            y=drawdowns,
            title="Evolution of Drawdown",
            labels={'y': 'Drawdown Points', 'date': 'Date'},
            template="plotly_dark",
            color_discrete_sequence=['#ff1f1f']
        )
        st.plotly_chart(fig_dd, use_container_width=True)

    # Detailed Table
    st.markdown("---")
    st.subheader("📑 Trade History")
    
    # Style the dataframe
    display_df = filtered_df.drop(columns=['cumulative_pnl'])
    display_df = display_df.sort_values('date', ascending=False)
    
    st.dataframe(
        display_df.style.background_gradient(subset=['pnl'], cmap='RdYlGn', vmin=-100, vmax=100),
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("Please ensure 'backtest_results.csv' is available in the directory.")
