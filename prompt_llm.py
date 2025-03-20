from groq import Groq
from langchain.prompts import PromptTemplate
from config import GROQ_API_KEY, GROQ_MODEL

# Instantiate the Groq client using the API key from config
client = Groq(
    api_key=GROQ_API_KEY,
)

def build_prompt(query: str, context: str) -> str:
    prompt_template = """
You are a cybersecurity assistant. Based on the following context, provide a well informed answer to the user , Refer to the context but do not be limited to it. Also tell about how to safeguard against such attacks.
Query: {query}
Context: {context}
Answer:
"""
    prompt = PromptTemplate(input_variables=["query", "context"], template=prompt_template)
    return prompt.format(query=query, context=context)

def get_llm_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model=GROQ_MODEL,  # This value is loaded from your .env via config.py
        messages=[
            {"role": "system", "content": "You are a cybersecurity assistant."},
            {"role": "user", "content": prompt}
        ],
        
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    sample_query = "How do malicious scripts compromise systems?"
    sample_context = "Malicious scripts manipulate system files and initiate unauthorized network connections."
    full_prompt = build_prompt(sample_query, sample_context)
    print("Constructed Prompt:\n", full_prompt)
    answer = get_llm_response(full_prompt)
    print("LLM Response:\n", answer)
