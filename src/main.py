from config.load_openai_key import api_key
from openai import OpenAI
from week2.day4 import Chat
from week2.day5 import Artist
import gradio as gr
from IPython.display import display
from week4.day3 import System

openai = OpenAI(api_key=api_key)

chatInstance = Chat(openai)
artistInstance = Artist(openai)

def create_first_ui_with_gradio():
    gr.ChatInterface(fn=chatInstance.chat).launch()

def get_ticket_price(city):
    chatInstance.get_ticket_price(city)

def generate_image():
    artist = Artist(openai)
    image = artist.generate_image("Paris")
    image.show()

def talker():
    gr.ChatInterface(fn=artistInstance.chat).launch()

def main():
    system = System(openai)
    system.compile_and_run()


if __name__ == "__main__":
    main()