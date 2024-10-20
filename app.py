import cohere
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
import io

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Cohere API client with your API key
COHERE_API_KEY = os.getenv('COHERE_API_KEY', 'DC3z79fsbexHYYOoShuufn4syRm3jqPA4LUsSXeb')  # Replace with your actual key or set as an environment variable
cohere_client = cohere.Client(COHERE_API_KEY)

class SocraticAssistant:
    def ask_cohere(self, student_response, previous_question, topic):
        # Define the prompt for the Socratic method based on the selected topic
        prompt = f"""
        You are a Socratic teaching assistant specializing in {topic}.
        Your goal is to guide the student to a deeper understanding by asking probing, thought-provoking questions based on their responses.

        Previous question: {previous_question if previous_question else "None"}
        Student's response: {student_response}

        Generate a relevant, Socratic-style follow-up question to help the student think critically about {topic}.
        """

        try:
            # Call the Cohere API for text generation
            response = cohere_client.generate(
                model='command-xlarge-nightly',  # Use an appropriate Cohere model
                prompt=prompt,
                max_tokens=50,
                temperature=0.7,
                stop_sequences=["\n"]
            )

            # Extract the generated question
            question = response.generations[0].text.strip()
            return question

        except Exception as e:
            print(f"Error communicating with Cohere API: {e}")
            return "I'm here to help! Can you tell me more about your approach?"

assistant = SocraticAssistant()

# Store the selected topic for the session
user_topic = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/set_topic', methods=['POST'])
def set_topic():
    topic = request.form.get('topic', '').strip()
    if topic:
        user_topic['topic'] = topic
        return jsonify({"message": f"Topic set to {topic}. You can start answering questions!"})
    return jsonify({"error": "Please provide a valid topic."})

@app.route('/ask', methods=['POST'])
def ask():
    student_response = request.form.get('student_response', '').strip()
    previous_question = request.form.get('previous_question', '').strip()
    topic = user_topic.get('topic', 'sorting algorithms')  # Default topic

    if not student_response:
        return jsonify({"question": "Please provide a response to continue."})

    # Get the next Socratic question from Cohere based on the selected topic
    next_question = assistant.ask_cohere(student_response, previous_question, topic)
    return jsonify({"question": next_question})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Here, you can implement further processing or response generation based on the image
        return jsonify({"message": f"Image '{filename}' uploaded successfully."})

    return jsonify({"error": "File type not allowed."})

if __name__ == '__main__':
    app.run(debug=True)
