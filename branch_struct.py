'''
langgraph分支结构
使agent在运行过程中可以根据实际输出进入不同的逻辑处理中
'''

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class BranchState(TypedDict):
    name: str
    age: int
    result: str

def process_node(state: BranchState) -> dict:
    name = state["name"]
    age = state["age"]
    return {"result": f"用户【{name}】，年龄{age}岁："}

def adult_node(state: BranchState) -> dict:
    return {"result": state["result"] + "已成年，可访问全部内容"}

def minor_node(state: BranchState) -> dict:
    return {"result": state["result"] + "尚未成年，仅可访问青少年专区"}

def old_node(state: BranchState) -> dict:
    return {"result": state["result"] + "老年人，进入特殊模式"}

def invalid_node(state: BranchState) -> dict:
    name = state["name"]
    age = state["age"]
    return {"result": f"用户【{name}】的年龄{age}无效，不允许进入"}

# 分支逻辑的路由函数，根据这个函数可以知道下一步该执行什么节点
def age_router(state: BranchState) -> str:
    age = state["age"]

    if age < 0 or age > 150:
        return "invalid"
    elif age >= 60:
        return "old"
    elif age >= 18:
        return "adult"
    else:
        return "minor"
    
workflow = StateGraph(BranchState)

workflow.add_node("process", process_node)
workflow.add_node("adult", adult_node)
workflow.add_node("minor", minor_node)
workflow.add_node("old", old_node)
workflow.add_node("invalid", invalid_node)

workflow.add_edge(START, "process")
# 分支结构中的条件边，第一个参数是源，表示从那个节点出来之后进入分支逻辑；第二个参数是路由函数
workflow.add_conditional_edges(source="process", path=age_router)
workflow.add_edge("adult", END)
workflow.add_edge("minor", END)
workflow.add_edge("old", END)
workflow.add_edge("invalid", END)

app = workflow.compile()

if __name__ == "__main__":
    # 测试1：成年用户
    result1 = app.invoke({"name": "小明", "age": 22})
    print("测试1结果：", result1["result"])

    # 测试2：未成年用户
    result2 = app.invoke({"name": "小红", "age": 14})
    print("测试2结果：", result2["result"])

    # 测试2：非法用户
    result2 = app.invoke({"name": "老王", "age": 190})
    print("测试2结果：", result2["result"])

    # 测试2：老年用户
    result2 = app.invoke({"name": "老李", "age": 70})
    print("测试2结果：", result2["result"])
