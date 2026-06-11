import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from tools.corpus_client import CorpusClient

def test_corpus_client_pinecone_init():
    client = CorpusClient()
    # Check mock parameters are initialized
    assert client.pinecone_api_key is not None
    assert "mock" in client.pinecone_api_key.lower()
    assert client.pinecone_environment == "us-east-1-aws"
    assert client.pinecone_index_name == "indian-case-law-index"

def test_vector_search_structure():
    client = CorpusClient()
    results = client.vector_search("theft case law")
    assert len(results) > 0
    
    # Check that each result matches the Pinecone index query schema
    for res in results:
        assert "id" in res
        assert "score" in res
        assert "metadata" in res
        assert isinstance(res["score"], float)
        assert 0.0 <= res["score"] <= 1.0

def test_vector_search_statutes_fallback():
    client = CorpusClient()
    results = client.search_statutes("theft BNS")
    assert len(results) > 0
    
    # Check fields mapped by the statutes search wrapper
    first = results[0]
    assert "statute" in first
    assert "section" in first
    assert "title" in first
    assert "text" in first
    assert "_score" in first

def test_vector_search_case_law_fallback():
    client = CorpusClient()
    results = client.search_case_law("cheque dishonour")
    assert len(results) > 0
    
    first = results[0]
    assert "case_name" in first
    assert "citation" in first
    assert "court" in first
    assert "summary" in first
    assert "relevant_for" in first
    assert "_score" in first
