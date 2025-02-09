import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageEnhance, ImageTk, ImageOps
import logging
from datetime import datetime

class GIFtoHexConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("GIF to Hex Converter")
        self.root.configure(bg="#0d1b2a")  # Dark futuristic background

        # Styling
        style = ttk.Style()
        style.configure("TLabel", foreground="cyan", background="#0d1b2a", font=("Arial", 10, "bold"))
        style.configure("TButton", foreground="black", background="cyan", font=("Arial", 10, "bold"), padding=5)
        style.configure("TEntry", font=("Arial", 10), padding=5)
        style.configure("Horizontal.TScale", background="#1b263b")

        # Input File
        ttk.Label(root, text="Input GIF:").grid(row=0, column=0, padx=5, pady=5)
        self.input_path = ttk.Entry(root, width=40)
        self.input_path.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(root, text="Browse", command=self.load_input_files).grid(row=0, column=2, padx=5, pady=5)

        # Output File
        ttk.Label(root, text="Output File:").grid(row=1, column=0, padx=5, pady=5)
        self.output_path = ttk.Entry(root, width=40)
        self.output_path.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(root, text="Browse", command=self.load_output_file).grid(row=1, column=2, padx=5, pady=5)

        # Width & Height
        ttk.Label(root, text="Width:").grid(row=2, column=0, padx=5, pady=5)
        self.width_entry = ttk.Entry(root, width=10)
        self.width_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.width_entry.insert(0, "64")
        self.width_entry.bind("<KeyRelease>", lambda e: self.update_preview())

        ttk.Label(root, text="Height:").grid(row=3, column=0, padx=5, pady=5)
        self.height_entry = ttk.Entry(root, width=10)
        self.height_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.height_entry.insert(0, "64")
        self.height_entry.bind("<KeyRelease>", lambda e: self.update_preview())

        # Invert Checkbox
        self.invert_var = tk.IntVar()
        ttk.Checkbutton(root, text="Invert Colors", variable=self.invert_var, command=self.update_preview).grid(row=4, column=1, sticky="w")

        # Gamma Correction
        ttk.Label(root, text="Gamma:").grid(row=5, column=0, padx=5, pady=5)
        self.gamma_value = tk.DoubleVar(value=128)
        self.gamma_entry = ttk.Entry(root, width=10, textvariable=self.gamma_value)
        self.gamma_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.gamma_entry.bind("<KeyRelease>", lambda e: self.update_preview())

        # Gamma Slider
        self.gamma_slider = ttk.Scale(root, from_=10, to=255, orient="horizontal", variable=self.gamma_value, command=self.update_preview)
        self.gamma_slider.grid(row=5, column=2, padx=5, pady=5, sticky="we")

        # Add to __init__
        ttk.Label(root, text="Frame Delay (ms):").grid(row=6, column=0, padx=5, pady=5)
        self.delay_entry = ttk.Entry(root, width=10)
        self.delay_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        self.delay_entry.insert(0, "30")

        # Convert Button
        ttk.Button(root, text="Convert", command=self.process_gif).grid(row=6, column=1, pady=10)

        # Preview Label
        self.preview_label = ttk.Label(root, text="Preview:")
        self.preview_label.grid(row=7, column=0, columnspan=3, pady=5)

        # Canvas for Image Preview
        self.canvas = tk.Canvas(root, width=100, height=100, bg="gray")
        self.canvas.grid(row=8, column=0, columnspan=3, pady=5)

        self.original_frame = None  # Store original GIF frame

        # Add Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=9, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # Add Log Display
        self.log_text = tk.Text(root, height=5, width=50, bg="#1b263b", fg="cyan")
        self.log_text.grid(row=10, column=0, columnspan=3, padx=5, pady=5)

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Configure logging to both file and GUI."""
        log_file = f"gif_converter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def log_message(self, message, level="info"):
        """Add message to log display and file."""
        if level == "info":
            self.logger.info(message)
        elif level == "error":
            self.logger.error(message)
        
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    # Change load_input_file to load_input_files
    def load_input_files(self):
        files = filedialog.askopenfilenames(
            title="Select GIF files",
            filetypes=[("GIF Files", "*.gif")]
        )
        if files:
            self.input_path.delete(0, tk.END)
            self.input_path.insert(0, ";".join(files))
            self.load_preview(files[0])



    def load_output_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".h", filetypes=[("Header Files", "*.h")])
        if file_path:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, file_path)

    def load_preview(self, gif_path):
        """Load the first frame of GIF for preview."""
        gif = Image.open(gif_path)
        gif.seek(0)  # First frame
        self.original_frame = gif.convert("L")  # Convert to grayscale
        self.update_preview()

    def update_preview(self, *_):
        """Update the preview based on user input."""
        if not self.original_frame:
            return
        
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            gamma = self.gamma_value.get()
            invert = bool(self.invert_var.get())

            img = self.original_frame.resize((width, height))
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(gamma / 128.0)
            
            # Convert to binary before inversion
            img = img.convert('1')
            
            # Apply inversion after binary conversion
            if invert:
                img = ImageOps.invert(img)

            img_tk = ImageTk.PhotoImage(img)
            self.canvas.config(width=width, height=height)
            self.canvas.create_image(width//2, height//2, image=img_tk, anchor=tk.CENTER)
            self.canvas.image = img_tk  

        except ValueError:
            pass  

    def process_gif(self):
        try:
            input_files = self.input_path.get().split(";") 
            output_file = self.output_path.get()
            
            # Get parameters from GUI inputs
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            gamma = self.gamma_value.get()
            invert = bool(self.invert_var.get())
            
            if not input_files or not output_file:
                messagebox.showerror("Error", "Please select input and output files.")
                return

            self.log_message("Starting GIF conversion process...")
            total_files = len(input_files)
            
            # Reset progress bar
            self.progress_var.set(0)
            
            # Write header once at the start
            with open(output_file, 'w') as f:
                f.write("#ifndef __GENERATED_GIFS_H__\n")
                f.write("#define __GENERATED_GIFS_H__\n\n")
                f.write("#include <Arduino.h>\n")
                f.write("#include <Adafruit_GFX.h>\n")
                f.write("#include <Adafruit_SSD1306.h>\n")
                f.write("#include <Wire.h>\n\n")
                f.write("#define SCREEN_WIDTH 128\n")
                f.write("#define SCREEN_HEIGHT 64\n")
                f.write("#define OLED_RESET -1\n")
                f.write("#define WHITE 1\n")
                f.write("#define OLED_ADDR 0x3C\n\n")
                f.write("extern Adafruit_SSD1306 display;\n\n")

                # Process each GIF file
                for index, gif_path in enumerate(input_files):
                    self.log_message(f"Processing {os.path.basename(gif_path)}...")
                    frames = self.gif_to_frames(gif_path)
                    base_name = os.path.splitext(os.path.basename(gif_path))[0]
                    
                    # Write frame arrays
                    for i, frame in enumerate(frames):
                        hex_array = self.image_to_hex_array(frame, width, height, gamma, invert)
                        f.write(f"const PROGMEM unsigned char {base_name}_frame{i+1}[] = {{{hex_array}}};\n")
                    
                    # Write pointer array
                    f.write(f"\nconst PROGMEM unsigned char* const {base_name}_frames[] = {{")
                    f.write(", ".join([f"{base_name}_frame{i+1}" for i in range(len(frames))]))
                    f.write("};\n\n")
                    
                    # Write dimensions and frame count
                    f.write(f"#define {base_name.upper()}_WIDTH {width}\n")
                    f.write(f"#define {base_name.upper()}_HEIGHT {height}\n")
                    f.write(f"#define {base_name.upper()}_FRAMES {len(frames)}\n\n")
                    
                    # Add frame access function
                    f.write(f"const unsigned char* {base_name}(int frame){{return {base_name}_frames[frame];}}\n\n")
                    
                    # Add display function with frame_delay parameter
                    f.write(f"void display_{base_name}(uint16_t frame_delay = 30) {{\n")
                    f.write("    display.clearDisplay();\n")
                    f.write(f"    for (int i = 0; i < {base_name.upper()}_FRAMES; i++) {{\n")
                    f.write(f"        display.drawBitmap(32, 0, {base_name}(i), {base_name.upper()}_WIDTH, {base_name.upper()}_HEIGHT, WHITE);\n")
                    f.write("        display.display();\n")
                    f.write("        delay(frame_delay);\n")
                    f.write("        display.clearDisplay();\n")
                    f.write("    }\n")
                    f.write("}\n\n")
                
                    # Update progress bar
                    progress = ((index + 1) / total_files) * 100
                    self.progress_var.set(progress)
                    self.root.update_idletasks()

                # Close header guard at the very end
                f.write("#endif // __GENERATED_GIFS_H__\n")

            self.log_message("Conversion completed successfully!")
            messagebox.showinfo("Success", "GIF conversion completed successfully!")
                    
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            self.log_message(error_msg, "error")
            messagebox.showerror("Error", error_msg)

    def gif_to_frames(self, gif_path, num_frames=28):
        """Extract frames from the GIF."""
        gif = Image.open(gif_path)
        frames = []
        for i in range(min(num_frames, gif.n_frames)):
            gif.seek(i)
            frames.append(gif.copy())
        return frames

    def image_to_hex_array(self, image, width, height, gamma, invert):
        """Convert image to a hex array."""
        img = image.convert('L')
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(gamma / 128.0)
        img = img.resize((width, height))
        
        # Convert to binary image before inversion
        img = img.convert('1')

        # Apply inversion after binary conversion if needed
        if invert:
            img = ImageOps.invert(img)

        pixel_data = list(img.getdata())
        hex_array = []
        for i in range(0, len(pixel_data), 8):
            byte = 0
            for j in range(8):
                if i + j < len(pixel_data):
                    # Changed the condition to match the preview
                    byte = (byte << 1) | (1 if pixel_data[i + j] > 128 else 0)
            hex_array.append(f'0x{byte:02x}')
        return ', '.join(hex_array)

    def generate_bitmap_arrays_from_gif(self, gif_path, output_file, width, height, gamma, invert):
        """Generate and save the hex array."""
        base_name = os.path.splitext(os.path.basename(gif_path))[0]
        frames = self.gif_to_frames(gif_path)
        with open(output_file, 'a') as f:  # Changed to append mode
            if os.path.getsize(output_file) == 0:  # Only write headers for first GIF
                f.write("#ifndef __GENERATED_GIFS_H__\n")
                f.write("#define __GENERATED_GIFS_H__\n\n")
                f.write("#include <Arduino.h>\n")
                f.write("#include <Adafruit_GFX.h>\n")
                f.write("#include <Adafruit_SSD1306.h>\n")
                f.write("#include <Wire.h>\n\n")
                f.write("#define SCREEN_WIDTH 128\n")
                f.write("#define SCREEN_HEIGHT 64\n")
                f.write("#define OLED_RESET -1\n")
                f.write("#define WHITE 1\n")
                f.write("extern Adafruit_SSD1306 display;\n\n")
            
            # Write individual frame arrays with PROGMEM
            for i, frame in enumerate(frames):
                hex_array = self.image_to_hex_array(frame, width, height, gamma, invert)
                f.write(f"const PROGMEM unsigned char {base_name}_frame{i+1}[] = {{{hex_array}}};\n")
            
            # Write pointer array in a single line with PROGMEM
            f.write(f"\nconst PROGMEM unsigned char* const {base_name}_frames[] = {{")
            f.write(", ".join([f"{base_name}_frame{i+1}" for i in range(len(frames))]))
            f.write("};\n\n")
            
            # Write array dimensions and frame count
            f.write(f"#define {base_name.upper()}_WIDTH {width}\n")
            f.write(f"#define {base_name.upper()}_HEIGHT {height}\n")
            f.write(f"#define {base_name.upper()}_FRAMES {len(frames)}\n\n")
            
            # Add function to access frames
            f.write(f"const unsigned char* {base_name}(int frame){{return {base_name}_frames[frame];}}\n\n")
            
            # Add after writing frame arrays
            f.write(f"void display_{base_name}() {{\n")
            f.write("    display.clearDisplay();\n")
            f.write(f"    for (int i = 0; i < {base_name.upper()}_FRAMES; i++) {{\n")
            f.write(f"        display.drawBitmap(32, 0, {base_name}(i), {base_name.upper()}_WIDTH, {base_name.upper()}_HEIGHT, WHITE);\n")
            f.write("        display.display();\n")
            f.write("        delay(30);\n")
            f.write("        display.clearDisplay();\n")
            f.write("    }\n")
            f.write("}\n\n")
            
            if os.path.getsize(output_file) == 0:  # Add endif only for first GIF
                f.write("#endif\n")

       

if __name__ == "__main__":
    root = tk.Tk()
    app = GIFtoHexConverter(root)
    root.mainloop()
