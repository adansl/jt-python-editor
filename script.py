import pygame
import pygame_gui
import numpy as np
import json
import os
from PIL import Image
import io

class PixelArtEditor:
    def __init__(self):
        pygame.init()
        self.screen_width = 1500
        self.screen_height = 1200
        
        # Add RESIZABLE flag to the display mode
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("Pixel Art Editor")
        self.clock = pygame.time.Clock()
        
        self.bg_color = "#2D2D2D"  # Dark gray background
        # Initialize pygame_gui with the theme
        self.manager = pygame_gui.UIManager((self.screen_width, self.screen_height), 'theme.json')
        
        # Set a darker background color for the application
     
        # Define the color palette with names
        self.color_names = {
            '#000000': 'Black',
            '#FF0000': 'Red',
            '#00FF00': 'Green',
            '#FFFF00': 'Yellow',
            '#0000FF': 'Blue',
            '#FF00FF': 'Magenta',
            '#00FFFF': 'Cyan',
            '#FFFFFF': 'White'
        }
        
        # Define the color palette with binary codes
        self.color_map = {
            '000': '#000000',  # Black
            '001': '#FF0000',  # Red
            '010': '#00FF00',  # Green
            '011': '#FFFF00',  # Yellow
            '100': '#0000FF',  # Blue
            '101': '#FF00FF',  # Magenta
            '110': '#00FFFF',  # Cyan
            '111': '#FFFFFF'   # White
        }
        
        # Reverse color map for binary representation
        self.reverse_color_map = {v: k for k, v in self.color_map.items()}
        
        # Global variables
        self.selected_format = "v2"  # Only v2 format now
        self.selected_size = "16x64"  # Only 16x64 resolution
        self.start_color = "#FFFFFF"
        self.right_mouse_btn_color = "#000000"
        self.initial_pixel_size = 20
        self.current_mode = "static"
        self.bg_color = "#b2b2b2"
        self.jt_file_name = "image.jt"
        self.image_file_name = "coolLED_img.png"
        self.animation_file_name = "coolLED_ani.png"
        
        # Animation variables
        self.is_playing = False
        self.current_frame_index = 0
        self.total_frames = 1
        self.speed = 255
        self.mode = 1
        self.stay_time = 3
        self.graffiti_type = 1
        self.ani_type = 1
        self.delays = 250
        self.data_type = 1  # default to static
        
        # Initialize canvas
        self.canvas_width = int(self.selected_size.split('x')[1])
        self.canvas_height = int(self.selected_size.split('x')[0])
        self.pixel_size = self.initial_pixel_size
        
        # Color system
        self.selected_color = self.start_color
        self.right_mouse_color = self.right_mouse_btn_color
        
        # Mouse button tracking
        self.mouse_btn_global = -1  # -1 = none, 0 = left, 2 = right
        
        # Binary arrays for color representation
        self.red_binary_array = []
        self.green_binary_array = []
        self.blue_binary_array = []
        
        # Create UI elements
        self.create_ui()
        
        # Initialize pixel arrays
        self.initialize_pixel_arrays()
            
        # Make sure animation controls visibility is set correctly at startup
        self.update_animation_controls_visibility()
        
    def initialize_pixel_arrays(self):
        # Create pixel arrays for frames
        self.pixel_array_frames = []
        self.pixel_array_frames.append(self.create_pixel_array(self.canvas_height, self.canvas_width, self.right_mouse_color))
        
    def create_pixel_array(self, height, width, color):
        # Create a new pixel array with the specified color
        return np.full((height, width), color, dtype=object)
        
    def create_ui(self):
        # Canvas area
        self.canvas_rect = pygame.Rect(20, 20,
                                    self.canvas_width * self.pixel_size,
                                    self.canvas_height * self.pixel_size)
        # UI Controls
        button_width = 100
        button_height = 30
        dropdown_width = 120
        dropdown_height = 30
        
        # Define button_y BEFORE using it
        button_y = 180  # Adjusted starting position
        
        # Format dropdown (restored)
        self.format_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["v1", "v2"],
            starting_option=self.selected_format,
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, 20),
                                    (dropdown_width, dropdown_height)),
            manager=self.manager
        )
        
        # Mode dropdown (moved down)
        self.mode_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["static", "animation"],
            starting_option=self.current_mode,
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, 60),
                                    (dropdown_width, dropdown_height)),
            manager=self.manager
        )
        
        # Color dropdown with names (moved down)
        color_options = [self.color_names[hex_code] for hex_code in self.color_map.values()]
        self.color_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=color_options,
            starting_option=self.color_names[self.selected_color],
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, 100),
                                    (dropdown_width, dropdown_height)),
            manager=self.manager
        )
        
        # Pixel size slider (moved down)
        self.pixel_size_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, 140),
                                    (dropdown_width, 20)),
            start_value=self.pixel_size,
            value_range=(5, 30),
            manager=self.manager
        )
        
        # Buttons
        button_y = 180  # Adjusted starting position
        
        # Debug toggle button (now button_y is defined)
        self.debug_toggle_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width, button_height)),
            text="Toggle Debug",
            manager=self.manager
        )
        
        button_y += 40
        self.toggle_animation_mode_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width, button_height)),
            text="Toggle Animation",
            manager=self.manager
        )
        
        # Paint bucket button
        self.paint_bucket_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width, button_height)),
            text="Fill All",
            manager=self.manager
        )
        
        button_y += 40
        # Right mouse paint bucket button
        self.rmb_paint_bucket_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width, button_height)),
            text="Fill RMB",
            manager=self.manager
        )
        
        button_y += 40
        # Add swap button (moved up in the UI order)
        self.swap_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width, button_height)),
            text="Swap Black",
            manager=self.manager
        )
        print("Swap button created at position:", self.canvas_rect.right + 20, button_y)  # Debug output
        
        button_y += 40
        # Load button
        self.load_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width, button_height)),
            text="Load",
            manager=self.manager
        )
        
        button_y += 40
        # Save button
        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width, button_height)),
            text="Save",
            manager=self.manager
        )
        
        button_y += 40
        # Add filename input field with better positioning
        button_y += 40
        self.filename_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width, button_height)),
            text="Filename:",
            manager=self.manager
        )
        
        button_y += 30
        self.filename_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width + 50, button_height)),
            manager=self.manager
        )
        self.filename_input.set_text("image")  # Default filename
        
        # Add more space after the filename input
        button_y += 50
        
        # Add text input label
        self.text_input_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width, button_height)),
            text="Text to Draw:",
            manager=self.manager
        )
        
        button_y += 30
        # Add text input field
        self.text_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width + 50, button_height)),
            manager=self.manager
        )
        
        # Add font size control
        button_y += 40
        self.font_size_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width, button_height)),
            text="Font Size:",
            manager=self.manager
        )
        
        button_y += 30
        self.font_size_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (dropdown_width, 20)),
            start_value=8,
            value_range=(6, 14),
            manager=self.manager
        )
        
        # Add letter spacing control
        button_y += 40
        self.letter_spacing_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width, button_height)),
            text="Letter Spacing:",
            manager=self.manager
        )
        
        button_y += 30
        self.letter_spacing_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (dropdown_width, 20)),
            start_value=1,
            value_range=(0, 5),
            manager=self.manager
        )
        
        # Add draw text button
        button_y += 40
        self.draw_text_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.canvas_rect.right + 20, button_y),
                                    (button_width, button_height)),
            text="Draw Text",
            manager=self.manager
        )
        
        # Animation controls (initially hidden)
        animation_controls_y = self.canvas_rect.bottom + 10
        # Make sure animation controls are within the visible screen area
        if animation_controls_y + 100 > self.screen_height:
            animation_controls_y = self.screen_height - 150
        
        self.animation_controls_rect = pygame.Rect(20, animation_controls_y,
                                                self.canvas_rect.width, 40)
        
        # Back button
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.animation_controls_rect.left, self.animation_controls_rect.top),
                                    (40, 40)),
            text="<",
            manager=self.manager
        )
        
        # Play/Pause button
        self.play_pause_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.animation_controls_rect.left + 50, self.animation_controls_rect.top),
                                    (40, 40)),
            text="PLAY",
            manager=self.manager
        )
        
        # Forward button
        self.forward_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.animation_controls_rect.left + 100, self.animation_controls_rect.top),
                                    (40, 40)),
            text=">",
            manager=self.manager
        )
        
        # Plus button (add frame)
        self.plus_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.animation_controls_rect.left + 150, self.animation_controls_rect.top),
                                    (40, 40)),
            text="+",
            manager=self.manager
        )
        
        # Minus button (delete frame)
        self.minus_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.animation_controls_rect.left + 200, self.animation_controls_rect.top),
                                    (40, 40)),
            text="-",
            manager=self.manager
        )
        
        # Clone frame button
        self.clone_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.animation_controls_rect.left + 250, self.animation_controls_rect.top),
                                    (40, 40)),
            text="CP",
            manager=self.manager
        )
        
        # Directional buttons
        self.up_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.animation_controls_rect.left + 300, self.animation_controls_rect.top),
                                    (40, 40)),
            text="UP",
            manager=self.manager
        )
        
        # Status message display
        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, self.screen_height - 40),
                                    (self.screen_width - 40, 30)),
            text="WHAT",
            manager=self.manager
        )
        
        self.left_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.animation_controls_rect.left + 300 - 50, self.animation_controls_rect.top + 50),
                                    (40, 40)),
            text="LEFT",
            manager=self.manager
        )
        
        self.down_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.animation_controls_rect.left + 300, self.animation_controls_rect.top + 50),
                                    (40, 40)),
            text="DOWN",
            manager=self.manager
        )
        
        self.right_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.animation_controls_rect.left + 300 + 50, self.animation_controls_rect.top + 50),
                                    (40, 40)),
            text="RIGHT",
            manager=self.manager
        )
        
        # Delay input for animation
        self.delay_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.animation_controls_rect.left + 400, self.animation_controls_rect.top),
                                    (50, 40)),
            text="Delay:",
            manager=self.manager
        )
        
        self.delay_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.animation_controls_rect.left + 450, self.animation_controls_rect.top),
                                    (50, 40)),
            manager=self.manager
        )
        self.delay_input.set_text(str(self.delays))
        
        # Frame counter
        self.frame_counter = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.animation_controls_rect.left + 510, self.animation_controls_rect.top),
                                    (100, 40)),
            text="Frame: 1/1",
            manager=self.manager
        )
        
        # Text display for binary representation (initially hidden)
        self.text_display = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((20, self.animation_controls_rect.bottom + 10),
                                    (self.screen_width - 40, 150)),
            html_text="",
            manager=self.manager
        )
        self.text_display.visible = False  # Hide by default
        
        # Set visibility of animation controls based on mode
        self.update_animation_controls_visibility()
        
    def draw_text_on_canvas(self):
        # Get the text from the input field
        text = self.text_input.get_text()
        if not text:
            self.status_label.set_text("Please enter text to draw")
            return
        
        print(f"Drawing text: '{text}'")  # Debug output
        
        # Get font size and letter spacing
        try:
            font_size = int(self.font_size_slider.get_current_value())
        except:
            font_size = 8
        
        try:
            letter_spacing = int(self.letter_spacing_slider.get_current_value())
        except:
            letter_spacing = 1
        
        # Use pygame's font rendering directly
        pygame.font.init()
        
        # Try to load a font
        try:
            font = pygame.font.SysFont("Arial", font_size)
            print("Using Arial font")
        except:
            try:
                font = pygame.font.SysFont("Courier", font_size)
                print("Using Courier font")
            except:
                font = pygame.font.Font(None, font_size)
                print("Using default font")
        
        # Render the text to a surface
        text_surface = font.render(text, True, (255, 255, 255), (0, 0, 0))
        
        # Calculate position to center the text
        position = ((self.canvas_width - text_surface.get_width()) // 2, 
                    (self.canvas_height - text_surface.get_height()) // 2)
        
        # Ensure position is not negative
        position = (max(0, position[0]), max(0, position[1]))
        
        print(f"Text dimensions: {text_surface.get_width()}x{text_surface.get_height()}")
        print(f"Text position: {position}")
        
        # Create a temporary surface the size of the canvas
        temp_surface = pygame.Surface((self.canvas_width, self.canvas_height))
        temp_surface.fill((0, 0, 0))  # Fill with black
        
        # Draw the text onto the temporary surface
        temp_surface.blit(text_surface, position)
        
        # Save debug image
        pygame.image.save(temp_surface, "debug_text_render.png")
        print("Saved debug image to debug_text_render.png")
        
        # Get the current frame
        current_frame = self.pixel_array_frames[self.current_frame_index]
        
        # Count how many pixels we change
        pixels_changed = 0
        
        # Transfer pixels from the surface to the pixel array
        for y in range(self.canvas_height):
            for x in range(self.canvas_width):
                # Check if we're within bounds
                if x < temp_surface.get_width() and y < temp_surface.get_height():
                    # Get the pixel color from the pygame surface
                    pixel_color = temp_surface.get_at((x, y))
                    
                    # Check if the pixel is not black (part of the text)
                    # Use a very low threshold to catch anti-aliased edges
                    if pixel_color[0] > 20 or pixel_color[1] > 20 or pixel_color[2] > 20:
                        # Set the pixel in your canvas to the selected color
                        current_frame[y][x] = self.selected_color
                        pixels_changed += 1
        
        # Update the display
        self.draw_pixels()
        self.update_text_display()
        self.status_label.set_text(f"Drew text: '{text}' ({pixels_changed} pixels)")
    

        
    def swap_black_pixels(self):
            # Debug output
        print(f"Selected color: {self.selected_color}")
        print(f"Selected color from dropdown: {self.color_dropdown.selected_option}")
        # Swap black pixels with selected color and non-black pixels with black
        current_frame = self.pixel_array_frames[self.current_frame_index]
        
        # Get the currently selected color (directly use self.selected_color)
        selected_color = self.selected_color
        selected_color_name = self.color_names.get(selected_color.upper(), "Unknown")
        
        # Iterate through all pixels
        for row_idx in range(self.canvas_height):
            for col_idx in range(self.canvas_width):
                # Get current pixel color (convert to uppercase for comparison)
                current_color = current_frame[row_idx][col_idx].upper()
                
                # If the pixel is black, change to selected color
                if current_color == '#000000':
                    current_frame[row_idx][col_idx] = selected_color
                # If the pixel is not black, change to black
                else:
                    current_frame[row_idx][col_idx] = '#000000'
        
        # Update the display
        self.draw_pixels()
        self.update_text_display()
        
        # Show a status message
        self.status_label.set_text(f"Swapped black pixels with {selected_color_name} and non-black pixels to black")
    
    def update_animation_controls_visibility(self):
        # Show/hide animation controls based on current mode
        visible = self.current_mode == "animation"
        
        # Print debug info
        print(f"Setting animation controls visibility to: {visible}")
        print(f"Current mode is: {self.current_mode}")
        
        # Force visibility for all animation controls
        try:
            self.back_button.visible = visible
            self.play_pause_button.visible = visible
            self.forward_button.visible = visible
            self.plus_button.visible = visible
            self.minus_button.visible = visible
            self.clone_button.visible = visible
            self.up_button.visible = visible
            self.left_button.visible = visible
            self.down_button.visible = visible
            self.right_button.visible = visible
            self.delay_label.visible = visible
            self.delay_input.visible = visible
            self.frame_counter.visible = visible
            
            # Print the visibility state of one control to verify
            print(f"Back button visibility is now: {self.back_button.visible}")
        except Exception as e:
            print(f"Error setting visibility: {e}")
    
    def handle_mode_change(self):
        # Handle mode change (static/animation)
        self.is_playing = False
        pygame.time.set_timer(pygame.USEREVENT, 0)  # Stop any running animation
        
        # Extract the mode from the dropdown selection
        # If it's a tuple, take the first element
        selected_option = self.mode_dropdown.selected_option
        if isinstance(selected_option, tuple):
            self.current_mode = selected_option[0]
        else:
            self.current_mode = selected_option
        
        self.data_type = 0 if self.current_mode == "animation" else 1
        
        # Update animation controls visibility
        self.update_animation_controls_visibility()
        
        # Debug output to confirm mode change
        print(f"Mode changed to: {self.current_mode}")
        print(f"Animation controls should be: {'visible' if self.current_mode == 'animation' else 'hidden'}")
    
    def handle_paint_bucket(self):
        # Fill all pixels with selected color
        # Find the hex code for the selected color name
        selected_color_name = self.color_dropdown.selected_option
        selected_hex = next((hex_code for hex_code, name in self.color_names.items() if name == selected_color_name), self.start_color)
        self.selected_color = selected_hex
        
        self.pixel_array_frames[self.current_frame_index] = self.create_pixel_array(
            self.canvas_height, self.canvas_width, self.selected_color)
        self.draw_pixels()
        self.update_text_display()
    
    def handle_rmb_paint_bucket(self):
        # Fill all pixels with right mouse button color
        self.pixel_array_frames[self.current_frame_index] = self.create_pixel_array(
            self.canvas_height, self.canvas_width, self.right_mouse_color)
        self.draw_pixels()
        self.update_text_display()
    
    def update_frame_display(self):
        # Update frame counter display
        c_txt = f"{self.current_frame_index + 1:02d}"
        t_txt = f"{self.total_frames:02d}"
        self.frame_counter.set_text(f"Frame: {c_txt}/{t_txt}")
        
        # Update delay value from input field
        try:
            self.delays = int(self.delay_input.get_text())
        except ValueError:
            self.delays = 250  # Default if invalid
    
    def toggle_pixel(self, row, col):
        # Toggle pixel color based on mouse button
        if self.mouse_btn_global == 0:  # Left mouse button
            # Use the already selected color (no need to look it up again)
            self.pixel_array_frames[self.current_frame_index][row][col] = self.selected_color
            self.draw_pixels()
            self.update_text_display()
        elif self.mouse_btn_global == 2:  # Right mouse button
            self.pixel_array_frames[self.current_frame_index][row][col] = self.right_mouse_color
            self.draw_pixels()
            self.update_text_display()

    def get_binary_component(self, color, position):
        # Get binary component for a specific color
        color = color.upper()
        color_map = {
            '#000000': '000',  # Black
            '#FF0000': '001',  # Red
            '#00FF00': '010',  # Green
            '#FFFF00': '011',  # Yellow
            '#0000FF': '100',  # Blue
            '#FF00FF': '101',  # Magenta
            '#00FFFF': '110',  # Cyan
            '#FFFFFF': '111'   # White
        }
        current_color = color_map.get(color, '000')
        # Extract the specific bit at position
        binary_value = current_color[position] if position < len(current_color) else '0'
        return binary_value

    def update_text_display(self):
        # Update text display with binary representation
        pixel_array = self.pixel_array_frames[self.current_frame_index]
        
        red_binary_array = []
        green_binary_array = []
        blue_binary_array = []
        
        row_length = len(pixel_array[0])
        
        for j in range(row_length):
            red_binary = ''
            green_binary = ''
            blue_binary = ''
            
            for i in range(len(pixel_array)):
                color = pixel_array[i][j]
                red_value = self.get_binary_component(color, 2)
                green_value = self.get_binary_component(color, 1)
                blue_value = self.get_binary_component(color, 0)
                
                red_binary += red_value
                green_binary += green_value
                blue_binary += blue_value
                
                # Group every 8 bits and convert to decimal
                if len(red_binary) == 8:
                    red_binary_array.append(int(red_binary, 2))
                    red_binary = ''
                
                if len(green_binary) == 8:
                    green_binary_array.append(int(green_binary, 2))
                    green_binary = ''
                
                if len(blue_binary) == 8:
                    blue_binary_array.append(int(blue_binary, 2))
                    blue_binary = ''
        
        # Add any remaining bits
        if red_binary:
            red_binary = red_binary.ljust(8, '0')
            red_binary_array.append(int(red_binary, 2))
        
        if green_binary:
            green_binary = green_binary.ljust(8, '0')
            green_binary_array.append(int(green_binary, 2))
        
        if blue_binary:
            blue_binary = blue_binary.ljust(8, '0')
            blue_binary_array.append(int(blue_binary, 2))
        
        # Update text display
        red_decimal_text = f"Red: [{', '.join(map(str, red_binary_array))}]"
        green_decimal_text = f"Green: [{', '.join(map(str, green_binary_array))}]"
        blue_decimal_text = f"Blue: [{', '.join(map(str, blue_binary_array))}]"
        
        self.text_display.html_text = f"{red_decimal_text}<br><br>{green_decimal_text}<br><br>{blue_decimal_text}"
        self.text_display.rebuild()

    def draw_pixels(self):
        # Draw pixels on the canvas
        self.screen.fill(pygame.Color(self.bg_color))
        
        # Draw the current color indicator
        color_indicator_rect = pygame.Rect(
            self.canvas_rect.right + 20 + 130,
            100,  # Adjusted to match the color dropdown position
            30,
            30
        )
        # Make sure to use the current selected color
        pygame.draw.rect(self.screen, pygame.Color(self.selected_color), color_indicator_rect)
        pygame.draw.rect(self.screen, pygame.Color('#000000'), color_indicator_rect, 1)  # Border
        
        # Draw the right mouse button color indicator
        rmb_color_indicator_rect = pygame.Rect(
            self.canvas_rect.right + 20 + 130,
            140,  # Adjusted to match the slider position
            30,
            30
        )
        pygame.draw.rect(self.screen, pygame.Color(self.right_mouse_color), rmb_color_indicator_rect)
        pygame.draw.rect(self.screen, pygame.Color('#000000'), rmb_color_indicator_rect, 1)  # Border
        
        # Draw the pixel grid
        pixel_array = self.pixel_array_frames[self.current_frame_index]
        for row_idx, row in enumerate(pixel_array):
            for col_idx, color in enumerate(row):
                rect = pygame.Rect(
                    self.canvas_rect.left + col_idx * self.pixel_size,
                    self.canvas_rect.top + row_idx * self.pixel_size,
                    self.pixel_size,
                    self.pixel_size
                )
                pygame.draw.rect(self.screen, pygame.Color(color), rect)
                pygame.draw.rect(self.screen, pygame.Color('#000000'), rect, 1)  # Border

    # Animation functions
    def add_frame(self):
        # Add a new frame
        new_pixel_array = self.create_pixel_array(self.canvas_height, self.canvas_width, self.right_mouse_color)
        self.pixel_array_frames.append(new_pixel_array)
        self.total_frames = len(self.pixel_array_frames)
        self.current_frame_index = self.total_frames - 1  # Set current frame to the newly added frame
        self.update_frame_display()
        self.draw_pixels()
        self.update_text_display()

    def delete_frame(self):
        # Delete the current frame if there's more than one
        if self.total_frames > 1:
            # Remove the current frame
            self.pixel_array_frames.pop(self.current_frame_index)
            self.total_frames = len(self.pixel_array_frames)
            
            # Adjust current frame index if needed
            if self.current_frame_index >= self.total_frames:
                self.current_frame_index = self.total_frames - 1
            
            self.update_frame_display()
            self.draw_pixels()
            self.update_text_display()

    def copy_current_frame_to_end(self):
        # Clone the current frame and add it to the end
        if self.pixel_array_frames and self.current_frame_index >= 0:
            current_frame = self.pixel_array_frames[self.current_frame_index]
            new_frame = np.copy(current_frame)
            self.pixel_array_frames.append(new_frame)
            
            self.total_frames = len(self.pixel_array_frames)
            self.current_frame_index = self.total_frames - 1  # Set current frame to the newly added frame
            
            self.update_frame_display()
            self.draw_pixels()
            self.update_text_display()

    def shift_image_up(self):
        # Shift image up by moving the first row to the end
        if self.pixel_array_frames and self.current_frame_index >= 0:
            current_frame = self.pixel_array_frames[self.current_frame_index]
            first_row = current_frame[0].copy()
            current_frame[:-1] = current_frame[1:]
            current_frame[-1] = first_row
            
            self.draw_pixels()
            self.update_text_display()

    def shift_image_down(self):
        # Shift image down by moving the last row to the beginning
        if self.pixel_array_frames and self.current_frame_index >= 0:
            current_frame = self.pixel_array_frames[self.current_frame_index]
            last_row = current_frame[-1].copy()
            current_frame[1:] = current_frame[:-1]
            current_frame[0] = last_row
            
            self.draw_pixels()
            self.update_text_display()

    def shift_image_left(self):
        # Shift image left by moving the first column to the end
        if self.pixel_array_frames and self.current_frame_index >= 0:
            current_frame = self.pixel_array_frames[self.current_frame_index]
            for row in current_frame:
                first_element = row[0]
                row[:-1] = row[1:]
                row[-1] = first_element
            
            self.draw_pixels()
            self.update_text_display()

    def shift_image_right(self):
        # Shift image right by moving the last column to the beginning
        if self.pixel_array_frames and self.current_frame_index >= 0:
            current_frame = self.pixel_array_frames[self.current_frame_index]
            for row in current_frame:
                last_element = row[-1]
                row[1:] = row[:-1]
                row[0] = last_element
            
            self.draw_pixels()
            self.update_text_display()

    def play_animation(self):
        # Start or stop animation playback
        self.is_playing = not self.is_playing
        if self.is_playing:
            pygame.time.set_timer(pygame.USEREVENT, self.delays)
            # Update button text to show pause symbol
            self.play_pause_button.set_text("Pause")
        else:
            # Stop the timer
            pygame.time.set_timer(pygame.USEREVENT, 0)
            # Update button text to show play symbol
            self.play_pause_button.set_text("Play")

    def next_frame(self):
        # Go to next frame in animation
        if self.total_frames > 1:
            self.current_frame_index = (self.current_frame_index + 1) % self.total_frames
            self.update_frame_display()
            self.draw_pixels()
            self.update_text_display()

    def prev_frame(self):
        # Go to previous frame in animation
        if self.total_frames > 1:
            self.current_frame_index = (self.current_frame_index - 1) % self.total_frames
            self.update_frame_display()
            self.draw_pixels()
            self.update_text_display()
            
    def save_jt_file(self):
        # Save as JT file format
        filename = self.filename_input.get_text()
        if not filename:
            filename = "image"
        if not filename.endswith(".jt"):
            filename += ".jt"
        
        # Create the data structure based on format and mode
        if self.current_mode == "static":
            # Static image
            data = [{
                "dataType": 1,
                "data": {
                    "speed": 255,
                    "mode": 1,
                    "pixelHeight": self.canvas_height,
                    "stayTime": 3,
                    "graffitiData": self.get_binary_data_for_jt(),
                    "pixelWidth": self.canvas_width,
                    "graffitiType": 1
                }
            }]
        else:
            # Animation
            data = [{
                "dataType": 0,
                "data": {
                    "pixelWidth": self.canvas_width,
                    "aniData": self.get_binary_data_for_jt(True),
                    "frameNum": self.total_frames,
                    "delays": self.delays,
                    "aniType": 1,
                    "pixelHeight": self.canvas_height
                }
            }]
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f)
            # Show a success message
            self.status_label.set_text(f"File saved successfully as {filename}")
            print(f"File saved successfully as {filename}")
        except Exception as e:
            # Show an error message
            self.status_label.set_text(f"Error saving file: {e}")
            print(f"Error saving file: {e}")

    def get_binary_data_for_jt(self, is_animation=False, is_v1=False):
        # Convert pixel data to binary format for JT file
        binary_data = []
        frames_to_process = self.pixel_array_frames if is_animation else [self.pixel_array_frames[self.current_frame_index]]
        
        if is_v1:
            # v1 format - different binary data organization
            for frame in frames_to_process:
                frame_data = []
                for row in range(self.canvas_height):
                    for col in range(self.canvas_width):
                        color = frame[row][col]
                        binary = self.reverse_color_map.get(color.upper(), '000')
                        # In v1, we store each pixel as a single byte (0-7)
                        # Convert binary string to decimal (0-7)
                        decimal_value = int(binary, 2)
                        frame_data.append(decimal_value)
                binary_data.extend(frame_data)
        else:
            # v2 format - match JavaScript implementation
            red_data = []
            green_data = []
            blue_data = []
            
            # Process each frame
            for frame_idx, frame in enumerate(frames_to_process):
                # Process each column
                for col in range(self.canvas_width):
                    # Process each group of 8 rows (or less for the last group)
                    for row_group in range(0, self.canvas_height, 8):
                        red_byte = 0
                        green_byte = 0
                        blue_byte = 0
                        
                        # Process each bit in the group
                        for bit in range(8):
                            if row_group + bit < self.canvas_height:
                                color = frame[row_group + bit][col].upper()
                                binary = self.reverse_color_map.get(color, '000')
                                
                                # Set the appropriate bit if the color component is 1
                                if binary[2] == '1':  # Red
                                    red_byte |= (1 << (7 - bit))
                                if binary[1] == '1':  # Green
                                    green_byte |= (1 << (7 - bit))
                                if binary[0] == '1':  # Blue
                                    blue_byte |= (1 << (7 - bit))
                        
                        # Add the bytes to their respective arrays
                        red_data.append(red_byte)
                        green_data.append(green_byte)
                        blue_data.append(blue_byte)
            
            # Combine all data in the correct order
            # First all red data for all frames
            binary_data.extend(red_data)
            # Then all green data for all frames
            binary_data.extend(green_data)
            # Then all blue data for all frames
            binary_data.extend(blue_data)
        
        return binary_data

    def show_save_dialog(self, extension, file_type_desc):
        # Get the filename from the input field
        filename = self.filename_input.get_text()
        
        # If the filename is empty, use a default name
        if not filename:
            filename = "image"
        
        # Make sure the filename doesn't already have the extension
        if not filename.endswith(extension):
            filename += extension
        
        # In a real application, you would show a file dialog here
        # For now, we'll just return the filename
        return filename

    def show_load_dialog(self, extensions, file_type_desc):
        # Simple dialog to get load path (in a real app, use a proper file dialog)
        # For simplicity, just return None
        return None

    def play_animation(self):
        # Start or stop animation playback
        self.is_playing = not self.is_playing
        if self.is_playing:
            # Set a timer event that will trigger frame changes
            # Use the delays value (in milliseconds) for the interval
            pygame.time.set_timer(pygame.USEREVENT, self.delays)
            # Update button text to show pause symbol
            self.play_pause_button.set_text("⏸")
        else:
            # Stop the timer
            pygame.time.set_timer(pygame.USEREVENT, 0)
            # Update button text to show play symbol
            self.play_pause_button.set_text("▶")
                        
    def handle_events(self):
        time_delta = self.clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle window resize events
            elif event.type == pygame.VIDEORESIZE:
                # Update screen dimensions
                self.screen_width = event.w
                self.screen_height = event.h
                
                # Recreate the display surface
                self.screen = pygame.display.set_mode(
                    (self.screen_width, self.screen_height),
                    pygame.RESIZABLE
                )
                
                # Update text display size
                self.text_display.set_dimensions((self.screen_width - 40, 150))
                
                # Update status label position
                self.status_label.set_position((20, self.screen_height - 40))
                self.status_label.set_dimensions((self.screen_width - 40, 30))
            
            # Handle animation timer event
            elif event.type == pygame.USEREVENT:
                if self.is_playing and self.current_mode == "animation" and self.total_frames > 1:
                    self.next_frame()
                
            # Handle mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 3):  # Left or right mouse button
                    self.mouse_btn_global = 0 if event.button == 1 else 2
                    
                    # Check if click is within canvas
                    if self.canvas_rect.collidepoint(event.pos):
                        # Convert mouse position to pixel coordinates
                        x = (event.pos[0] - self.canvas_rect.left) // self.pixel_size
                        y = (event.pos[1] - self.canvas_rect.top) // self.pixel_size
                        
                        # Ensure coordinates are within bounds
                        if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
                            self.toggle_pixel(y, x)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_btn_global = -1
            
            elif event.type == pygame.MOUSEMOTION:
                # Handle drawing while dragging
                if self.mouse_btn_global in (0, 2) and self.canvas_rect.collidepoint(event.pos):
                    x = (event.pos[0] - self.canvas_rect.left) // self.pixel_size
                    y = (event.pos[1] - self.canvas_rect.top) // self.pixel_size
                    
                    # Ensure coordinates are within bounds
                    if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
                        self.toggle_pixel(y, x)
            
            # Handle UI events
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.paint_bucket_button:
                    self.handle_paint_bucket()
                elif event.ui_element == self.rmb_paint_bucket_button:
                    self.handle_rmb_paint_bucket()
                elif event.ui_element == self.swap_button:
                    self.swap_black_pixels()
                elif event.ui_element == self.back_button:
                    self.prev_frame()
                elif event.ui_element == self.play_pause_button:
                    self.play_animation()
                    # Update button text
                    self.play_pause_button.set_text("⏸" if self.is_playing else "▶")
                elif event.ui_element == self.forward_button:
                    self.next_frame()
                elif event.ui_element == self.plus_button:
                    self.add_frame()
                elif event.ui_element == self.minus_button:
                    self.delete_frame()
                elif event.ui_element == self.clone_button:
                    self.copy_current_frame_to_end()
                elif event.ui_element == self.up_button:
                    self.shift_image_up()
                elif event.ui_element == self.down_button:
                    self.shift_image_down()
                elif event.ui_element == self.left_button:
                    self.shift_image_left()
                elif event.ui_element == self.right_button:
                    self.shift_image_right()
                elif event.ui_element == self.save_button:
                    self.save_jt_file()
                elif event.ui_element == self.draw_text_button:
                    print("Draw Text button clicked")  # Debug output
                    self.draw_text_on_canvas()
                elif event.ui_element == self.debug_toggle_button:
                    self.text_display.visible = not self.text_display.visible
                elif event.ui_element == self.load_button:
                    # Load file functionality would go here
                    pass
            
            elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == self.format_dropdown:
                    self.selected_format = event.text
                elif event.ui_element == self.mode_dropdown:
                    self.handle_mode_change()
                elif event.ui_element == self.color_dropdown:
                    # Convert color name to hex code
                    selected_color_name = event.text
                    selected_hex = next((hex_code for hex_code, name in self.color_names.items() if name == selected_color_name), self.start_color)
                    self.selected_color = selected_hex
                    # Redraw to update color indicators
                    self.draw_pixels()
            
            elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.pixel_size_slider:
                    self.pixel_size = int(event.value)
                    # Update canvas rect
                    self.canvas_rect = pygame.Rect(20, 20,
                                                self.canvas_width * self.pixel_size,
                                                self.canvas_height * self.pixel_size)
                    self.draw_pixels()
            
            # Process other pygame_gui events
            self.manager.process_events(event)
        
        # Update pygame_gui
        self.manager.update(time_delta)
        
        return True

    def run(self):
        # Main application loop
        running = True
        self.draw_pixels()
        self.update_text_display()
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Draw everything
            self.draw_pixels()
            self.manager.draw_ui(self.screen)
            
            # Update display
            pygame.display.update()
        
        pygame.quit()

# Create and run the application
if __name__ == "__main__":
    editor = PixelArtEditor()
    editor.run()
