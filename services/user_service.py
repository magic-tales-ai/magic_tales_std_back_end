import logging
import uuid
from utils.log_utils import get_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
# Get a logger instance for this module
logger = get_logger(__name__)

def check_validation_code(validation_code: int, user_validation_code: int):
    """
    Check the validation code

    Args:
        validation_code (int): Validation code to check
        user_validation_code (int): Real validation code

    Returns:
        bool: True if the codes are the same
    """
    if user_validation_code != validation_code:
        logger.error(f"Validation code {validation_code} is not valid")
        return False
    
    return True

def generate_random_string():
    random_string = str(uuid.uuid4())
    random_string = random_string.lower()
    random_string = random_string.replace("-", "")
    return random_string[0:6] + "_TMP"