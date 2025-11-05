replacement_table = (
    (4, 10, 9, 2, 13, 8, 0, 14, 6, 11, 1, 12, 7, 15, 5, 3),
    (14, 11, 4, 12, 6, 13, 15, 10, 2, 3, 8, 1, 0, 7, 5, 9),
    (5, 8, 1, 13, 10, 3, 4, 2, 14, 15, 12, 7, 6, 0, 9, 11),
    (7, 13, 10, 1, 0, 8, 9, 15, 14, 4, 6, 12, 11, 2, 5, 3),
    (6, 12, 7, 1, 5, 15, 13, 8, 4, 10, 9, 14, 0, 3, 11, 2),
    (4, 11, 10, 0, 7, 2, 1, 13, 3, 6, 8, 5, 9, 12, 15, 14),
    (13, 11, 4, 1, 3, 15, 5, 9, 0, 10, 14, 7, 6, 8, 2, 12),
    (1, 15, 13, 0, 5, 7, 10, 4, 9, 2, 3, 14, 6, 11, 8, 12),
)

def get_out(in_right: int, key: int) -> int:
    out_score = 0
    temp_val = (in_right + key) % (1 << 32)

    for i in range(8):
        phonetic = (temp_val >> (4 * i)) & 0b1111
        out_score |= (replacement_table[i][phonetic] << (4 * i))

    out_score = ((out_score >> 21) | (out_score << 11)) & 0xFFFFFFFF

    return out_score

def crypt_operation(in_left: int, in_right: int, key: int) -> tuple[int, int]:
    out_left = in_right
    out_right = in_left ^ get_out(in_right, key)

    return out_left, out_right

class Gost:
    def __init__(self):
        self.key: list[int] = [0] * 8

    def set_key(self, key: int):
        for i in range(8):
            self.key[i] = (key >> (32 * i)) & 0xFFFFFFFF

        print("Key:", self.key)

    def _process_block(self, left: int, right: int, encrypt: bool) -> tuple[int, int]:
        if encrypt:
            for q in range(24):
                left, right = crypt_operation(left, right, self.key[q % 8])
            for q in range(8):
                left, right = crypt_operation(left, right, self.key[7 - q])
        else:
            for q in range(8):
                left, right = crypt_operation(left, right, self.key[q])
            for q in range(24):
                left, right = crypt_operation(left, right, self.key[7 - (q % 8)])
        
        return right, left
    
    def encrypt_block(self, block: int) -> int:
        left_part = (block >> 32) & 0xFFFFFFFF
        right_part = block & 0xFFFFFFFF

        new_left_part, new_right_part = self._process_block(left_part, right_part, encrypt=True)

        return (new_left_part << 32) | new_right_part

    def decrypt_block(self, block: int) -> int:
        left_part = (block >> 32) & 0xFFFFFFFF
        right_part = block & 0xFFFFFFFF

        new_left_part, new_right_part = self._process_block(left_part, right_part, encrypt=False)

        return (new_left_part << 32) | new_right_part

    def encrypt(self, text: str) -> bytes:
        data = text.encode('utf-8')
        
        block_size = 8  
        padding_len = block_size - (len(data) % block_size)
        data += bytes([padding_len] * padding_len)

        encrypted_text = bytearray()
        
        for i in range(0, len(data), 8):
            block = int.from_bytes(data[i:i+8], 'big')
            encrypted_block = self.encrypt_block(block)
            encrypted_text.extend(encrypted_block.to_bytes(8, 'big'))

        return bytes(encrypted_text)

    def decrypt(self, encrypted_data: bytes) -> str:
        decrypted_text = bytearray()

        for i in range(0, len(encrypted_data), 8):
            block = int.from_bytes(encrypted_data[i:i+8], 'big')
            decrypted_block = self.decrypt_block(block)
            decrypted_text.extend(decrypted_block.to_bytes(8, 'big'))

        padding_len = decrypted_text[-1]
        decrypted_text = decrypted_text[:-padding_len]

        return decrypted_text.decode('utf-8')

    def hash_function(self, text: str) -> int:
        data = text.encode('utf-8')
        
        block_size = 8
        padding_len = block_size - (len(data) % block_size)
        data += bytes([padding_len] * padding_len)

        hash_left = 0
        hash_right = 0

        for i in range(0, len(data), 8):
            block_int = int.from_bytes(data[i:i+8], 'big')
            
            block_left = (block_int >> 32) & 0xFFFFFFFF
            block_right = block_int & 0xFFFFFFFF
            
            block_left ^= hash_left   
            block_right ^= hash_right
            
            for q in range(16):  
                block_left, block_right = crypt_operation(
                    block_left, block_right, self.key[q % 8]
                )
            
            hash_left = block_left
            hash_right = block_right
        
        return (hash_left << 32) | hash_right

    def check_hash(self, check_str: str, hash: int) -> bool:
        if self.hash_function(check_str) == hash:
            return True
        
        return False

def main():
    gost = Gost()
    
    key_input = input("Введите ключ (256 бит в hex, 64 символа) или нажмите Enter для ключа по умолчанию: ").strip()
    
    if key_input:
        try:
            key = int(key_input, 16)
            gost.set_key(key)
        except ValueError:
            print("Неверный формат ключа! Используется ключ по умолчанию.")
            gost.set_key(0x1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff)
    else:
        gost.set_key(0x1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff)
    
    while True:
        print("-" * 30)

        print("Выберите операцию:")
        print("1. Зашифровать файл")
        print("2. Расшифровать файл")
        print("3. Вычислить хэш")
        print("4. Выход")

        choice = input("Ваш выбор (1-4): ").strip()

        if choice == '1':
            print("-" * 30)

            input_file = input("Введите путь к файлу для шифрования: ").strip()
            output_file = input("Введите путь для сохранения зашифрованного файла (или Enter для [имя].encrypted): ").strip()
            
            if not output_file:
                output_file = input_file + ".encrypted"
            
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    plaintext = f.read()
                
                encrypted = gost.encrypt(plaintext)
                
                with open(output_file, 'wb') as f:
                    f.write(encrypted)
                
                print(f"  Файл успешно зашифрован: {output_file}")
                
            except FileNotFoundError:
                print(f"  Ошибка: файл '{input_file}' не найден!")
            except Exception as e:
                print(f"  Ошибка при шифровании: {e}")
        
        elif choice == '2':
            print("-" * 30)

            input_file = input("Введите путь к зашифрованному файлу: ").strip()
            output_file = input("Введите путь для сохранения расшифрованного файла (или Enter для [имя].decrypted): ").strip()
            
            if not output_file:
                if input_file.endswith('.encrypted'):
                    output_file = input_file[:-10] + ".decrypted"
                else:
                    output_file = input_file + ".decrypted"
            
            try:
                with open(input_file, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypted = gost.decrypt(encrypted_data)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(decrypted)
                
                print(f"  Файл успешно расшифрован: {output_file}")
                
            except FileNotFoundError:
                print(f"  Ошибка: файл '{input_file}' не найден!")
            except Exception as e:
                print(f"  Ошибка при дешифровании: {e}")
        
        elif choice == '3':
            print("-" * 30)
            
            text = input("Введите текст для хэширования: ")
            hash_value = gost.hash_function(text)

            print(f" Хэш (десятичный): {hash_value}")
            print(f" Хэш (hex): {hex(hash_value)}")
                
            verify = input("Проверить хэш? (y/[n]): ").strip().lower()
            if verify == 'y':
                check_text = input("Введите текст для проверки: ")
                if gost.check_hash(check_text, hash_value):
                    print("  Хэш совпадает!")
                else:
                    print("  Хэш не совпадает!")
        
        elif choice == '4':
            break
        
        else:
            print("Неверный выбор! Пожалуйста, выберите 1-4.")

if __name__ == "__main__":
    main()
