FUNCTIONS_Chain_PROMPT = """Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.

{history}
Human: {input}
Chatbot:"""


EXTRACT_STRATEGY = """Extract the trading strategy logic from the following, don't describe anything other than strategy: 
```
{raw_input}
```

Use the following output format:
Strategy Description: `content`
"""

EXTRACT_AKSHARE = """Extract task information related to obtaining data from AkShare from the following, don't reply to anything other than the mission objective: 
```
{raw_input}
```

Use the following output format:
AkShare Description: `content`
"""
