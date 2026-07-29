import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tools import AVAILABLE_TOOLS

load_dotenv()
client = OpenAI()

# Define structural guidelines using explicit markdown instructions
SYSTEM_PROMPT = """You are an Agentic Assistant with access to tools. 
You must solve the user's request by alternating between Thinking and Action phases.

When you need information, call a tool using this exact JSON format:
{"tool": "web_search", "argument": "Name of topic"}

When you have the final answer to satisfy the query, respond directly with text. Do not output JSON if you are finished.
"""

def run_agent(user_query: str):
    # Initialize the memory array to track the state across loops
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]
    
    print(f"🚀 Starting Agent with task: '{user_query}'\n")
    
    # Run the loop up to 5 iterations max to prevent infinite API calls
    for turning_step in range(5):
        print(f"--- 🔄 Iteration Loop Step {turning_step + 1} ---")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        ai_output = response.choices[0].message.content.strip()
        print(f"🤖 AI Output:\n{ai_output}\n")
        
        # Check if the AI wants to use a tool by trying to parse its response as JSON
        try:
            tool_call = json.loads(ai_output)
            tool_name = tool_call.get("tool")
            tool_arg = tool_call.get("argument")
            
            if tool_name in AVAILABLE_TOOLS:
                print(f"🛠️ Executing Tool [{tool_name}] with parameter: '{tool_arg}'")
                tool_result = AVAILABLE_TOOLS[tool_name](tool_arg)
                print(f"📄 Tool Output Received: {tool_result}\n")
                
                # Append both the AI's intent and the physical execution data to the history
                messages.append({"role": "assistant", "content": ai_output})
                messages.append({"role": "user", "content": f"Tool Result: {tool_result}"})
            else:
                print("❌ LLM requested an unavailable tool.")
                break
                
        except json.JSONDecodeError:
            # If it's not valid JSON, the agent is providing its final text summary
            print("🎯 Final Agent Answer Achieved!")
            break

if __name__ == "__main__":
    # Test the agent with a prompt requiring real-world external lookups
    run_agent("give me the movie review of Odyssey in 3 sentences?")
