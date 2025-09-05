

def load_all_documents(data_folder: Path = UPLOAD_DIR) -> None:
    """Load and index all documents from the data folder."""
    data_folder = Path(data_folder)
    data_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"\n=== Loading documents from: {data_folder.absolute()} ===")
    print(f"Directory exists: {data_folder.exists()}")
    print(f"Directory contents: {list(data_folder.glob('*'))}")
    
    all_chunks = []
    all_metadata = []
    
    for filename in os.listdir(data_folder):
        if filename.endswith('.json'):
            file_path = data_folder / filename
            chunks = load_document(file_path)
            all_chunks.extend(chunk['text'] for chunk in chunks)
            all_metadata.extend(chunks)
    
    if all_chunks:
        print(f"\nFound {len(all_chunks)} document chunks to index")
        tfidf_matrix = _state['vectorizer'].fit_transform(all_chunks)
        _state.update({
            'documents': all_chunks,
            'doc_metadata': all_metadata,
            'tfidf_matrix': tfidf_matrix
        })
        print(f"TF-IDF matrix created with shape: {tfidf_matrix.shape}")
    else:
        print("\nNo valid document chunks found to index")
