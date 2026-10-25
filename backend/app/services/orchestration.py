from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from app.services.llm import LLMProvider, ChatMessage, get_llm_provider
from app.tools import TOOLS, TOOL_SCHEMAS, ToolContext, ToolResult
from app.db.base import get_db
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession


SYSTEM_PROMPT = """You are EnterpriseOps Copilot, a secure assistant for enterprise business operations.

You have access to approved tools for retrieving business data. You MUST use these tools to answer questions about:
- Purchase orders, approvals, procurement
- Suppliers and delivery performance
- Inventory levels and stock movements
- Invoices and three-way matching
- Business policies

RULES:
1. ALWAYS use tools to retrieve data before making claims about business records
2. NEVER invent or hallucinate data - if tools return no results, say so
3. Cite source records using the citation format provided by tools
4. Distinguish facts from interpretations
5. If a question is ambiguous, ask for clarification
6. For calculations, use deterministic tool results, not mental arithmetic
7. Respect authorization - you only see data the user has permission to access

When answering:
- Provide concise, grounded answers
- Include relevant dates, amounts, and identifiers
- State when data is incomplete
- Reference specific records (PO numbers, supplier codes, invoice numbers, SKUs)
- Never claim an action was performed unless confirmed by the backend"""


class OrchestrationService:
    def __init__(self, db: AsyncSession, user_id: int):
        self.db = db
        self.user_id = user_id
        self.llm = get_llm_provider(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            demo_mode=settings.DEMO_MODE,
        )
        self.tool_context = ToolContext(db, user_id)
        self.max_iterations = 5
        self.tools = TOOLS
        self.tool_schemas = list(TOOL_SCHEMAS.values())

    async def process_question(self, question: str, conversation_history: List[ChatMessage] = None) -> Dict[str, Any]:
        messages = [ChatMessage(role="system", content=SYSTEM_PROMPT)]
        
        if conversation_history:
            messages.extend(conversation_history[-10:])
        
        messages.append(ChatMessage(role="user", content=question))
        
        all_citations = []
        all_tool_calls = []
        
        for iteration in range(self.max_iterations):
            response = await self.llm.chat(messages, tools=self.tool_schemas)
            
            if response.tool_calls:
                messages.append(ChatMessage(role="assistant", content=response.content or "", tool_calls=response.tool_calls))
                
                for tool_call in response.tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])
                    
                    if tool_name not in self.tools:
                        tool_result = ToolResult(success=False, error=f"Unknown tool: {tool_name}")
                    else:
                        tool_func = self.tools[tool_name]
                        tool_result = await tool_func(self.tool_context, **tool_args)
                    
                    all_tool_calls.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": tool_result.success,
                        "error": tool_result.error,
                    })
                    
                    if tool_result.citations:
                        all_citations.extend(tool_result.citations)
                    
                    result_content = json.dumps({
                        "success": tool_result.success,
                        "data": tool_result.data,
                        "error": tool_result.error,
                    })
                    
                    messages.append(ChatMessage(
                        role="tool",
                        content=result_content,
                        tool_call_id=tool_call["id"],
                    ))
            else:
                messages.append(ChatMessage(role="assistant", content=response.content or ""))
                break
        
        final_response = messages[-1].content if messages else ""
        
        return {
            "answer": final_response,
            "citations": all_citations,
            "tool_calls": all_tool_calls,
            "iterations": iteration + 1,
        }


async def create_orchestration_service(db: AsyncSession, user_id: int) -> OrchestrationService:
    return OrchestrationService(db, user_id)