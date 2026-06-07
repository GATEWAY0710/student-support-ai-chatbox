from typing import Dict, Any

# These will be mapped to actual API calls in the OllamaClient/ChatService
# We define them here so the AI knows their schema.

def get_student_profile() -> str:
    """Get the authenticated student's full profile including bio data (email, phone) and academic details (matric number, current level)."""
    return "This tool requires a connection to the student portal."

def get_student_dashboard() -> str:
    """Get a comprehensive summary of the student's status. Returns: Current Level, Programme, Total Paid Amount, and Total Outstanding Fees. 
    Use this for 'How am I doing?' or 'Give me a summary' questions."""
    return "This tool requires a connection to the student portal."

def get_student_ledger() -> str:
    """Get the student's full ledger (debits and credits). Use this for specific 'How much do I owe?' or 'Show me my fees' questions."""
    return "This tool requires a connection to the student portal."

def get_payment_history() -> str:
    """Get the student's transaction list and statuses. Use this for 'Did my payment go through?' or 'Show my past payments'."""
    return "This tool requires a connection to the student portal."

def say_hello(name: str) -> str:
    """Say hello to the user."""
    return f"Hello {name}, welcome to your Student Support System!"


# --- Tool Registry ---

AVAILABLE_FUNCTIONS = {
    'say_hello': say_hello,
    'get_student_profile': get_student_profile,
    'get_student_dashboard': get_student_dashboard,
    'get_student_ledger': get_student_ledger,
    'get_payment_history': get_payment_history,
}


TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'say_hello',
            'description': 'Say hello to the user.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                },
                'required': ['name'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_student_profile',
            'description': "Get the student's bio data and academic profile. This uses the authenticated session; NO GUID or ID is required.",
            'parameters': {
                'type': 'object',
                'properties': {},
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_student_dashboard',
            'description': "Get a summary of fees, programme, and level. This uses the authenticated session; NO GUID or ID is required.",
            'parameters': {
                'type': 'object',
                'properties': {},
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_student_ledger',
            'description': "Get detailed fee debits (breakdown), payments, and outstanding balances. This uses the authenticated session; NO GUID or ID is required.",
            'parameters': {
                'type': 'object',
                'properties': {},
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_payment_history',
            'description': "Get the history of all payment transactions.",
            'parameters': {
                'type': 'object',
                'properties': {},
            },
        },
    }
]