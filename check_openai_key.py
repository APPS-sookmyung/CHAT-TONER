import os
import openai

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    try:
        with open("python_backend/.env") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    api_key = line.strip().split("=")[1].strip('"').strip("'")
                    break
    except FileNotFoundError:
        pass

if not api_key:
    print("OpenAI API key not found in environment variables or python_backend/.env file.")
else:
    try:
        client = openai.OpenAI(api_key=api_key)
        models = client.models.list()
        print("Successfully connected to OpenAI API.")
    except openai.AuthenticationError:
        print("AuthenticationError: The provided OpenAI API key is invalid.")
    except Exception as e:
        print(f"An error occurred: {e}")
