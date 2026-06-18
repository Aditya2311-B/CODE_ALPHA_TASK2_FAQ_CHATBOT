# Import the User model from centralized database configuration
# to avoid circular import issues in Flask Blueprints.
from database import User

# This file can be used to add authentication-specific model hooks
# or methods if needed in the future.
