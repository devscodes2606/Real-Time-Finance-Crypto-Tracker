import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Set up clean, wide layout page configuration
st.set_page_config(page_title="Market Analytics", layout="wide")

st.title(" Live Market Analytics Dashboard")
st.write("Enter any stock or crypto ticker symbol below to fetch real-time data and interactive charts.")

# User configuration input area
col_input1, col_input2 = st.columns([2, 1])
with col_input1:
    ticker = st.text_input("Enter Ticker Symbol (e.g., AAPL, TSLA, BTC-USD, ETH-USD)", "BTC-USD").upper().strip()
with col_input2:
    period = st.selectbox("Time Horizon / Period", ["1d", "5d", "1mo", "1y", "5y"], index=2)

if ticker:
    with st.spinner(f"Fetching real-time data for {ticker}..."):
        # Fetch data via API 
        # (1-day period uses 15-minute intervals, others default to daily intervals)
        interval_mapping = "15m" if period == "1d" else "1d"
        data = yf.download(tickers=ticker, period=period, interval=interval_mapping)
    
    if not data.empty and len(data) > 0:
        try:
            # Flatten multi-indexed columns if yfinance returns them grouped by ticker
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Safely extract scalar numeric float values from the Pandas Series
            latest_close_series = data['Close'].iloc[-1]
            first_open_series = data['Open'].iloc[0]
            
            # Using values[0] or item() extracts the native python float 
            latest_price = float(latest_close_series.values[0] if hasattr(latest_close_series, 'values') else latest_close_series)
            prev_price = float(first_open_series.values[0] if hasattr(first_open_series, 'values') else first_open_series)
            
            # Calculate percentage change matrix
            delta_val = ((latest_price - prev_price) / prev_price) * 100
            
            # Display real-time KPI Metrics
            st.divider()
            metric_col1, metric_col2 = st.columns(2)
            
            with metric_col1:
                st.metric(
                    label=f"{ticker} Latest Closing Price", 
                    value=f"${latest_price:,.2f}"
                )
            with metric_col2:
                st.metric(
                    label=f"Period Performance ({period})", 
                    value=f"{delta_val:+.2f}%", 
                    delta=f"{delta_val:.2f}%"
                )
            
            st.subheader("Interactive Price Movement Chart")
            
            # Generate Interactive Plotly Candlestick Chart 
            fig = go.Figure(data=[go.Candlestick(
                x=data.index,
                open=data['Open'].squeeze(), 
                high=data['High'].squeeze(),
                low=data['Low'].squeeze(), 
                close=data['Close'].squeeze(),
                name=ticker
            )])
            
            # Layout optimization for seamless viewing experience
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=10, t=10, b=10),
                height=500
            )
            
            # Render the chart responsively
            st.plotly_chart(fig, use_container_width=True)
            
            # Optional Expander to view raw structural data table
            with st.expander("📊 View Raw Data Table"):
                st.dataframe(data, use_container_width=True)
                
        except Exception as e:
            st.error(f"An error occurred while parsing the data: {e}")
            st.info("Tip: Make sure the ticker name is valid on Yahoo Finance.")
    else:
        st.error(f"No market data found for ticker symbol '{ticker}'. Please check your spelling.")
