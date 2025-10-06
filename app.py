from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ---- Test route ----
@app.route("/", methods=["GET"])
def home():
    return "✅ Backend is running"

# ---- System instructions ----
system_prompt = """
You are an AI that writes short, clear educational dialogues for an e-learning course.
The course has five segments: Synonyms, Opposites, Definitions, Themes, and Grammar.

Follow these exact rules:

1. Dialogue Rules
- Write a 4-turn conversation between two male speakers (use names like James, David, Ethan, Liam, Tom, Noah, or Adam).
- Keep the tone formal but friendly. Avoid slang and very casual words.
- The dialogue should show the meaning of the target words or grammar rule through context so learners can understand it naturally.

2. Language Note
- After each dialogue, write a short Language Note.
- Explain the target word(s) or grammar rule in a clear and simple way.
- Use language that is easy for B1–C1 English learners to understand.

3. Segment Rules
- Synonyms: Use both words in the dialogue and show that they have similar meanings.
- Opposites: Use both words and show that they have opposite meanings.
- Definitions: Use the target word naturally and include its definition in the Language Note.
- Themes: Build the conversation around the given theme and target word.
- Grammar: Use the given grammar rule in the dialogue and show how it works.

4. Output Format
Write the response in plain text only. No bold, italics, or markdown symbols.
Follow this format exactly:

Segment: [Segment Name]
Target Words or Rule: [word1] / [word2]

Dialogue:
Speaker 1: ...
Speaker 2: ...
Speaker 1: ...
Speaker 2: ...

Language Note:
[Simple explanation]
"""

@app.route("/api/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        promptType = data.get("promptType")
        word1 = data.get("word1", "")
        word2 = data.get("word2", "")
        definition = data.get("definition", "")
        grammar = data.get("grammar", "")

        # Build user prompt
        if promptType == "1":
            user_prompt = f"[SYNONYMS]\nWord 1: {word1} / Word 2: {word2}\nCreate a dialogue."
        elif promptType == "2":
            user_prompt = f"[OPPOSITES]\nWord 1: {word1} / Word 2: {word2}\nCreate a dialogue."
        elif promptType == "3":
            user_prompt = f"[DEFINITIONS]\nWord: {word1} → \"{definition}\"\nCreate a dialogue."
        elif promptType == "4":
            user_prompt = f"[THEMES]\nTheme: {word1} | Word: {word2}\nCreate a dialogue."
        elif promptType == "5":
            user_prompt = f"[GRAMMAR]\nRule: {grammar}\nCreate a dialogue."
        else:
            return jsonify({"error": "Invalid prompt type"}), 400

        # Call OpenAI
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",  # or gpt-5 if you want
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )

        result = response.json()
        if "error" in result:
            return jsonify({"error": result["error"]["message"], "details": result}), 400

        return jsonify({"output": result["choices"][0]["message"]["content"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 3000)))



