import json
import sqlite3

MODEL = "gpt-4.1-mini"
DB = "prices.db"

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
        self.init_db()

    def init_db(self):
        with sqlite3.connect(DB) as conn:
            conn.execute('CREATE TABLE IF NOT EXISTS prices (city TEXT PRIMARY KEY, price REAL)')

        ticket_prices = {"london": 799, "paris": 899, "tokyo": 1420, "sydney": 2999}
        for city, price in ticket_prices.items():
            self.set_ticket_price(city, price)

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

        set_price_function = {
            "name": "set_ticket_price",
            "description": "Set the price of ticket for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination_city": {
                        "type": "string",
                        "description": "The new city need to be add in database"
                    },
                    "price": {
                        "type": "number",
                        "description": "The price of ticket to the new city to add in database"
                    }
                },
                "required": ["destiny_city", "price"],
                "additionalProperties": False
            },

        }

        history = [{ "role": h["role"], "content": h["content"]} for h in history]
        messages = [{ "role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
        tools = [{"type": "function", "function": price_function}, {"type": "function", "function": set_price_function}]

        response = self.openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

        if response.choices[0].finish_reason == "tool_calls":
            message = response.choices[0].message
            responses = self.handle_tool_calls(message)
            messages.append(message)
            messages.extend(responses)
            response = self.openai.chat.completions.create(model=MODEL, messages= messages)

        return response.choices[0].message.content

    def get_ticket_price(self, destination_city):
        print(f"DATABASE TOOL CALLED: Getting price for {destination_city}", flush=True)
        with sqlite3.connect(DB) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT price FROM prices WHERE city = ?', (destination_city.lower(),))
            result = cursor.fetchone()
            return f"Ticket price to {destination_city} is ${result[0]}" if result else "No price data available for this city"

    def set_ticket_price(self,city, price):
        with sqlite3.connect(DB) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO prices (city, price) VALUES (?, ?) ON CONFLICT(city) DO UPDATE SET price = ?', (city.lower(), price, price))
            conn.commit()
        return f"The price of a ticket to {city} is now ${price}"

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

            elif tool_call.function.name == "set_ticket_price":
                arguments = json.loads(tool_call.function.arguments)
                city = arguments.get("destination_city")
                price = arguments.get("price")
                set_price = self.set_ticket_price(city, price)
                responses.append({
                    "role": "tool",
                    "content": set_price,
                    "tool_call_id": tool_call.id
                })
        return responses
