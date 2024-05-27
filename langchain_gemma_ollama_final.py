import asyncio
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
import chainlit as cl
import os

# Set up ElevenLabs client
# os.environ["ELEVEN_API_KEY"] = "32d2a71750ac41c74e5751f54a84a349"
# eleven_client = ElevenLabs()

@cl.on_chat_start
async def on_chat_start():
    print("Executing on_chat_start()")
    elements = [
    ]
    await cl.Message(content="Hello there, I am SmartServe. How can I help you ?", elements=elements).send()
    
    model = Ollama(model="gemma:2b")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are SmartServe, you are an expert in science similar to albert einstein. Your task is to help the user with its queries and doubts.do not deviate from your role . Stay on point, be crisp, concise. Do not do unnecessary interactions or long conversations",
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    
    # Set the runnable object in the user session
    cl.user_session.set("runnable", runnable)
    print("Runnable object is set in the session.")

@cl.on_message
async def on_message(message: cl.Message):
    print("Executing on_message()")
    # Retrieve the runnable object from the user session
    runnable = cl.user_session.get("runnable")

    if runnable is None:
        print("Runnable object is not set in the session.")
        return

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

# Start the asyncio event loop and run the chat handlers
async def main():
    await cl.run_handlers()

if __name__ == "__main__":
    asyncio.run(main())
