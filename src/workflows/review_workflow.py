from typing import Dict, List
from langgraph.graph import Graph
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from ..agents.code_reviewer import CodeReviewAgent
from ..agents.security_checker import SecurityAgent
from ..agents.style_checker import StyleAgent

class PRReviewWorkflow:
    def __init__(self, llm):
        self.llm = llm
        self.code_reviewer = CodeReviewAgent(llm)
        self.security_checker = SecurityAgent(llm)
        self.style_checker = StyleAgent(llm)
        self.graph = self._build_graph()

    def _build_graph(self) -> Graph:
        # Define the nodes
        nodes = {
            "parse_diff": self._parse_diff,
            "analyze_code": self.code_reviewer.analyze,
            "check_security": self.security_checker.analyze,
            "check_style": self.style_checker.analyze,
            "generate_summary": self._generate_summary,
        }

        # Create the graph
        workflow = Graph()

        # Add nodes
        for name, func in nodes.items():
            workflow.add_node(name, func)

        # Define the flow
        workflow.add_edge("parse_diff", "analyze_code")
        workflow.add_edge("analyze_code", "check_security")
        workflow.add_edge("check_security", "check_style")
        workflow.add_edge("check_style", "generate_summary")

        return workflow.compile()

    async def execute(self, pr_diff: str) -> Dict:
        """Execute the workflow"""
        try:
            result = await self.graph.ainvoke({
                "diff": pr_diff,
                "metadata": {}
            })
            return self._generate_summary(result)
        except Exception as e:
            return {
                "error": str(e),
                "summary": {
                    "total_files": 0,
                    "total_issues": 0,
                    "critical_issues": 0
                }
            }

    def _parse_diff(self, diff: str) -> Dict:
        """Parse the PR diff into structured format"""
        return {
            "files": [],
            "changes": [],
            "stats": {"additions": 0, "deletions": 0}
        }

    def _generate_summary(self, data: Dict) -> Dict:
        """Generate final analysis summary"""
        return {
            "summary": {
                "total_files": len(data.get("files", [])),
                "total_issues": len(data.get("issues", [])),
                "critical_issues": 0
            },
            "details": data
        }
