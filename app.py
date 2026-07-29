import streamlit as st
import json
#rom dotenv import load_dotenv  
import os
from openai import OpenAI
from tools import AVAILABLE_TOOLS

#oad_dotenv()
# Page Configuration
st.set_page_config(page_title="CS Agent Hub", page_icon="🎧", layout="centered")
st.title("🎧 Customer Service Agent Workspace")
st.caption("AI Assistant powered by a custom ReAct Agent loop")

# Initialize OpenAI client and session memory structures
client = OpenAI()

SYSTEM_PROMPT = """You are a helpful Customer Service Assistant. 
You support internal agents by answering policy questions and looking up data.

If you need data from the system, you MUST call a tool using this exact JSON format:
{"tool": "check_order_status", "argument": "ORD12345"}

CRITICAL RULE: When calling a tool, output ONLY the raw JSON string. Do not include any polite intros, chatter, explanations, or text outside of the JSON block.

When you have the final helpful answer for the user, respond with standard conversational text. Do not output JSON.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Render historical messages on the web UI (skipping system prompt or tool results for cleanliness)
for msg in st.session_state.messages:
    if msg["role"] == "user" and not msg["content"].startswith("Tool Result:"):
        with st.chat_message("user", avatar="👤"):
            st.write(msg["content"])
    elif msg["role"] == "assistant" and not msg["content"].startswith("{"):
        with st.chat_message("assistant", avatar="🤖"):
            st.write(msg["content"])

# Render historical messages on the web UI (skipping system prompt or tool results for cleanliness)
for msg in st.session_state.messages:
    if msg["role"] == "user" and not msg["content"].startswith("Tool Result:"):
        with st.chat_message("user", avatar="👤"):
            st.write(msg["content"])
    elif msg["role"] == "assistant" and not msg["content"].startswith("{"):
        with st.chat_message("assistant", avatar="🤖"):
            st.write(msg["content"])

# User prompt field input
if user_input := st.chat_input("Ask about order tracking or return policies..."):
    # Display human message
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
        
    st.session_state.messages.append({"role": "user", "content": user_input})
    turn_complete = False

    # Execute ReAct loop dynamically behind UI status containers
    while not turn_complete:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        ai_output = response.choices[0].message.content.strip()

        try:
            # Markdown parser fallback
            cleaned_output = ai_output
            if cleaned_output.startswith("```"):
                lines = cleaned_output.splitlines()
                if lines and lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned_output = "\n".join(lines).strip()

            tool_call = json.loads(cleaned_output)
            tool_name = tool_call.get("tool")
            tool_arg = tool_call.get("argument")

            if tool_name in AVAILABLE_TOOLS:
                # Render tool actions live to the agent using status dropdown bars
                with st.status(f"⚙️ Running tool: {tool_name}...", expanded=False) as status:
                    st.write(f"Parameter passed: `{tool_arg}`")
                    tool_result = AVAILABLE_TOOLS[tool_name](tool_arg)
                    st.write(f"Result returned: `{tool_result}`")
                    status.update(label="System action complete!", state="complete")

                st.session_state.messages.append({"role": "assistant", "content": ai_output})
                st.session_state.messages.append({"role": "user", "content": f"Tool Result: {tool_result}"})
            else:
                st.error(f"Tool '{tool_name}' not available.")
                turn_complete = True

        except json.JSONDecodeError:
            # Display finalized text output inside native chat layout bubbles
            with st.chat_message("assistant", avatar="🤖"):
                st.write(ai_output)
                
            st.session_state.messages.append({"role": "assistant", "content": ai_output})
            turn_complete = True