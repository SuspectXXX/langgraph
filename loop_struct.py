'''
langgraph循环结构
依赖分支结构而成，本身并没有类似其余语言的do...while循环
'''
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class LoopState(TypedDict):
    input_text: str
    answer: str
    retry_count: int
    is_qualified: bool

# 不符合要求的时候，会根据上一轮的结果继续生成
def generate_answer(state: LoopState) -> dict:
    current_answer = state.get("state", "")
    if not current_answer:
        current_answer = f"关于「{state['input_text']}」的回答"
    for _ in range(state["retry_count"]):
        current_answer += "（优化）"
    return {
        "answer": current_answer,
        "retry_count": state["retry_count"] + 1 
    }

def check_qualified(state: LoopState) -> dict:
    is_ok = len(state["answer"]) > 20
    return {"is_qualified": is_ok}

# 路由函数，也是实现循环的根本，不符合要求就重新进入生产节点
def loop_router(state: LoopState) -> dict:
    if state["is_qualified"]:
        return "end"
    max_retry = 3
    if state["retry_count"] >= 3:
        return "end"
    return "generate"

workflow = StateGraph(LoopState)

workflow.add_node("generate", generate_answer)
workflow.add_node("check", check_qualified)

# 类似于do...while循环
workflow.add_edge(START, "generate")
workflow.add_edge("generate", "check")
# 条件边，实现循环的底层实现
workflow.add_conditional_edges(
    source="check",
    path=loop_router,
    path_map={
        "generate": "generate",
        "end": END
    }
)

app = workflow.compile()

if __name__ == "__main__":
    # 初始状态：计数器从0开始
    result = app.invoke({
        "input_text": "什么是LangGraph",
        "retry_count": 0,
        "is_qualified": False
    })
    
    print("最终回答：", result["answer"])
    print("实际重试次数：", result["retry_count"])
    print("是否合格：", result["is_qualified"])