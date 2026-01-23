"""
Init LLM/embeddings/index from local `data/*.txt` without loading TensorFlow model.
Saves index via available API and writes `data/index_docs.json` as fallback.
"""
"""
Init LLM/embeddings/index from local `data/*.txt` without loading TensorFlow model.
Saves index via available API and writes `data/index_docs.json` as fallback.
"""
import os
import pathlib
import json
import traceback

os.environ.setdefault('OLLAMA_HOST', os.environ.get('OLLAMA_HOST', '127.0.0.1:11434'))

def _log(msg):
    try:
        print(msg, flush=True)
    except Exception:
        pass
    try:
        with open('server_debug.log', 'a', encoding='utf-8') as fh:
            fh.write(str(msg) + '\n')
    except Exception:
        pass

def _log_exc(prefix):
    try:
        tb = traceback.format_exc()
        _log(f"{prefix}: {tb}")
        with open('data/init_error.log', 'a', encoding='utf-8') as fh:
            fh.write(f"{prefix}: {tb}\n")
    except Exception:
        pass

try:
    from llama_index import VectorStoreIndex, Document
except Exception:
    VectorStoreIndex = None
    Document = None

try:
    from llama_index.llms.ollama import Ollama
except Exception:
    Ollama = None

try:
    from llama_index.embeddings import HuggingFaceEmbedding
except Exception:
    HuggingFaceEmbedding = None

print('Ollama available:', Ollama is not None)
print('HuggingFaceEmbedding available:', HuggingFaceEmbedding is not None)
print('VectorStoreIndex available:', VectorStoreIndex is not None)

# Create Ollama LLM if available
llm = None
if Ollama is not None:
    try:
        model_name = os.environ.get('OLLAMA_MODEL')
        host = os.environ.get('OLLAMA_HOST')
        if model_name:
            llm = Ollama(model=model_name, host=host) if host else Ollama(model=model_name)
        else:
            try:
                llm = Ollama()
            except Exception:
                llm = Ollama(model='llama2')
    except Exception as e:
        print('Could not create Ollama LLM:', e)

# Create embedding if available
embed = None
if HuggingFaceEmbedding is not None:
    try:
        embed = HuggingFaceEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2')
    except Exception as e:
        print('Could not create HuggingFaceEmbedding:', e)

# Build docs from data/*.txt
docs = []
data_dir = pathlib.Path('data')
if data_dir.exists():
    for f in data_dir.glob('*.txt'):
        try:
            docs.append(Document(text=f.read_text(encoding='utf-8'), doc_id=str(f)))
        except Exception as e:
            print('Skipping', f, e)

if not docs:
    print('No docs found in data/*.txt; aborting index build')
else:
    index = None
    chat_engine = None
    if VectorStoreIndex is not None:
        try:
            if hasattr(VectorStoreIndex, 'from_documents'):
                index = VectorStoreIndex.from_documents(docs, embed_model=embed)
            else:
                index = VectorStoreIndex(docs)

            if hasattr(index, 'as_query_engine'):
                chat_engine = index.as_query_engine()
            elif hasattr(index, 'as_chat_engine'):
                chat_engine = index.as_chat_engine()
            else:
                chat_engine = index

            print('Built index, chat_engine:', type(chat_engine).__name__)

            # Try to persist index via available API
            try:
                if hasattr(index, 'save_to_disk'):
                    try:
                        index.save_to_disk('data/index_store')
                        print('Index saved to data/index_store via save_to_disk')
                    except Exception as e:
                        print('save_to_disk failed:', e)
                elif hasattr(index, 'storage_context') and hasattr(index.storage_context, 'persist'):
                    try:
                        index.storage_context.persist()
                        print('Index persisted via storage_context.persist()')
                    except Exception as e:
                        print('storage_context.persist failed:', e)
            except Exception as e:
                print('Error while trying to persist index:', e)

        except Exception as e:
            print('Could not build index:', e)

    # Always write fallback JSON of docs
    try:
        docs_out = []
        for d in docs:
            docs_out.append({'id': getattr(d, 'doc_id', None) or getattr(d, 'id', None) or None,
                             'text': getattr(d, 'text', None) or str(d)})
        with open('data/index_docs.json', 'w', encoding='utf-8') as fh:
            json.dump(docs_out, fh, ensure_ascii=False, indent=2)
        print('Wrote data/index_docs.json with', len(docs_out), 'documents')
    except Exception as e:
        print('Failed writing index_docs.json:', e)

    # Test a simple query if chat_engine exists
    if chat_engine is not None:
        try:
            q = 'Provide a short ENGLISH and HINDI summary for Taj Mahal'
            resp = None
            try:
                resp = chat_engine.chat(q)
            except Exception:
                try:
                    resp = chat_engine.query(q)
                except Exception:
                    try:
                        resp = chat_engine.run(q)
                    except Exception:
                        resp = None
            print('Sample query response type:', type(resp))
            if resp is not None:
                if hasattr(resp, 'response'):
                    print('Response (truncated):', resp.response[:500])
                elif hasattr(resp, 'text'):
                    print('Response (truncated):', resp.text[:500])
                else:
                    print('Response (str):', str(resp)[:500])
            else:
                print('No response from chat_engine')
        except Exception as e:
            print('Error querying chat_engine:', e)
