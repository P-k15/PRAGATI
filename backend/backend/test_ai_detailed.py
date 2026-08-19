import asyncio
import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def test_raw_ai_response():
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY environment variable is not set")

    client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )
    model = "nvidia/nemotron-3-nano-30b-a3b"

    system_instruction = """You are PRAGATI, an AI-powered public grievance classification and routing engine.

Your task is to analyze a citizen's public grievance and convert it into structured information that can be used by a government grievance-management workflow.

You MUST return a JSON object with EXACTLY these fields (use these exact field names):
- "category": string (e.g., "Public Infrastructure")
- "subcategory": string (e.g., "Street Lighting")
- "severity": string (must be one of: "Low", "Medium", "High")
- "priority": string (must be one of: "P1", "P2", "P3", "P4")
- "department": string (e.g., "Electrical Maintenance")
- "sla_hours": integer (e.g., 72)
- "summary": string (concise summary of the complaint)
- "recommended_action": string (specific immediate administrative action to take)
- "confidence": float (confidence score between 0 and 1)

Rules:
* Do not invent facts that are not present in the complaint.
* Use the most appropriate department based on the issue.
* Assign priority based on urgency, public impact, safety risk, and severity.
* Return ONLY the JSON object described above.
* Do not include ANY text before or after the JSON.
* Do not include markdown fences or code blocks.
* Do not include explanations outside the JSON."""

    complaint_text = "The street lights near our college have not been working for five days."

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": complaint_text}
            ],
            temperature=0.1,
            max_tokens=500
        )

        ai_response = response.choices[0].message.content.strip()
        print("Raw AI Response:")
        print(repr(ai_response))
        print("\nFormatted AI Response:")
        print(ai_response)
        print(f"\nLength: {len(ai_response)} characters")

        # Try to parse it
        try:
            result_dict = json.loads(ai_response)
            print("\nParsed JSON:")
            print(json.dumps(result_dict, indent=2))
        except json.JSONDecodeError as e:
            print(f"\nJSON Parse Error: {e}")
            print(f"Error at position {e.pos}: {e.doc[e.pos:e.pos+20]}")

    except Exception as e:
        print(f"Error calling NVIDIA API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_raw_ai_response())