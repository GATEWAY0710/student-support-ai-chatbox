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
        # Student Support Specific System Prompt
        system_msg = {
            "role": "system",
            "content": """You are a helpful Student Support Chatbot for Minaret University. You are integrated directly into the student portal.

    ### CRITICAL INSTRUCTIONS:
    1. **AUTHENTICATED CONTEXT**: You are ALWAYS talking to a student who is already logged in. 
    2. **NO ASKING FOR IDENTITY**: NEVER ask the student for their Matric Number, Name, or Profile ID. You already have access to this through your tools.
    3. **CURRENCY**: All fees and payments are in **Nigerian Naira (₦)**. NEVER use dollars ($) or any other currency symbol.
    4. **PROACTIVE TOOL USE**: If a student asks about fees, profile, or payments, CALL THE RELEVANT TOOL IMMEDIATELY. 
    - Example: If they ask "What is my balance?", call `get_student_ledger` right away.
    5. **GUID vs MATRIC**: Some tools (like `get_ledger_summary`) require a Profile GUID. If you don't have it, call `get_student_profile` first to retrieve it, then call the second tool. Do NOT involve the student in this process.

    ### YOUR RESPONSIBILITIES:
    - PERSONALIZED DATA: Use tools to check profile, ledger, and payments.
    - FAQ SUPPORT: Answer questions about hostel allocation, campus rules, and moral policies.
    - MULTI-LANGUAGE: Respond in the same language as the user (English or Yoruba).
    - ETHICAL GUIDELINES: Respect MU's Islamic ethics and Ahmadiyya community values.

    Always maintain a helpful, respectful tone. If you encounter an error with a tool, explain that you're having trouble reaching the student records at the moment."""
        }

        messages = [system_msg] + history + [{"role": "user", "content": message}]

        while True:
            # REAL STREAMING: We use stream=True for immediate feedback
            response_stream = await self.client.chat(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                stream=True
            )

            has_tools = False
            full_content = ""

            async for chunk in response_stream:
                # 1. Check for content and yield immediately
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    if content:
                        full_content += content
                        yield content # This sends text to UI immediately!

                # 2. Check for tool calls
                if 'message' in chunk and chunk['message'].get('tool_calls'):
                    # If we found tools, we stop yielding text and prepare for execution
                    # Note: Most models don't mix text and tools in one stream turn
                    tool_calls = chunk['message']['tool_calls']
                    has_tools = True
                    # Add the assistant's "thinking" (the tool call) to message history
                    messages.append(chunk['message'])

                    for tool in tool_calls:
                        # Handle both object and dict styles
                        if hasattr(tool, 'function'):
                            function_name = tool.function.name
                            args = tool.function.arguments
                        else:
                            function_name = tool.get('function', {}).get('name')
                            args = tool.get('function', {}).get('arguments', {})

                        if isinstance(args, str):
                            try: args = json.loads(args)
                            except: args = {}

                        print(f"DEBUG: Executing tool '{function_name}'")

                        result = None
                        if portal_client and student_id:
                            if function_name == "get_student_profile":
                                result = await portal_client.get_profile(student_id)
                            elif function_name == "get_student_dashboard":
                                result = await portal_client.get_dashboard(student_id)
                            elif function_name == "get_student_ledger":
                                result = await portal_client.get_ledger(student_id)
                            elif function_name == "get_payment_history":
                                result = await portal_client.get_payments(student_id)

                        if result is None:
                            if function_name in AVAILABLE_FUNCTIONS:
                                func = AVAILABLE_FUNCTIONS[function_name]
                                try:
                                    result = await func(**args) if asyncio.iscoroutinefunction(func) else func(**args)
                                except Exception as e:
                                    result = f"Error executing tool: {e}"
                            else:
                                result = "Error: Tool not found"

                        messages.append({'role': 'tool', 'content': str(result), 'name': function_name})

            # If no tools were called in this turn, we are finished
            if not has_tools:
                break
            # Otherwise, the loop continues and the model processes tool results