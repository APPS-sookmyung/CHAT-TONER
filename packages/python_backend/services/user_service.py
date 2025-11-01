"""
User Service - Temporary implementation for surveys functionality
"""

class UserService:
    """Temporary UserService implementation"""

    def __init__(self):
        pass

    def get_user(self, user_id: str):
        """Get user by ID - temporary implementation"""
        return {"id": user_id, "name": "Test User"}

    def create_user(self, user_data: dict):
        """Create user - temporary implementation"""
        return {"id": "temp_id", **user_data}