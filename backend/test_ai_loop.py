import asyncio
import os
from dotenv import load_dotenv
from app.services.ai_service import ai_service

load_dotenv()

async def test_multiple():
    complaints = [
        "The street lights near our college have not been working for five days.",
        "Garbage has not been collected from our area for three days and it is creating a bad smell.",
        "A major water pipeline has burst and water is flooding the road.",
        "There is a large pothole on the main road causing accidents.",
        "The street light near my house is flickering."
    ]
    for i, complaint_text in enumerate(complaints):
        print(f"\n=== Test {i+1} ===")
        print(f"Complaint: {complaint_text}")
        try:
            result = await ai_service.analyze_complaint(complaint_text)
            print(f"Category: {result.category}")
            print(f"Subcategory: {result.subcategory}")
            print(f"Severity: {result.severity}")
            print(f"Priority: {result.priority}")
            print(f"Department: {result.department}")
            print(f"SLA Hours: {result.sla_hours}")
            print(f"Summary: {result.summary}")
            print(f"Recommended Action: {result.recommended_action}")
            print(f"Confidence: {result.confidence}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_multiple())