import os
import json
import asyncio
import re
from typing import List, Dict, Any, AsyncGenerator
from ollama import AsyncClient
from dotenv import load_dotenv
from agentic.infrastructure.tools import TOOLS, AVAILABLE_FUNCTIONS
from agentic.application.portal_interface import IPortalApiClient

load_dotenv()

class OllamaClient:
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
        self.host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = AsyncClient(host=self.host)

    async def generate_response_stream(
        self, 
        history: List[Dict[str, str]], 
        message: str,
        portal_client: IPortalApiClient = None,
        student_id: str = None
    ) -> AsyncGenerator[str, None]:
        # Compressed System Prompt for faster processing
        system_msg = {
            "role": "system",
            "content": """Minaret University Support Bot. 
- You talk to ALREADY AUTHENTICATED students.
- NEVER ask for GUID, Matric Number, ID, or name. 
- If you need student data, CALL THE TOOLS IMMEDIATELY. They use the active session.
- For fee breakdowns, always call 'get_student_ledger'.
- For a summary, call 'get_student_dashboard'.
- Use Naira (₦) ONLY.
- Support ONLY English for now.
- Islamic Ethics (MANDATORY): START every response with 'Assalamu Alaikum'. END every response with 'Jazakallah Khair' or 'Ma'assalam'. Maintain a respectful, helpful tone.
- Out of Scope: If asked about Hostel Allocation, Campus Rules, or Moral Policies (where no tool exists), state you cannot access that data yet and offer to escalate the enquiry to the Student Affairs department.
- Be direct: Act first, then explain based on data."""
        }

        messages = [system_msg] + history + [{"role": "user", "content": message}]

        while True:
            # REAL STREAMING: We use stream=True for immediate feedback
            # Optimized options for local inference speed
            response_stream = await self.client.chat(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                stream=True,
                options={
                    "temperature": 0.1,      
                    "num_predict": 400,       
                    "num_ctx": 2048,          
                    "top_p": 0.9,
                    "stop": ["\nUser:", "User:"], 
                }
            )

            has_tools = False
            full_content = ""

            async for chunk in response_stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    if content:
                        full_content += content
                        yield content 
                # 2. Check for tool calls
                if 'message' in chunk and chunk['message'].get('tool_calls'):
                    tool_calls = chunk['message']['tool_calls']
                    has_tools = True
                    messages.append(chunk['message'])

                    async def execute_single_tool(tool_call):
                        if hasattr(tool_call, 'function'):
                            name = tool_call.function.name
                            args = tool_call.function.arguments
                        else:
                            name = tool_call.get('function', {}).get('name')
                            args = tool_call.get('function', {}).get('arguments', {})

                        if isinstance(args, str):
                            try: args = json.loads(args)
                            except: args = {}

                        print(f"DEBUG: Executing tool '{name}' concurrently")
                        
                        res = None
                        if portal_client and student_id:
                            if name == "get_student_profile":
                                res = await portal_client.get_profile(student_id)
                            elif name == "get_student_dashboard":
                                res = await portal_client.get_dashboard(student_id)
                            elif name == "get_student_ledger":
                                res = await portal_client.get_ledger(student_id)
                            elif name == "get_payment_history":
                                res = await portal_client.get_payments(student_id)

                        if res is None:
                            if name in AVAILABLE_FUNCTIONS:
                                func = AVAILABLE_FUNCTIONS[name]
                                try:
                                    res = await func(**args) if asyncio.iscoroutinefunction(func) else func(**args)
                                except Exception as e:
                                    res = f"Error executing tool: {e}"
                            else:
                                res = "Error: Tool not found"
                        
                        return {'role': 'tool', 'content': str(res), 'name': name}

                    # Execute all tools in parallel!
                    tool_results = await asyncio.gather(*(execute_single_tool(t) for t in tool_calls))
                    messages.extend(tool_results)

            if not has_tools:
                break
