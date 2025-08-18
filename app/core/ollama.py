from django.conf import settings
from langchain_core.runnables import RunnableSequence
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# llm = OllamaLLM(
#     model="qwen2.5:7b",
#     temperature=0.1,
#     base_url="http://ollama:11434",
#     top_p=0.3,
#     top_k=10,
#     repeat_penalty=1.1
# )
# prompt = PromptTemplate(
#     input_variables=["ingredient", "language"],
#     template=
#     """
# Translate the food recipe ingredient '{ingredient}' into {language}.
#
# Instructions:
# 1. Always translate the main ingredient using the correct culinary term in {language}.
#    Examples:
#    - 'Venison' → 'Hirschfleisch'
#    - 'Beef' → 'Rindfleisch'
#    - 'Chicken' → 'Hähnchen'
# 2. Translate all descriptive words, states, or preparation notes (e.g., 'raw', 'fresh', 'organic', 'exposed to ultraviolet light') into correct {language} culinary terms.
#    Examples:
#    - 'Raw' → 'Roh'
#    - 'Fresh' → 'Frisch'
#    - 'Exposed to ultraviolet light' → 'UV-bestrahlt'
# 3. For geographical origins (countries, cities, regions):
#    - Translate into {language} if a standard German name exists.
#    - Otherwise, keep the original name.
# 4. Combine all parts into a **natural German culinary phrase**, following this style:
#    - "Venison Sitka Raw Alaska Native" → "Rohes Hirschfleisch aus Sitka, Alaska, von Ureinwohnern"
#    - "Mushrooms, portabella, exposed to ultraviolet light, raw" → "Rohe Portabella-Pilze (UV-bestrahlt)"
# 5. Return ONLY a JSON object in this format: {{"translated": "translated text"}}
# 6. Do not include explanations, extra text, or formatting.
# 7. Never make mistakes like confusing 'Venison' with 'Wildschwein'.
# 8. Always focus on clarity, correctness, and usability in a **recipe context**.
#     """
# )
# data = {
#     "ingredient": "Venison Sitka Raw Alaska Native",
#     "language": "german"
# }
# chain = RunnableSequence(prompt | llm)
# print(chain.invoke(data))


#     """
# Translate USDA food database entry to {language}. Keep comma structure identical.
#
# Input: {ingredient}
# Output: {{"name": "exact translation preserving commas"}}
#     """


# prompt = PromptTemplate(
#     input_variables=["ingredient"],
#     template="Optimize this ingredient name to make it more agreeable within a recipe app to not have too long names. But still keep the important details that this name brings with. The ingredient name: {ingredient}"
# )
#
# chain = RunnableSequence(prompt | llm)
# print(chain.invoke({"ingredient": 'Beef, loin, top loin steak, boneless, lip off, separable lean and fat, trimmed to 0" fat, all grades, raw'}))

def use_ollama(prompt: PromptTemplate, data):
    llm = OllamaLLM(
        model="qwen2.5:7b",
        temperature=0.1,
        base_url="http://ollama:11434",
        top_p=0.3,
        top_k=10,
        repeat_penalty=1.1
    )
    chain = RunnableSequence(prompt | llm)
    return chain.invoke(data)
