import secrets
import string

def generate_password(length: int = 16) -> str:

    # Define the character sets to use
    letters = string.ascii_letters  # a-z, A-Z
    digits = string.digits          # 0-9
    special_chars = string.punctuation # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

    # Create the complete alphabet of all possible characters
    alphabet = letters + digits + special_chars

    # 1. Start by ensuring the password contains at least one of each character type
    password_list = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(special_chars)
    ]

    # 2. Fill the rest of the password length with random characters from the entire alphabet
    for _ in range(length - 4):
        password_list.append(secrets.choice(alphabet))

    # 3. Shuffle the list to ensure the character order is random
    secrets.SystemRandom().shuffle(password_list)

    # 4. Join the list back into a string
    password = "".join(password_list)

    return password