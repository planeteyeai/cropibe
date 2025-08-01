from llama_cpp import Llama
import streamlit as st

MODEL_NAME = 'Mistral-7B-Instruct-v0.3.Q8_0.gguf'
MODEL_PATH = 'model/Mistral-7B-Instruct-v0.3.Q8_0.gguf'
NUM_THREADS = 8

def init():
    st.set_page_config(page_title='Local LLama', page_icon=':robot_face: ')
    st.sidebar.title('Local LLama')
    
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

def generate_response(prompt):
    llm = Llama(model_path=MODEL_PATH, n_threads=NUM_THREADS)
    formatted_prompt = f"Human: {prompt}\nAssistant: "
    output = llm(
        formatted_prompt, 
        max_tokens=512, 
        stop=["Human:"], 
        echo=True
    )
    full_response = output['choices'][0]['text']
    # Extract just the assistant's response
    response = full_response[len(formatted_prompt):]
    return response

def clear_conversation():
    st.session_state['messages'] = []

if __name__ == '__main__':
    init()
    
    # Add a clear button
    if st.sidebar.button("Clear Conversation"):
        clear_conversation()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Get user input
    user_input = st.chat_input("Say something...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_response(user_input)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})