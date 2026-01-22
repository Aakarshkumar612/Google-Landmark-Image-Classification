import os
# Ensure legacy Keras behavior for loading older HDF5 models
os.environ.setdefault('TF_USE_LEGACY_KERAS', '1')
import io
import pathlib
import tensorflow as tf
import numpy as np
from PIL import Image

class LandmarkEngine:
    def __init__(self, model_path, class_names):
        # --- 1. VISION SETUP ---
        # load model, with a fallback shim for older/newer Keras layer config mismatches
        try:
            self.model = tf.keras.models.load_model(model_path)
        except Exception:
            # some saved models include unexpected kwargs (e.g. 'groups') for DepthwiseConv2D
            try:
                from tensorflow.keras import layers
                from tensorflow.keras.utils import get_custom_objects

                class DepthwiseConv2DShim(layers.DepthwiseConv2D):
                    def __init__(self, *args, **kwargs):
                        kwargs.pop('groups', None)
                        super().__init__(*args, **kwargs)

                get_custom_objects()['DepthwiseConv2D'] = DepthwiseConv2DShim
                self.model = tf.keras.models.load_model(model_path)
            except Exception as e:
                raise
        self.class_names = class_names
        self.img_size = (224, 224) 

        # --- 2. NLP SETUP (Lazy-loaded, skipped at init to avoid blocking) ---
        self.llm = None
        self.embed_model = None
        self.index = None
        self.chat_engine = None
        self._llm_initialized = False

    def _init_llm_models(self):
        """Initialize LLM and embedding models on-demand (skipped if not available)"""
        if self._llm_initialized:
            return

        # Mark initialized early to avoid re-entrancy during attempts
        self._llm_initialized = True
        try:
            # Lazy imports
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

            # Create Ollama LLM if available
            self.llm = None
            if Ollama is not None:
                try:
                    host = os.environ.get('OLLAMA_HOST')
                    model_name = os.environ.get('OLLAMA_MODEL')
                    if model_name:
                        self.llm = Ollama(model=model_name, host=host) if host else Ollama(model=model_name)
                    else:
                        try:
                            self.llm = Ollama()
                        except Exception:
                            # try a common default model name
                            self.llm = Ollama(model='llama2')
                except Exception as e:
                    print('Could not create Ollama LLM:', e)

            # Create embedding model if available
            self.embed_model = None
            if HuggingFaceEmbedding is not None:
                try:
                    self.embed_model = HuggingFaceEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2')
                except Exception as e:
                    print('Could not create HuggingFaceEmbedding:', e)

            # Build a small index from ./data/*.txt if possible
            self.index = None
            self.chat_engine = None
            if VectorStoreIndex is not None and Document is not None:
                docs = []
                data_dir = pathlib.Path('data')
                if data_dir.exists():
                    for f in data_dir.glob('*.txt'):
                        try:
                            docs.append(Document(text=f.read_text(encoding='utf-8'), doc_id=str(f)))
                        except Exception:
                            pass

                if docs:
                    try:
                        if hasattr(VectorStoreIndex, 'from_documents'):
                            self.index = VectorStoreIndex.from_documents(docs, embed_model=self.embed_model)
                        else:
                            self.index = VectorStoreIndex(docs)

                        if hasattr(self.index, 'as_query_engine'):
                            self.chat_engine = self.index.as_query_engine()
                        elif hasattr(self.index, 'as_chat_engine'):
                            self.chat_engine = self.index.as_chat_engine()
                        else:
                            self.chat_engine = self.index
                        # Attempt to persist the built index and the raw documents to disk
                        try:
                            # Preferred: use index's own save/persist API if available
                            if hasattr(self.index, 'save_to_disk'):
                                try:
                                    self.index.save_to_disk('data/index_store')
                                except Exception:
                                    pass
                            elif hasattr(self.index, 'storage_context') and hasattr(self.index.storage_context, 'persist'):
                                try:
                                    self.index.storage_context.persist()
                                except Exception:
                                    pass
                        except Exception:
                            pass

                        # Fallback: write the document texts to a simple JSON file for later reloading
                        try:
                            import json
                            docs_out = []
                            for d in docs:
                                try:
                                    docs_out.append({
                                        'id': getattr(d, 'doc_id', None) or getattr(d, 'id', None) or None,
                                        'text': getattr(d, 'text', None) or str(d)
                                    })
                                except Exception:
                                    continue
                            if docs_out:
                                with open('data/index_docs.json', 'w', encoding='utf-8') as fh:
                                    json.dump(docs_out, fh, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                    except Exception as e:
                        print('Could not build index/chat engine:', e)

            print('LLM/embeddings initialization attempted (check logs for errors)')

        except Exception as e:
            print('LLM models unavailable:', e)

    def predict(self, image_bytes, threshold=0.80):
        # Robust byte-to-tensor conversion
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB').resize(self.img_size)
        img_array = tf.keras.utils.img_to_array(img) / 255.0
        
        predictions = self.model.predict(tf.expand_dims(img_array, 0), verbose=0)
        idx = np.argmax(predictions[0])
        confidence = float(predictions[0][idx])
        label = self.class_names[idx]

        return (label, confidence) if confidence >= threshold else ("Uncertain", confidence)

    def get_expert_response(self, landmark_name):
        # 1) Prefer a local data file in ./data that contains the bilingual info
        try:
            data_dir = pathlib.Path('data')
            if data_dir.exists():
                # match files ignoring case/underscores
                target = landmark_name.lower().replace(' ', '_')
                for f in data_dir.glob('*.txt'):
                    name = f.stem.lower()
                    if target in name or name in target:
                        try:
                            return f.read_text(encoding='utf-8')
                        except Exception:
                            continue
        except Exception:
            pass

        # 2) Fallback to the chat engine / index if available
        if self.chat_engine:
            prompt = f"Landmark: {landmark_name}. Provide a detailed history in [ENGLISH] and [HINDI]."
            try:
                # handle several possible APIs
                resp = None
                try:
                    resp = self.chat_engine.chat(prompt)
                except Exception:
                    try:
                        resp = self.chat_engine.query(prompt)
                    except Exception:
                        try:
                            resp = self.chat_engine.run(prompt)
                        except Exception as e:
                            return f"Error querying chat engine: {e}"

                if hasattr(resp, 'response'):
                    return resp.response
                if hasattr(resp, 'text'):
                    return resp.text
                return str(resp)
            except Exception as e:
                return f"Error getting expert response: {e}"

        return "Information not available locally and LLM/index not initialized."