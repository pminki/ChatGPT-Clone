from altair.vegalite.v5.schema.core import Text
import dotenv
import asyncio
import streamlit as st
from agents import Agent, Runner, SQLiteSession
from streamlit import delta_generator

dotenv.load_dotenv()

# agent 설정 (웹페이지가 리로드 되도 1번만 실행되도록 설정)
if "agent" not in st.session_state:
  st.session_state["agent"] = Agent(
    name="ChatGPT Clone",
    instructions="""
    You are a helpful assistant.
    """,
  )

agent = st.session_state["agent"]


# memory 설정 (웹페이지가 리로드 되도 1번만 실행되도록 설정)
if "session" not in st.session_state:
  st.session_state["session"] = SQLiteSession(
    "chat-history",
    "chat-gpt-clone-memory.db",
  )

session = st.session_state["session"]

def to_generator(delta):
  text = delta if isinstance(delta, str) else str(delta)

  for ch in text:
    yield ch

async def run_agent(message):
  stream = Runner.run_streamed(
    agent,
    message,
    session=session,
  )

  async for event in stream.stream_events():
    if event.type == "raw_response_event":
      if event.data.type == "response.output_text.delta":
        with st.chat_message("ai"):
          st.write_stream(to_generator(event.data.delta))

prompt = st.chat_input("Write a message for your assistant")

if prompt:
  with st.chat_message("human"):
    st.write(prompt)

  asyncio.run(run_agent(prompt))


with st.sidebar:
  reset = st.button("Reset memory")

  if reset:
    asyncio.run(session.clear_session())
  
  st.write(asyncio.run(session.get_items()))


# 실행방법
# uv run streamlit run main.py