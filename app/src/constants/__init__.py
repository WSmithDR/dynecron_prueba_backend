
_state = {
    'documents': [],
    'doc_metadata': [],
    'tfidf_matrix': None,
    'vectorizer': TfidfVectorizer(
        token_pattern=r'(?u)\b\w[\w-]*\w\b',
        ngram_range=(1, 2),
        max_features=SEARCH_CONFIG["max_results"],
        strip_accents='unicode',
        lowercase=True
    )
}