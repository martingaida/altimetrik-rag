import streamlit as st
import requests
from typing import List
import json

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def query_rag_system(question: str) -> str:
    """Send query to FastAPI backend and get response"""
    try:
        response = requests.post(
            "http://localhost:8000/rag",
            json={"query": question}
        )
        response.raise_for_status()
        return response.json()["answer"]
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("📊 Salesforce Earnings Call RAG")
st.write("Ask questions about Salesforce's earnings calls and get AI-powered answers!")

# Chat input
if prompt := st.chat_input("Ask a question about Salesforce's earnings calls"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get response from RAG system
    response = query_rag_system(prompt)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Add some example questions in the sidebar
st.sidebar.title("Example Questions")
example_questions = [
    "What are the risks that Salesforce has faced?",
    "Can you summarize Salesforce's strategy at the beginning of 2023?",
    "How many earnings call documents do you have indexed?",
    "How many pages are in the most recent earnings call?"
]

st.sidebar.write("Try asking:")
for question in example_questions:
    if st.sidebar.button(question):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": question})
        
        # Get response from RAG system
        response = query_rag_system(question)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun the app to update the chat
        st.rerun()