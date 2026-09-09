def analyze_ticket(ticket):
    text = (ticket.get("title", "") + " " + ticket.get("description", "")).lower()
    keywords = [kw for kw in ["vpn", "network", "firewall", "authentication", "timeout", "connection"] if kw in text]
    
    return {
        "ticket_id": ticket.get("id", "T-NEW"),
        "category": ticket.get("category", "General"),
        "priority": ticket.get("priority", "P2"),
        "keywords": keywords,
        "query": text
    }