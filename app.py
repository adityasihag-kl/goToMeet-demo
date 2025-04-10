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

def format_service_response(service_response):
    """Format a service response into a pretty HTML string"""
    if (not service_response or 
        service_response.get("error") or 
        not service_response.get("response_parsed") or 
        service_response.get("response_parsed", {}).get("impact_score", 0) <= 7):
        return None
    
    service_section = service_response.get("service_section", "Unknown Section")
    service_name = service_response.get("service_name", "Unknown Service")
    impact_score = service_response.get("response_parsed", {}).get("impact_score", "N/A")
    summary = service_response.get("response_parsed", {}).get("summary_report", "No summary available")
    details = service_response.get("response_parsed", {}).get("detailed_reasoning_report", "No details available")
    
    # Format impact score with stars
    impact_stars = "⭐" * int(impact_score) if isinstance(impact_score, (int, float)) else ""
    
    html = f"""
    <div style="margin-bottom: 20px; padding: 15px; border-radius: 10px; background-color: #1E293B; color: #E2E8F0;">
        <h3 style="color: #38BDF8; margin-top: 0;">{service_section}: {service_name}</h3>
        <div style="margin-bottom: 10px;">
            <span style="font-weight: bold; color: #7DD3FC;">Impact Score:</span> {impact_score} {impact_stars}
        </div>
        <div style="margin-bottom: 15px;">
            <span style="font-weight: bold; color: #7DD3FC;">Summary:</span>
            <p>{summary}</p>
        </div>
        <details>
            <summary style="cursor: pointer; color: #7DD3FC; font-weight: bold;">Detailed Analysis</summary>
            <div style="margin-top: 10px; padding: 10px; background-color: #334155; border-radius: 5px;">
                {details}
            </div>
        </details>
    </div>
    """
    return html

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
        st.session_state.researcher = deepReseacher()
        researcher = st.session_state.researcher
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
                report_results_response, service_responses = researcher.process_template(company_details=st.session_state.selected_company)
                
                # Create a formatted message for chat history
                company_name = st.session_state.selected_company.get('company_name', 'Unknown')
                
                # Start with the main report
                if report_results_response:
                    main_report = f"## Research Report: {company_name}\n\n{report_results_response}\n\n"
                else:
                    main_report = f"## Research Report: {company_name}\n\nNo general report available.\n\n"
                
                # Add section for high-impact recommendations
                main_report += "### Key Opportunities\n\n"
                
                # Add to message history
                st.session_state.messages.append({"role": "assistant", "content": main_report})
                
                # Store service responses in session state for display
                st.session_state.service_responses = service_responses
                st.session_state.initial_research_done = True
        
        # Chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)
        
        # Display service recommendations after the first message
        if st.session_state.initial_research_done and hasattr(st.session_state, 'service_responses'):
            service_responses = st.session_state.service_responses
            
            # Filter for high-impact services
            high_impact_services = []
            for service in service_responses:
                if (service and 
                    not service.get("error") and 
                    service.get("response_parsed") and 
                    service.get("response_parsed", {}).get("impact_score", 0) > 7):
                    high_impact_services.append(service)
            
            # Display recommendations in expanders
            if high_impact_services:
                for i, service in enumerate(high_impact_services):
                    service_section = service.get("service_section", "Unknown Section")
                    service_name = service.get("service_name", "Unknown Service")
                    impact_score = service.get("response_parsed", {}).get("impact_score", "N/A")
                    summary = service.get("response_parsed", {}).get("summary_report", "No summary available")
                    details = service.get("response_parsed", {}).get("detailed_reasoning_report", "No details available")
                    
                    with st.expander(f"{service_section}: {service_name} (Impact: {impact_score})", expanded=(i==0)):
                        st.markdown(f"**Summary:** {summary}")
                        st.markdown("**Detailed Analysis:**")
                        st.markdown(details)
            else:
                st.info("No high-impact opportunities (impact score > 7) were identified. Please ask a specific question to learn more.")
        
        # Chat input - only show if company is selected
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process response - for all subsequent messages, use the message parameter
            with st.spinner("Generating response..."):
                response_text = researcher.process_template(message=prompt)
                
                # For chat responses, just use the text directly
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
                # Display assistant response
                with st.chat_message("assistant"):
                    st.markdown(response_text, unsafe_allow_html=True)
        
        # Reset button in sidebar
        if st.sidebar.button("Reset Chat"):
            st.session_state.messages = []
            st.session_state.initial_research_done = False
            if hasattr(st.session_state, 'service_responses'):
                delattr(st.session_state, 'service_responses')
            st.rerun()

if __name__ == "__main__":
    main() 