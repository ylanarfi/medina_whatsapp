# Medina WhatsApp Chef
Immerse yourself in the flavors of the Mediterranean with Medina, a Python-powered app revolutionizing the way we explore and create traditional cuisine. Medina is not just a cookbook; it's a culinary companion designed to guide you through the rich tapestry of Mediterranean cooking. Medina offers an innovative and interactive cooking experience by leveraging the power of chatbot technology. By simply sending a message through WhatsApp, you can instantly access a treasure trove of Mediterranean recipes.

# Prerequisites

To follow this tutorial, you will need the following prerequisites:

Python 3.7+ installed on your machine.
PostgreSQL installed on your machine.
A Twilio account set up. If you don't have one, you can create a free account here.
An OpenAI API key to access ChatGPT.
A smartphone with WhatsApp installed to test your AI chatbot.
A basic understanding of FastAPI, a modern, fast (high-performance), web framework for building APIs with Python 3.6+.
A basic understanding of what an ORM is. If you are not familiar with ORM, we recommend you to read this wiki page to get an idea of what it is and how it works.

# Installation

```bash
mkdir medina_whatsapp
cd media_whatsapp
python3 -m venv venv; . venv/bin/activate; pip install --upgrade pip
```

Create a requirements.txt file that includes the following:

```bash
fastapi
uvicorn
twilio
openai
python-decouple
sqlalchemy
psycopg2-binary
python-multipart
pyngrok
```

Install these dependencies

```bash
pip install -r requirements.txt
```

Configuring database

You can use your own PostgreSQL database or set up a new database with the createdb PostgreSQL utility command:

```bash
createdb mydb
```

In this tutorial, you will use SQLAlchemy to access the PostgreSQL database. Put the following into a new models.py file:

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker
from decouple import config


url = URL.create(
    drivername="postgresql",
    username=config("DB_USER"),
    password=config("DB_PASSWORD"),
    host="localhost",
    database="mydb",
    port=5432
)

engine = create_engine(url)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    message = Column(String)
    response = Column(String)


Base.metadata.create_all(engine)
```

So the goal of this simple model is to store conversations for your app.

Note: here, you've used decouple.config to access the environment variables for your database: DB_USER and DB_PASSWORD. You should now create a .env file that stores these credentials with their associated values. Something like the following, but replacing the placeholder text with your actual values:

```bash
DB_USER=<your-database-username>
DB_PASSWORD=<your-database-password>
```

# Creating your chatbot

Now that you have set up your environment and created the database, it's time to build the chatbot. In this section, you will write the code for a basic chatbot using OpenAI and Twilio.

Configuring your Twilio Sandbox for WhatsApp
To use Twilio's Messaging API to enable the chatbot to communicate with WhatsApp users, you need to configure the Twilio Sandbox for WhatsApp. Here's how to do it:

1. Assuming you've already set up a new Twilio account, go to the Twilio Console and choose the Messaging tab on the left panel.
2. Under Try it out, click on Send a WhatsApp message. You'll land on the Sandbox tab by default and you'll see a phone number "+14155238886" with a code to join next to it on the left and a QR code on the right.
3. To enable the Twilio testing environment, send a WhatsApp message with this code's text to the displayed phone number. You can click on the hyperlink to direct you to the WhatsApp chat if you are using the web version. Otherwise, you can scan the QR code on your phone.

Now, the Twilio sandbox is set up, and it's configured so that you can try out your application after setting up the backend. Before leaving the Twilio Console, you should take note of your Twilio credentials and edit the .env file as follows:

```bash
B_USER=<your-database-username>
DB_PASSWORD=<your-database-password>
TWILIO_ACCOUNT_SID=<your-twilio-account-sid>
TWILIO_AUTH_TOKEN=<your-twilio-auth-token>
TWILIO_NUMBER=+14155238886
```

# Setting up your Twilio WhatsApp API snippet

Before setting up the FastAPI endpoint to send a POST request to WhatsApp, let's build a utility script first to set up sending a WhatsApp message through the Twilio Messaging API.

Create a new file called utils.py and fill it with the following code:


```python
# Standard library import
import logging

# Third-party imports
from twilio.rest import Client
from decouple import config


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = config("TWILIO_ACCOUNT_SID")
auth_token = config("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)
twilio_number = config('TWILIO_NUMBER')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sending message logic through Twilio Messaging API
def send_message(to_number, body_text):
    try:
        message = client.messages.create(
            from_=f"whatsapp:{twilio_number}",
            body=body_text,
            to=f"whatsapp:{to_number}"
            )
        logger.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")
```

First, the necessary libraries are imported, which include the logging library, the Twilio REST client, and the decouple library used to store private credentials in a .env file.

Next, the Twilio Account SID, Auth Token, and phone number are retrieved from the .env file using the decouple library. The Account SID and Auth Token are required to authenticate your account with Twilio, while the phone number is the Twilio WhatsApp sandbox number.

Then, a logging configuration is set up for the function to log any info or errors related to sending messages. If you want more advanced logging to use as a boilerplate, check this out.

The meat of this utility script is the send_message function which takes two parameters, the to_number and body_text, which are the recipient's WhatsApp number and the message body text, respectively.

The function tries to send the message using the client.messages.create method, which takes the Twilio phone number as the sender (from_), the message body text (body), and the recipient's WhatsApp number (to). If the message is successfully sent, the function logs an info message with the recipient's number and the message body. If there is an error sending the message, the function logs an error message with the error message.

# Setting up your FastAPI backend

To set up the FastAPI backend for the chatbot, navigate to the project directory and create a new file called main.py. Inside that file, you will set up a basic FastAPI application that will handle a single incoming request:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def index():
    return {"msg": "working"}
```

To run the app, run the following command:

```bash
uvicorn main:app --reload
```

Open your browser to http://localhost:8000. The result you should see is a JSON response of {"msg": "working"}.

However, since Twilio needs to send messages to your backend, you need to host your app on a public server. An easy way to do that is to use Ngrok.

If you're new to Ngrok, you can consult this blog post and create a new account.

Leave the FastAPI app running on port 8000, and run this ngrok command from another terminal window:

```bash
ngrok http 8000
```

The above command sets up a connection between your local server running on port 8000 and a public domain created on the ngrok.io website. Once you have the Ngrok forwarding URL, any requests from a client to that URL will be automatically directed to your FastAPI backend.

If you click on the forwarding URL, Ngrok will redirect you to your FastAPI app's index endpoint. It's recommended to use the https prefix when accessing the URL.

# Configuring the Twilio webhook

You must set up a Twilio-approved webhook to be able to receive a response when you message the Twilio WhatsApp sandbox number.

To do that, head over to the Twilio Console and choose the Messaging tab on the left panel. Under the Try it out tab, choose Send a WhatsApp message. Next to the Sandbox tab, choose the Sandbox settings tab.

The complete URL should look like this: https://d8c1-197-36-101-223.ngrok.io/message.

The endpoint you will configure in the FastAPI application is /message, as noted. The chatbot logic will be on this endpoint.

When done, press the Save button.

# Sending your message with OpenAI API

Now, it's time to create the logic for sending the WhatsApp message to the OpenAI API so that you'll get a response from the ChatGPT API.

Update the main.py script to the following:

```python
# Third-party imports
import openai
from fastapi import FastAPI, Form, Depends, Request
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Internal imports
from models import Conversation, SessionLocal
from utils import send_message, logger


app = FastAPI()
# Set up the OpenAI API client
openai.api_key = config("OPENAI_API_KEY")

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
async def index():
    return {"msg": "working"}

@app.post("/message")
async def reply(request: Request, Body: str = Form(), db: Session = Depends(get_db)):
    # Extract the phone number from the incoming webhook request
    form_data = await request.form()
    whatsapp_number = form_data['From'].split("whatsapp:")[-1]
    print(f"Sending the ChatGPT response to this number: {whatsapp_number}")

    # Call the OpenAI API to generate text with ChatGPT
    messages = [{"role": "user", "content": Body}]
    messages.append({"role": "system", "content": "You're an investor, a serial founder and you've sold many startups. You understand nothing but business."})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5
        )

    # The generated text
    chatgpt_response = response.choices[0].message.content

    # Store the conversation in the database
    try:
        conversation = Conversation(
            sender=whatsapp_number,
            message=Body,
            response=chatgpt_response
            )
        db.add(conversation)
        db.commit()
        logger.info(f"Conversation #{conversation.id} stored in database")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error storing conversation in database: {e}")
    send_message(whatsapp_number, chatgpt_response)
    return ""
```

This code sets up a straightforward web application that can receive messages and respond to them using OpenAI's ChatGPT language model. The application listens for incoming requests on two endpoints: the root URL (/) and /message.

The openai.api_key variable is set to the value of the OPENAI_API_KEY environment variable using the config() function from the decouple library. The .env file should now look like the following:

```bash
DB_USER=<your-database-username>
DB_PASSWORD=<your-database-password>
TWILIO_ACCOUNT_SID=<your-twilio-account-sid>
TWILIO_AUTH_TOKEN=<your-twilio-auth-token>
TWILIO_NUMBER=+14155238886
OPENAI_API_KEY=<your-openai-api-key>
```

The SessionLocal class and Conversation model are imported from the models.py file as you defined previously. These classes are used to set up a database connection and define the structure of the conversation data that will be stored in the database.

The get_db function defines a dependency that is used by the /message endpoint to get a database session object. This function creates a new session object and yields it to the calling function. Once the calling function is finished executing, the finally block ensures that the session object is closed properly.

The / endpoint returns a simple JSON message indicating that the application is working, which was tested already with your ngrok setup.

The /message endpoint is used to receive incoming messages from the user. The Body parameter is used to extract the text of the message. The request parameter is used to extract the sender's phone number from the incoming webhook request.

The ChatGPT API is called to generate a response to the user's message. The prompt consists of the user's message and an additional context message that describes the user as an experienced investor and founder. The generated response is stored in the chatgpt_response variable.

The conversation data (sender phone number, user message, and ChatGPT response) are stored in the database using an instance of the Conversation model. If there is an error when storing the conversation data in the database, the function logs an error message and rolls back the transaction.

Finally, the response generated by ChatGPT is sent back to the user using the send_message function, which is imported from the utility module.