import streamlit as st
import pandas as pd # Even if not directly used, good to keep for sections
import plotly.graph_objects as go # Even if not directly used, good to keep for sections
import io # Even if not directly used, good to keep for sections
import sys
import os

# Import option_menu
from streamlit_option_menu import option_menu

# Add the project root to the Python path
# This ensures that modules within the 'app' directory can be imported correctly.
current_dir = os.path.dirname(os.path.abspath(__file__)) # Gets the directory of interface.py (app/)
project_root = os.path.dirname(current_dir) # Goes up one level to the project root (e.g., stock-screener/)
sys.path.insert(0, project_root)

# Import your classes (for session state initialization)
from app.data.fetcher import DataFetcher
from app.indicators.indicators import TechnicalIndicators
from app.screener.screener import StockScreener

# Import the section functions from the new ui_sections directory
from app.ui_sections.technical_analysis_section import show_technical_analysis_section
from app.ui_sections.fundamental_analysis_section import show_fundamental_analysis_section
from app.ui_sections.stock_screener_section import show_stock_screener_section

# --- Session State Initialization ---
def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'screener' not in st.session_state:
        st.session_state.screener = StockScreener()
    if 'fetcher' not in st.session_state:
        st.session_state.fetcher = DataFetcher()
    if 'indicators' not in st.session_state:
        st.session_state.indicators = TechnicalIndicators()

# --- Main App Layout ---
def main():
    st.set_page_config(layout="wide", page_title="Stock Market Analysis")
    st.title("Stock Market Analysis")

    initialize_session_state()

    # --- Main Navigation using option_menu ---
    # You can choose the orientation (horizontal or vertical) and menu position (e.g., 'sidebar')
    with st.sidebar: # This places the menu in the sidebar, like traditional navigation
        selected = option_menu(
            menu_title="Main Menu",  # required
            options=["Technical Analysis", "Fundamental Analysis", "Stock Screener"],  # required
            icons=["graph-up", "cash-stack", "funnel"],  # optional, find more at https://icons.getbootstrap.com/
            menu_icon="cast",  # optional
            default_index=0,  # optional
        )

    # Display content based on selection
    if selected == "Technical Analysis":
        show_technical_analysis_section()
    elif selected == "Fundamental Analysis":
        show_fundamental_analysis_section()
    elif selected == "Stock Screener":
        show_stock_screener_section()

if __name__ == "__main__":
    main() 