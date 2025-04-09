import streamlit as st
import json
from deep_research import deepReseacher

# Sample template data - replace with actual data later
TEMPLATES = [
    {
        "company_name": "Pidilite USA, Inc.",
        "country": "United States of America",
        "headquarters": None,
        "industry_sector": "Manufacturing of art supplies/chemicals",
        "key_locations": [
            "Hazleton, Pennsylvania (Sargent Art division)",
        ],
        "number_of_employees": 0,
        "website": None,
        "year_of_incorporation": 2006
    },
    {
        "company_name": "Mahindra USA, Inc.",
        "country": "United States of America",
        "headquarters": None,
        "industry_sector": "Agricultural Machinery/Automotive",
        "key_locations": [],
        "number_of_employees": None,
        "website": None,
        "year_of_incorporation": 1994
    }
]

def main():
    """Main application function"""
    # Configure Streamlit page settings
    st.set_page_config(page_title="GoTo Meet - Demo", page_icon="💬", layout="wide")
    
    # Custom CSS to hide the Streamlit toolbar
    st.markdown("""
        <style>
            .stAppToolbar {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "company_selected" not in st.session_state:
        st.session_state.company_selected = False

    if "selected_company" not in st.session_state:
        st.session_state.selected_company = None
        
    if "initial_research_done" not in st.session_state:
        st.session_state.initial_research_done = False
        
    # Initialize deepReseacher only once per session
    if "researcher" not in st.session_state:
        st.session_state.researcher = deepReseacher()
    
    # Use the researcher from session state
    researcher = st.session_state.researcher
    
    # App header in main area
    st.title("GoTo Meet - demo")

    # Sidebar with company selection dropdown
    st.sidebar.header("Company Selection")
    
    # Get list of company names for dropdown
    company_names = [template.get('company_name', 'Unknown') for template in TEMPLATES]
    
    # Dropdown for company selection
    selected_company_name = st.sidebar.selectbox(
        "Select a company:",
        company_names,
        key="company_dropdown"
    )
    
    # Find the selected template based on company name
    selected_template = next((template for template in TEMPLATES if template.get('company_name') == selected_company_name), None)
    
    # Button to confirm selection
    if st.sidebar.button("Confirm Selection"):
        st.session_state.selected_company = selected_template
        st.session_state.company_selected = True
        st.session_state.initial_research_done = False
        st.rerun()
    
    # If company is selected, show company details in sidebar
    if st.session_state.company_selected and st.session_state.selected_company:
        template = st.session_state.selected_company
        
        st.sidebar.markdown("---")
        st.sidebar.header("Company Details")
        st.sidebar.write(f"Name: {template.get('company_name', 'Unknown')}")
        st.sidebar.write(f"Industry: {template.get('industry_sector', 'Unknown')}")
        st.sidebar.write(f"Country: {template.get('country', 'Unknown')}")
        
        # Display locations if available
        if template.get('key_locations'):
            st.sidebar.write("Key Locations:")
            for location in template.get('key_locations', []):
                st.sidebar.write(f"- {location}")
                
        # Display other details if available
        if template.get('year_of_incorporation'):
            st.sidebar.write(f"Founded: {template.get('year_of_incorporation')}")
        
        if template.get('website'):
            st.sidebar.write(f"Website: {template.get('website')}")
            
        if template.get('number_of_employees'):
            st.sidebar.write(f"Employees: {template.get('number_of_employees')}")
    
    # Initial message asking to select a company
    if not st.session_state.company_selected:
        st.info("👈 Please select a company from the sidebar and press 'Confirm Selection' to start chatting.")
    else:
        # Process the initial template research if not already done
        if not st.session_state.initial_research_done:
            with st.spinner("Generating company research report..."):
                # Process the template and add initial message
                response_text, _ = researcher.process_template(template_json=st.session_state.selected_company)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                st.session_state.initial_research_done = True
        
        # Chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input - only show if company is selected
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process response - for all subsequent messages, use the message parameter
            with st.spinner("Generating response..."):
                response_text, _ = researcher.process_template(message=prompt)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
                # Display assistant response
                with st.chat_message("assistant"):
                    st.markdown(response_text)
        
        # Reset button in sidebar
        if st.sidebar.button("Reset Chat"):
            st.session_state.messages = []
            st.session_state.initial_research_done = False
            st.rerun()

if __name__ == "__main__":
    main() 