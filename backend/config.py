import os
from dotenv import load_dotenv
import supabase

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
