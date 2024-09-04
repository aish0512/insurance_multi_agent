import streamlit as st
from sales_agent import sales_agent_executor
from needs_assessment_agent import handle_needs_assessment
from product_agent import handle_product_recommendation, process_product_query

st.title("Multi-Agent AI Chatbot")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your Sales Agent. How can I assist you today?"}]
    st.session_state.current_agent = None
    st.session_state.needs_summary = None
    st.session_state.user_data = {}
    st.session_state.show_needs_form = False
    st.session_state.product_recommendation = None
    st.session_state.agent_selected = False

# Function to display chat messages
def display_chat_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Display chat messages
display_chat_messages()

# Agent selection buttons
if not st.session_state.agent_selected:
    st.write("Please select how you'd like to proceed:")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("General Q&A"):
            st.session_state.current_agent = 'sales'
            st.session_state.messages.append({"role": "assistant", "content": "Great! I'm here to answer any general questions you may have. What would you like to know?"})
            st.session_state.agent_selected = True

    with col2:
        if st.button("Product Info"):
            st.session_state.current_agent = 'product'
            st.session_state.messages.append({"role": "assistant", "content": "Certainly! I'm switching to our Product Agent. What specific product information are you looking for?"})
            st.session_state.agent_selected = True

    with col3:
        if st.button("Needs Assessment"):
            st.session_state.current_agent = 'needs'
            st.session_state.show_needs_form = True
            st.session_state.messages.append({"role": "assistant", "content": "Sure, let's do a needs assessment. I'll ask you a few questions to better understand your requirements."})
            st.session_state.agent_selected = True

    if st.session_state.agent_selected:
        st.rerun()

else:
    # Reset Chat button
    if st.button("Reset Chat"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your Sales Agent. How can I assist you today?"}]
        st.session_state.current_agent = None
        st.session_state.agent_selected = False
        st.rerun()

    # User input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        if st.session_state.current_agent == 'sales':
            response = sales_agent_executor.run(input=user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
        elif st.session_state.current_agent == 'product':
            answer = process_product_query(user_input)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        elif st.session_state.current_agent == 'needs':
            st.session_state.messages.append({"role": "assistant", "content": "Please fill out the needs assessment form below."})
        
        st.rerun()

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
                        st.session_state.messages.append({"role": "assistant", "content": needs_summary})
                        st.success(f"Your information has been saved to {file_path}.")
                        st.session_state.show_needs_form = False

                        # Trigger product recommendation immediately
                        product_recommendation = handle_product_recommendation(st.session_state.needs_summary)
                        st.session_state.product_recommendation = product_recommendation
                        st.session_state.messages.append({"role": "assistant", "content": product_recommendation})
                        st.rerun()
                    else:
                        st.warning("Please fill in all fields before submitting.")