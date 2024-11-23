from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Fungsi chatbot sederhana
def chatbot_response(user_input):
    # Contoh respon sederhana
    responses = {
        "hello": "Hi there! How can I assist you?",
        "how are you?": "I'm just a bot, but I'm functioning well!",
        "bye": "Goodbye! Have a great day!",
    }
    return responses.get(user_input.lower(), "I'm not sure how to respond to that.")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.json.get("message")
    response = chatbot_response(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
    