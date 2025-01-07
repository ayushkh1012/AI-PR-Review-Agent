from langchain.prompts import ChatPromptTemplate
from langchain.llms.base import BaseLLM
from typing import Dict, List

class StyleAgent:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a code style expert. Analyze the code for:
            1. Code formatting issues
            2. Naming conventions
            3. Code organization
            4. Documentation quality
            5. Best practices compliance
            
            Provide specific style improvements and formatting suggestions."""),
            ("human", "{diff}")
        ])

    async def analyze(self, diff: str) -> Dict:
        chain = self.prompt | self.llm
        response = await chain.ainvoke({"diff": diff})
        
        return self._parse_response(response)

    def _parse_response(self, response) -> Dict:
        return {
            "style_issues": [],
            "formatting_suggestions": [],
            "documentation_issues": [],
            "best_practice_violations": []
        } 