import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import openai

app = Flask(__name__)

# Set environment variables
openai.api_key = os.environ['OPENAI_API_KEY']
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_client = Client(account_sid, auth_token)

# Create an empty list, store the chat history, and add my system message
message_history = [{'role': 'system', 'content': "You are an AI that is intelligent, creative, and clever. You generate two or three interesting conversation starters based on observations made and provided by the user. Observations might only be one or two words. You provide multifaceted questions(Interesting sombrero, ¿Cuál es la historia detrás de él? - What's the story behind it?), factual trivia(Did you know that many resorts outlawed snowboarding when the sport was invented back in the 80's?), and complex conundrums(If both your parents need a kidney to live and you're the only match in the world - what would you do?)."}]

@app.route('/sms', methods=['POST'])
def sms_reply(role="user"):
    message_history.append({"role": role, "content": request.form.get('Body', '').strip()})

    # Generate a response using GPT-3.5
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_history
    )

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