# Template Chat App

A simple Streamlit chat application that allows users to select from 6 template options and engage in a conversation.

## Features

- Select from 6 different template options
- Template information is processed and a summary is provided
- Chat interface for interacting with the system
- Responses are generated based on the selected template

## Setup and Running

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

3. Open your browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

## How to Use

1. Select one of the six template options displayed on the home screen
2. Review the template summary that appears in the chat
3. Type your messages in the chat input box
4. Reset or select a different template using the button in the sidebar

## File Structure

- `app.py`: Main Streamlit application
- `deep_research.py`: Contains functions for processing templates and generating responses
- `requirements.txt`: List of required Python packages 