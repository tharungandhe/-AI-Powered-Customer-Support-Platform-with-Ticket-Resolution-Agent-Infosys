import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import functools

# =========================================================
# KNOWLEDGE BASE
# =========================================================
try:
    with open("data/knowledge_base.json", "r", encoding="utf-8") as file:
        KNOWLEDGE_BASE = json.load(file)
except FileNotFoundError:
    KNOWLEDGE_BASE = []

# =========================================================
# 1. DIAGNOSIS AGENT
# =========================================================
class DiagnosisAgent:
    def analyze(self, ticket):
        text = ticket.lower()
        
        categories = {
            "Network / VPN": ["vpn", "network", "internet", "connection", "wifi", "offline"],
            "Authentication": ["password", "login", "authentication", "access", "locked", "account"],
            "Email": ["email", "outlook", "mailbox", "spam", "inbox", "exchange"],
            "Printer": ["printer", "printing", "print", "paper", "ink", "toner"],
            "Performance": ["slow", "performance", "cpu", "memory", "lag", "freezing", "crash"]
        }
        
        best_category = "General IT Issue"
        best_score = 0
        
        for cat, keywords in categories.items():
            score = sum(1 for word in keywords if word in text)
            if score > best_score:
                best_score = score
                best_category = cat

        # Dynamic confidence based on keyword matches
        if best_score > 0:
            # Base 65%, add 15% per matched keyword, max out at 95%
            confidence = min(0.65 + (best_score * 0.15), 0.95)
        else:
            # If no keywords match, it falls to General IT with a low confidence
            confidence = 0.50

        # Determine priority based on urgency keywords in the text
        p1_keywords = ["urgent", "emergency", "critical", "down", "outage", "asap", "immediately", "broken", "client meeting", "vpn not working", "vpn is not connecting", "network down", "no internet"]
        p2_keywords = ["important", "high", "stuck", "blocker", "can't", "cannot", "failing", "timeout", "crashing", "deadline", "delay", "waiting"]
        p3_keywords = ["slow", "issue", "error", "bug", "help", "glitch", "how to", "question", "typo", "incorrect"]
        
        if any(word in text for word in p1_keywords):
            priority = "P1"
        elif any(word in text for word in p2_keywords):
            priority = "P2"
        elif any(word in text for word in p3_keywords):
            priority = "P3"
        else:
            priority = "P4"

        return {
            "category": best_category,
            "diagnosis": f"Ticket classified as {best_category}",
            "confidence": round(confidence, 2),
            "priority": priority
        }

# =========================================================
# 2. RETRIEVAL AGENT
# =========================================================
class RetrievalAgent:
    def __init__(self):
        if not KNOWLEDGE_BASE:
            self.documents = [""]
            self.matrix = None
            return

        self.documents = []
        for item in KNOWLEDGE_BASE:
            # Combine relevant fields for semantic matching
            title = item.get("title", "")
            problem = item.get("problem", "")
            symptoms = " ".join(item.get("symptoms", []))
            self.documents.append(f"{title} {problem} {symptoms}")

        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.documents)

    @functools.lru_cache(maxsize=1000)
    def search(self, query):
        if self.matrix is None or not KNOWLEDGE_BASE:
            return {"article": None, "similarity": 0.0}

        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix)[0]
        best_index = scores.argmax()
        
        return {
            "article": KNOWLEDGE_BASE[best_index],
            "similarity": float(scores[best_index])
        }

# =========================================================
# 3. RESOLUTION AGENT
# =========================================================
class ResolutionAgent:
    def generate(self, diagnosis, article):
        category = diagnosis["category"]
        
        # If we found a highly relevant article with structured solutions, use them
        if article and "solution" in article and isinstance(article["solution"], list):
            steps = article["solution"]
            
            display_category = category
            if category == "Network / VPN":
                display_category = "VPN connection"
            elif category == "General IT Issue":
                display_category = "general IT"
            else:
                display_category = category.lower()
                
            response = f"We identified your issue as a {display_category} problem.\n\nPlease follow these steps:"
            return {
                "response": response,
                "steps": steps
            }

        # Fallback to predefined steps from the PDF
        if category == "Network / VPN":
            steps = [
                "Check internet connectivity.",
                "Restart the VPN client.",
                "Verify username and password.",
                "Clear the VPN cache.",
                "Restart the computer.",
                "Check firewall and network configuration."
            ]
        elif category == "Authentication":
            steps = [
                "Open the company password portal.",
                "Select 'Forgot Password'.",
                "Verify employee identity.",
                "Create a new password.",
                "Confirm the new password.",
                "Login again."
            ]
        elif category == "Email":
            steps = [
                "Check internet connectivity.",
                "Verify mailbox storage.",
                "Restart Outlook.",
                "Remove and re-add the email account.",
                "Verify email server settings."
            ]
        else:
            steps = [
                "Restart your computer.",
                "Check for recent software updates.",
                "Clear your browser or application cache."
            ]

        display_category = category
        if category == "Network / VPN":
            display_category = "VPN connection"
        elif category == "General IT Issue":
            display_category = "general IT"
        else:
            display_category = category.lower()
            
        response = f"We identified your issue as a {display_category} problem.\n\nPlease follow these steps:"
        return {
            "response": response,
            "steps": steps
        }

# =========================================================
# 4. VALIDATION AGENT
# =========================================================
class ValidationAgent:
    def validate(self, diagnosis_confidence, retrieval_similarity, number_of_steps):
        # Weighted confidence calculation
        confidence = (
            diagnosis_confidence * 0.50
            + retrieval_similarity * 0.20
            + min(number_of_steps / 6, 1) * 0.30
        )
        
        confidence = round(confidence * 100, 2)
        
        if confidence >= 75:
            status = "AUTO_RESOLVE"
        else:
            status = "ESCALATE"
            
        return {
            "confidence": confidence,
            "status": status
        }

# =========================================================
# 5. ESCALATION AGENT
# =========================================================
class EscalationAgent:
    def should_escalate(self, validation):
        return validation["status"] == "ESCALATE"

# =========================================================
# MULTI-AGENT ORCHESTRATOR
# =========================================================
class SupportPilot:
    def __init__(self):
        self.diagnosis_agent = DiagnosisAgent()
        self.retrieval_agent = RetrievalAgent()
        self.resolution_agent = ResolutionAgent()
        self.validation_agent = ValidationAgent()
        self.escalation_agent = EscalationAgent()

    def process_ticket(self, ticket):
        # ---------------------------------------
        # STEP 1: DIAGNOSIS
        # ---------------------------------------
        diagnosis = self.diagnosis_agent.analyze(ticket)
        
        # ---------------------------------------
        # STEP 2: KNOWLEDGE RETRIEVAL
        # ---------------------------------------
        retrieval = self.retrieval_agent.search(ticket)
        
        # ---------------------------------------
        # STEP 3: RESOLUTION GENERATION
        # ---------------------------------------
        resolution = self.resolution_agent.generate(
            diagnosis,
            retrieval["article"]
        )
        
        # ---------------------------------------
        # STEP 4: VALIDATION
        # ---------------------------------------
        validation = self.validation_agent.validate(
            diagnosis["confidence"],
            retrieval["similarity"],
            len(resolution["steps"])
        )
        
        # ---------------------------------------
        # STEP 5: ESCALATION
        # ---------------------------------------
        escalation = self.escalation_agent.should_escalate(validation)
        
        return {
            "diagnosis": diagnosis,
            "retrieval": retrieval,
            "resolution": resolution,
            "validation": validation,
            "escalation": escalation
        }
