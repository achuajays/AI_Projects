from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel

agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=HfApiModel())

result = agent.run("Write the opening paragraph of a science fiction novel exploring new technological trends and possibilities.")
print(result)