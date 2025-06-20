import os
from steg import hide_data, extract_data

def main():
    """
    Main function to run the steganography application via command line.
    Allows user to choose between hiding and extracting data.
    """
    print("\n--- Steganography Tool ---")
    print("1. Hide data in an image")
    print("2. Extract data from an image")
    print("3. Exit")

    choice = input("Enter your choice (1, 2, or 3): ").strip()

    # Define paths relative to the script's location
    # Assumes 'images' folder is in the same directory as main.py
    current_dir = os.path.dirname(__file__)
    images_dir = os.path.join(current_dir, "images")

    if not os.path.exists(images_dir):
        os.makedirs(images_dir) # Create images folder if it doesn't exist
        print(f"Created '{images_dir}' folder. Please place your cover image inside it.")
        return # Exit if folder just created, user needs to add image

    if choice == '1':
        print("\n--- Hide Data ---")
        cover_image_name = input("Enter the name of the cover image (e.g., cover_image.png): ").strip()
        cover_image_path = os.path.join(images_dir, cover_image_name)

        if not os.path.exists(cover_image_path):
            print(f"Error: Cover image '{cover_image_path}' not found. Please ensure it's in the 'images/' folder.")
            return

        secret_message = input("Enter the secret message you want to hide: ").strip()

        output_stego_image_name = input("Enter the name for the output stego-image (e.g., stego_image.png): ").strip()
        output_stego_image_path = os.path.join(images_dir, output_stego_image_name)

        # Call the hide function from steganography_core
        if hide_data(cover_image_path, secret_message, output_stego_image_path):
            print("Operation completed successfully.")
        else:
            print("Operation failed.")

    elif choice == '2':
        print("\n--- Extract Data ---")
        stego_image_name = input("Enter the name of the stego-image (e.g., stego_image.png): ").strip()
        stego_image_path = os.path.join(images_dir, stego_image_name)

        if not os.path.exists(stego_image_path):
            print(f"Error: Stego-image '{stego_image_path}' not found. Please ensure it's in the 'images/' folder.")
            return

        # Call the extract function from steganography_core
        extracted_message = extract_data(stego_image_path)

        if extracted_message is not None:
            print("\n------------------------------")
            print("Extracted Message:")
            print(extracted_message)
            print("------------------------------")
        else:
            print("Extraction operation failed or no message was found.")

    elif choice == '3':
        print("Exiting Steganography Tool. Goodbye!")
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()