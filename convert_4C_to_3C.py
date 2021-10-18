from PIL import Image
import os
 
path = "./for_spa/data/test/small/norain/"  
all_images = os.listdir(path)
# print(all_images)
 
for image in all_images:
    image_path = os.path.join(path, image)
    try: 
        img = Image.open(image_path) # Open the image
    except:
        continue
    print(image_path)
    img = img.convert("RGB") # 4 channels are converted to RGB three channels
    #save_path = path
    img.save(image_path + "out.png")
