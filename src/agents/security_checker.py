from langchain.prompts import ChatPromptTemplate
from langchain.llms.base import BaseLLM
from typing import Dict, List

class SecurityAgent:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a security expert. Analyze the code for:
            1. Security vulnerabilities (OWASP Top 10)
            2. Data exposure risks
            3. Authentication/Authorization issues
            4. Input validation problems
            5. Dependency security concerns
            
            Provide detailed security analysis with severity levels."""),
            ("human", "{diff}")
        ])

    async def analyze(self, diff: str) -> Dict:
        chain = self.prompt | self.llm
        response = await chain.ainvoke({"diff": diff})
        
        return self._parse_response(response)

    def _parse_response(self, response) -> Dict:
        return {
            "security_issues": [],
            "risk_level": "low",
            "critical_vulnerabilities": 0,
            "recommendations": []
        } 