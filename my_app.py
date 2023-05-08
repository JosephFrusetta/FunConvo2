import os
import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from tenacity import retry, stop_after_attempt, wait_exponential

app = Flask(__name__)

# Set environment variables
openai.api_key = os.environ['OPENAI_API_KEY']
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_client = Client(account_sid, auth_token)

# Create an empty list, store the chat history, and add my system message
message_history = [{'role': 'system', 'content': "You are an AI designed to generate three engaging conversation starters by utilizing user-provided observations. You provide multifaceted questions (Interesting sombrero, ¿Cuál es la historia detrás de él? - What's the story behind it?), factual trivia (Did you know that many resorts outlawed snowboarding when the sport was invented back in the 80's?), and complex conundrums (If both your parents need a kidney to live and you were the only match in the world - what would you do?)."}]

# Decorator from tenacity, used to configure retry logic
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=60))
def call_openai_api(messages):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
# Decorator from Flask, defines a route for handling incoming HTTP POST requests at the /sms endpoint.
@app.route('/sms', methods=['POST'])
def sms_reply(role="user"):
    message_history.append({"role": role, "content": request.form.get('Body', '').strip()})

    # Try to generate a response using GPT-3.5
    try:
        completion = call_openai_api(message_history)
    except Exception as e:
        error_message = f"Error: {e}. Please try again later."
        twilio_response = MessagingResponse()
        twilio_response.message(error_message)
        return str(twilio_response)

    # Extract the generated text
    generated_text = completion.choices[0].message.content

    # Create a Twilio MessagingResponse object
    twilio_response = MessagingResponse()
    
    # Add the generated response to the chat history
    message_history.append({"role": "assistant", "content": f"{generated_text}"}) 

    # Add the generated text as a reply
    twilio_response.message(generated_text)

    # Send the response back as an SMS
    return str(twilio_response)