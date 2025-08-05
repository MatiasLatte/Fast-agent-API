from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcp_agent.core.fastagent import FastAgent
import os
from dotenv import load_dotenv
import asyncio
from typing import Dict
import uuid

load_dotenv()
conversation_sessions: Dict[str, list] = {}

required_env_vars = ['SHOPIFY_ACCESS_TOKEN', 'SHOPIFY_DOMAIN']
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"Environmental variable required and not found: {var}")
app = FastAPI(title="Nassau National Cable AI Assistant")
fast = FastAgent("Shopify Assistant")

class ChatMessage(BaseModel):
    message: str
    session_id: str = None

#AGENT DEFINITION
@fast.agent(
    name="shopify_helper",
    instruction="""
    Main purpose:

You are an intelligent support agent designed to assist with product information across multiple channels. Your main function is to provide accurate, clear, and helpful information about our products in particular our range of cables by pulling data from Shopify and associated internal databases about the products we offer and complementing to their usage.

**Your core responsibilities:**

**Inform, not sell:** Only provide factual information about product usage, specifications, compatibility, features, installation, and maintenance.

**Focus on cables:** Give detailed, relevant insights about the various types of cables offered, including but not limited to: use cases, materials, certifications, safety standards, and connectivity.

**Strict boundaries:** Under no circumstances may you disclose or refer to:

Prices or pricing structures

Discounts, promotions, or special offers

Internal stock levels or availability

Commercial management policies or personnel

**Guidelines:**

Respond professionally, clearly, and in a customer-friendly tone.

Always prioritize technical accuracy and usefulness.

Search for maximum 5-8 products per query

Keep responses concise and focused

If a request pertains to pricing or commercial topics, respond with:

"I'm here to provide technical and usage information only. For pricing or commercial details, please contact our sales or customer service team directly."

This is an informational agent only, not a sales or customer service tool.
**CRITICAL: Each conversation is separate. Only use the conversation history provided in the current request. Do not reference information from other conversations or sessions unless the have the same session ID.**
    """,
    servers=["shopify"],
    model="haiku",
    use_history=True,
)
async def shopify_helper(message: str) -> str:
    # Este cuerpo nunca se ejecuta directamente
    return "This is a placeholder response from the agent"

agent_instance = None


@app.get("/")
def root():
    return {"message": "AI Assistant API is running"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "ai_ready": agent_instance is not None
    }


# Runs ONCE when the API starts up
@app.on_event("startup")
async def startup_event():
    global agent_instance
    print("Starting up the AI assistant")

    try:
        agent_instance = await fast.run().__aenter__()
        print("AI assistant is ready and connected to Shopify!")
    except Exception as e:
        print(f"Failed to start AI assistant: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    global agent_instance
    if agent_instance:
        print("Shutting down AI assistant")
        try:
            await fast.run().__aexit__(None, None, None)
            print("AI assistant shut down")
        except Exception as e:
            print(f"Error during shutdown: {e}")


@app.post("/chat")
async def chat_with_ai(message: ChatMessage):
    if not agent_instance:
        raise HTTPException(status_code=503, detail="AI agent is still starting up")

    session_id = message.session_id or str(uuid.uuid4())

    try:
        print(f"Customer message: {message.message} (Session: {session_id})")

        if session_id not in conversation_sessions:
            conversation_sessions[session_id] = []

        conversation_sessions[session_id].append(f"User: {message.message}")

        recent_history = conversation_sessions[session_id][-10:]
        context = "\n".join(recent_history) if recent_history else ""

        full_message = f"[Session {session_id[:8]}] Conversation history:\n{context}\n\nCurrent question: {message.message}"

        ai_response = await asyncio.wait_for(
            agent_instance.shopify_helper.send(full_message),
            timeout=90.0
        )

        if '{"products":' in ai_response:
            parts = ai_response.split('}]}')
            if len(parts) > 1:
                ai_response = parts[-1].strip()

        conversation_sessions[session_id].append(f"Assistant: {ai_response}")

        print(f"AI response: {ai_response[:100]}")

        return {
            "response": ai_response,
            "status": "success",
            "session_id": session_id
        }

    except asyncio.TimeoutError:
        print("Request timed out - high volume of inquiries")
        return {
            "response": "We're currently receiving a high volume of inquiries. Please hold on, we'll get back to you shortly.",
            "status": "timeout"
        }

    except Exception as e:
        error_message = str(e).lower()
        print(f"Error processing message: {e}")

        if ("404" in error_message or
                "usage" in error_message or
                "limit" in error_message or
                "quota" in error_message or
                "budget" in error_message or
                "rate_limit" in error_message):
            return {
                "response": "The AI assistant is temporarily unavailable. Please contact us again tomorrow.",
                "status": "usage_limit_exceeded"
            }

        # General error
        return {
            "response": "I'm sorry, I'm having technical difficulties right now. Please try again in a moment.",
            "status": "error"
        }