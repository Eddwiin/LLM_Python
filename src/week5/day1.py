import os
import glob
from dotenv import load_dotenv
from pathlib import Path
import gradio as gr
from openai import OpenAI


load_dotenv(override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")

MODEL = "gpt-6-luna"
openai = OpenAI()

knowledge = {}

BASE_DIR = Path(__file__).resolve().parent
filenames = glob.glob(str(BASE_DIR / "knowledge-base" / "employees" / "*"))


for filename in filenames:
    name = Path(filename).stem.split(' ')[-1]
    with open(filename, "r", encoding="utf-8") as f:
        knowledge[name.lower()] = f.read()

filenames = glob.glob("knowledge-base/products/*")

for filename in filenames:
    name = Path(filename).stem
    with open(filename, "r", encoding="utf-8") as f:
        knowledge[name.lower()] = f.read()

print(knowledge.keys())

SYSTEM_PREFIX = """
You represent Insurellm, the Insurance Tech company.
You are an expert in answering questions about Insurellm; its employees and its products.
You are provided with additional context that might be relevant to the user's question.
Give brief, accurate answers. If you don't know the answer, say so.

Relevant context:
"""

def get_relevant_context(message):
    text = ''.join(ch for ch in message if ch.isalpha() or ch.isspace())
    words = text.lower().split()
    relevant_context = []
    return [knowledge[word] for word in words if word in knowledge]


# get_relevant_context("Who is lancaster?")

# get_relevant_context("Who is Lancaster and what is carllm?")

def additional_context(message):
    relevant_context = get_relevant_context(message)
    if not relevant_context:
        result = "There is no additional context relevant to the user's question."
    else:
        result = "The following additional context might be relevant in answering the user's question:\n\n"
        result += "\n\n".join(relevant_context)
    return result

# print(additional_context("Who is Alex Lancaster?"))


def chat(message, history):
    system_message = SYSTEM_PREFIX + additional_context(message)
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, reasoning_effort="none", messages=messages)
    return response.choices[0].message.content

view = gr.ChatInterface(chat).launch(inbrowser=True)
