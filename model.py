import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# --------------------------------------------------
# LOAD API KEY
# --------------------------------------------------
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY is missing. "
        "Add it to your .env file."
    )

# --------------------------------------------------
# CONFIGURE GEMINI
# --------------------------------------------------
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    "gemini-3.5-flash"
)


# --------------------------------------------------
# FAKE NEWS DETECTOR
# --------------------------------------------------
def detect_news(news, source=""):

    prompt = f"""
You are a careful AI misinformation analysis assistant.

Analyze the following news claim.

NEWS:
{news}

SOURCE:
{source if source else "Not provided"}

Your job is NOT to automatically call something fake merely
because it sounds unusual. Analyze the claim carefully.

Consider:

1. Internal consistency
2. Specific factual claims
3. Dates and locations
4. Names of people and organizations
5. Extraordinary claims
6. Sensational or emotionally manipulative language
7. Missing context
8. Unsupported statistics
9. Contradictions
10. Whether the information would require independent verification

IMPORTANT:
You do not have guaranteed access to live news databases.
Do not invent sources, URLs, quotations, statistics, or evidence.

If the supplied information does not provide enough evidence
to determine whether the claim is true, use "Uncertain".

Return ONLY valid JSON in this exact format:

{{
    "verdict": "Likely Fake",
    "confidence": "High",
    "explanation": "Clear explanation of the analysis.",
    "warning_signs": [
        "Warning sign 1",
        "Warning sign 2"
    ],
    "evidence": [
        "What should be independently verified"
    ],
    "recommendation": "What the user should do next."
}}

The verdict MUST be exactly one of:

"Likely Fake"
"Likely Real"
"Uncertain"

Confidence MUST be exactly one of:

"High"
"Medium"
"Low"

Do not claim certainty unless the supplied evidence supports it.
"""


    try:

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 2000
            }
        )

        text = response.text.strip()

        # Remove markdown JSON fences if returned
        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        result = json.loads(text)

        # Safety defaults
        if "verdict" not in result:
            result["verdict"] = "Uncertain"

        if "confidence" not in result:
            result["confidence"] = "Low"

        if "warning_signs" not in result:
            result["warning_signs"] = []

        if "evidence" not in result:
            result["evidence"] = []

        if "explanation" not in result:
            result["explanation"] = (
                "The claim requires additional verification."
            )

        if "recommendation" not in result:
            result["recommendation"] = (
                "Verify the information using reliable "
                "independent sources."
            )

        return result

    except json.JSONDecodeError:

        return {
            "verdict": "Uncertain",
            "confidence": "Low",
            "explanation": (
                "The AI response could not be interpreted "
                "reliably."
            ),
            "warning_signs": [],
            "evidence": [],
            "recommendation": (
                "Please try again or verify the news through "
                "reliable independent sources."
            )
        }

    except Exception as error:

        return {
            "verdict": "Uncertain",
            "confidence": "Low",
            "explanation": (
                "The news detector encountered an error."
            ),
            "warning_signs": [],
            "evidence": [],
            "recommendation": (
                f"Check your API configuration and try again. "
                f"Error: {error}"
            )
        }


# --------------------------------------------------
# YES/NO CHATBOT AGENT
# --------------------------------------------------
def generate_yes_no_response(question, history=None):
    if history is None:
        history = []

    history_context = ""
    if history:
        history_context = "Conversation history:\n"
        # Only take the last 6 messages to keep context window clean
        for msg in history[-6:]:
            role = "User" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "")
            history_context += f"{role}: {content}\n"
        history_context += "\n"

    prompt = f"""
You are a factual truth verification and chatbot assistant. Your job is to evaluate the user's input (which could be a question, headline, or claim) and determine whether it is true (Yes / Real News) or false (No / Fake News).

{history_context}Current Input:
{question}

Analyze the input carefully. Refer to reliable, widely established real-world facts.
Determine the truth value of the input:
- If the statement is false, a known hoax, fake news, or the answer to the question is no: the "answer" must be "No / Fake News".
- If the statement is true, a confirmed fact, or the answer to the question is yes: the "answer" must be "Yes / Real News".
- If the statement is a future prediction, subjective opinion, or cannot be verified: the "answer" must be "Uncertain".

Example Cases:
1. "Modi is dead" -> Answer: "No / Fake News" (Narendra Modi, Prime Minister of India, is alive. Rumors of his death are false.)
2. "Is the earth flat?" -> Answer: "No / Fake News"
3. "Is the earth round?" -> Answer: "Yes / Real News"
4. "The moon is made of cheese" -> Answer: "No / Fake News"

Return ONLY valid JSON in this exact format:

{{
    "answer": "No / Fake News",
    "confidence": "High",
    "explanation": "Narendra Modi is the current Prime Minister of India and is alive. Any claims stating otherwise are false and constitute fake news."
}}

The "answer" MUST be exactly one of:
"Yes / Real News"
"No / Fake News"
"Uncertain"

Confidence MUST be exactly one of:
"High"
"Medium"
"Low"

Do not include any other markdown formatting other than the raw JSON or json block.
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 1000
            }
        )

        text = response.text.strip()

        # Remove markdown JSON fences if returned
        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        result = json.loads(text)

        # Safety defaults
        if "answer" not in result:
            result["answer"] = "Uncertain"

        if "confidence" not in result:
            result["confidence"] = "Low"

        if "explanation" not in result:
            result["explanation"] = "No explanation was provided."

        return result

    except json.JSONDecodeError:
        # Fallback to parsing text manually if Gemini didn't return valid JSON
        lower_text = text.lower()
        if "yes" in lower_text[:20]:
            ans = "Yes / Real News"
        elif "no" in lower_text[:20]:
            ans = "No / Fake News"
        else:
            ans = "Uncertain"
        return {
            "answer": ans,
            "confidence": "Low",
            "explanation": text[:200] if text else "The response could not be fully analyzed, but here is the raw output."
        }
    except Exception as error:
        return {
            "answer": "Uncertain",
            "confidence": "Low",
            "explanation": f"An error occurred: {error}"
        }
