import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger("clausely.rag_service")

# Try to import pypdf
try:
    import pypdf
except ImportError:
    pypdf = None

# Try to import docx
try:
    import docx
except ImportError:
    docx = None

# Try to import faiss and sentence_transformers
try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    faiss = None
    SentenceTransformer = None

class RAGService:
    def __init__(self):
        self.sources_config_path = "context_sources.json"
        self.model = None
        self.index = None
        self.chunks = []
        
    def load_sources_config(self) -> Dict[str, str]:
        if os.path.exists(self.sources_config_path):
            with open(self.sources_config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def extract_text_from_file(self, filepath: str) -> str:
        ext = os.path.splitext(filepath)[1].lower()
        if ext in [".txt", ".md"]:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Error reading text file {filepath}: {e}")
        elif ext == ".docx":
            if docx is not None:
                try:
                    doc = docx.Document(filepath)
                    return "\n".join([p.text for p in doc.paragraphs])
                except Exception as e:
                    logger.warning(f"Error reading docx file {filepath}: {e}")
            else:
                logger.warning(f"python-docx not installed. Cannot extract text from DOCX {filepath}")
        elif ext == ".json":
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            except Exception as e:
                logger.warning(f"Error reading json file {filepath}: {e}")
        elif ext == ".pdf":
            if pypdf is not None:
                try:
                    reader = pypdf.PdfReader(filepath)
                    text = []
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text.append(extracted)
                    return "\n".join(text)
                except Exception as e:
                    logger.warning(f"Error reading PDF {filepath}: {e}")
            else:
                logger.warning(f"pypdf not installed. Cannot extract text from PDF {filepath}")
        return ""

    def chunk_text(self, text: str, filepath: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        chunks = []
        filename = os.path.basename(filepath)
        if not text.strip():
            return []
        
        # Simple character-based sliding window chunking
        start = 0
        text_len = len(text)
        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "source": filename,
                "filepath": filepath,
                "start_idx": start,
                "end_idx": end
            })
            start += chunk_size - overlap
            if start >= text_len or end == text_len:
                break
        return chunks

    def build_index(self, selected_sources: Dict[str, bool], uploaded_files: List[Dict[str, str]] = None) -> int:
        """Scan files in selected folders, extract text, chunk and build FAISS index."""
        config = self.load_sources_config()
        self.chunks = []
        
        # Collect files
        for source_key, is_selected in selected_sources.items():
            if not is_selected:
                continue
            folder_path = config.get(source_key)
            if not folder_path or not os.path.isdir(folder_path):
                logger.warning(f"Folder for source {source_key} does not exist: {folder_path}")
                continue
                
            logger.info(f"Scanning folder: {folder_path}")
            
            # List files, sorting by last modified to process newest/most relevant first
            files = []
            for root_dir, _, filenames in os.walk(folder_path):
                for fname in filenames:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext in [".txt", ".md", ".pdf", ".docx", ".json"]:
                        fpath = os.path.join(root_dir, fname)
                        try:
                            mtime = os.path.getmtime(fpath)
                            files.append((fpath, mtime))
                        except Exception:
                            files.append((fpath, 0))
            
            # Sort by mtime descending
            files.sort(key=lambda x: x[1], reverse=True)
            
            # Process up to top 15 files per directory to keep RAG indexing within sensible bounds
            for filepath, _ in files[:15]:
                text = self.extract_text_from_file(filepath)
                if text:
                    file_chunks = self.chunk_text(text, filepath)
                    self.chunks.extend(file_chunks)
                    
        # Index dynamically uploaded files if any
        if uploaded_files:
            for file_info in uploaded_files:
                name = file_info.get("name", "uploaded_file")
                content = file_info.get("content", "")
                if content:
                    file_chunks = self.chunk_text(content, name)
                    self.chunks.extend(file_chunks)
                    
        if not self.chunks:
            logger.info("No chunks created from selected sources.")
            return 0
            
        logger.info(f"Created {len(self.chunks)} chunks. Indexing using FAISS...")
        
        # Initialize SentenceTransformer and FAISS index
        if SentenceTransformer is None or faiss is None:
            logger.error("SentenceTransformer or FAISS is not imported. Cannot index.")
            return 0
            
        try:
            if self.model is None:
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
            
            texts = [c["text"] for c in self.chunks]
            embeddings = self.model.encode(texts, show_progress_bar=False)
            
            import numpy as np
            embeddings = np.array(embeddings).astype("float32")
            
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings)
            logger.info(f"FAISS index built successfully with {len(self.chunks)} chunks.")
            return len(self.chunks)
        except Exception as e:
            logger.error(f"Error building FAISS index: {e}", exc_info=True)
            return 0

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if not self.chunks or self.index is None or self.model is None:
            return []
            
        try:
            import numpy as np
            query_emb = self.model.encode([query], show_progress_bar=False)
            query_emb = np.array(query_emb).astype("float32")
            
            distances, indices = self.index.search(query_emb, k)
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < 0 or idx >= len(self.chunks):
                    continue
                chunk = self.chunks[idx].copy()
                chunk["distance"] = float(distances[0][i])
                results.append(chunk)
            return results
        except Exception as e:
            logger.error(f"Error during FAISS retrieval: {e}", exc_info=True)
            return []
