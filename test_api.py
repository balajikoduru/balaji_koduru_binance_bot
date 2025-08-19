import os
from dotenv import load_dotenv


# load environment variables
load_dotenv(override=True)

print("API_KEY:", os.environ.get("BINANCE_API_KEY"))
print("API_SECRET:", os.environ.get("BINANCE_API_SECRET"))
