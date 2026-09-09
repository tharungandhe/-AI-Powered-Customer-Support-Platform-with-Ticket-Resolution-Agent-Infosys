from rag.analyzer import analyze_ticket
from rag.retriever import KnowledgeRetriever
from rag.generator import build_context, generate_resolution

def run_pipeline(ticket, knowledge_base):
    print("=" * 60)
    print("AI RESOLUTION GENERATOR")
    print("=" * 60)

    analysis = analyze_ticket(ticket)
    print("\n[1] Ticket Analysis")
    print(analysis)

    retriever = KnowledgeRetriever(knowledge_base)
    results = retriever.search(analysis["query"], top_k=3)
    print("\n[2] Knowledge Base Retrieval")
    for doc in results:
        print(f"- {doc['title']} (relevance={doc['score']:.2f})")

    context = build_context(results)
    print("\n[3] Context Augmentation")
    print(context)

    resolution = generate_resolution(ticket, results)
    print("\n[4] Resolution Generation")
    print(resolution)

    return {
        "analysis": analysis,
        "documents": results,
        "resolution": resolution
    }