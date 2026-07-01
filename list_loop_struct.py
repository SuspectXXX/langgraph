'''
列表状态和循环结合
可以实现历史消息记录
stream输出时，默认是updates模式，节点执行事件通知，仅在节点执行之后才会输出
stream输出时，values全量模式，会输出完整的状态快照，包含没执行任何节点时的初始状态
'''
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, START, END

class SolveState(TypedDict):
    question: str
    step_history: Annotated[list, operator.add]
    step_count: int
    max_steps: int
    is_done: bool

def generate_step(state: SolveState) -> dict:
    current = state["step_count"] + 1
    question = state["question"]

    step_current = f"第{current}步：处理「{question}」的第{current}个环节"

    return {
        "step_history": [step_current],
        "step_count": current
    }

def check_done(state: SolveState) -> dict:
    is_ok = state["step_count"] >= state["max_steps"]
    return {"is_done": is_ok}

def loop_router(state: SolveState) -> str:
    if state["is_done"]:
        return "end"
    
    return "generate"

workflow = StateGraph(SolveState)

workflow.add_node("generate", generate_step)
workflow.add_node("check", check_done)

workflow.add_edge(START, "generate")
workflow.add_edge("generate", "check")
workflow.add_conditional_edges(
    source="check",
    path=loop_router,
    path_map={
        "generate": "generate",
        "end": END
    }
)

app = workflow.compile()

'''
if __name__ == "__main__":
    result = app.invoke({
        "question": "LangGraph 循环实现",
        "step_history": [],    # 初始为空列表
        "step_count": 0,
        "max_steps": 3,        # 总共走3步
        "is_done": False
    })

    print("=== 最终步骤历史 ===")
    for step in result["step_history"]:
        print(step)
    print(f"\n总步数：{result['step_count']}")
    print(f"是否完成：{result['is_done']}")
'''

'''
# ========== 核心改动：用 stream 流式遍历 ==========
if __name__ == "__main__":
    initial_state = {
        "question": "LangGraph 循环实现",
        "step_history": [],
        "step_count": 0,
        "max_steps": 3,
        "is_done": False
    }

    print("=== 流式输出（增量模式）===")
    # 遍历流式结果，每执行完一个节点就会 yield 一次
    for chunk in app.stream(initial_state):
        # chunk 是字典，键是节点名，值是该节点返回的增量更新
        for node_name, node_output in chunk.items():
            print(f"\n👉 节点执行完成：{node_name}")
            print(f"   节点输出：{node_output}")
'''

if __name__ == "__main__":
    initial_state = {
        "question": "LangGraph 循环实现",
        "step_history": [],
        "step_count": 0,
        "max_steps": 3,
        "is_done": False
    }

    print("=== 流式输出（全量状态模式）===")
    # 指定 stream_mode="values"，每次返回完整 state
    for current_state in app.stream(initial_state, stream_mode="values"):
        print(f"\n📌 当前步数：{current_state['step_count']}")
        print("   当前步骤历史：")
        for step in current_state["step_history"]:
            print(f"     - {step}")