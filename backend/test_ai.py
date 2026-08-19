import asyncio
import os
from dotenv import load_dotenv
from app.services.ai_service import ai_service

load_dotenv()

async def test_ai_service():
    complaint_text = "The street lights near our college have not been working for five days."
    try:
        result = await ai_service.analyze_complaint(complaint_text)
        print("AI Analysis Result:")
        print(f"Category: {result.category}")
        print(f"Subcategory: {result.subcategory}")
        print(f"Severity: {result.severity}")
        print(f"Priority: {result.priority}")
        print(f"Department: {result.department}")
        print(f"SLA Hours: {result.sla_hours}")
        print(f"Summary: {result.summary}")
        print(f"Recommended Action: {result.recommended_action}")
        print(f"Confidence: {result.confidence}")
        print(f"Result dict: {result.dict()}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_service())