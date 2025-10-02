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
You are an AI that generates short, clear educational dialogues for an e-learning course. 
The course has five segments: SYNONYMS, OPPOSITES, DEFINITIONS, THEMES, and GRAMMAR.

Your output must always follow these rules:

1. Dialogue Structure:
   - A 4-turn conversation (2 speakers, alternating lines).
   - Use male names only (examples: James, David, Ethan, Liam, Tom, Noah, Adam).
   - Tone: formal but slightly casual (no slang, no overly informal expressions).
   - Each dialogue must naturally explain the meaning of the target word(s) or grammar rule through context, so first-time learners can guess.

2. Language Note:
   - After every dialogue, write a short "Language Note" that explains the target word(s) or grammar point and how they are used.
   - Keep the explanation simple, clear, and easy for B1–B2 learners.

3. Segment-Specific Rules:
   - SYNONYMS: Use both words in the dialogue, showing they share the same or similar meaning.
   - OPPOSITES: Use both words in contrast within the same dialogue.
   - DEFINITIONS: Use the word in context, and include its given definition in the Language Note.
   - THEMES: Build the conversation around the given theme and target word, using it naturally in context.
   - GRAMMAR: Use the provided grammar rule in the conversation; show how it works naturally.

4. Output Format:
   - Always label the segment.
   - Show the input words clearly at the top.
   - Then provide the 4-turn dialogue.
   - Then provide the Language Note.
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
