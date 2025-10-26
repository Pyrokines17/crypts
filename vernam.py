import random

def generate_random_key(plaintext_length: int) -> str:
    generated_key = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(plaintext_length))
    return generated_key

def encrypt_text(plaintext: str, key: str) -> str:
    encrypted_text = ''.join(chr(ord(p) ^ ord(k)) for p, k in zip(plaintext, key))
    return encrypted_text

def decrypt_text(ciphertext: str, key: str) -> str:
    decrypted_text = ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(ciphertext, key))
    return decrypted_text

if __name__ == "__main__":
    text_for_encryption = input("Enter text for encryption: ")
    print("Plaintext:", text_for_encryption)

    generated_key = generate_random_key(len(text_for_encryption))
    print("Key:", generated_key)

    encrypted_text = encrypt_text(text_for_encryption, generated_key)
    print("Ciphertext:", encrypted_text)

    decrypted_text = decrypt_text(encrypted_text, generated_key)
    print("Decrypted Text:", decrypted_text)
