from flask import Flask, request, jsonify
from flask_cors import CORS
from pypdf import PdfReader
import re

app = Flask(__name__)
CORS(app)


def summarize_text(text, max_sentences=5):
    # Clean the text
    text = re.sub(r'\s+', ' ', text).strip()

    if not text:
        return "No readable text was found in the PDF."

    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Remove very short sentences
    sentences = [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip().split()) >= 5
    ]

    if not sentences:
        return text[:1000]

    # Common words that shouldn't affect sentence importance
    stop_words = {
        "the", "is", "are", "was", "were", "a", "an", "and",
        "or", "of", "to", "in", "on", "for", "with", "as",
        "by", "at", "from", "this", "that", "it", "be",
        "can", "will", "has", "have", "had"
    }

    # Count important words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    word_frequency = {}

    for word in words:
        if word not in stop_words:
            word_frequency[word] = word_frequency.get(word, 0) + 1

    # Score each sentence
    sentence_scores = []

    for index, sentence in enumerate(sentences):
        sentence_words = re.findall(
            r'\b[a-zA-Z]{3,}\b',
            sentence.lower()
        )

        score = sum(
            word_frequency.get(word, 0)
            for word in sentence_words
            if word not in stop_words
        )

        # Give a small preference to earlier sentences
        if index < 3:
            score += 2

        sentence_scores.append((score, index, sentence))

    # Select highest-scoring sentences
    best_sentences = sorted(
        sentence_scores,
        reverse=True
    )[:max_sentences]

    # Restore original order
    best_sentences.sort(key=lambda x: x[1])

    summary = " ".join(
        sentence[2] for sentence in best_sentences
    )

    return summary


@app.route("/upload", methods=["POST"])
def upload_pdf():

    if "pdf" not in request.files:
        return jsonify({
            "error": "No PDF received"
        }), 400

    pdf = request.files["pdf"]

    try:
        reader = PdfReader(pdf)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        if not text.strip():
            return jsonify({
                "error": "Could not extract text from this PDF."
            }), 400

        summary = summarize_text(text)

        return jsonify({
            "message": "PDF summarized successfully",
            "filename": pdf.filename,
            "summary": summary
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)