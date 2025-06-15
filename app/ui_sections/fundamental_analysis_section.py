import streamlit as st
# Import your classes (relative imports from project root)
from app.data.fetcher import DataFetcher

def show_fundamental_analysis_section():
    st.header("Fundamental Analysis")
    st.write("This section will allow you to view and analyze fundamental data for stocks.")
    
    # Placeholder for stock selection in Fundamental Analysis
    if 'fetcher' in st.session_state:
        symbols = st.session_state.fetcher.get_stock_symbols("sp500")
        symbol = st.selectbox("Select Stock for Fundamental Analysis", symbols, key="fund_symbol_select")
    else:
        st.error("DataFetcher not initialized. Please ensure session state is set up correctly.")
        symbol = "AAPL" # Fallback for display

    if st.button("Fetch Fundamental Data", key="fetch_fund_data_btn"):
        with st.spinner(f"Fetching fundamental data for {symbol}..."):
            # Only fetch info, historical not needed here for fundamental analysis
            data = st.session_state.fetcher.fetch_yfinance_data(symbol, period="1d", interval="1d") 
            if data and symbol in data and 'info' in data[symbol]:
                info = data[symbol]['info']
                st.subheader(f"Key Information for {info.get('shortName', symbol)}")
                st.json(info) # Display all raw info
            else:
                st.warning(f"No fundamental data found for {symbol}.") 