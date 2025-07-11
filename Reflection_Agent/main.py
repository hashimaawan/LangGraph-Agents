from langgraph.graph import StateGraph, END
from typing import TypedDict

from chains import initial_chain, reflection_chain, improvement_chain
class ReflectionState(TypedDict):
    question: str
    initial_answer: str
    reflection: str
    final_answer: str
    iteration: int

class ReflectionAgent:
    def __init__(self, max_iterations: int = 2):
        self.max_iterations = max_iterations
        self.graph = self._build_graph()

    def _build_graph(self):
        """ Constructs the state graph for the reflection agent."""
        graph = StateGraph(ReflectionState)

        graph.add_node("initial", self.initial_step)
        graph.add_node("reflect", self.reflect_step)
        graph.add_node("improve", self.improve_step)

        graph.set_entry_point("initial")
        graph.add_edge("initial", "reflect")
        graph.add_edge("reflect", "improve")

        graph.add_conditional_edges("improve", self.should_continue, {
            "continue": "reflect",
            "end": END
        })

        return graph.compile()

    def initial_step(self, state):
        response = initial_chain.invoke({"question": state["question"]})
        return {
            "initial_answer": response.content,
            "iteration": 1
        }

    def reflect_step(self, state):
        response = reflection_chain.invoke({
            "question": state["question"],
            "initial_answer": state["initial_answer"]
        })
        return {"reflection": response.content}

    def improve_step(self, state):
        response = improvement_chain.invoke({
            "question": state["question"],
            "initial_answer": state["initial_answer"],
            "reflection": state["reflection"]
        })

        return {
            "final_answer": response.content,
            "initial_answer": response.content,  
            "iteration": state["iteration"] + 1
        }

    def should_continue(self, state):
        if state["iteration"] < self.max_iterations:
            return "continue"
        else:
            return "end"

    def run(self, question: str):
        return self.graph.invoke({"question": question})


# Entry point
if __name__ == "__main__":
    agent = ReflectionAgent(max_iterations=1)
    result = agent.run("Why do we dream?")
    
    print(f"\n Final Answer after {result['iteration']} iterations:\n")
    print(result["final_answer"])