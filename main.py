import requests
import json

def extract(text):
    prompt = f"""Extract every person and organization mentioned in this text, and every relationship between them, as JSON only — no other text, no explanation.

Every organization, location, or institution mentioned must have at least one relation connecting it to a person, if the text implies any connection (works at, located at, target of, member of, investigated by). Do not leave organizations or locations disconnected if the text mentions who is associated with them.

Every relation MUST include a real evidence_quote copied directly from the text. Never leave evidence_quote empty.

Use ONLY these entity types: "person", "organization"
Use ONLY these relation types: "colleague", "employer", "founder", "co-founder", "introduced_by", "board_member", "conflict_with", "family", "informant_to", "represented_by", "directed_by", "investigated_by", "located_at", "member_of", "target_of"

Format:
{{
  "entities": [{{"name": "...", "type": "person|organization"}}],
  "relations": [{{"source": "...", "target": "...", "type": "...", "evidence_quote": "..."}}]
}}

Text:
{text}"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False}
    )
    return response.json()["response"]


def clean_roles(data):
    """Second pass: merge role/title entities into the person they belong to."""
    entity_names = [e["name"] for e in data.get("entities", [])]

    prompt = f"""Here is a list of extracted entity names from a document:
{json.dumps(entity_names)}

Some of these might be roles or titles rather than real named entities (e.g. "White House counsel", "Attorney General", "secret informant", "chief of staff") that actually refer to a specific PERSON also in this list.

Return ONLY a JSON object mapping any such role/title entity name to the real person's name it refers to. If a name is already a proper name (a real person or organization), do not include it in the output. If unsure, don't include it.

Format: {{"role or title name": "real person name", ...}}

If none apply, return {{}}.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False}
    )
    raw = response.json()["response"]
    try:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {}