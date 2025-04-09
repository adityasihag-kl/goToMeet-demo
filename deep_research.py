def process_template(template_json):
    """
    Process the selected template JSON and return a summary paragraph.
    
    Args:
        template_json (dict): The JSON data from the selected template
        
    Returns:
        str: A summary paragraph based on the template
    """
    # For now, return a preset sample summary
    company = template_json.get('company', 'Unknown')
    return f"This is a summary of the {template_json.get('title', 'Unknown')} template from {company}. " \
           f"This template contains {len(template_json.get('content', []))} content items " \
           f"and is categorized as {template_json.get('category', 'uncategorized')}."


def respond_to_message(user_message, template_json):
    """
    Respond to a user message in the chat.
    
    Args:
        user_message (str): The message sent by the user
        template_json (dict): The JSON data from the selected template
        
    Returns:
        str: A response to the user message
    """
    # For now, return preset sample responses
    company = template_json.get('company', 'Unknown')
    
    responses = [
        f"I analyzed your request using {company}'s template data. Here's what I found...",
        f"Based on {company}'s template information, I'd recommend...",
        f"Interesting question! According to {company}'s template data...",
        f"Let me check {company}'s template data for you. It appears that...",
        f"The {company} template you selected suggests that...",
        f"I've analyzed this in the context of {company}'s template..."
    ]
    
    import random
    return random.choice(responses) + f" (Template: {template_json.get('title', 'Unknown')})" 