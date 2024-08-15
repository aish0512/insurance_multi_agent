import streamlit as st
from sales_agent import sales_agent_executor
from needs_assessment_agent import handle_needs_assessment
from product_agent import handle_product_recommendation, process_product_query

st.title("Multi-Agent AI Chatbot")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.current_agent = 'sales'
    st.session_state.needs_summary = None
    st.session_state.user_data = {}
    st.session_state.show_needs_form = False
    st.session_state.product_recommendation = None

    # Initial message from Sales Agent
    st.session_state.messages.append({"role": "assistant", "content": "Hello! I am your Sales Agent. How can I assist you today?"})

# Function to display chat messages
def display_chat_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User input
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.current_agent == 'sales':
        response = sales_agent_executor.run(input=user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        if "needs assessment" in response.lower():
            st.session_state.messages.append({"role": "assistant", "content": "I am now handing you over to our Needs Assessment Agent."})
            st.session_state.current_agent = 'needs'
            st.session_state.show_needs_form = True
            st.session_state.messages.append({"role": "assistant", "content": "Let's move on to the needs assessment."})
    elif st.session_state.current_agent == 'product':
        answer = process_product_query(user_input)
        st.session_state.messages.append({"role": "assistant", "content": answer})
    
    st.rerun()

# Display chat messages
display_chat_messages()


# Needs assessment form
if st.session_state.current_agent == 'needs' and st.session_state.show_needs_form:
    with st.chat_message("assistant"):
        with st.form(key='needs_assessment_form'):
            st.write("Please fill in the following details for needs assessment:")
            st.session_state.user_data["Name"] = st.text_input("What is your name?", value=st.session_state.user_data.get("Name", ""))
            st.session_state.user_data["Age and Family Status"] = st.text_input("What is your age and family status?", value=st.session_state.user_data.get("Age and Family Status", ""))
            st.session_state.user_data["Current Income"] = st.text_input("What is your current income?", value=st.session_state.user_data.get("Current Income", ""))

            submit_button = st.form_submit_button(label='Submit Needs Assessment')
            
            if submit_button:
                if all(st.session_state.user_data.values()):
                    needs_summary, file_path = handle_needs_assessment(st.session_state.user_data)
                    st.session_state.needs_summary = needs_summary
                    st.session_state.current_agent = 'product'
                    st.session_state.messages.append({"role": "assistant", "content": needs_summary})
                    st.success(f"Your information has been saved to {file_path}.")
                    st.session_state.show_needs_form = False

                    # Handover to Product Agent
                    st.session_state.messages.append({"role": "assistant", "content": "Thank you! I am now handing you over to our Product Agent."})
                    
                    # Trigger product recommendation immediately
                    product_recommendation = handle_product_recommendation(st.session_state.needs_summary)
                    st.session_state.product_recommendation = product_recommendation
                    st.session_state.messages.append({"role": "assistant", "content": product_recommendation})
                    st.rerun()
                else:
                    st.warning("Please fill in all fields before submitting.")
