import base64
from io import BytesIO
from PIL import Image

MODEL = "gpt-image-1-mini"
system_message = """
                You are a helpful assistant for an Airline called FlightAI.
                Give short, courteous answers, no more than 1 sentence.
                Always be accurate. If you don't know the answer, say so.
            """

class Artist:
    def __init__(self, openai):
        self.openai = openai

    def chat(self, history):
        history = [{ "role": h["role"], "content": h["content"]} for h in history]
        messages = [{ "role": "system", "content": system_message}] + history
        price_function = {
            "name": "get_ticket_price",
            "description": "Get the price of a return ticket to the destination city.",
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
        tools = [{"type": "function", "function": price_function}]
        response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)
        cities = []
        image = None

        while response.choices[0].finish_reason == "tool_calls":
            message = response.choices[0].message
            responses, cities = handle_tool_calls_and_return_cities(message)
            messages.append(message)
            messages.extend(responses)
            response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

        reply = response.choices[0].message.content
        history += [{"role":"assistant", "content":reply}]

        voice = talker(reply)
        if cities:
            image = artist(cities[0])
            image.show()

        return history, voice, image

    def generate_image(self, city):
        image_response = self.openai.images.generate(
            model=MODEL,
            prompt=f"An image representing a vacation in {city}, showing tourist spots and everything unique about {city}, in a vibrant pop-art style",
            size="1024x1024",
            n=1,
        )

        image_base64 = image_response.data[0].b64_json
        image_data = base64.b64decode(image_base64)
        return Image.open(BytesIO(image_data))

    def talker(self, message):
        response = openai.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="coral",    # Also, try replacing onyx with alloy or coral
            input=message
        )
        return response.content

    def handle_tool_calls_and_return_cities(self, message):
        responses = []
        cities = []

        for tool_call in message.tool_calls:
            if tool_call.function.name == "get_ticket_price":
                arguments = json.loads(tool_call.function.arguments)
                city = arguments.get("destination_city")
                cities.append(city)
                price_details = get_ticket_price(city)
                responses.append({
                    "role": "tool",
                    "content": price_details,
                    "tool_call_id": tool_call.id
                })
        return responses, cities
