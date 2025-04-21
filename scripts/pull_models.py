import os
import sys
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
ENTITY_MODEL = os.getenv("ENTITY_MODEL", "llama3")

def check_ollama_available():
    """
    Check if Ollama API is available.
    
    Returns:
        bool: True if available, False otherwise
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            print(f"Ollama API is available at {OLLAMA_BASE_URL}")
            return True
        else:
            print(f"Ollama API returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error connecting to Ollama API: {str(e)}")
        return False

def get_available_models():
    """
    Get list of models available in Ollama.
    
    Returns:
        list: List of available model names
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            models_data = response.json()
            models = [model["name"] for model in models_data.get("models", [])]
            return models
        else:
            print(f"Error getting available models: Status code {response.status_code}")
            return []
    except Exception as e:
        print(f"Error getting available models: {str(e)}")
        return []

def pull_model(model_name):
    """
    Pull a model from Ollama.
    
    Args:
        model_name: Name of the model to pull
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"Pulling model {model_name}...")
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/pull",
            json={"name": model_name}
        )
        
        if response.status_code == 200:
            print(f"Successfully pulled model {model_name}")
            return True
        else:
            print(f"Error pulling model {model_name}: Status code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error pulling model {model_name}: {str(e)}")
        return False

def main():
    """
    Main function to pull required models from Ollama.
    """
    print("Checking Ollama availability...")
    
    # Check if Ollama is available
    if not check_ollama_available():
        print("Ollama is not available. Please make sure Ollama is running.")
        sys.exit(1)
    
    # Get available models
    available_models = get_available_models()
    print(f"Available models: {', '.join(available_models) if available_models else 'None'}")
    
    # Pull embedding model if not available
    if EMBEDDING_MODEL not in available_models:
        if not pull_model(EMBEDDING_MODEL):
            print(f"Failed to pull embedding model {EMBEDDING_MODEL}")
            sys.exit(1)
    else:
        print(f"Embedding model {EMBEDDING_MODEL} is already available")
    
    # Pull entity model if not available
    if ENTITY_MODEL not in available_models:
        if not pull_model(ENTITY_MODEL):
            print(f"Failed to pull entity model {ENTITY_MODEL}")
            sys.exit(1)
    else:
        print(f"Entity model {ENTITY_MODEL} is already available")
    
    print("All required models are available!")

if __name__ == "__main__":
    main()
