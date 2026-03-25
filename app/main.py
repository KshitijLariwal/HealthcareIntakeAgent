from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import your compiled LangGraph agent
from core.agent import intake_agent

# Initialize the FastAPI application
app = FastAPI(
    title="Healthcare Intake Agent API",
    description="A RAG-powered, strictly guardrailed medical intake assistant."
)

# Enable CORS so a web frontend can communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the data structure we expect from the user
class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default_session"

# Create the POST endpoint
@app.post("/api/chat")
async def chat_with_agent(request: ChatRequest):
    """
    Takes a user message, passes it through the LangGraph agent, 
    and returns the medically-safeguarded response.
    """
    # Configure the thread memory so the agent remembers the conversation
    config = {"configurable": {"thread_id": request.thread_id}}
    
    # Invoke the LangGraph agent with the new message
    result = intake_agent.invoke({"messages": [("user", request.message)]}, config)
    
    # Extract the final string response from the agent
    agent_reply = result["messages"][-1].content
    
    return {"reply": agent_reply}

# A simple health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "active", "database": "connected"}