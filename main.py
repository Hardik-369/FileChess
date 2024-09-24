import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Listbox, Scrollbar
from PIL import Image, ImageTk
import os

# Starting block size in bytes (1MB for the first block)
INITIAL_BLOCK_SIZE = 1 * 1024 * 1024  # 1MB in bytes

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography - Chessboard Data Storage")
        self.chessboard_size = 8  # 8x8 grid
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        # Initialize an 8x8 chessboard
        self.chessboard = [[None for _ in range(self.chessboard_size)] for _ in range(self.chessboard_size)]
        self.stored_data = {}  # To keep track of data stored in each block
        self.selected_block = None  # To track selected block for decoding
        
        # Track total storage
        self.total_storage = self.calculate_total_storage()
        self.used_storage = 0

        # Labels for displaying storage status
        self.storage_label = tk.Label(self.root, text=f"Used Storage: {self.used_storage / (1024 * 1024):.2f} MB / {self.total_storage / (1024 * 1024):.2f} MB")
        self.storage_label.grid(row=1, column=0)

        # Draw initial chessboard
        self.draw_chessboard()

        # Buttons
        self.upload_button = tk.Button(self.root, text="Upload File", command=self.upload_file)
        self.upload_button.grid(row=2, column=0)
        self.decode_button = tk.Button(self.root, text="Decode Block", command=self.decode_block)
        self.decode_button.grid(row=3, column=0)
        self.dashboard_button = tk.Button(self.root, text="Open Dashboard", command=self.open_dashboard)
        self.dashboard_button.grid(row=4, column=0)
    
    def draw_chessboard(self):
        """Draws an 8x8 chessboard on the canvas."""
        block_size = 50
        for row in range(self.chessboard_size):
            for col in range(self.chessboard_size):
                x1, y1 = col * block_size, row * block_size
                x2, y2 = x1 + block_size, y1 + block_size
                color = "white" if (row + col) % 2 == 0 else "black"
                self.chessboard[row][col] = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags=f"block_{row}_{col}")
                self.canvas.tag_bind(self.chessboard[row][col], '<Button-1>', lambda event, r=row, c=col: self.select_block(r, c))
    
    def select_block(self, row, col):
        """Handles the selection of a block for decoding."""
        if self.selected_block:
            # Reset the color of the previously selected block
            prev_row, prev_col = self.selected_block
            color = "white" if (prev_row + prev_col) % 2 == 0 else "black"
            self.canvas.itemconfig(self.chessboard[prev_row][prev_col], fill=color)
        
        # Highlight the selected block
        self.selected_block = (row, col)
        self.canvas.itemconfig(self.chessboard[row][col], fill="blue")
        print(f"Block selected for decoding: ({row}, {col})")
    
    def upload_file(self):
        """Handles file upload and stores data starting from block (7, 7)."""
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            total_size = len(file_data)
            print(f"File size: {total_size} bytes")
            
            # Start storing the file from block (7, 7)
            current_block = (7, 7)
            block_data = []
            block_index = self.get_block_index(current_block)  # Get the index of the starting block
            
            while total_size > 0:
                if current_block:
                    block_row, block_col = current_block
                    # Calculate how much data the current block can hold
                    block_size = self.calculate_block_size(block_index)
                    data_chunk = file_data[:block_size]
                    file_data = file_data[block_size:]  # Remove the stored chunk from the original data
                    self.store_in_block(data_chunk, block_row, block_col)
                    block_data.append(current_block)
                    total_size -= len(data_chunk)
                    block_index += 1
                    current_block = self.get_next_block(current_block)
                else:
                    break
            
            self.stored_data[tuple(block_data)] = file_path
            self.used_storage += len(data_chunk)
            self.update_storage_label()
            messagebox.showinfo("File Stored", "File stored across multiple blocks.")
    
    def store_in_block(self, data, row, col):
        """Stores file data in the specified block."""
        # This is a placeholder for actual encoding logic.
        self.canvas.itemconfig(self.chessboard[row][col], fill="green")
        print(f"Data stored in block ({row}, {col}) - {len(data)} bytes")
        
    def get_next_block(self, current_block):
        """Finds the next block to store data in, going from right to left and upwards."""
        row, col = current_block
        if col > 0:
            return row, col - 1
        elif row > 0:
            return row - 1, self.chessboard_size - 1
        else:
            return None
    
    def calculate_block_size(self, block_index):
        """Calculates how much data a given block can hold, based on the index (exponential growth)."""
        return INITIAL_BLOCK_SIZE * (2 ** block_index)
    
    def get_block_index(self, block):
        """Returns the index of a block in the chessboard, where the bottom-right block is index 0."""
        row, col = block
        # Calculate the index, starting from bottom-right and moving left and up
        return (self.chessboard_size - row - 1) * self.chessboard_size + (self.chessboard_size - col - 1)
    
    def decode_block(self):
        """Decodes and retrieves data from the selected block."""
        if not self.selected_block:
            messagebox.showwarning("No Block Selected", "Please select a block to decode.")
            return
        
        selected_row, selected_col = self.selected_block
        # Check which file contains the selected block
        for blocks, file_path in self.stored_data.items():
            if (selected_row, selected_col) in blocks:
                messagebox.showinfo("File Retrieved", f"File retrieved: {file_path}")
                return
        
        messagebox.showwarning("No Data Found", "No data found in the selected block.")
    
    def open_dashboard(self):
        """Opens a dashboard window to display stored files."""
        if not self.stored_data:
            messagebox.showinfo("No Files", "No files have been stored yet.")
            return
        
        dashboard_window = Toplevel(self.root)
        dashboard_window.title("Stored Files Dashboard")
        dashboard_window.geometry("300x300")
        
        scrollbar = Scrollbar(dashboard_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = Listbox(dashboard_window, yscrollcommand=scrollbar.set, height=12)
        for blocks, file in self.stored_data.items():
            listbox.insert(tk.END, os.path.basename(file))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        
        scrollbar.config(command=listbox.yview)
        
        def on_select_file(event):
            """Highlights blocks associated with the selected file."""
            selected_file = listbox.get(listbox.curselection())
            file_blocks = [key for key, val in self.stored_data.items() if os.path.basename(val) == selected_file]
            if file_blocks:
                self.highlight_blocks(file_blocks[0])
        
        listbox.bind('<<ListboxSelect>>', on_select_file)
        
    def highlight_blocks(self, blocks):
        """Highlights the blocks associated with the selected file."""
        # Reset all blocks to their original colors
        for row in range(self.chessboard_size):
            for col in range(self.chessboard_size):
                color = "white" if (row + col) % 2 == 0 else "black"
                self.canvas.itemconfig(self.chessboard[row][col], fill=color)
        
        # Highlight the blocks storing the selected file
        for row, col in blocks:
            self.canvas.itemconfig(self.chessboard[row][col], fill="yellow")

    def update_storage_label(self):
        """Updates the storage label with current used storage information."""
        self.storage_label.config(text=f"Used Storage: {self.used_storage / (1024 * 1024):.2f} MB / {self.total_storage / (1024 * 1024):.2f} MB")
    
    def calculate_total_storage(self):
        """Calculates total storage capacity based on block sizes."""
        total = 0
        for i in range(self.chessboard_size * self.chessboard_size):
            total += self.calculate_block_size(i)
        return total

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
