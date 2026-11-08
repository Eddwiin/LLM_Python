from config.load_openai_key import api_key
from openai import OpenAI
from week2.day4 import Chat
import gradio as gr

openai = OpenAI(api_key=api_key)

chatInstance = Chat(openai)

def create_first_ui_with_gradio():
    gr.ChatInterface(fn=chatInstance.chat).launch()

def get_ticket_price(city):
    chatInstance.get_ticket_price(city)

def main():
    create_first_ui_with_gradio()


if __name__ == "__main__":
    main()