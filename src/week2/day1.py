import json
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
        price_function = {
            "name": "get_ticket_price",
            "description": "Get the price of a return ticket to the destination city",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination_city": {
                        "type": "string",
                        "description": "The city that the customer wants to travel to",
                    },
                },
                "required": ["destination_city"],
                "additionalProperties": False
            }
        }
        history = [{ "role": h["role"], "content": h["content"]} for h in history]
        messages = [{ "role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
        tools = [{"type": "function", "function": price_function}]

        response = self.openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

        if response.choices[0].finish_reason == "tool_calls":
            message = response.choices[0].message
            responses = self.handle_tool_calls(message)
            messages.append(message)
            messages.extend(responses)
            response = self.openai.chat.completions.create(model=MODEL, messages= messages)

        return response.choices[0].message.content

    def get_ticket_price(self, destination_city):
        ticket_prices = {"london": "$799", "paris": "$899", "tokyo": "$1400", "berlin": "$499"}

        print(f"Tool called for city {destination_city}")
        price = ticket_prices.get(destination_city.lower(), "Unknown ticket price")
        return f"The price of a ticket to {destination_city} is {price}"

    def handle_tool_call(self, message):
        tool_call = message.tool_calls[0]
        if tool_call.function.name == "get_ticket_price":
            arguments = json.loads(tool_call.function.arguments)
            city = arguments.get('destination_city')
            price_details = self.get_ticket_price(city)
            response = {
                "role": "tool",
                "content": price_details,
                "tool_call_id": tool_call.id
            }
            return response

    def handle_tool_calls(self, message):
        responses = []
        for tool_call in message.tool_calls:
            if tool_call.function.name == "get_ticket_price":
                arguments = json.loads(tool_call.function.arguments)
                city = arguments.get("destination_city")
                price_details = self.get_ticket_price(city)
                responses.append({
                    "role": "tool",
                    "content": price_details,
                    "tool_call_id": tool_call.id
                })
        return responses
