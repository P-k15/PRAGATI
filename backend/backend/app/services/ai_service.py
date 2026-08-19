from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import Optional
import logging
import os
import json
import re
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

    def _extract_json(self, text: str) -> dict:
        """
        Extract a JSON object from text.
        Looks for the first '{' and the last '}' and tries to parse the substring.
        If that fails, tries to find JSON array or object using regex.
        """
        # Try to find a JSON object (between first { and last })
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and start < end:
            json_str = text[start:end+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass  # Fall through to other methods

        # Try to find JSON using regex (for objects or arrays)
        json_pattern = re.compile(r'\{.*\}|\[.*\]', re.DOTALL)
        match = json_pattern.search(text)
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # If we still haven't found valid JSON, raise an error
        raise ValueError("No valid JSON found in the response")

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

            # Call the NVIDIA API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": complaint_text}
                ],
                temperature=0.1,  # Low temperature for consistent outputs
                max_tokens=500
            )

            # Extract the response content
            ai_response = response.choices[0].message.content.strip()

            # Parse the JSON response, being resilient to extra text
            try:
                result_dict = self._extract_json(ai_response)
                # Validate using Pydantic model
                validated_result = AIAnalysisResult(**result_dict)
                return validated_result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {ai_response}")
                raise ValueError(f"AI returned invalid JSON: {str(e)}")
            except Exception as e:
                logger.error(f"Failed to validate AI response: {ai_response}")
                raise ValueError(f"AI response validation failed: {str(e)}")

        except Exception as e:
            logger.error(f"Error calling NVIDIA API: {str(e)}")
            # Re-raise with a generic message to avoid exposing API key or internal details
            raise Exception("Failed to analyze complaint. Please try again later.")

# Create a singleton instance
ai_service = AIService()