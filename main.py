from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI(title="Nassau National Cable AI Assistant")


# MOCK VERSION
class MockCableAgent:
    async def send(self, message: str):
        await asyncio.sleep(1)

        message_lower = message.lower()
        if "cable" in message_lower or "wire" in message_lower:
            return """I can help you with information about our cable products! We offer various types including:

- Power cables for electrical installations
- Data cables for networking and communications  
- Coaxial cables for audio/video applications
- Fiber optic cables for high-speed data transmission

Each type has specific use cases, materials, and certifications. What type of cable application are you looking for?"""

        elif "specification" in message_lower or "spec" in message_lower:
            return """I can provide detailed specifications for our cables including:

- Conductor materials and gauge
- Insulation types and ratings
- Temperature ratings and environmental specifications
- Safety certifications (UL, CSA, etc.)
- Installation guidelines and bend radius requirements

Which specific product or application would you like specifications for?"""

        elif "installation" in message_lower or "install" in message_lower:
            return """For installation guidance, I can help with:

- Proper cable routing and support methods
- Minimum bend radius requirements
- Environmental considerations (indoor/outdoor, temperature, moisture)
- Safety protocols and electrical codes compliance
- Tools and accessories needed

What type of installation are you planning?"""

        elif "price" in message_lower or "cost" in message_lower or "discount" in message_lower:
            return "I'm here to provide technical and usage information only. For pricing or commercial details, please contact our sales or customer service team directly."

        elif "hello" in message_lower or "hi" in message_lower:
            return """Hello! I'm Nassau National Cable's technical support assistant. I'm here to help you with:

- Cable specifications and technical details
- Installation and usage guidance  
- Product compatibility and applications
- Safety standards and certifications

I focus on technical information only. How can I assist you today?"""

        else:
            return f"""Thank you for your question about: "{message}"

I'm here to provide technical information about Nassau National Cable's products, including cable specifications, usage applications, installation guidance, and safety standards.

I focus on technical and educational information only. For pricing or commercial inquiries, please contact our sales team directly.

How can I help you with technical information today?"""


class ChatMessage(BaseModel):
    message: str

mock_agent = MockCableAgent()
agent_instance = None


@app.get("/")
def root():
    return {"message": "Nassau Cable AI Assistant API is running (Mock Mode)"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "ai_ready": agent_instance is not None,
        "mode": "mock" #Mock mode
    }



@app.on_event("startup")
async def startup_event():
    global agent_instance
    print("Starting up the MOCK AI assistant")

    # Simulate startup time
    await asyncio.sleep(2)
    agent_instance = mock_agent
    print("✅ Mock AI assistant is ready!")


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down mock AI assistant")


@app.post("/chat")
async def chat_with_ai(message: ChatMessage):
    if not agent_instance:
        raise HTTPException(
            status_code=503,
            detail="AI assistant is still starting up, please try again in a moment"
        )

    try:
        print(f"Customer message: {message.message}")
        ai_response = await agent_instance.send(message.message)

        print(f"Mock AI response: {ai_response[:100]}...")

        return {
            "response": ai_response,
            "status": "success"
        }

    except Exception as e:
        print(f"Error processing message: {e}")

        return {
            "response": "I'm sorry, I'm having technical difficulties right now. Please try again in a moment.",
            "status": "error"
        }