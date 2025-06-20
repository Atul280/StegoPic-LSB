from PIL import Image
import os

# Define a constant for the stop signal
# This is a sequence of characters that marks the end of the hidden message.
# It's converted to binary and appended to the message during embedding.
# The extractor looks for this signal to know when to stop reading.
STOP_SIGNAL = "#####END#####" # A longer, more unique signal is better

def to_binary(data):
    """
    Converts input data (string or bytes) into a binary string.
    Each character/byte is converted to its 8-bit binary representation.
    """
    if isinstance(data, str):
        # Convert string to binary ASCII representation
        # format(ord(char), "08b") converts a char to its ASCII int, then to 8-bit binary string
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes):
        # Convert bytes to binary
        return ''.join([format(i, "08b") for i in data])
    elif isinstance(data, int):
        # Convert single integer to 8-bit binary
        return format(data, "08b")
    else:
        raise TypeError(f"Input type {type(data)} not supported for binary conversion.")

def load_image(image_path):
    """
    Loads an image from the given path and converts it to RGB mode.
    Returns the Image object or None if an error occurs.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at '{image_path}'")
        return None
    try:
        # Open the image and ensure it's in RGB format (3 channels)
        img = Image.open(image_path).convert("RGB")
        return img
    except Exception as e:
        print(f"Error loading image '{image_path}': {e}")
        return None

def hide_data(image_path, secret_message, output_path):
    """
    Hides a secret message within a cover image using LSB substitution.
    The secret message is appended with a STOP_SIGNAL.
    """
    img = load_image(image_path)
    if img is None:
        return False

    # Convert secret message and stop signal to binary
    binary_secret_message = to_binary(secret_message) + to_binary(STOP_SIGNAL)

    # Calculate maximum embedding capacity (1 bit per R, G, B channel per pixel)
    # Each pixel has 3 color components, so 3 bits per pixel.
    max_capacity_bits = img.width * img.height * 3

    if len(binary_secret_message) > max_capacity_bits:
        print(f"Error: Message ({len(binary_secret_message)} bits) is too large for the image "
              f"({max_capacity_bits} bits capacity).")
        return False

    data_index = 0
    # Get a mutable copy of pixel data (list of (R, G, B) tuples)
    pixels = list(img.getdata())
    new_pixels = []

    for pixel in pixels:
        r, g, b = pixel
        new_r, new_g, new_b = r, g, b # Initialize with original values

        # Modify LSB of Red channel
        if data_index < len(binary_secret_message):
            # Clear the LSB (AND with 11111110 -> 0xFE) and set it to the new bit
            new_r = (r & 0xFE) | int(binary_secret_message[data_index])
            data_index += 1

        # Modify LSB of Green channel
        if data_index < len(binary_secret_message):
            new_g = (g & 0xFE) | int(binary_secret_message[data_index])
            data_index += 1

        # Modify LSB of Blue channel
        if data_index < len(binary_secret_message):
            new_b = (b & 0xFE) | int(binary_secret_message[data_index])
            data_index += 1

        new_pixels.append((new_r, new_g, new_b))

        # Optimization: If all data is embedded, we can stop modifying pixels
        # The remaining pixels will remain unchanged.
        if data_index >= len(binary_secret_message):
            # Append the rest of the original pixels
            new_pixels.extend(pixels[len(new_pixels):])
            break

    # Create a new image from the modified pixel data
    stego_img = Image.new(img.mode, img.size)
    stego_img.putdata(new_pixels)

    try:
        stego_img.save(output_path)
        print(f"Message hidden successfully! Stego-image saved to '{output_path}'")
        return True
    except Exception as e:
        print(f"Error saving stego-image to '{output_path}': {e}")
        return False

def extract_data(stego_image_path):
    """
    Extracts a hidden message from a stego-image using LSB extraction.
    It stops when the defined STOP_SIGNAL is found.
    Returns the extracted message string or None if an error occurs.
    """
    stego_img = load_image(stego_image_path)
    if stego_img is None:
        return None

    pixels = stego_img.getdata()
    extracted_binary_data = ""
    stop_signal_binary = to_binary(STOP_SIGNAL)
    stop_signal_length = len(stop_signal_binary)

    for pixel in pixels:
        r, g, b = pixel
        # Extract the LSB of each color channel
        extracted_binary_data += bin(r)[-1]
        extracted_binary_data += bin(g)[-1]
        extracted_binary_data += bin(b)[-1]

        # Check for the stop signal. We check if the last 'stop_signal_length' bits
        # of the extracted data match the stop signal.
        if len(extracted_binary_data) >= stop_signal_length and \
           extracted_binary_data[-stop_signal_length:] == stop_signal_binary:
            break # Found the stop signal, message ends here

    # Remove the stop signal from the extracted binary data
    if stop_signal_binary in extracted_binary_data:
        extracted_binary_data = extracted_binary_data[:-stop_signal_length]
    else:
        # If stop signal not found, it means either no message was hidden or it's corrupted
        print("Warning: Stop signal not found. Message might be incomplete or corrupted.")
        # Attempt to decode what was extracted anyway, but warn the user.
        # Alternatively, you could return None here if finding the signal is mandatory.

    extracted_message = ""
    try:
        # Convert binary string back to characters (8 bits per character)
        for i in range(0, len(extracted_binary_data), 8):
            byte_binary = extracted_binary_data[i:i+8]
            if len(byte_binary) == 8: # Ensure it's a complete byte
                extracted_message += chr(int(byte_binary, 2))
            else:
                # Handle cases where the last part is incomplete (shouldn't happen with stop signal)
                print(f"Warning: Incomplete byte found at end of extracted data: {byte_binary}")
    except ValueError as e:
        print(f"Error decoding binary data to text: {e}. Data might be corrupted.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during message extraction: {e}")
        return None

    return extracted_message

# Example of how you could test functions directly if needed (remove or comment out for main.py)
if __name__ == "__main__":
    print("--- Running steganography_core.py as main for testing ---")

    # Define paths (assuming 'images' folder is in the same directory as this script)
    current_dir = os.path.dirname(__file__)
    images_dir = os.path.join(current_dir, "images")
    cover_img = os.path.join(images_dir, "cover_image.png") # Make sure this file exists!
    stego_img = os.path.join(images_dir, "stego_image_test.png")
    extracted_text_file = os.path.join(images_dir, "extracted_message.txt")

    test_message = "Hello, this is a secret test message for my steganography project. It's quite long to test capacity!"

    print(f"\nAttempting to hide: '{test_message}' in '{cover_img}'")
    success_hide = hide_data(cover_img, test_message, stego_img)

    if success_hide:
        print(f"\nAttempting to extract from: '{stego_img}'")
        extracted = extract_data(stego_img)

        if extracted is not None:
            print(f"\nExtracted Message: '{extracted}'")
            if extracted == test_message:
                print("SUCCESS: Original and extracted messages match!")
            else:
                print("WARNING: Messages do NOT match. Check code or image corruption.")
        else:
            print("Extraction failed.")
    else:
        print("Hiding data failed.")

    print("\n--- Testing complete for steganography_core.py ---")