import os
import requests
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env file!")
    exit()

print("Fetching authorized models from Google...")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

if response.status_code != 200:
    print(f"❌ API Error: {response.status_code}")
    print(response.text)
    exit()

data = response.json()
print("\n✅ AVAILABLE TEXT GENERATION MODELS FOR YOUR KEY:")
print("-" * 40)

# Filter the list to only show models that support text generation (chat)
for model in data.get("models", []):
    if "generateContent" in model.get("supportedGenerationMethods", []):
        # We strip out the "models/" prefix to give you the exact string LangChain needs
        clean_name = model["name"].replace("models/", "")
        print(f"-> {clean_name}")

print("-" * 40)