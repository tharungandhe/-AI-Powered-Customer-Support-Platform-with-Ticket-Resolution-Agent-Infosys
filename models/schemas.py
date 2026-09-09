from typing import TypedDict, List, Optional

class Ticket(TypedDict):
    id: str
    title: str
    description: str
    category: str
    priority: str

class Document(TypedDict):
    id: str
    title: str
    category: str
    subcategory: str
    problem: str
    symptoms: List[str]
    solution: List[str]
    severity: str
    keywords: List[str]
    score: Optional[float]