# Third-party imports
import openai
from fastapi import FastAPI, Form, Depends, Request
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Unique Violation
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors

# Internal imports
from models import Conversation, SessionLocal
from utils import send_message, logger


app = FastAPI(debug=True)
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
    messages.append({"role": "system", "content": "You're an experienced chef specialized in mediterranean dishes wit many years of experience, a passionate by very short and easy recipes to make at home. Your answers contain 1600 characters maximum. You understand nothing but cooking."})
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5
        )

    # The generated text
    chatgpt_response = response.choices[0].message.content
    print(chatgpt_response)

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