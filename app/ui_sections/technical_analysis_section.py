import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# Import your classes (relative imports from project root)
from app.data.fetcher import DataFetcher
from app.indicators.indicators import TechnicalIndicators

def show_technical_analysis_section():
    st.header("Technical Analysis")
    
    # Organize inputs into rows and columns
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        # Stock selection with autocomplete
        # Ensure fetcher is in session_state, initialized by interface.py
        if 'fetcher' in st.session_state:
            symbols = st.session_state.fetcher.get_stock_symbols("sp500")
            symbol = st.selectbox("Select Stock", symbols, index=symbols.index("AAPL") if "AAPL" in symbols else 0)
        else:
            st.error("DataFetcher not initialized. Please ensure session state is set up correctly.")
            symbol = "AAPL" # Fallback
        
        # Time period selection
        period = st.selectbox(
            "Select Time Period",
            ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
            index=3 # Default to 3mo
        )
        
        # Interval selection
        interval = st.selectbox(
            "Select Interval",
            ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"],
            index=5 # Default to 1d
        )
    
    with col2:
        # Indicator selection
        indicators_selected = st.multiselect(
            "Select Technical Indicators",
            [
                "Moving Average",
                "Exponential Moving Average",
                "RSI",
                "MACD",
                "Bollinger Bands",
                "Average True Range",
                "On-Balance Volume",
                "Stochastic Oscillator",
                "Rate of Change"
            ],
            default=["Moving Average", "RSI"]
        )

    # Indicator parameters (conditional rendering based on selection)
    with col3:
        # Default values for parameters
        ma_period = 20
        rsi_period = 14
        macd_fast_period = 12
        macd_slow_period = 26
        macd_signal_period = 9

        if "Moving Average" in indicators_selected:
            ma_period = st.number_input("MA Period", min_value=5, max_value=200, value=20, key="ma_period_tech")
        if "RSI" in indicators_selected:
            rsi_period = st.number_input("RSI Period", min_value=5, max_value=30, value=14, key="rsi_period_tech")
        if "MACD" in indicators_selected:
            macd_fast_period = st.number_input("MACD Fast Period", min_value=5, max_value=50, value=12, key="macd_fast_period_tech")
            macd_slow_period = st.number_input("MACD Slow Period", min_value=10, max_value=100, value=26, key="macd_slow_period_tech")
            macd_signal_period = st.number_input("MACD Signal Period", min_value=5, max_value=50, value=9, key="macd_signal_period_tech")

    with col4:
        # Default values for parameters
        bb_period = 20
        bb_std = 2.0
        atr_period = 14
        stoch_k_window = 14
        stoch_d_window = 3
        roc_period = 12 # Using a default period for ROC

        if "Bollinger Bands" in indicators_selected:
            bb_period = st.number_input("BB Period", min_value=5, max_value=50, value=20, key="bb_period_tech")
            bb_std = st.number_input("BB Std Dev", min_value=1.0, max_value=3.0, value=2.0, step=0.1, key="bb_std_tech")
        if "Average True Range" in indicators_selected:
            atr_period = st.number_input("ATR Period", min_value=5, max_value=50, value=14, key="atr_period_tech")
        if "Stochastic Oscillator" in indicators_selected:
            stoch_k_window = st.number_input("Stoch %K Window", min_value=5, max_value=50, value=14, key="stoch_k_window_tech")
            stoch_d_window = st.number_input("Stoch %D Window", min_value=2, max_value=10, value=3, key="stoch_d_window_tech")
        if "Rate of Change" in indicators_selected:
            roc_period = st.number_input("ROC Period", min_value=5, max_value=50, value=12, key="roc_period_tech")

    # --- Analyze Button ---
    if st.button("Analyze", type="primary"):
        with st.spinner(f"Fetching data for {symbol} ({period} {interval})..."):
            data = st.session_state.fetcher.fetch_yfinance_data(symbol, period=period, interval=interval)
            
            if data and symbol in data and 'historical' in data[symbol]:
                df = data[symbol]['historical']
                
                # Convert string representation back to DataFrame if needed
                if isinstance(df, str):
                    try:
                        # Parse the string representation
                        df = pd.read_csv(io.StringIO(df), sep=r"\s+", engine="python")
                        # Convert the index to datetime
                        if 'Date' in df.columns:
                            df['Date'] = pd.to_datetime(df['Date'])
                            df.set_index('Date', inplace=True)
                        elif isinstance(df.index, (pd.Int64Index, pd.RangeIndex)):
                            try:
                                df.index = pd.to_datetime(df.index)
                            except Exception:
                                st.warning("Could not convert DataFrame index to DatetimeIndex. Charting might be affected.")
                                pass
                        
                    except Exception as e:
                        st.error(f"Could not parse historical data string to DataFrame: {e}")
                        st.info("Please ensure the historical data is in a valid format for parsing.")
                        return

                if df.empty:
                    st.error(f"No valid historical data found for {symbol} after processing.")
                    return
                
                # Ensure DataFrame has expected columns
                required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                if not all(col in df.columns for col in required_cols):
                    st.error(f"Missing required columns in historical data. Expected: {required_cols}, Found: {df.columns.tolist()}")
                    return

                # Create tabs for different views
                tab1, tab2 = st.tabs(["Price Chart", "Technical Indicators"])
                
                with tab1:
                    # Create candlestick chart
                    fig = go.Figure(data=[go.Candlestick(
                        x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'],
                        increasing_line_color='green', # Custom color for increasing candles
                        decreasing_line_color='red',   # Custom color for decreasing candles
                        name="Price"
                    )])
                    
                    # Add selected indicators that overlay on the price chart
                    if "Moving Average" in indicators_selected:
                        ma = st.session_state.indicators.moving_average(df['Close'], window=ma_period)
                        fig.add_trace(go.Scatter(
                            x=df.index,
                            y=ma,
                            mode='lines',
                            name=f"MA({ma_period})",
                            line=dict(color='blue', width=2)
                        ))
                    
                    if "Exponential Moving Average" in indicators_selected:
                        ema = st.session_state.indicators.exponential_moving_average(df['Close'], span=ma_period) # Using MA period for EMA
                        fig.add_trace(go.Scatter(
                            x=df.index,
                            y=ema,
                            mode='lines',
                            name=f"EMA({ma_period})",
                            line=dict(color='orange', width=2)
                        ))

                    if "Bollinger Bands" in indicators_selected:
                        upper, middle, lower = st.session_state.indicators.bollinger_bands(
                            df['Close'],
                            window=bb_period,
                            num_std=bb_std
                        )
                        fig.add_trace(go.Scatter(x=df.index, y=upper, mode='lines', name="Upper BB", line=dict(color='purple', width=1, dash='dash')))
                        fig.add_trace(go.Scatter(x=df.index, y=middle, mode='lines', name="Middle BB", line=dict(color='darkblue', width=1)))
                        fig.add_trace(go.Scatter(x=df.index, y=lower, mode='lines', name="Lower BB", line=dict(color='purple', width=1, dash='dash')))

                    fig.update_layout(
                        title=f"{symbol} Price Chart",
                        yaxis_title="Price",
                        xaxis_title="Date",
                        template="plotly_dark",
                        xaxis_rangeslider_visible=False # Hide range slider for cleaner look
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    # Create separate charts for technical indicators (sub-plots)
                    # RSI
                    if "RSI" in indicators_selected:
                        rsi = st.session_state.indicators.relative_strength_index(df['Close'], window=rsi_period)
                        fig_rsi = go.Figure()
                        fig_rsi.add_trace(go.Scatter(x=df.index, y=rsi, name="RSI", line=dict(color='cyan', width=2)))
                        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)", annotation_position="top right")
                        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)", annotation_position="bottom right")
                        fig_rsi.update_layout(title=f"RSI ({rsi_period})", yaxis_title="RSI", template="plotly_dark")
                        st.plotly_chart(fig_rsi, use_container_width=True)

                    # MACD
                    if "MACD" in indicators_selected:
                        macd_line, signal_line, histogram = st.session_state.indicators.macd(
                            df['Close'],
                            fast_period=macd_fast_period,
                            slow_period=macd_slow_period,
                            signal_period=macd_signal_period
                        )
                        fig_macd = go.Figure()
                        fig_macd.add_trace(go.Scatter(x=df.index, y=macd_line, name="MACD Line", line=dict(color='blue', width=2)))
                        fig_macd.add_trace(go.Scatter(x=df.index, y=signal_line, name="Signal Line", line=dict(color='orange', width=2)))
                        # Use a bar chart for histogram with conditional coloring
                        histogram_colors = ['green' if val >= 0 else 'red' for val in histogram]
                        fig_macd.add_trace(go.Bar(x=df.index, y=histogram, name="Histogram", marker_color=histogram_colors))
                        fig_macd.update_layout(title=f"MACD ({macd_fast_period},{macd_slow_period},{macd_signal_period})", yaxis_title="Value", template="plotly_dark")
                        st.plotly_chart(fig_macd, use_container_width=True)

                    # Average True Range (ATR)
                    if "Average True Range" in indicators_selected:
                        # Ensure 'High', 'Low', 'Close' columns are available and numerical
                        if all(col in df.columns for col in ['High', 'Low', 'Close']):
                            atr = st.session_state.indicators.average_true_range(df['High'], df['Low'], df['Close'], window=atr_period)
                            fig_atr = go.Figure()
                            fig_atr.add_trace(go.Scatter(x=df.index, y=atr, name="ATR", line=dict(color='yellow', width=2)))
                            fig_atr.update_layout(title=f"Average True Range ({atr_period})", yaxis_title="ATR Value", template="plotly_dark")
                            st.plotly_chart(fig_atr, use_container_width=True)
                        else:
                            st.warning("Missing 'High', 'Low', or 'Close' data for ATR calculation.")

                    # On-Balance Volume (OBV)
                    if "On-Balance Volume" in indicators_selected:
                        if 'Volume' in df.columns:
                            obv = st.session_state.indicators.on_balance_volume(df['Close'], df['Volume'])
                            fig_obv = go.Figure()
                            fig_obv.add_trace(go.Scatter(x=df.index, y=obv, name="OBV", line=dict(color='pink', width=2)))
                            fig_obv.update_layout(title="On-Balance Volume", yaxis_title="OBV", template="plotly_dark")
                            st.plotly_chart(fig_obv, use_container_width=True)
                        else:
                            st.warning("Missing 'Volume' data for OBV calculation.")
                    
                    # Stochastic Oscillator
                    if "Stochastic Oscillator" in indicators_selected:
                        if all(col in df.columns for col in ['High', 'Low', 'Close']):
                            k_percent, d_percent = st.session_state.indicators.stochastic_oscillator(
                                df['High'], df['Low'], df['Close'], 
                                k_window=stoch_k_window, d_window=stoch_d_window
                            )
                            fig_stoch = go.Figure()
                            fig_stoch.add_trace(go.Scatter(x=df.index, y=k_percent, name="%K", line=dict(color='lime', width=2)))
                            fig_stoch.add_trace(go.Scatter(x=df.index, y=d_percent, name="%D", line=dict(color='magenta', width=2)))
                            fig_stoch.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Overbought (80)", annotation_position="top right")
                            fig_stoch.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="Oversold (20)", annotation_position="bottom right")
                            fig_stoch.update_layout(title=f"Stochastic Oscillator ({stoch_k_window},{stoch_d_window})", yaxis_title="%", template="plotly_dark")
                            st.plotly_chart(fig_stoch, use_container_width=True)
                        else:
                            st.warning("Missing 'High', 'Low', or 'Close' data for Stochastic Oscillator calculation.")

                    # Rate of Change (ROC)
                    if "Rate of Change" in indicators_selected:
                        roc = st.session_state.indicators.rate_of_change(df['Close'], window=roc_period)
                        fig_roc = go.Figure()
                        fig_roc.add_trace(go.Scatter(x=df.index, y=roc, name="ROC", line=dict(color='white', width=2)))
                        fig_roc.add_hline(y=0, line_dash="dash", line_color="grey")
                        fig_roc.update_layout(title=f"Rate of Change ({roc_period})", yaxis_title="%", template="plotly_dark")
                        st.plotly_chart(fig_roc, use_container_width=True)

            else:
                st.error(f"No historical data found for the selected symbol ({symbol}) or period ({period}). Please try different selections.") 