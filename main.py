from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class HelloState(TypedDict):
    name: str
    greeting: str

def say_hello(state: HelloState) -> dict:
    # 1. 从状态中读取name
    name = state["name"]
    # 2. 执行业务逻辑
    result = f"你好，{name}！欢迎学习langgraph"
    return {"greeting": result}

# 初始化工作流图
workflow = StateGraph(HelloState)

# 为图添加节点，第一个参数是节点名，第二个参数是节点函数
workflow.add_node("hello", say_hello)

# 为图增加边，第一个参数是边的起点，第二个参数是边的终点
# START、END为langgraph中的内置的起点和终点，近做标记，不执行业务逻辑
# 整体流向为 START -> hello -> END
workflow.add_edge(START, "hello")
workflow.add_edge("hello", END)

# 编译图，生成可执行实例。使图从定义阶段跨入可执行阶段
app = workflow.compile()

# 传入初始状态，同步执行整个图
result = app.invoke({"name": "小明"})

# 查看图执行完成后的结果
print(result["greeting"])