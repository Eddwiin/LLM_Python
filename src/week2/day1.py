def first_conversation(openai):
    system_prompt = """
        You are a snarky assistant that analyzes the contents of a website,
        and provides a short, snarky, humorous summary, ignoring text that might be navigation related.
        Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
    """
    
    user_prompt_prefix = """
        Here are the contents of a website.
        Provide a short summary of this website.
        If it includes news or announcements, then summarize these too.
    """
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "What is 2 + 2?"}
    ]
    
    response = openai.chat.completions.create(model="gpt-4.1-mini", messages=messages)
    return response.choices[0].message.content