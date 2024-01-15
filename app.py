import streamlit as st
from streamlit_chat import message
from langchain.llms import HuggingFaceHub
from langchain.chains import LLMChain, ConversationChain
from langchain.chains.conversation.memory import (ConversationBufferMemory,
                                                  ConversationSummaryMemory,
                                                  ConversationBufferWindowMemory
                                                 )
import re 
import string


if 'conversation' not in st.session_state:
    st.session_state['conversation'] = None

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'API_KEY' not in st.session_state:
    st.session_state['API_KEY'] = ''

#import os 
#os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

def remove_unwanted_patterns(response):
    # Remove instances of "<pad>" or variations in case
    cleaned_response = re.sub(r'<\s*p\W*a\W*d\s*>', '', response, flags=re.IGNORECASE)
    
    # Remove any words starting with "<" or special characters at the beginning
    cleaned_response = ' '.join(word for word in cleaned_response.split() if not (word.startswith('<') or word[0] in string.punctuation))

    return cleaned_response.strip()

def get_response(userInput, api_key):

    if st.session_state['conversation'] is None:
        #1e-10
        llm = HuggingFaceHub(repo_id="lmsys/fastchat-t5-3b-v1.0",
                            model_kwargs={"temperature": 0.9, "max_length": 64},
                            huggingfacehub_api_token=api_key
                            )
        
        st.session_state['conversation'] = ConversationChain(
            llm= llm,
            verbose=True,
            memory=ConversationBufferMemory()
        )
    
    # Get the raw response from the model
    raw_response = st.session_state['conversation'].predict(input=userInput)

    # Clean the response to remove unwanted patterns
    cleaned_response = remove_unwanted_patterns(raw_response)

    print(st.session_state['conversation'].memory.buffer)
    
    return cleaned_response



# Setting page title and header 
st.set_page_config(page_title="Chat GPT Clone", page_icon="🤖")
st.markdown("<h1 style='text-align: center;> How Can I assist you? </h1>", unsafe_allow_html=True)

st.sidebar.title("🤖")
st.session_state['API_KEY'] = st.sidebar.text_input("What's your API key?", type="password")
summarize_button = st.sidebar.button("Summarize the conversation", key= 'summarize')

if summarize_button:
    summarize_placeholder = st.sidebar.write("Nice chatting with you my friend 🥰:\n\n"+st.session_state['conversation'].memory.buffer)


response_container = st.container()

#Container for user input text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("Your question goes here:", key="input", height=100)
        submit_button = st.form_submit_button(label="Send")
        if submit_button:
            st.session_state['messages'].append(user_input)
            model_response = get_response(user_input,st.session_state['API_KEY'])
            st.session_state['messages'].append(model_response)

            with response_container:
                for i in range(len(st.session_state['messages'])):
                    if (i % 2) == 0:
                        message(st.session_state['messages'][i], is_user = True, key=str(i) +"_user")
                    else:
                        message(st.session_state['messages'][i], key=str(i) +"_AI")




