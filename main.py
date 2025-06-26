from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

model = OllamaLLM(model='llama3.2')

template = """
I want you to create a small comprehensive recipe description with a maximum of 250 characters in the language of the title.
As result print just the description.

Here is the recipe title the description should be tailored for: {recipe_title}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

result = chain.invoke({"recipe_title": "Bratwurst mit Paprikazwiebeln"})
print(result)
