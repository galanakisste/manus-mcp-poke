#!/usr/bin/env python3
"""
Manus MCP Server for Poke - Render Deployment
Bridges Poke AI to Manus AI API using FastMCP
"""
import os
import httpx
from fastmcp import FastMCP
from typing import Optional

# Configuration
MANUS_API_KEY = os.environ.get("MANUS_API_KEY", "")
MANUS_API_BASE = os.environ.get("MANUS_API_BASE", "https://api.manus.im/v1")
MANUS_AGENT_PROFILE = os.environ.get("MANUS_AGENT_PROFILE", "manus-1.6")

mcp = FastMCP("Manus AI Server")


def _get_headers():
    """Get headers for Manus API requests"""
    return {
        "API_KEY": MANUS_API_KEY,
        "Content-Type": "application/json"
    }


def _handle_response(response: httpx.Response) -> dict:
    """Handle Manus API response"""
    try:
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        error_msg = f"Manus API Error: {e}"
        try:
            error_body = response.json()
            error_msg = f"Manus API Error: {error_body.get('message', str(e))}"
        except:
            pass
        return {"error": error_msg, "status_code": response.status_code}


@mcp.tool(description="Create a new Manus AI task. Manus is an AI agent that can browse the web, write code, create files, and complete complex tasks autonomously.")
def create_task(
    prompt: str,
    agent_profile: Optional[str] = None,
    task_mode: Optional[str] = "agent",
    project_id: Optional[str] = None
) -> dict:
    """
    Create a new task in Manus AI.
    
    Args:
        prompt: The task instructions/command for the Manus AI agent
        agent_profile: Agent profile - 'manus-1.6', 'manus-1.6-lite', or 'manus-1.6-max'
        task_mode: Task mode - 'agent', 'chat', or 'adaptive'
        project_id: Optional project ID to organize tasks
    """
    url = f"{MANUS_API_BASE}/tasks"
    
    payload = {
        "prompt": prompt,
        "agentProfile": agent_profile or MANUS_AGENT_PROFILE,
        "taskMode": task_mode or "agent"
    }
    
    if project_id:
        payload["projectId"] = project_id
    
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=_get_headers(), json=payload)
        return _handle_response(response)


@mcp.tool(description="Get the current status and output of a Manus task")
def get_task_status(task_id: str) -> dict:
    """Get the status of a Manus task."""
    url = f"{MANUS_API_BASE}/tasks/{task_id}"
    
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, headers=_get_headers())
        return _handle_response(response)


@mcp.tool(description="List recent Manus tasks with optional filtering")
def list_tasks(
    status: Optional[str] = None,
    limit: Optional[int] = 20,
    project_id: Optional[str] = None
) -> dict:
    """List Manus tasks with optional filtering."""
    url = f"{MANUS_API_BASE}/tasks"
    params = {"limit": limit or 20}
    
    if status:
        params["status"] = [status]
    if project_id:
        params["project_id"] = project_id
    
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, headers=_get_headers(), params=params)
        return _handle_response(response)


@mcp.tool(description="Continue an existing Manus task with additional instructions")
def continue_task(task_id: str, prompt: str) -> dict:
    """Continue an existing Manus task."""
    url = f"{MANUS_API_BASE}/tasks"
    
    payload = {
        "prompt": prompt,
        "agentProfile": MANUS_AGENT_PROFILE,
        "taskId": task_id
    }
    
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=_get_headers(), json=payload)
        return _handle_response(response)


@mcp.tool(description="Get information about this MCP server")
def get_server_info() -> dict:
    """Get information about the Manus MCP server"""
    return {
        "server_name": "Manus AI MCP Server",
        "version": "1.0.0",
        "description": "Bridge between Poke AI and Manus AI",
        "manus_api_base": MANUS_API_BASE,
        "agent_profile": MANUS_AGENT_PROFILE
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting Manus MCP server on {host}:{port}")
    print(f"MCP endpoint will be at: http://{host}:{port}/mcp")
    
    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True
    )
