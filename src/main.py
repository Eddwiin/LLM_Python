from config.load_openai_key import api_key
from openai import OpenAI
from week2.day1 import first_conversation


openai = OpenAI(api_key=api_key)

def main():
    print(first_conversation(openai))


if __name__ == "__main__":
    main()