from typing import Dict, Any, TypedDict
from langgraph.graph import Graph, END
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)

class GraphState(TypedDict):
    diff: str
    metadata: Dict[str, Any]
    style_issues: list
    formatting_suggestions: list
    documentation_issues: list
    best_practice_violations: list

class PRReviewWorkflow:
    def __init__(self, llm: Ollama):
        self.llm = llm
        self.graph = self._build_graph()

    def _analyze_code_style(self, state: GraphState) -> GraphState:
        """Analyze code style and formatting"""
        prompt = ChatPromptTemplate.from_template("""
        You are a code reviewer analyzing a PR diff. Review the code for style and formatting issues.
        Focus on:
        - Code style consistency
        - Proper indentation
        - Line length
        - Naming conventions
        - Code organization

        PR Diff:
        {diff}

        Provide your analysis in a structured format.
        """)
        
        try:
            if not state.get('diff'):
                logger.warning("No diff provided for analysis")
                return state
            
            response = self.llm.invoke(prompt.format(diff=state['diff']))
            logger.info(f"Style analysis response: {response}")
            
            # Parse response and update state
            state['style_issues'] = [{'description': response}] if response else []
            
        except Exception as e:
            logger.error(f"Error in style analysis: {e}")
            state['style_issues'] = []
            
        return state

    def _analyze_best_practices(self, state: GraphState) -> GraphState:
        """Analyze code for best practices"""
        prompt = ChatPromptTemplate.from_template("""
        Review the following code diff for best practices and potential improvements:
        
        {diff}
        
        Focus on:
        - Code efficiency
        - Error handling
        - Security concerns
        - Performance implications
        - Design patterns
        
        Provide specific suggestions for improvement.
        """)
        
        try:
            response = self.llm.invoke(prompt.format(diff=state['diff']))
            logger.info(f"Best practices analysis response: {response}")
            state['best_practice_violations'] = [{'description': response}] if response else []
        except Exception as e:
            logger.error(f"Error in best practices analysis: {e}")
            state['best_practice_violations'] = []
            
        return state

    def _build_graph(self) -> Graph:
        """Build the analysis workflow graph"""
        workflow = Graph()

        # Add nodes
        workflow.add_node("style_analysis", self._analyze_code_style)
        workflow.add_node("best_practices", self._analyze_best_practices)

        # Define edges
        workflow.add_edge("style_analysis", "best_practices")
        workflow.add_edge("best_practices", END)

        # Set entry point
        workflow.set_entry_point("style_analysis")

        return workflow.compile()

    async def execute(self, diff: str) -> Dict[str, Any]:
        """Execute the analysis workflow"""
        try:
            # Initialize state
            initial_state = {
                "diff": diff,
                "metadata": {"files_changed": diff.count("diff --git")},
                "style_issues": [],
                "formatting_suggestions": [],
                "documentation_issues": [],
                "best_practice_violations": []
            }

            # Execute workflow
            result = await self.graph.ainvoke(initial_state)
            
            # Add summary
            result["summary"] = {
                "total_issues": (
                    len(result.get("style_issues", [])) +
                    len(result.get("formatting_suggestions", [])) +
                    len(result.get("documentation_issues", [])) +
                    len(result.get("best_practice_violations", []))
                ),
                "status": "completed",
                "files_analyzed": result["metadata"]["files_changed"]
            }

            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "error": str(e),
                "summary": {
                    "total_issues": 0,
                    "status": "failed",
                    "files_analyzed": 0
                }
            }
