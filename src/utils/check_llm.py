from langchain.llms import Ollama
import asyncio

async def check_llm():
    """Verify Llama 3.2 is working"""
    try:
        llm = Ollama(
            base_url="http://localhost:11434",
            model="llama2:3.2"
        )
        response = await llm.ainvoke("Hello! Are you Llama 3.2?")
        print("LLM Response:", response)
        return True
    except Exception as e:
        print("Error connecting to Llama:", str(e))
        return False

if __name__ == "__main__":
    asyncio.run(check_llm()) 