import streamlit as st
import json
from deep_research import process_template, respond_to_message

# Page config
st.set_page_config(page_title="Template Chat App", page_icon="💬", layout="wide")

# Sample template data - replace with actual data later
TEMPLATES = [
    {
        "id": 1,
        "title": "Financial Analysis",
        "company": "Goldman Sachs",
        "category": "Finance",
        "content": ["budget", "forecast", "investments"],
        "description": "Template for financial analysis and reporting"
    },
    {
        "id": 2,
        "title": "Market Research",
        "company": "McKinsey & Co",
        "category": "Marketing",
        "content": ["competitors", "trends", "demographics"],
        "description": "Template for market research and analysis"
    },
    {
        "id": 3,
        "title": "Product Development",
        "company": "Apple Inc",
        "category": "Product",
        "content": ["features", "roadmap", "timeline"],
        "description": "Template for product development planning"
    },
    {
        "id": 4,
        "title": "Customer Support",
        "company": "Zendesk",
        "category": "Support",
        "content": ["tickets", "responses", "satisfaction"],
        "description": "Template for customer support operations"
    },
    {
        "id": 5,
        "title": "HR Management",
        "company": "LinkedIn",
        "category": "HR",
        "content": ["hiring", "training", "performance"],
        "description": "Template for human resources management"
    },
    {
        "id": 6,
        "title": "Project Planning",
        "company": "Microsoft",
        "category": "Project",
        "content": ["tasks", "resources", "timeline"],
        "description": "Template for project planning and tracking"
    }
]

# Custom CSS for template tiles
st.markdown("""
<style>
    .template-tile {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        height: 100%;
        color: #E2E8F0;
    }
    .company-name {
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 5px;
        color: #38BDF8;
    }
    .template-title {
        font-size: 1.1em;
        margin-bottom: 10px;
        color: #F1F5F9;
    }
    .template-category {
        background-color: #334155;
        color: #7DD3FC;
        border-radius: 15px;
        padding: 3px 10px;
        font-size: 0.8em;
        display: inline-block;
        margin-bottom: 10px;
    }
    .select-button {
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS to hide the Streamlit toolbar
st.markdown("""
    <style>
        .stAppToolbar {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "template_selected" not in st.session_state:
    st.session_state.template_selected = False

if "selected_template" not in st.session_state:
    st.session_state.selected_template = None

# App header
st.title("GoTo Meet - demo")

# Template selection if not already selected
if not st.session_state.template_selected:
    st.header("Select a Company")
    
    # Display template options in a grid of tiles
    cols = st.columns(3)
    for i, template in enumerate(TEMPLATES):
        with cols[i % 3]:
            tile_html = f"""
            <div class="template-tile">
                <div class="company-name">{template['company']}</div>
                <div class="template-title">{template['title']}</div>
                <div class="template-category">{template['category']}</div>
                <div>{template['description']}</div>
            </div>
            """
            st.markdown(tile_html, unsafe_allow_html=True)
            
            # Add selection button
            if st.button(f"Select", key=f"template_{i}", help=f"Select {template['company']} template"):
                st.session_state.selected_template = template
                st.session_state.template_selected = True
                
                # Process the template and add initial message
                summary = process_template(template)
                st.session_state.messages.append({"role": "assistant", "content": summary})
                st.rerun()

# Chat interface if template has been selected
else:
    # Display template info
    template = st.session_state.selected_template
    st.sidebar.header(f"Company Details")
    st.sidebar.write(f"Name: {template['company']}")
    st.sidebar.write(f"Title: {template['title']}")
    st.sidebar.write(f"Category: {template['category']}")
    st.sidebar.write(f"Description: {template['description']}")
    
    # Chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Process response
        response = respond_to_message(prompt, st.session_state.selected_template)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)

# Reset button in sidebar
if st.session_state.template_selected:
    if st.sidebar.button("Select Different Template"):
        st.session_state.template_selected = False
        st.session_state.selected_template = None
        st.session_state.messages = []
        st.rerun() 