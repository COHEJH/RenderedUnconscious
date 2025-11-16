import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

class Canvas():
    def __init__(self, dimX: int, dimY: int):
        self.dimX: int = dimX
        self.dimY: int = dimY
        
        # Create window
        self.root = tk.Tk()
        self.root.title("RenderedUnconscious - Video Output")
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=dimX, 
            height=dimY, 
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Create numpy array for pixel buffer (RGB)
        self.buffer = np.zeros((dimY, dimX, 3), dtype=np.uint8)
        
        # Image placeholder
        self.image_id = None
        self.photo_image = None
    
    def setPixel(self, xCoord: int, yCoord: int, pixelColour: np.ndarray[3]):
        # Convert coordinates (center origin to top-left origin)
        x = xCoord + self.dimX // 2
        y = self.dimY // 2 - yCoord
        
        # Check bounds
        if 0 <= x < self.dimX and 0 <= y < self.dimY:
            self.buffer[y, x] = tuple(pixelColour)
    
    def clearBuffer(self, color: tuple[int, int, int] = (0, 0, 0)):
        self.buffer[:] = color
    
    def updateCanvas(self):
        img = Image.fromarray(self.buffer, 'RGB')
        self.photo_image = ImageTk.PhotoImage(image=img)
        
        if self.image_id is None:
            self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        else:
            self.canvas.itemconfig(self.image_id, image=self.photo_image)
        
        self.root.update()
    
    def finishRendering(self):
        # Keep screen open
        self.root.mainloop()