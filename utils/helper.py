""" 
This script handles the extra functions needed for the endpoint from the action of the Rasa project. 
All functions required to handle the business logic externally to the Rasa project should be included here.

"""

from typing import Text
import re


def validate_ecuadorian_id(id_number: Text) -> bool:
    """
    Validate an Ecuadorian national identification number (cédula).
    
    Args:
    id_number (str): The identification number to validate.
    
    Returns:
    bool: True if the id_number is valid, False otherwise.
    """

    id_number = (id_number or '').replace('-', '', 1)

    if len(id_number) != 10 or not id_number.isdigit():
        return False
    
    # Extract province code and digits
    province_code = int(id_number[:2])
    if province_code < 1 or province_code > 24:
        return False
    
    # Extract the last digit for checksum validation
    last_digit = int(id_number[-1])
    
    # Weights for validation
    weights = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    
    # Compute checksum
    total_sum = 0
    for i in range(9):
        digit = int(id_number[i])
        product = digit * weights[i]
        if product > 9:
            product -= 9
        total_sum += product
    
    # Compute check digit
    check_digit = (10 - (total_sum % 10)) % 10
    
    return check_digit == last_digit


def validate_ecuadorian_phone(phone_number: str) -> bool:
    """
    Validate an Ecuadorian cellular phone number.
    
    Args:
    phone_number (str): The phone number to validate.
    
    Returns:
    bool: True if the phone number is valid, False otherwise.
    """
    
    # Ecuadorian phone numbers should be 10 digits long
    if len(phone_number) != 10 or not phone_number.isdigit():
        return False
    
    # The first digit should be 0, and the second digit should be 9
    if phone_number[:2] != "09":
        return False
    
    return True


def validate_email_string(email: str) -> bool:
    """
    Validate if the provided string is a valid email address.
    
    Args:
    email (str): The email address to validate.
    
    Returns:
    bool: True if valid email, False otherwise.
    """
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None
