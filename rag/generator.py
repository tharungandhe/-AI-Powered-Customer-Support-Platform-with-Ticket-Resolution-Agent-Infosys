def build_context(results):
    context = ""
    for doc in results:
        context += f"SOURCE: {doc['id']}\nTITLE: {doc['title']}\nRELEVANCE: {doc['score']:.2f}\n{doc['content']}\n=============================\n"
    return context

def generate_resolution(ticket, documents):
    if not documents:
        return "No relevant knowledge-base information was found."
        
    # Only use the top (most relevant) document to keep it concise
    best_doc = documents[0]
    
    resolution = ["Recommended Resolution:"]
    step_number = 1
    
    lines = best_doc["content"].split("\n")
    for line in lines:
        line = line.strip()
        # Skip introductory and empty lines
        if not line or line.lower().startswith("problem:") or line.lower().startswith("symptoms:") or line.lower().startswith("step-by-step"):
            continue
            
        # Remove existing numbering if present
        if line[0].isdigit() and len(line) > 2 and line[1] == ".":
            cleaned = line.split(".", 1)[1].strip()
        else:
            cleaned = line
            
        resolution.append(f"{step_number}. {cleaned}")
        step_number += 1
        
        # Cap the number of steps to keep output concise (8-10 lines total)
        if step_number > 8:
            break
            
    resolution.append(f"{step_number}. If the problem persists, escalate the ticket to the appropriate team.")
    return "\n".join(resolution)