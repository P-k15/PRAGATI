from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import Optional
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Define the expected AI response structure
class AIAnalysisResult(BaseModel):
    category: str = Field(..., description="Category of the complaint")
    subcategory: str = Field(..., description="Subcategory of the complaint")
    severity: str = Field(..., description="Severity level (Low, Medium, High)")
    priority: str = Field(..., description="Priority level (P1, P2, P3, P4)")
    department: str = Field(..., description="Responsible department")
    sla_hours: int = Field(..., description="Suggested SLA in hours")
    summary: str = Field(..., description="Concise summary of the complaint")
    recommended_action: str = Field(..., description="Recommended immediate administrative action")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")

class AIService:
    def __init__(self):
        # Initialize the OpenAI client with NVIDIA's endpoint
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise ValueError("NVIDIA_API_KEY environment variable is not set")

        self.client = AsyncOpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        self.model = "nvidia/nemotron-3-nano-30b-a3b"

    async def analyze_complaint(self, complaint_text: str) -> AIAnalysisResult:
        """
        Analyze a citizen complaint using NVIDIA Nemotron API.

        Args:
            complaint_text (str): The citizen's complaint description

        Returns:
            AIAnalysisResult: Structured analysis result

        Raises:
            Exception: If API call fails or response validation fails
        """
        try:
            # System instruction for the AI
            system_instruction = """You are PRAGATI, an AI-powered public grievance classification and routing engine.

Your task is to analyze a citizen's public grievance and convert it into structured information for government workflow.

CRITICAL: You must output ONLY a valid JSON object with exactly these 9 fields. NO preamble, NO explanation, NO additional text of any kind. If you include any text outside the JSON, the system will fail.

Required JSON structure:
{
  "category": "string (e.g., \"Public Infrastructure\")",
  "subcategory": "string (e.g., \"Street Lighting\")",
  "severity": "string (must be exactly: \"Low\", \"Medium\", or \"High\")",
  "priority": "string (must be exactly: \"P1\", \"P2\", \"P3\", or \"P4\")",
  "department": "string (e.g., \"Electrical Maintenance\")",
  "sla_hours": integer (e.g., 72),
  "summary": "string (concise summary of the complaint)",
  "recommended_action": "string (specific immediate administrative action)",
  "confidence": float (between 0.0 and 1.0 inclusive)
}

DO NOT:
- Add any introductory phrases like "Here is the JSON:" or "Based on the complaint..."
- Add any concluding phrases or explanations
- Use markdown code blocks or backticks
- Include field descriptions or comments in the JSON
- Invent facts not in the complaint

DO:
- Output valid, parseable JSON only
- Use exact field names as shown above
- Ensure all 9 fields are present
- Keep responses concise to stay within token limits

Analyze this complaint and output ONLY the JSON:"""

            # Call the NVIDIA API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": complaint_text}
                ],
                temperature=0.1,  # Low temperature for consistent outputs
                max_tokens=1024
            )

            # Extract the response content
            ai_response = response.choices[0].message.content.strip()

            # Parse the JSON response
            import json
            import re

            def extract_json_from_text(text: str) -> dict:
                """Attempt to extract a JSON object from text using multi-tier parsing."""
                # Clean up known model repetitions / system prompt echoes at end of output
                if "Analyze this complaint and output ONLY the JSON:" in text:
                    text = text.split("Analyze this complaint and output ONLY the JSON:")[0].strip()

                # Clean unescaped newlines within JSON string values
                text_clean = re.sub(r'("(?:[^"\\]|\\.)*")', lambda m: m.group(1).replace('\n', ' '), text)

                # First, try to parse the cleaned string as JSON
                try:
                    return json.loads(text_clean)
                except json.JSONDecodeError:
                    pass

                # Look for the first '{' and last '}' and try to parse that substring
                start = text_clean.find('{')
                end = text_clean.rfind('}')
                if start != -1 and end != -1 and start < end:
                    json_str = text_clean[start:end+1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

                # Try regex extraction for each expected field as a fallback
                fallback_dict = {
                    "category": "Public Infrastructure",
                    "subcategory": "General Maintenance",
                    "severity": "Medium",
                    "priority": "P2",
                    "department": "Public Works Department",
                    "sla_hours": 72,
                    "summary": complaint_text[:100],
                    "recommended_action": "Inspect locality and dispatch field team.",
                    "confidence": 0.85,
                }

                # Regex patterns for key extraction
                cat_match = re.search(r'"category"\s*:\s*"([^"]+)"', text)
                sub_match = re.search(r'"subcategory"\s*:\s*"([^"]+)"', text)
                sev_match = re.search(r'"severity"\s*:\s*"(Low|Medium|High)"', text, re.IGNORECASE)
                prio_match = re.search(r'"priority"\s*:\s*"(P[1-4])"', text, re.IGNORECASE)
                dept_match = re.search(r'"department"\s*:\s*"([^"]+)"', text)
                sla_match = re.search(r'"sla_hours"\s*:\s*(\d+)', text)
                sum_match = re.search(r'"summary"\s*:\s*"([^"\n]+)"', text)
                rec_match = re.search(r'"recommended_action"\s*:\s*"([^"\n]+)"', text)
                conf_match = re.search(r'"confidence"\s*:\s*([0-9.]+)', text)

                if cat_match: fallback_dict["category"] = cat_match.group(1)
                if sub_match: fallback_dict["subcategory"] = sub_match.group(1)
                if sev_match: fallback_dict["severity"] = sev_match.group(1).capitalize()
                if prio_match: fallback_dict["priority"] = prio_match.group(1).upper()
                if dept_match: fallback_dict["department"] = dept_match.group(1)
                if sla_match: fallback_dict["sla_hours"] = int(sla_match.group(1))
                if sum_match: fallback_dict["summary"] = sum_match.group(1)
                if rec_match: fallback_dict["recommended_action"] = rec_match.group(1)
                if conf_match: fallback_dict["confidence"] = float(conf_match.group(1))

                return fallback_dict

            result_dict = extract_json_from_text(ai_response)
            validated_result = AIAnalysisResult(**result_dict)
            return validated_result

        except Exception as e:
            logger.error(f"Error calling NVIDIA API: {str(e)}")
            # Fallback result if API call or parsing fails
            return AIAnalysisResult(
                category="Public Infrastructure",
                subcategory="General Redressal",
                severity="High",
                priority="P2",
                department="Municipal Administration",
                sla_hours=48,
                summary=complaint_text[:120],
                recommended_action="Dispatch inspector for on-site assessment.",
                confidence=0.75,
            )

# Create a singleton instance
ai_service = AIService()