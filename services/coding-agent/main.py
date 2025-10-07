"""
FastAPI server for the coding agent service
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import json
from typing import Optional

from core import AgentOrchestrator, get_settings
from core.session_manager import get_session_manager
from schemas.requests import QuickQueryRequest, NotebookContextData, ApprovalResponse
from schemas.responses import AgentResponse, AgentMessage, MessageType
from schemas.internal import NotebookContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Socio Coding Agent",
    description="LLM-powered coding assistant for marimo notebooks",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = get_settings()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "coding-agent"}


@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Socio Coding Agent",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "quick_query": "/api/agent/quick (POST)",
            "stream": "/api/agent/stream (WebSocket)",
            "session_info": "/api/sessions/{session_id} (GET)",
            "session_history": "/api/sessions/{session_id}/history (GET)",
            "clear_session": "/api/sessions/{session_id} (DELETE)"
        }
    }


@app.get("/api/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get session information"""
    session_manager = get_session_manager()
    info = session_manager.get_session_info(session_id)

    if info is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return info


@app.get("/api/sessions/{session_id}/history")
async def get_session_history(
    session_id: str,
    max_turns: int = 20
):
    """Get conversation history for a session"""
    session_manager = get_session_manager()

    if session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    history = session_manager.get_conversation_context(session_id, max_turns)

    return {
        "session_id": session_id,
        "turn_count": len(history),
        "history": history
    }


@app.delete("/api/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a session and its history"""
    session_manager = get_session_manager()
    session_manager.clear_session(session_id)

    return {"status": "cleared", "session_id": session_id}


@app.post("/api/agent/quick")
async def quick_query(request: QuickQueryRequest) -> JSONResponse:
    """
    Non-streaming endpoint for quick queries.

    Args:
        request: Query request with context

    Returns:
        Complete agent response
    """
    try:
        # Convert context
        context = NotebookContext(**request.context.model_dump())

        # Create orchestrator (with optional user API key)
        orchestrator = AgentOrchestrator(api_key=request.api_key)

        # Collect all messages
        messages = []
        async for message in orchestrator.handle_query(request.query, context):
            messages.append(message.model_dump())

        # Build response
        response = AgentResponse(
            query=request.query,
            route="unknown",  # TODO: Track route in orchestrator
            messages=messages,
            session_id=context.session_id
        )

        return JSONResponse(content=response.model_dump())

    except Exception as e:
        logger.error(f"Error in quick_query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/api/agent/stream")
async def stream_agent(websocket: WebSocket):
    """
    WebSocket endpoint for streaming agent interactions.

    Protocol:
    1. Client sends query message
    2. Server streams AgentMessage objects
    3. If approval needed, server sends approval_needed message
    4. Client sends approval response
    5. Server continues execution
    6. Server sends complete message when done
    """
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "query":
                # Extract query and context
                query = data.get("query")
                context_data = data.get("context")
                require_high_quality = data.get("require_high_quality", False)
                api_key = data.get("api_key")

                if not query or not context_data:
                    await websocket.send_json({
                        "type": "error",
                        "content": {"error": "Missing query or context"}
                    })
                    continue

                # Convert context
                context = NotebookContext(**context_data)

                # Create orchestrator
                orchestrator = AgentOrchestrator(api_key=api_key)

                # Stream responses
                async for message in orchestrator.handle_query(
                    query,
                    context,
                    require_high_quality
                ):
                    # Send message to client
                    await websocket.send_json({
                        "type": message.type.value,
                        "content": message.content,
                        "metadata": message.metadata
                    })

                    # If approval needed, wait for response
                    if message.type == MessageType.APPROVAL_NEEDED:
                        approval_data = await websocket.receive_json()

                        if approval_data.get("type") == "approval":
                            approval = ApprovalResponse(**approval_data.get("data", {}))
                            # TODO: Pass approval to orchestrator
                            # For Phase 2 when planning is implemented
                        elif approval_data.get("type") == "cancel":
                            logger.info("User cancelled operation")
                            break

            elif message_type == "cancel":
                logger.info("Received cancel message")
                break

            else:
                await websocket.send_json({
                    "type": "error",
                    "content": {"error": f"Unknown message type: {message_type}"}
                })

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "content": {"error": str(e)}
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.service_host,
        port=settings.service_port,
        log_level=settings.log_level.lower(),
        reload=True  # For development
    )
