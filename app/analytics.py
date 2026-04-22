import collections
from typing import Dict, Any

class AnalyticsManager:
    def __init__(self):
        self.total_queries = 0
        self.keyword_counter = collections.Counter()
        self.slowest_query = {"question": None, "time": 0.0}

    def record_query(self, question: str, execution_time: float):
        self.total_queries += 1
        
        # Simple keyword extraction (ignoring common stop words could be added)
        words = [w.lower() for w in question.split() if len(w) > 3]
        self.keyword_counter.update(words)
        
        if execution_time > self.slowest_query["time"]:
            self.slowest_query = {"question": question, "time": execution_time}

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_queries": self.total_queries,
            "most_common_keywords": dict(self.keyword_counter.most_common(10)),
            "slowest_query": self.slowest_query if self.slowest_query["question"] else None
        }

# Global singleton for in-memory analytics tracking
analytics_manager = AnalyticsManager()
