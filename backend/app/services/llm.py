from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import json


@dataclass
class ChatMessage:
    role: str
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None


@dataclass
class ChatResponse:
    content: str
    tool_calls: Optional[List[Dict]] = None
    usage: Optional[Dict[str, int]] = None
    latency_ms: int = 0


class LLMProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> ChatResponse:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile", timeout: int = 30):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._client = None

    def _get_client(self):
        if self._client is None:
            import groq
            self._client = groq.AsyncGroq(api_key=self.api_key, timeout=self.timeout)
        return self._client

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> ChatResponse:
        import time
        start = time.time()
        
        client = self._get_client()
        
        formatted_messages = []
        for msg in messages:
            if msg.role == "tool":
                formatted_messages.append({
                    "role": "tool",
                    "content": msg.content,
                    "tool_call_id": msg.tool_call_id,
                })
            else:
                formatted_messages.append({"role": msg.role, "content": msg.content})
        
        kwargs = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        try:
            response = await client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            
            tool_calls = None
            if choice.message.tool_calls:
                tool_calls = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in choice.message.tool_calls
                ]
            
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            
            return ChatResponse(
                content=choice.message.content or "",
                tool_calls=tool_calls,
                usage=usage,
                latency_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            return ChatResponse(content="", error=str(e), latency_ms=int((time.time() - start) * 1000))


class DemoProvider(LLMProvider):
    def __init__(self):
        self.demo_responses = {
            "pending_approvals": "I found 3 purchase orders awaiting approval: PO-1001 (Supplier: Acme Corp, $15,000), PO-1003 (Supplier: Beta Ltd, $8,500), PO-1007 (Supplier: Gamma Inc, $22,000).",
            "overdue_deliveries": "There are 2 overdue deliveries: PO-1002 (Supplier: Delta Co, expected 2024-01-15) and PO-1005 (Supplier: Epsilon LLC, expected 2024-01-20).",
            "low_stock": "Products below reorder level: SKU-104 (Widget A, 5 units available, reorder level 20), SKU-208 (Gadget B, 0 units available, reorder level 15).",
            "invoice_match": "Invoice INV-2010 has a quantity mismatch: Invoiced 100 units but only 95 received (GR-3007). Amount matches PO.",
            "general": "I can help you query procurement, inventory, suppliers, and invoices. Try asking about pending approvals, overdue deliveries, low stock, or invoice matching.",
        }

    def is_available(self) -> bool:
        return True

    async def chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> ChatResponse:
        import time
        start = time.time()
        
        last_user_msg = ""
        for msg in reversed(messages):
            if msg.role == "user":
                last_user_msg = msg.content.lower()
                break
        
        response_text = self.demo_responses["general"]
        for key, resp in self.demo_responses.items():
            if key in last_user_msg:
                response_text = resp
                break
        
        if tools:
            for tool in tools:
                if tool["name"] in last_user_msg:
                    response_text = f"[DEMO MODE] Would call tool: {tool['name']}"
        
        return ChatResponse(
            content=f"[DEMO MODE] {response_text}",
            tool_calls=None,
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            latency_ms=int((time.time() - start) * 1000),
        )


def get_llm_provider(api_key: str = "", model: str = "llama-3.1-70b-versatile", demo_mode: bool = False) -> LLMProvider:
    if demo_mode or not api_key:
        return DemoProvider()
    return GroqProvider(api_key=api_key, model=model)