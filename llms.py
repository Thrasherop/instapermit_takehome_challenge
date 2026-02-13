from google import genai
from openai import OpenAI

def get_gemini_response(message : str) -> str:

    

    text = ""
    try:
        client = genai.Client()

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=message,
        ).to_json_dict()

        text = response['candidates'][0]['content']['parts'][0]['text']
    except:
        # Failed, use local LLMs
        text = _fallback_to_local_llm(message)

    return text


def _fallback_to_local_llm(message : str) -> str:

    MODEL = "openai/gpt-oss-20b"

    client = OpenAI(base_url="http://10.0.0.247:1234/v1", api_key="lm-studio")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role" : "system",
            "content" : message
        }],
    )
    text = response.choices[0].message.content

    return text