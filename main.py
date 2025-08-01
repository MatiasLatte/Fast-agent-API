from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcp_agent.core.fastagent import FastAgent
import os
from dotenv import load_dotenv

load_dotenv()

required_env_vars = ['SHOPIFY_ACCESS_TOKEN', 'SHOPIFY_DOMAIN']
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"Environmental variable required and not found: {var}")
app = FastAPI(title="Nassau National Cable AI Assistant")
fast = FastAgent("Shopify Assistant")

class ChatMessage(BaseModel):
    message: str

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
    """,
    servers=["shopify"],  # This connects to the MCP server defined in config (currently ran locally in docker)
    model="haiku",  # Use Claude haiku
    use_history=True,  # Remember conversation context
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
        raise HTTPException(
            status_code=503,
            detail="AI agent is still starting up, please try again in a moment"
        )

    try:
        print(f"Customer message: {message.message}")

        # Send the message to your Fast-Agent
        ai_response = await agent_instance.shopify_helper.send(message.message)

        print(f"AI response: {ai_response[:100]}")

        return {
            "response": ai_response,
            "status": "success"
        }

    except Exception as e:
        print(f"Error processing message: {e}")

        # Return an error message to the customer
        return {
            "response": "I'm sorry, I'm having technical difficulties right now. Please try again in a moment.",
            "status": "error"
        }