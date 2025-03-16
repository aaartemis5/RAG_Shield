import openai
from langchain.prompts import PromptTemplate
from RagShield.config import OPENAI_API_KEY, OPENAI_MODEL

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

def build_prompt(query: str, context: str) -> str:
    prompt_template = """
You are a cybersecurity assistant. Based on the following context, provide a concise answer in two sentences maximum.
Query: {query}
Context: {context}
Answer:
"""
    prompt = PromptTemplate(input_variables=["query", "context"], template=prompt_template)
    return prompt.format(query=query, context=context)

def get_llm_response(prompt: str) -> str:
    # Use OpenAI ChatCompletion API to get the response
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,  # e.g., "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a cybersecurity assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.2
    )
    # Extract and return the assistant's response text
    return response["choices"][0]["message"]["content"].strip()

if __name__ == "__main__":
    sample_query = "How do malicious scripts compromise systems?"
    sample_context = "Malicious scripts manipulate system files and initiate unauthorized network connections."
    full_prompt = build_prompt(sample_query, sample_context)
    print("Constructed Prompt:\n", full_prompt)
    answer = get_llm_response(full_prompt)
    print("LLM Response:\n", answer)
