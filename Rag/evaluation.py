from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import pandas as pd
from datasets import Dataset

class RagEvaluator:
    def __init__(self, testset, rag_instance, embedding_model_name="all-MiniLM-L6-v2", similarity_threshold=0.8):
 
        self.testset = testset
        self.rag = rag_instance
        self.embedding_model_name = embedding_model_name
        self.similarity_threshold = similarity_threshold
        self.model = SentenceTransformer(embedding_model_name)

    def generate_testset_with_answers_and_contexts(self):
  
        ragas_dataset = []

        for index, row in tqdm(self.testset.iterrows(), total=len(self.testset), desc="Processing Questions"):
            answer = self.rag.query(row["Questions"])
            contexts = self.rag.retriever.query(row["Questions"])
            ragas_dataset.append(
                {
                    "Question": row["Questions"],
                    "Answer": answer,
                    "Contexts": contexts,
                    "GroundTruth": row["GroundTruth"]
                }
            )

        enriched_testset = pd.DataFrame(ragas_dataset)
        return enriched_testset

    def evaluate(self, enriched_testset):
 
        answer_relevancy_scores = []
        faithfulness_scores = []
        context_precision_scores = []

        for _, row in enriched_testset.iterrows():
            question = row["Question"]
            answer = row["Answer"]
            contexts = row["Contexts"]
            ground_truth = row["GroundTruth"]

            #  Answer Relevancy
            answer_embedding = self.model.encode(answer, convert_to_tensor=True)
            ground_truth_embedding = self.model.encode(ground_truth, convert_to_tensor=True)
            answer_relevancy = cosine_similarity(
                answer_embedding.reshape(1, -1),
                ground_truth_embedding.reshape(1, -1)
            )[0][0]
            answer_relevancy_scores.append(answer_relevancy)

            #  Faithfulness
            context_embedding = self.model.encode(contexts, convert_to_tensor=True)
            faithfulness = cosine_similarity(
                answer_embedding.reshape(1, -1),
                context_embedding.reshape(1, -1)
            )[0][0]
            faithfulness_scores.append(faithfulness)

            #  Context Precision
            context_parts = contexts.split("\n")  
            context_embeddings = self.model.encode(context_parts, convert_to_tensor=True)
            ground_truth_embeddings = self.model.encode([ground_truth] * len(context_parts), convert_to_tensor=True)

            precision_scores = [
                cosine_similarity(context_embedding.reshape(1, -1), ground_truth_embedding.reshape(1, -1))[0][0]
                for context_embedding, ground_truth_embedding in zip(context_embeddings, ground_truth_embeddings)
            ]
            relevant_contexts = sum(score > self.similarity_threshold for score in precision_scores) 
            context_precision = relevant_contexts / len(context_parts) if len(context_parts) > 0 else 0
            context_precision_scores.append(context_precision)


        enriched_testset["Answer Relevancy"] = answer_relevancy_scores
        enriched_testset["Faithfulness"] = faithfulness_scores
        enriched_testset["Context Precision"] = context_precision_scores

        return enriched_testset