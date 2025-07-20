import spacy
from transformers import pipeline
from app.services.ollama_service import ollama_infer
import re
nlp = spacy.load("en_core_web_sm")
sentiment_pipeline = pipeline("sentiment-analysis")


def classify_topic(text: str) -> list:
    """
    Extract 3 main topics using LLM and return as a list.
    """
    prompt = f"What are the main topics in the following content?\n\n{text}\n\nList 3 key topics:"
    try:
        raw = ollama_infer(prompt)
        topics = [
            line.split("**")[1].strip()
            for line in raw.split("\n")
            if "**" in line
        ]
         
        print(topics,'dff')
        return topics if topics else [raw]
    except Exception as e:
        print(f"⚠️ classify_topic error: {e}")
        return []


def extract_entities(text: str) -> dict:
    """
    Extract PERSON, ORG, and LOCATION entities using spaCy.
    """
    doc = nlp(text)
    return {
        "people": list({ent.text for ent in doc.ents if ent.label_ == "PERSON"}),
        "organizations": list({ent.text for ent in doc.ents if ent.label_ == "ORG"}),
        "locations": list({ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]}),
    }


def suggest_tags(text: str) -> list:
    """
    Extract 5 SEO-friendly tags using LLM and return as a list.
    """
    prompt = f"Extract 5 SEO-friendly tags from the following content:\n\n{text}"
    try:
        raw = ollama_infer(prompt)
        tags = [
            line.split("**")[1].strip()
            for line in raw.split("\n")
            if "**" in line
        ]
        return tags if tags else [raw]
    except Exception as e:
        print(f"⚠️ suggest_tags error: {e}")
        return []


def analyze_sentiment(text: str) -> dict:
    """
    Perform sentiment analysis using HuggingFace pipeline.
    """
    try:
        return sentiment_pipeline(text[:512])[0]
    except Exception as e:
        print(f"⚠️ analyze_sentiment error: {e}")
        return {"label": "UNKNOWN", "score": 0.0}



def multi_length_summary(text: str) -> dict:
    prompt = f"""
You are a professional summarizer. Read the text and respond **exactly** in the following format:

Headline: <one-liner headline>
TL;DR: <two-sentence summary>
Full Summary: <detailed multi-paragraph summary>

Do not skip or change any label. Follow the format strictly.

Text:
{text}
"""

    try:
        raw = ollama_infer(prompt)

        # 🧠 Debugging Output
        print("🧠 Raw Summary Response:\n", raw)

        # Use more robust multiline regex with fallback
        headline_match = re.search(r"(?i)^Headline:\s*(.+)", raw, re.MULTILINE)
        tldr_match = re.search(r"(?i)^TL;DR:\s*(.+)", raw, re.MULTILINE)
        full_match = re.search(r"(?i)^Full Summary:\s*([\s\S]+)", raw, re.MULTILINE)

        return {
            "Headline": headline_match.group(1).strip() if headline_match else text[:80],
            "TL;DR": tldr_match.group(1).strip() if tldr_match else "",
            "Full Summary": full_match.group(1).strip() if full_match else raw
        }

    except Exception as e:
        print(f"❌ multi_length_summary error: {e}")
        return {
            "Headline": text[:80],
            "TL;DR": "",
            "Full Summary": text
        }

def enrich_content(text: str) -> dict:
    """
    Run all enrichment steps and return a structured dictionary.
    """
    return {
        "topics": classify_topic(text),
        "entities": extract_entities(text),
        "seo_tags": suggest_tags(text),
        "sentiment": analyze_sentiment(text),
        "summaries": multi_length_summary(text)
    }
