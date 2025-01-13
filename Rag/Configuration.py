from .Retriever import ChromaRetriever
from .Generator import ResponseToQuery , FeedbackAnswering, RefinementAnswering
from .evaluation import RagEvaluator
from sentence_transformers import SentenceTransformer
import json
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np



load_dotenv()
url = os.getenv("url")

chunks= pd.read_csv('Rag/Chunks.csv')['Content'].tolist()
testset = pd.read_csv('Rag/testset.csv')



#rem : retriever embedding model
#eem : evaluator embedding model

class Configuration():
    def __init__(self,config_name,rem, top_k, approach,llm,eem,similarity_threshold ):
        self.config_name = config_name
        self.rem = rem
        self.top_k = top_k
        self.approach = approach
        self.llm = llm
        self.eem = eem
        self.similarity_threshold = similarity_threshold
        self.retriever = None
        self.rag_chain = None
        self.evaluator = None
        self.metrics = None


    def fit(self):
        self.retriever = ChromaRetriever(embedding_model=SentenceTransformer(str(self.rem)), chunks=chunks, top_k=self.top_k,collection_name="my_collection")
        if self.approach == 'FeedbackAnswering':

            self.rag_chain = FeedbackAnswering(retriever=self.retriever, url=url,llm=str(self.llm))

        elif self.approach == 'RefinementAnswering':
            
            self.rag_chain = RefinementAnswering(retriever=self.retriever , url=url,llm=str(self.llm))

        else:
            
            self.rag_chain  = ResponseToQuery(retriever=self.retriever, url=url , llm=str(self.llm))
        
        self.evaluator = RagEvaluator(testset=testset, rag_instance=self.rag_chain, embedding_model_name=str(self.eem), similarity_threshold=self.similarity_threshold)
    
    def measures(self):

        df = self.evaluator.generate_testset_with_answers_and_contexts()
        ddf = self.evaluator.evaluate(df)
        self.metrics = {'Answer_Relevancy':ddf['Answer Relevancy'].mean(), 'Context_Precision':ddf['Context Precision'].mean(), 'Faithfulness':ddf['Faithfulness'].mean() }
        
        return self.metrics
    
    def predict(self, query):

        return self.rag_chain.query(query)