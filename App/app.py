import logging

from flask import (Blueprint, Flask, flash, g, redirect, render_template,
                   request, session, url_for)
from flask_vite import Vite
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               MessagesPlaceholder,
                               SystemMessagePromptTemplate)

app = Flask(__name__)

vite = Vite(app)

logging.getLogger('flask_cors').level = logging.DEBUG

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are acting as an autocomplete tool to help complete sentences. You are not a chatbot. You are not a human. You are a tool. "
        "Do not repeat any part of what has already been said, only complete the sentences going forward starting at the elipses. "
    ),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

llm = ChatOpenAI(temperature=0)
memory = ConversationBufferMemory(return_messages=True)
conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)


@app.route('/')
def hello():
    return render_template("index.j2")


@app.route("/ghost", methods=['POST'])
def ghost():
    json = request.get_json()
    print(json)
    body = json['text']
    body = body + "..."
    prompt = "Complete the following sentence, do not include the part I have included: " + body
    response = conversation.predict(input=prompt)
    response = response.replace(body, "")
    jsonResponse = {
        "body": response
    }
    return jsonResponse
