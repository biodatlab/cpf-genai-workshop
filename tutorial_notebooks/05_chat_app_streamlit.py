# Run this script using ``streamlit run 05_chat_streamlit_base.py``
import streamlit as st
from openai import OpenAI


### OpenAI API
OPENAI_API_KEY = # put your OpenAI key here
client = OpenAI(api_key=OPENAI_API_KEY)


def complete_text(prompt: str):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to generate output prompt in Thai."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


### Streamlit app
st.set_page_config(page_title="Chatbot", page_icon="", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title('Chat Interface')

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "สอบถามข้อมูลที่สนใจ"}
    ]

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
messages = getattr(st.session_state, 'messages', [])
for message in messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

#If last message is not from assistant, generate a new response
if messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = complete_text(prompt)
            st.write(response)
            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message) # Add response to message history
