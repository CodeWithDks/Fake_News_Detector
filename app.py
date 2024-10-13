from flask import Flask, render_template, request, jsonify, session
import pickle
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
#from sklearn.metrics import confidence_score
import uuid

app = Flask(__name__)
app.secret_key = '+7nv0mToqv1UONSy+PAF7ZGQutVgc6Bf'  # Replace with a real secret key

# Load the model and vectorizer
with open('model/svm_classifier.pkl', 'rb') as model_file:
    svm_classifier = pickle.load(model_file)

with open('model/tfidf_vectorizer.pkl', 'rb') as vectorizer_file:
    tfidf_vectorizer = pickle.load(vectorizer_file)

# Download NLTK resources
import nltk
nltk.download('punkt')
nltk.download('stopwords')

def clean_text(text):
   # Convert text to lowercase
    text = text.lower()

    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # Remove links
    text = re.sub(r'http\S+', '', text)

    # Tokenize the text
    words = word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]

    # Initialize Porter Stemmer
    stemmer = PorterStemmer()

    # Perform stemming
    stemmed_words = [stemmer.stem(word) for word in filtered_words]

    # Join the stemmed words back into a single string
    cleaned_text = ' '.join(stemmed_words)

    return cleaned_text

def predict_fake_or_real(text):
    # Clean the input text
    cleaned_text = clean_text(text)

    # Transform the cleaned text using the TF-IDF vectorizer
    text_tfidf = tfidf_vectorizer.transform([cleaned_text])

    # Use the trained classifier to predict
    prediction = svm_classifier.predict(text_tfidf)
    confidence = svm_classifier.decision_function(text_tfidf)

    # Map prediction to label
    label = "fake" if prediction[0] == 1 else "real"
    
    # Calculate confidence percentage
    confidence_pct = (abs(confidence[0]) / 2) * 100  # Normalize to 0-100 range

    return label, confidence_pct

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['real_count'] = 0
        session['fake_count'] = 0
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data['text']
    prediction, confidence = predict_fake_or_real(text)
    
    # Update session counts
    if prediction == 'real':
        session['real_count'] += 1
    else:
        session['fake_count'] += 1
    
    return jsonify({
        'prediction': prediction,
        'confidence': confidence,
        'real_count': session['real_count'],
        'fake_count': session['fake_count']
    })

if __name__ == '__main__':
    app.run(debug=True)