"""
Fast local-only initializer: writes data/index_docs.json from data/*.txt
Does not import heavy libraries or contact external services.
"""
import pathlib, json

data_dir = pathlib.Path('data')
if not data_dir.exists():
    print('data/ directory not found')
else:
    docs_out = []
    for f in data_dir.glob('*.txt'):
        try:
            text = f.read_text(encoding='utf-8')
            docs_out.append({'id': str(f), 'text': text})
        except Exception as e:
            print('Failed reading', f, e)
    if docs_out:
        out = data_dir / 'index_docs.json'
        out.write_text(json.dumps(docs_out, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Wrote', out, 'with', len(docs_out), 'documents')
    else:
        print('No .txt docs found in data/')
