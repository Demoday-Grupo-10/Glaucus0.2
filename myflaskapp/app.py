from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from google.cloud import vision
from web_detect import annotate, report
import os
import json
import requests
import re

app = Flask(__name__)

os.environ['OPENAI_API_KEY'] = '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'
openai = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

chat_history = []

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    assistant_response = None
    if request.method == 'POST':
        user_input = request.form['user_input']
        assistant_response = call_openai_api(user_input)
        chat_history.append({'user': user_input, 'assistant': assistant_response})
    return render_template('chat.html', chat_history=chat_history, assistant_response=assistant_response)

def call_openai_api(user_input):
    url = "https://api.openai.com/v1/engines/text-davinci-002/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }
    data = {
        "prompt": user_input,
        "max_tokens": 400
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print ("Erro:",err)
        return None

    response_json = response.json()

    if 'error' in response_json:
        print(f"Erro ao chamar a API da OpenAI: {response_json['error']}")
        return None

    if 'choices' in response_json and len(response_json['choices']) > 0:
        text = response_json['choices'][0]['text'].strip() or "Sem resposta"
        text = filter_undesirable_words(text)
        text = text.replace('-BR', '')
        return text
    else:
        print(f"Resposta inesperada da API da OpenAI: {response_json}")
        return None

def filter_undesirable_words(text):
    undesirable_words = ['palavra1', 'palavra2', 'palavra3']
    for word in undesirable_words:
        regex = re.compile(rf'\\b{word}\\b', re.IGNORECASE)
        text = regex.sub('****', text)
    return text


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/mapa')
def mapa():
    return render_template('mapa.html')

@app.route('/scaner', methods=['GET', 'POST'])
def index():
    report_results = None
    image_url = None
    if request.method == 'POST':
        image_url = request.form.get('image_url')
        uploaded_file = request.files.get('image_file')
        annotations = annotate(image_url, uploaded_file)
        report_results = report(annotations)
    return render_template('index.html', report=report_results, image_url=image_url)

if __name__ == "__main__":
    app.run(debug=True)