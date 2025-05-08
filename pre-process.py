from PIL import ImageEnhance, Image, ImageOps
import sys
import os

folder_path = sys.argv[1]
output_path = sys.argv[2]

# Create the output folder if it doesn't exist
os.makedirs(output_path, exist_ok=True)

#traverse the structure of the inputfolder
for dirpath, dirnames, filenames in os.walk(folder_path):
    #recreate the input folder structure in the output folder
    relative_path = os.path.relpath(dirpath, folder_path)
    output_dir = os.path.join(output_path, relative_path)
    os.makedirs(output_dir, exist_ok=True)

for dirpath, dirnames, filenames in os.walk(folder_path):
    relative_path = os.path.relpath(dirpath, folder_path)
    output_dir = os.path.join(output_path, relative_path)

    for image_name in filenames:
        print(f"Found file: {image_name}")  # Debugging print statement
        if image_name.lower().endswith(('.jpg', '.jpeg')):
            input_image_path = os.path.join(dirpath, image_name)
            if os.path.isfile(input_image_path):
                try:
                    print(f'Processing {image_name} in {relative_path}')
                    with Image.open(input_image_path) as im:

                        # Convert image to grayscale
                        im = ImageOps.grayscale(im)

                        # Enhance the contrast
                        enhancer = ImageEnhance.Contrast(im)
                        contrast = enhancer.enhance(2)  # Adjust contrast, 2 for doubling contrast

                        # Double the size of the image
                        new_size = (contrast.width * 2, contrast.height * 2)
                        contrast = contrast.resize(new_size)

                        # Split the base name and extension from the image file name
                        base_name = os.path.splitext(image_name)[0]

                        # Append '_contrast.png' to the base name to ensure it has the .png extension
                        new_file_name = base_name + '_contrast.png'

                        # Combine the new file name with the output directory to get the full path
                        output_image_path = os.path.join(output_dir, new_file_name)

                        # Save the contrast-enhanced image to the output path
                        contrast.save(output_image_path)

                except Exception as e:
                    print(f"Error processing {image_name}: {e}")