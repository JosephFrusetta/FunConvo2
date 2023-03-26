import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import openai

app = Flask(__name__)

# Set your Twilio Account SID and Auth Token as environment variables
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']

twilio_client = Client(account_sid, auth_token)

# Set your OpenAI GPT-4 API key as an environment variable
openai.api_key = os.environ['OPENAI_API_KEY']

# Create an empty list, store the chat history, and add a system message to it
message_history = [{'role': 'system', 'content': "The following is a conversation with an AI that helps humans create interesting conversation starters. The AI is intelligent, creative, and clever. The AI will not provide boring nor conventional messages."}]

@app.route('/sms', methods=['POST'])
def sms_reply(role="user"):
    
    # Get the incoming SMS message / # Add the user input to the chat history
    message_history.append({"role": role, "content": request.form.get('Body', '')})   

    # Generate a response using GPT-3.5 API
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_history # Use the message history as input
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

if __name__ == "__main__":
    app.run(debug=True)
