"""Orchestrator for managing tool execution and response generation."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .knowledge_base import KnowledgeBase
from src.tools.tool_registry import ToolRegistry, BaseTool
from src.config import (
    MAX_TOOLS_PER_QUERY,
    MIN_SIMILARITY_SCORE,
    DEBUG
)

logger = logging.getLogger(__name__)

class Orchestrator:
    """Coordinates tool execution and response generation."""
    
    def __init__(self, tool_registry: ToolRegistry, knowledge_base: KnowledgeBase):
        """Initialize the orchestrator.
        
        Args:
            tool_registry: Tool registry instance
            knowledge_base: Knowledge base instance
        """
        self.tool_registry = tool_registry
        self.knowledge_base = knowledge_base
        self.conversation_history: List[Dict[str, Any]] = []
        
    def process_query(self, query: str) -> str:
        """Process a user query and generate a response."""
        try:
            # Validate input
            if not query or not isinstance(query, str):
                raise ValueError("Invalid query: Query must be a non-empty string")
            
            # Validate knowledge base
            if not hasattr(self, 'knowledge_base') or not self.knowledge_base:
                raise ValueError("Knowledge base not initialized")
            
            # Validate tool registry
            if not hasattr(self, 'tool_registry') or not self.tool_registry:
                raise ValueError("Tool registry not initialized")
            
            # Add query to conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': query,
                'timestamp': datetime.now().isoformat()
            })
            
            # Extract role and skills from query
            role = "software developer"  # Default role
            skills = ["python"]  # Default skills
            
            # Try to extract role and skills from query
            query_lower = query.lower()
            
            # Common roles
            roles = [
                "software developer", "data scientist", "data engineer",
                "machine learning engineer", "devops engineer", "cloud architect",
                "full stack developer", "frontend developer", "backend developer",
                "mobile developer", "security engineer", "product manager"
            ]
            
            # Common skills
            all_skills = [
                "python", "java", "javascript", "typescript", "react", "angular",
                "vue", "node.js", "django", "flask", "spring", "tensorflow",
                "pytorch", "scikit-learn", "pandas", "numpy", "aws", "azure",
                "gcp", "docker", "kubernetes", "terraform", "ansible", "jenkins",
                "git", "sql", "nosql", "mongodb", "postgresql", "mysql"
            ]
            
            # Find role in query
            for r in roles:
                if r in query_lower:
                    role = r
                    break
            
            # Find skills in query
            found_skills = []
            for skill in all_skills:
                if skill in query_lower:
                    found_skills.append(skill)
            
            if found_skills:
                skills = found_skills
            
            # Get career guidance from knowledge base
            try:
                kb_results = self.knowledge_base.get_career_guidance(role, skills)
                if not isinstance(kb_results, dict):
                    raise ValueError("Invalid knowledge base response format")
            except Exception as e:
                logger.error(f"Knowledge base error: {str(e)}")
                kb_results = {}
            
            # Select appropriate tools
            try:
                selected_tools = self._select_tools(query, kb_results)
                if not isinstance(selected_tools, list):
                    raise ValueError("Invalid tool selection response")
            except Exception as e:
                logger.error(f"Tool selection error: {str(e)}")
                selected_tools = []
            
            # Execute tools and collect results
            tool_results = []
            for tool in selected_tools:
                try:
                    result = tool.execute(query)
                    if result and isinstance(result, (str, dict)):
                        tool_results.append(result)
                except Exception as e:
                    logger.error(f"Error executing tool {tool.name}: {str(e)}")
            
            # Generate response
            try:
                response = self._generate_response(query, kb_results, tool_results)
                if not response or not isinstance(response, str):
                    raise ValueError("Invalid response format")
            except Exception as e:
                logger.error(f"Response generation error: {str(e)}")
                response = "I'm sorry, I encountered an error while generating the response. Please try again."
            
            # Add response to conversation history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            
            return response
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return f"I'm sorry, I couldn't process your query: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error processing query: {str(e)}")
            return "I'm sorry, I encountered an unexpected error. Please try again later."
    
    def _select_tools(self, query: str, kb_results: Dict[str, Any]) -> List[BaseTool]:
        """Select appropriate tools for the query.
        
        Args:
            query: User query
            kb_results: Knowledge base results
            
        Returns:
            List of selected tools
        """
        try:
            # Get all available tools
            all_tools = self.tool_registry.get_all_tools()
            
            # Score tools based on query and KB results
            tool_scores = []
            for tool in all_tools.values():
                score = self._score_tool(tool, query, kb_results)
                tool_scores.append((tool, score))
            
            # Sort tools by score
            tool_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select top tools
            selected_tools = [
                tool for tool, score in tool_scores[:MAX_TOOLS_PER_QUERY]
                if score >= MIN_SIMILARITY_SCORE
            ]
            
            if DEBUG:
                logger.debug(f"Selected tools: {[tool.name for tool in selected_tools]}")
            
            return selected_tools
            
        except Exception as e:
            logger.error(f"Error selecting tools: {str(e)}")
            return []
    
    def _score_tool(self, tool: BaseTool, query: str, kb_results: Dict[str, Any]) -> float:
        """Score a tool based on query and KB results.
        
        Args:
            tool: Tool to score
            query: User query
            kb_results: Knowledge base results
            
        Returns:
            Tool score
        """
        try:
            # Score based on tool description
            description_score = self._calculate_similarity(
                query.lower(),
                tool.description.lower()
            )
            
            # Score based on KB results
            kb_score = 0.0
            if kb_results:
                # Extract text from all KB results
                kb_texts = []
                
                # Add learning resources
                if "learning_resources" in kb_results:
                    for resources in kb_results["learning_resources"].values():
                        for resource in resources:
                            kb_texts.append(resource.get('title', ''))
                            kb_texts.append(resource.get('description', ''))
                
                # Add market trends
                if "market_trends" in kb_results:
                    for trend in kb_results["market_trends"].values():
                        if trend:
                            kb_texts.append(trend.get('title', ''))
                            kb_texts.append(trend.get('description', ''))
                
                # Add success stories
                if "success_stories" in kb_results:
                    for stories in kb_results["success_stories"].values():
                        for story in stories:
                            kb_texts.append(story.get('title', ''))
                            kb_texts.append(story.get('description', ''))
                
                # Add career advice
                if "career_advice" in kb_results:
                    for advice in kb_results["career_advice"].values():
                        for item in advice:
                            kb_texts.append(item.get('title', ''))
                            kb_texts.append(item.get('description', ''))
                
                # Calculate similarity with combined KB text
                if kb_texts:
                    kb_text = ' '.join(kb_texts)
                    kb_score = self._calculate_similarity(
                        query.lower(),
                        kb_text.lower()
                    )
            
            # Combine scores
            return 0.7 * description_score + 0.3 * kb_score
            
        except Exception as e:
            logger.error(f"Error scoring tool {tool.name}: {str(e)}")
            return 0.0
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score
        """
        try:
            # Simple word overlap similarity
            words1 = set(text1.split())
            words2 = set(text2.split())
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def _generate_response(self, query: str, kb_results: Dict[str, Any], tool_results: List[Dict[str, Any]]) -> str:
        """Generate a response based on query, KB results, and tool results."""
        try:
            context = []
            
            if kb_results:
                context.append("Based on my research:")
                
                if "learning_resources" in kb_results:
                    context.append("\nLearning Resources:")
                    for category, resources in kb_results["learning_resources"].items():
                        if resources:
                            context.append(f"\n{category.replace('_', ' ').title()}:")
                            for resource in resources[:3]:
                                context.append(f"- {resource['title']}")
                                if resource.get('description'):
                                    context.append(f"  {resource['description']}")
                
                if "market_trends" in kb_results:
                    context.append("\nMarket Trends:")
                    for category, trend in kb_results["market_trends"].items():
                        if trend:
                            context.append(f"\n{category.replace('_', ' ').title()}:")
                            context.append(f"- {trend['title']}")
                            if trend.get('description'):
                                context.append(f"  {trend['description']}")
                
                if "success_stories" in kb_results:
                    context.append("\nSuccess Stories:")
                    for category, stories in kb_results["success_stories"].items():
                        if stories:
                            context.append(f"\n{category.replace('_', ' ').title()}:")
                            for story in stories[:2]:
                                context.append(f"- {story['title']}")
                                if story.get('description'):
                                    context.append(f"  {story['description']}")
                
                if "career_advice" in kb_results:
                    context.append("\nCareer Advice:")
                    for level, advice in kb_results["career_advice"].items():
                        if advice:
                            context.append(f"\n{level.replace('_', ' ').title()}:")
                            for item in advice[:2]:
                                context.append(f"- {item['title']}")
                                if item.get('description'):
                                    context.append(f"  {item['description']}")
            
            if tool_results:
                context.append("\nAdditional Information:")
                for result in tool_results:
                    if isinstance(result, dict) and 'formatted_response' in result:
                        context.append(result['formatted_response'])
                    else:
                        context.append(str(result))
            
            response = "\n".join(context) if context else "I couldn't find specific information about that. Would you like me to search the web for more details?"
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I'm sorry, I couldn't generate a proper response. Please try rephrasing your question."