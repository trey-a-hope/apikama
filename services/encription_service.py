from base64 import b64encode, b64decode
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EncryptionService:
    _instance = None
    _key = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Get key from environment variable
            env_key = os.getenv("ENCRYPTION_KEY")
            if not env_key:
                raise ValueError("ENCRYPTION_KEY environment variable not set")
            cls._key = env_key.encode()
        return cls._instance

    def encrypt_server_string(self, server_string: str) -> str:
        try:
            # Simple XOR encryption with the key
            key_bytes = self._key
            data_bytes = server_string.encode()
            # Ensure the key is long enough
            key_repeated = key_bytes * (1 + len(data_bytes) // len(key_bytes))
            encrypted = bytes(a ^ b for a, b in zip(data_bytes, key_repeated))
            # Add padding info
            result = b64encode(encrypted).decode("utf-8")
            print(f"Encrypted result: {result}")  # Debug print
            return result
        except Exception as e:
            print(f"Encryption error: {str(e)}")  # Debug print
            raise

    def decrypt_server_string(self, encrypted_string: str) -> str:
        try:
            print(f"Attempting to decrypt: {encrypted_string}")  # Debug print
            # Add padding if necessary
            padding_needed = len(encrypted_string) % 4
            if padding_needed:
                encrypted_string += "=" * (4 - padding_needed)

            encrypted_bytes = b64decode(encrypted_string)
            key_bytes = self._key
            key_repeated = key_bytes * (1 + len(encrypted_bytes) // len(key_bytes))
            decrypted = bytes(a ^ b for a, b in zip(encrypted_bytes, key_repeated))
            result = decrypted.decode("utf-8")
            print(f"Decrypted result: {result}")  # Debug print
            return result
        except Exception as e:
            print(f"Decryption error: {str(e)}")  # Debug print
            raise ValueError(f"Failed to decrypt server string: {str(e)}")


def get_encryption_deps() -> EncryptionService:
    return EncryptionService()
