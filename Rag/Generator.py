import requests
import json
import os


class BaseAssistant:
    def __init__(self, url, retriever, llm = "mistral-7b-instruct-v0.3"):
        self.url = url
        self.headers = {"Content-Type": "application/json"}
        self.retriever = retriever
        self.llm = llm

class ResponseToQuery(BaseAssistant):
    def query(self, query):
        payload = {
            "model": f"{self.llm}",
            "messages": [
                {"role": "assistant", "content": "Tu es un assistant intelligent conçu pour répondre efficacement aux questions. Utilise le contexte fourni pour répondre en français de manière précise et concise."},
                {"role": "user", "content": f"réponds à la question suivante:{query} en se basant sur le contexte suivant {self.retriever.query(query)}"}
            ],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code}"

class RefinementAnswering(BaseAssistant):
    def query(self, query):
        payload_llm = {
            "model": f"{self.llm}",
            "messages": [
                {"role": "assistant", "content": "Tu es un assistant intelligent conçu pour essayer de répondre aux questions. Même si vous n'avez aucun savoir dessus, essayer de fromuler une réponse qui semble plausible."},
                {"role": "user", "content": f"hallucine une proposition de réponse à la question suivante:{query}"}
            ],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False
        }

        response_directe_llm = requests.post(self.url, headers=self.headers, data=json.dumps(payload_llm)).json()["choices"][0]["message"]["content"]

        final_payload = {
            "model": f"{self.llm}",
            "messages": [
                {"role": "assistant", "content": "Tu es un assistant intelligent conçu pour répondre efficacement aux questions. Utilise le contexte fourni pour répondre en français de manière précise et concise, et en s'inspirant de la réponse fictive"},
                {"role": "user", "content": f"réponds à la question suivante:{query} en se basant sur le contexte suivant {self.retriever.query(query)}, et en s'inspirant de la réponse fictive suivante: {response_directe_llm}"}
            ],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(final_payload)).json()["choices"][0]["message"]["content"]
        return response

class FeedbackAnswering(BaseAssistant):
    def query(self, query):
        response_to_query = ResponseToQuery(self.url, self.retriever,llm = self.llm).query(query)

        retrieved_context = self.retriever.query(response_to_query)

        combined_context = '\n\n'.join([self.retriever.query(query), retrieved_context])

        payload = {
            "model": f"{self.llm}",
            "messages": [
                {"role": "assistant", "content": "Tu es un assistant intelligent conçu pour répondre efficacement aux questions. Utilise le contexte fourni pour répondre en français de manière précise et concise."},
                {"role": "user", "content": f"réponds à la question suivante:{query} en se basant sur le contexte suivant {combined_context}."}
            ]
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(payload)).json()['choices'][0]['message']['content']

        return response
