import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore

# Load API keys
load_dotenv()

# 1. Define the Conversation State
# This holds the chat history and the retrieved medical context
class State(TypedDict):
    messages: Annotated[list, add_messages]
    context: str

# 2. Initialize the LLM and the Vector Database Connection
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")

vector_store = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name="medical_guidelines",
    url=qdrant_url,
    prefer_grpc=False
)
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# 3. Define the Nodes (The Actions)

def retrieve_guidelines(state: State):
    """Retrieves relevant medical guidelines based on the user's latest message."""
    last_message = state["messages"][-1].content
    docs = retriever.invoke(last_message)
    # Combine the text of the retrieved documents
    context = "\n\n".join([doc.page_content for doc in docs])
    return {"context": context}

def intake_chat(state: State):
    """Generates the empathetic response using the retrieved context."""
    context = state.get("context", "")
    
    # THE GUARDRAIL PROMPT
    system_prompt = f"""You are a highly empathetic healthcare intake assistant. 
    Your goal is to gather a structured medical history from the patient.
    
    CRITICAL RULES:
    1. You must NEVER provide a definitive diagnosis or suggest medications.
    2. If asked for a diagnosis, gently remind the patient that your role is strictly to summarize symptoms for a doctor.
    3. Use the following verified medical guidelines to inform what follow-up questions you should ask:
    
    <medical_guidelines>
    {context}
    </medical_guidelines>
    """
    
    # Prepend the system prompt to the conversation history
    messages_to_send = [SystemMessage(content=system_prompt)] + state["messages"]
    
    # Generate the response
    response = llm.invoke(messages_to_send)
    return {"messages": [response]}

# 4. Build and Compile the Graph
graph_builder = StateGraph(State)

# Add the nodes
graph_builder.add_node("retrieve", retrieve_guidelines)
graph_builder.add_node("chat", intake_chat)

# Define the flow: Start -> Retrieve Context -> Chat -> End
graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "chat")
graph_builder.add_edge("chat", END)

# Compile into a runnable agent
intake_agent = graph_builder.compile()

# --- TEMPORARY TESTING BLOCK ---
if __name__ == "__main__":
    print("🤖 Intake Agent Initialized. Type 'quit' to exit.")
    
    # We maintain the thread configuration so LangGraph remembers the history
    config = {"configurable": {"thread_id": "test_patient_1"}}
    
    while True:
        user_input = input("\nPatient: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        # Stream the agent's reasoning process and output
        for event in intake_agent.stream({"messages": [("user", user_input)]}, config):
            for value in event.values():
                if "messages" in value:
                    print(f"\nAgent: {value['messages'][-1].content}")