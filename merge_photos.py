from PIL import Image
import sys

def combine_images(image1_path, image2_path, output_path='combined_image.jpg'):
    # Load the two images
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    # Ensure both images are the same size
    if image1.size != image2.size:
        raise ValueError("Both images must have the same dimensions")

    # Get the dimensions of the images
    width, height = image1.size

    # Crop the left half of image1
    left_half = image1.crop((0, 0, width // 2, height))

    # Crop the right half of image2
    right_half = image2.crop((width // 2, 0, width, height))

    # Create a new blank image with the same dimensions
    combined_image = Image.new('RGB', (width, height))

    # Paste the left half of image1 and the right half of image2 into the new image
    combined_image.paste(left_half, (0, 0))
    combined_image.paste(right_half, (width // 2, 0))

    # Save the combined image
    combined_image.save(output_path)
    print(f"Combined image saved as {output_path}")

    # Optionally, show the combined image
    combined_image.show()

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python combine_images.py <image1_path> <image2_path>")
        sys.exit(1)

    # Get the image paths from command-line arguments
    image1_path = sys.argv[1]
    image2_path = sys.argv[2]

    # Call the function to combine the images
    combine_images(image1_path, image2_path)