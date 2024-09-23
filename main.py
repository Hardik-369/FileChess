import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

# Maximum data a single block can hold (adjust based on block size, bits used, etc.)
MAX_BLOCK_DATA_SIZE = 1024 *1024  # Example size in bytes

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography - Chessboard Data Storage")
        self.chessboard_size = 8  # 8x8 grid, modify if necessary
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        
        # Initialize an 8x8 chessboard
        self.chessboard = [[None for _ in range(self.chessboard_size)] for _ in range(self.chessboard_size)]
        self.selected_block = None
        self.stored_data = {}  # To keep track of data stored in each block
        
        # Draw initial chessboard
        self.draw_chessboard()
        
        # Buttons
        self.upload_button = tk.Button(self.root, text="Upload File", command=self.upload_file)
        self.upload_button.grid(row=1, column=0)
        self.decode_button = tk.Button(self.root, text="Decode Block", command=self.decode_block)
        self.decode_button.grid(row=2, column=0)
        
    def draw_chessboard(self):
        """Draws an 8x8 chessboard on the canvas."""
        block_size = 50
        for row in range(self.chessboard_size):
            for col in range(self.chessboard_size):
                x1, y1 = col * block_size, row * block_size
                x2, y2 = x1 + block_size, y1 + block_size
                color = "white" if (row + col) % 2 == 0 else "black"
                self.chessboard[row][col] = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags=f"block_{row}_{col}")
                self.canvas.tag_bind(f"block_{row}_{col}", '<Button-1>', lambda e, r=row, c=col: self.on_block_click(r, c))

    def on_block_click(self, row, col):
        """Handles block click for selection or decoding."""
        self.selected_block = (row, col)
        print(f"Block selected: {self.selected_block}")
        
    def upload_file(self):
        """Handles file upload and stores data in the selected block(s)."""
        if not self.selected_block:
            messagebox.showwarning("No Block Selected", "Please select a block to store the file.")
            return
        
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            total_size = len(file_data)
            print(f"File size: {total_size} bytes")
            
            # Calculate how many blocks are needed
            blocks_needed = (total_size // MAX_BLOCK_DATA_SIZE) + 1
            print(f"Blocks needed: {blocks_needed}")
            
            # Store file in the selected block and consecutive blocks
            current_block = self.selected_block
            block_data = []
            for i in range(blocks_needed):
                if current_block:
                    block_row, block_col = current_block
                    data_chunk = file_data[i * MAX_BLOCK_DATA_SIZE:(i + 1) * MAX_BLOCK_DATA_SIZE]
                    self.store_in_block(data_chunk, block_row, block_col)
                    block_data.append(current_block)
                    current_block = self.get_next_block(current_block)
                else:
                    break
            
            self.stored_data[tuple(block_data)] = file_path
            messagebox.showinfo("File Stored", f"File stored across {blocks_needed} blocks.")
    
    def store_in_block(self, data, row, col):
        """Stores file data in the specified block."""
        # For now, this is a placeholder for actual encoding logic (e.g., LSB encoding).
        self.canvas.itemconfig(self.chessboard[row][col], fill="green")
        print(f"Data stored in block ({row}, {col})")
        
    def get_next_block(self, current_block):
        """Finds the next block to store data in."""
        row, col = current_block
        if col < self.chessboard_size - 1:
            return row, col + 1
        elif row < self.chessboard_size - 1:
            return row + 1, 0
        else:
            return None
    
    def decode_block(self):
        """Decodes and retrieves data from the selected block."""
        if not self.selected_block:
            messagebox.showwarning("No Block Selected", "Please select a block to decode data.")
            return
        
        file_blocks = [key for key, val in self.stored_data.items() if self.selected_block in key]
        if file_blocks:
            file_path = self.stored_data[file_blocks[0]]
            print(f"Decoded data from block {self.selected_block}: {file_path}")
            messagebox.showinfo("File Retrieved", f"File retrieved: {file_path}")
        else:
            messagebox.showwarning("No Data Found", "No data found in the selected block.")
            
# Run the application
root = tk.Tk()
app = SteganographyApp(root)
root.mainloop()
