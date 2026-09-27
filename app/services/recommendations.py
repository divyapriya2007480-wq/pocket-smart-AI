# Dummy file to fix import error

class RecommendationService:
    def get_recommendations(self, *args, **kwargs):
        return []

def get_recommendations(*args, **kwargs):
    return []

def generate_recommendations(*args, **kwargs):
    return []

# This will handle any other name api.py is trying to import
def __getattr__(name):
    def dummy(*args, **kwargs):
        return []
    return dummy

recommendation_service = RecommendationService()