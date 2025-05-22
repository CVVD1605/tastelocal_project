from openai import OpenAI
import os

#  Hardcode your API key temporarily or use .env
client = OpenAI(api_key="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")

def run_chat():
    print("Welcome to TasteLocal Bot! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful chatbot for tourists looking for food recommendations."},
                    {"role": "user", "content": user_input}
                ]
            )
            reply = response.choices[0].message.content.strip()
            print("Bot:", reply)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    run_chat()
