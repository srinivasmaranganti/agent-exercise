import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tools import AVAILABLE_TOOLS

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """You are a helpful Customer Service Assistant. 
You support internal agents by answering policy questions and looking up data.

If you need data from the system, you MUST call a tool using this exact JSON format:
{"tool": "check_order_status", "argument": "ORD12345"}

CRITICAL RULE: When calling a tool, output ONLY the raw JSON string. Do not include any polite intros, chatter, explanations, or text outside of the JSON block.

When you have the final helpful answer for the user, respond with standard conversational text. Do not output JSON.
"""

def chat_session():
    conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    print("🎧 Customer Service Agent Active. Type 'exit' to quit.\n")
    
    while True:
        user_input = input("👤 Customer Service Rep: ")
        if user_input.lower() == 'exit':
            print("Session ended.")
            break
            
        conversation_history.append({"role": "user", "content": user_input})
        
        # This flag tracks if the agent is completely done responding to the user's turn
        turn_complete = False
        
        while not turn_complete:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation_history
            )
            ai_output = response.choices[0].message.content.strip()
            
            try:
                # Clean out Markdown code block formatting if present
                cleaned_output = ai_output
                if cleaned_output.startswith("```"):
                    lines = cleaned_output.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].startswith("```"):
                        lines = lines[:-1]
                    cleaned_output = "\n".join(lines).strip()

                # Attempt to parse a tool command
                tool_call = json.loads(cleaned_output)
                tool_name = tool_call.get("tool")
                tool_arg = tool_call.get("argument")
                
                if tool_name in AVAILABLE_TOOLS:
                    print(f"⚙️ [System Action] Running tool '{tool_name}' for '{tool_arg}'...")
                    tool_result = AVAILABLE_TOOLS[tool_name](tool_arg)
                    
                    # Store both the tool call intent and its outcome in history
                    conversation_history.append({"role": "assistant", "content": ai_output})
                    conversation_history.append({"role": "user", "content": f"Tool Result: {tool_result}"})
                else:
                    print("❌ Error: Tool unavailable.")
                    turn_complete = True
                    
            except json.JSONDecodeError:
                # If it's not JSON, it is a final conversational text response for the user
                print(f"🤖 Bot: {ai_output}\n")
                conversation_history.append({"role": "assistant", "content": ai_output})
                turn_complete = True # Safely exit the inner thought loop

if __name__ == "__main__":
    chat_session()
