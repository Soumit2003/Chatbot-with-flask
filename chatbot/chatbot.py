import os
import ollama
import PyPDF2 as pdf
from flask import Flask, render_template, request
import pandas as pd 
from docx import Document

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

client = ollama.Client()

@app.route('/')
def chat():
    return render_template("chat.html") 

@app.route('/send_query', methods=['POST'])
def send_query():
    user_query = request.form.get("query")
    selected_model = request.form.get("model")    
    return chosen_model(user_query, selected_model)

def chosen_model(prompt, selected_model=None):  
    model_mapping = {
        'model1': "deepseek-r1:1.5b",
        'model2': "gemma2:2b",
        'model3': "llama3.2:1b"
    }
    model = model_mapping.get(selected_model, "deepseek-r1:1.5b")  
    response = client.generate(model=model, prompt=prompt)
    return render_template("chat.html", response=response.response, selected_model=selected_model)
@app.route('/upload', methods=['POST'])
def selected_files():
    uploaded_file = request.files.get("file")
    if not uploaded_file or uploaded_file.filename == "":
        return "No file provided", 400

    filename = uploaded_file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    uploaded_file.save(file_path)
    selected_model = request.form.get("model")  

    if filename.endswith(".pdf"):
        reader = pdf.PdfReader(file_path)
        all_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"
        prompt = f"can you summerize the {all_text}"
        return chosen_model(prompt, selected_model)
    
    elif filename.endswith(".csv") or filename.endswith(".xlsx"):
        if filename.endswith(".csv"):
            reader = pd.read_csv(file_path, encoding='latin1', sep=',')  
        elif filename.endswith(".xlsx"):
            reader = pd.read_excel(file_path)
        prompt = f"Can you summarize this: '{reader.describe()}'"
        return chosen_model(prompt, selected_model)
    elif filename.endswith(".docx"):
        doc = Document(file_path)  # Open the document
        all_text = "\n".join([para.text for para in doc.paragraphs])  
        prompt = f"Summarize this document: '{all_text[:500]}'"
        return chosen_model(prompt, selected_model)

    else:
        return "File type not supported", 400

if __name__ == "__main__":
    app.run(debug=True)
