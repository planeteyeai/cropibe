from llama_cpp import Llama
import os
import json
from datetime import datetime

# Config
# Load the model once during module import
MODEL_PATH = 'model/MiniPLM-Qwen-200M-Q8_0.gguf'
NUM_THREADS = 8
MAX_TOKENS = 256  # reduced to avoid overflowing context window
MAX_HISTORY_CHARS = 2000  # maximum allowed prompt size to stay within context

# Load model once
llm = Llama(model_path=MODEL_PATH, n_threads=NUM_THREADS)


def truncate_chat_history(chat_history, max_chars=MAX_HISTORY_CHARS):
    """Trim chat history to avoid overflowing the context window."""
    total = 0
    trimmed = []
    for message in reversed(chat_history):
        total += len(message['content'])
        if total > max_chars:
            break
        trimmed.insert(0, message)
    return trimmed


def format_prompt(prompt, farm_data, chat_history):
    """Build the full prompt to send to the LLM."""
    history_text = ""
    for msg in chat_history:
        if msg["role"] == "user":
            history_text += f"Human: {msg['content']}\n"
        else:
            history_text += f"Assistant: {msg['content']}\n"

    context = f"""You are a helpful agronomist assistant.
The user is managing a farm with the following details:
Farm Name: {farm_data.get('name')}
Soil Type: {farm_data.get('soil_type')}
Irrigation: {farm_data.get('irrigation_type')}
Crop: {farm_data.get('crop')}
Location: {farm_data.get('location')}

Provide clear, concise, and expert agricultural advice.
"""

    full_prompt = context + "\n" + history_text + f"Human: {prompt}\nAssistant:"
    return full_prompt


def generate_response(prompt, farm_data, chat_history):
    """Generate a response from the LLM."""
    trimmed_history = truncate_chat_history(chat_history)
    formatted_prompt = format_prompt(prompt, farm_data, trimmed_history)

    try:
        output = llm(
            formatted_prompt,
            max_tokens=MAX_TOKENS,
            stop=["Human:"],
            echo=True
        )
        full_response = output['choices'][0]['text']
        response = full_response[len(formatted_prompt):].strip()
        return response
    except ValueError as e:
        return f"[Error generating response: {str(e)}]"


def chat_loop():
    # Sample farm data (replace with dynamic data if needed)
    farm_data = {
        "name": "Green Acres",
        "soil_type": "Loamy",
        "irrigation_type": "Drip",
        "crop": "Tomatoes",
        "location": "Maharashtra"
    }

    chat_history = []

    print("👩‍🌾 Welcome to your Agronomist Assistant! Type 'exit' to quit, 'clear' to reset chat.\n")

    while True:
        user_input = input("👩‍🌾 You: ")
        if user_input.lower() == "exit":
            break
        elif user_input.lower() == "clear":
            chat_history = []
            print("🔄 Chat history cleared.\n")
            continue

        chat_history.append({"role": "user", "content": user_input})
        response = generate_response(user_input, farm_data, chat_history)
        print(f"🤖 Assistant: {response}\n")

        chat_history.append({"role": "assistant", "content": response})


if __name__ == '__main__':
    chat_loop()
