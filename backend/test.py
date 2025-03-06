import supabase

SUPABASE_URL = "https://wvyayeiuhuuhzeleepef.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind2eWF5ZWl1aHV1aHplbGVlcGVmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEyMjQ4MzYsImV4cCI6MjA1NjgwMDgzNn0.JG1cYzH4y-vhFPVVBZWCrif3-ByHk1tukVjixWW9Roc"

supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

# Use a real email address
try:
    response = supabase_client.auth.sign_up({"email": "tharanimtharan@gmail.com", "password": "password123"})
    print("Supabase Connection Successful:", response)
except Exception as e:
    print("Error Connecting to Supabase:", e)