from app.rag.simple_tfidf import Document, TfidfRetriever


def test_retriever_finds_mhs_context() -> None:
    r = TfidfRetriever(
        [
            Document("mhs", "MHS-ready hardware registry exposes normalized capabilities through MCP."),
            Document("power", "The AquaEdge electronics use a photovoltaic battery 24 VDC subsystem."),
        ]
    )
    hit, _ = r.search("How is MHS exposed to the LLM through MCP?", k=1)[0]
    assert hit.doc_id == "mhs"
