import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, "tickets.db")
    KB_PATH = os.path.join(BASE_DIR, "data", "knowledge_base.json")
    MIN_RELEVANCE_SCORE = 0.15
    TOP_K_DOCUMENTS = 3