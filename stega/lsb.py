import numpy as np
import cv2
import os

def get_image(filename: str) -> list:
    img = cv2.imread(filename)

    if img is None:
        raise FileNotFoundError

    area = img.shape
    res_list = []
    row = area[0]
    col = area[1]

    for i in range(row):
        for j in range(col):
            pix_b = img[i][j][0]
            pix_g = img[i][j][1]
            pix_r = img[i][j][2]

            res_list.append([i, j, pix_r, pix_g, pix_b])

    return res_list

def put_data_in_pixel(index: int, six_bin_arr: str, pixels: list) -> None:
    pixels[index][2] &= 252
    pixels[index][3] &= 252
    pixels[index][4] &= 252

    pixels[index][2] |= int(six_bin_arr[0:2], 2)
    pixels[index][3] |= int(six_bin_arr[2:4], 2)
    pixels[index][4] |= int(six_bin_arr[4:6], 2)

def export_data_from_pixel(index: int, pixels: list) -> str:
    res = ""

    first_local = bin(pixels[index][2] & 3)[2:]
    first_local = (2 - len(first_local))*"0" + first_local
    res += first_local

    second_local = bin(pixels[index][3] & 3)[2:]
    second_local = (2 - len(second_local))*"0" + second_local
    res += second_local

    third_local = bin(pixels[index][4] & 3)[2:]
    third_local = (2 - len(third_local))*"0" + third_local
    res += third_local

    return res

def make_picture(picture: list) -> np.ndarray:
    img1 = []
    img2 = []

    row = picture[-1][0] + 1
    col = picture[-1][1] + 1

    for i in range(row):
        for j in range(col):
            index = i*col + j
            img1 += [[np.uint8(picture[index][4]), np.uint8(picture[index][3]), np.uint8(picture[index][2])]]

        img2 += [img1]
        img1 = []

    return np.array(img2)

def encrypt(message: str, pixels: list) -> None:
    message_bytes = message.encode('utf-8')
    mes_len = len(message_bytes) 
    
    mes_len_bin = bin(mes_len)[2:]
    mes_len_bin = (24 - len(mes_len_bin))*"0" + mes_len_bin
    pixel_index = 0

    for i in range(0, 24, 6):
        put_data_in_pixel(pixel_index, mes_len_bin[i: i + 6], pixels)
        pixel_index += 1

    mes_in_bin = ""
    for byte in message_bytes:
        bin_str = bin(byte)[2:]
        bin_str = (8 - len(bin_str))*"0" + bin_str
        mes_in_bin += bin_str
    
    if len(mes_in_bin) % 6 != 0:
        mes_in_bin += (6 - (len(mes_in_bin) % 6))*"0"

    for i in range(0, len(mes_in_bin), 6):
        put_data_in_pixel(pixel_index, mes_in_bin[i: i + 6], pixels)
        pixel_index += 1

def decrypt(pixels: list) -> str:
    msg_len_bin = ""
    secret_msg_in_bin = ""

    for ind in range(4):
        msg_len_bin += export_data_from_pixel(ind, pixels)

    msg_len = int(msg_len_bin, 2) 
    
    if msg_len > 1000000 or msg_len == 0:
        raise ValueError(f"Invalid message length: {msg_len}. Image may not contain encrypted data or was corrupted.")
    
    num_bits = msg_len * 8 
    num_pixels = (num_bits + 5) // 6

    if 4 + num_pixels > len(pixels):
        raise ValueError(f"Not enough pixels to decrypt. Need {4 + num_pixels}, but only have {len(pixels)}.")
    
    for i in range(4, 4 + num_pixels):
        secret_msg_in_bin += export_data_from_pixel(i, pixels)

    secret_msg_in_bin = secret_msg_in_bin[:num_bits]
    
    message_bytes = bytearray()
    for j in range(0, num_bits, 8):
        byte_value = int(secret_msg_in_bin[j: j + 8], 2)
        message_bytes.append(byte_value)
    
    secret_msg = message_bytes.decode('utf-8')

    return secret_msg

def main():
    print("You can:")
    print("1. Encrypt")
    print("2. Decrypt")
    print("3. Exit")

    while True:
        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            picture_name = input("Enter Picture Name: ")
            message = input("Enter Message: ")

            try:
                pixels = get_image(filename=picture_name)
                encrypt(message=message, pixels=pixels)
                encrypted_image = make_picture(pixels)

                name_without_ext = os.path.splitext(picture_name)[0]
                write_name = 'encrypted_' + name_without_ext + '.bmp'
                cv2.imwrite(write_name, encrypted_image)
                
                print(f"  Message encrypted and saved to: {write_name}")
            except FileNotFoundError:
                print("File Not Found")
            except Exception as e:
                print(e)
        elif choice == "2":
            picture_name = input("Enter Picture Name: ")
            
            try:
                pixels = get_image(filename=picture_name)
                secret_msg = decrypt(pixels=pixels)
                
                output_name = 'decrypted_message.txt'
                with open(output_name, 'w', encoding='utf-8') as f:
                    f.write(secret_msg)
                
                print(f"Message decrypted and saved to {output_name}")
                print(f"Decrypted message: {secret_msg}")
            except FileNotFoundError:
                print("File Not Found")
            except Exception as e:
                print(f"Error during decryption: {e}")
        elif choice == "3":
            break
        else:
            print("Invalid choice")

if __name__ == '__main__':
    main()
