MODEL = "gpt-4.1-mini"

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

class Chat:
    def __init__(self, openai):
        self.openai = openai

    def chat(self, message, history):
        system_message = """
                You are a helpful assistant for an Airline called FlightAI.
                Give short, courteous answers, no more than 1 sentence.
                Always be accurate. If you don't know the answer, say so.
            """
        history = [{ "role": h["role"], "content": h["content"]} for h in history]
        messages = [{ "role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
        response = self.openai.chat.completions.create(model=MODEL, messages=messages)
        return response.choices[0].message.content
