import cv2
import os
import errno
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image, ImageSequence 
    
FOLDER_PATH = os.path.join(os.path.dirname(__file__),'')
CAPTURE_SQUARE_DIM = 300

# this function draws a square on the camera that will be the eventual GIF
def capture_image():
    pixelDepth = int(input("Give me the square pixel depth for GIF ex.32 will be 32x32 grainy GIF: "))
    print("opening camera.")
    
    # default camera
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        print("Error: can't find camera.")
        return

    # Screen Square dimensions
    frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    rect_width, rect_height = CAPTURE_SQUARE_DIM, CAPTURE_SQUARE_DIM
    rect_x = (frame_width - rect_width) // 2
    rect_y = (frame_height - rect_height) // 2

    # count the number of images to be used in GIF, incase the folder contains images not for GIF
    image_num = 0
    start_capture = False
    
    print("\nGo to CV2 window and press 'c' to start capturing for GIF or 'q' to exit.\n")
    caption = "Press 'c' to start capturing for GIF or 'q' to exit."
    while True:
        # number the images
        saved_image_path = FOLDER_PATH  + "pngHolder\\" + str(image_num) + '.png'
        ret, frame = capture.read()
        
        if not ret:
            print("Error: Could not read frame.")
            break
        
        # Draw a rectangle in the center of the screen
        cv2.rectangle(frame, (rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height), (0, 255, 0), 2)
        cropped_image = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]
        
        # instructions for user camera control are on the screen and updated
        font = cv2.FONT_HERSHEY_SIMPLEX
        origin = (10, 20)
        fontScale = .5
        color = (255, 0, 0) # Blue
        thickness = 1
        frame = cv2.putText(frame, caption,
                            origin, font, fontScale, color, thickness, cv2.LINE_AA)
        
        # Display the live feed 
        cv2.imshow("Retro TV", frame)
        
        # Capture keyboard input
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('c'):
            start_capture = True

        if(start_capture):
            caption = "CAPTURING! press 'q' to finish."
            cv2.imwrite(saved_image_path, cropped_image)
            
            # resize image to give it a retro effect dictated by user ex a 32x32 pixel look ect...
            image = Image.open(saved_image_path)
            resized_image = image.resize((pixelDepth, pixelDepth))
            
            # Save the and count number of resized_image
            resized_image.save(saved_image_path)
            image_num += 1

        # If 'q' is pressed, exit the loop
        if key == ord('q'):
            print("Exiting...")
            break

    print("Creating GIF")
    capture.release()
    cv2.destroyAllWindows()
    return image_num

if __name__ == "__main__":
    try:
        os.mkdir(FOLDER_PATH  + "pngHolder\\")
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass

    gifName = input("Give me the name of your GIF to create: ")
    gifRate = int(input("Give me the frame rate of your desired GIF in secounds: "))
    finalSize = int(input("How large should the final square GIF be ex: 60 will be 60x60 pixels: "))
    num_images = capture_image()
    
    
    
    # # Get all files in the folder
    # png_files = os.listdir(FOLDER_PATH)
    
    tempFiles = []
    for i in range(num_images):
        img = FOLDER_PATH + "pngHolder\\" + str(i) +".png"
        
        # blow up or shrink final GIF to user specifications
        image = Image.open(img)
        resized_image = image.resize((finalSize, finalSize),resample=Image.NEAREST)
        resized_image.save(img)
        tempFiles.append(img)
    
    # Open the images
    frames = [Image.open(png) for png in tempFiles]
    
    print("Finishing up...")
    
    # Make and save GIF from images
    if(len(frames) != 0):
        frames[0].save(
            FOLDER_PATH + gifName + ".gif",
            save_all = True,
            append_images = frames[1:],
            duration = gifRate*10,  # frame duration in milliseconds
            loop=0                  # should loop for num times (0 = infinite)
        )
        
        print("GIF created successfully!")
        
        # use matplot to show GIF
        gif = Image.open(FOLDER_PATH + gifName + ".gif")
        # get GIF's frames
        frames = [frame.copy() for frame in ImageSequence.Iterator(gif)]
        
        fig, ax = plt.subplots()
        # simple function for animation
        displayedImg = ax.imshow(frames[0])        
        def update(frame):
            displayedImg.set_array(frame)
            return [displayedImg]
        
        # animate with help from pillow using gif.info.get() to get gifs metadata
        animate = animation.FuncAnimation(fig, update, frames, interval = gif.info.get("duration", 0))        
        plt.show()
    else:
        print("No images to make a GIF exiting...")
