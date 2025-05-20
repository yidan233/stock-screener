from config import ALPHA_VANTAGE_API_KEY
if not ALPHA_VANTAGE_API_KEY:
    print("API key missing!")
else:
    print("API key loaded.")