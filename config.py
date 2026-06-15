import os
from dotenv import load_dotenv

# Load from the project root
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

def get_env(key):
    return os.getenv(key)