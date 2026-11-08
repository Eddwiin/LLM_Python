from config.load_openai_key import api_key
from openai import OpenAI
from week2.day1 import Chat
import gradio as gr

openai = OpenAI(api_key=api_key)

def create_first_ui_with_gradio():
    chatInstance = Chat(openai)
    gr.ChatInterface(fn=chatInstance.chat).launch()

def main():
    create_first_ui_with_gradio()


if __name__ == "__main__":
    main()