# Common data processing
import json
import os
import sys
import re
from llama_index.llms.openai import OpenAI
from llama_index.core import (
    Settings,
    Document,
    VectorStoreIndex,
    SimpleDirectoryReader,
    KnowledgeGraphIndex,
)
from llama_index.core.extractors import (
    KeywordExtractor,
    BaseExtractor,
)
from llama_index.core.llms import MockLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline

from llama_index.llms.openai import OpenAI

# define LLM
llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
Settings.llm = llm
Settings.chunk_size = 512

# Warning control
import warnings
warnings.filterwarnings("ignore")

# Load from environment
NEO4J_URI = 'bolt://localhost:7687'
NEO4J_USERNAME = 'neo4j'
NEO4J_PASSWORD = 'master2031'
NEO4J_DATABASE = 'neo4j'

# os.environ["OPENAI_API_KEY"] = API_key
# OPENAI_API_KEY = API_key

# Connect to the knowledge graph instance using LangChain
graph_store = Neo4jGraphStore(
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    url=NEO4J_URI,
    database=NEO4J_DATABASE,
)
storage_context = StorageContext.from_defaults(graph_store=graph_store)

first_file_name = "income-tax-act-1961-amended-by-finance-act-2024.json"
first_file_as_object = json.load(open(first_file_name))

print(len(first_file_as_object["pages"]))

# llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")

Settings.llm = MockLLM(max_tokens=256)
# Settings.llm = llm
embeddings = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.embed_model = embeddings
Settings.chunk_size = 512

class CustomExtractor(BaseExtractor):
    def extract(self, nodes):
        metadata_list = [
            {
                "custom": (
                    node.metadata["document_title"]
                    + "\n"
                    + node.metadata["excerpt_keywords"]
                )
            }
            for node in nodes
        ]
        return metadata_list

transformations = [
    SentenceSplitter(chunk_size=2000,chunk_overlap=200),
    KeywordExtractor(keywords=2),
]


# text_splitter = SentenceSplitter(
#     chunk_size=2000,
#     chunk_overlap=200,
# )

# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size = 2000,
#     chunk_overlap  = 200,
#     length_function = len,
#     is_separator_regex = False,
# )

chunks_with_metadata = []
section_id = 0
documents = []
pattern = r"Section (\d+[A-Z]?)"

form_id = "income_tax_act_1961_amended_finance_act_2024"
for page in first_file_as_object["pages"]:
    title = page["title"]
    match = re.search(pattern, title)
    session_number = "others"
    if match:
        session_number = match.group(1)
    
    item1_text = page["text"]
    documents.append(
        Document(
            text=item1_text,
            metadata={
                "title": title,
                "section": session_number,
                'formId': f'{form_id}', # pulled from the filename
            }
        )
    )


pipeline = IngestionPipeline(transformations=transformations)

all_tax_nodes = pipeline.run(documents=documents)

# print(len(all_tax_nodes))
print(all_tax_nodes[1].metadata)

# for page in first_file_as_object["pages"]:
#     title = page["title"]
#     item1_text = page["text"]
#     item_text_chunks = text_splitter.split_text(item1_text)
#     print(type(item_text_chunks))
#     print(len(item_text_chunks))
#     chunk_seq_id = 0
#     for chunk in item_text_chunks[:20]:
#         chunks_with_metadata.append({
#             'text': chunk, 
#             # metadata from looping...
#             'section': section_id,
#             'title': title,
#             'chunkSeqId': chunk_seq_id,
#             # constructed metadata...
#             'formId': f'{form_id}', # pulled from the filename
#             'chunkId': f'{form_id}-{section_id}-chunk{chunk_seq_id:04d}',
#             # metadata from file...
#         })
#         chunk_seq_id += 1
    
#     print(f'Split into {chunk_seq_id} chunks')    
#     section_id += 1
        
#     break

# index = KnowledgeGraphIndex.from_documents(
#     documents,
#     storage_context=storage_context,
#     max_triplets_per_chunk=2,
# )
