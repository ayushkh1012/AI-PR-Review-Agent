from langchain_community.llms import Ollama
import asyncio
from ..core.config import Settings

async def check_llm():
    """Verify Llama is working"""
    settings = Settings()
    try:
        llm = Ollama(
            base_url=settings.OLLAMA_URL,
            model=settings.MODEL_NAME
        )
        response = await llm.ainvoke("Hello! Are you working?")
        print("LLM Response:", response)
        return True
    except Exception as e:
        print("Error connecting to LLM:", str(e))
        return False

if __name__ == "__main__":
    asyncio.run(check_llm()) 