"""
PDF Viewer Component

This module provides the PDFViewer class for displaying and navigating PDF documents.
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class PDFViewer(ttk.Frame):
    """
    A widget for viewing PDF documents with navigation and zoom capabilities.
    """
    
    def __init__(self, parent, document, **kwargs):
        """
        Initialize the PDF viewer.
        
        Args:
            parent: Parent widget
            document (PDFDocument): Document to display
            **kwargs: Additional arguments for ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        self.document = document
        self.current_page = 0
        self.zoom_level = 1.0  # 100%
        self.min_zoom = 0.25   # 25%
        self.max_zoom = 3.0    # 300%
        self.zoom_step = 0.1   # 10% per step
        
        # Search variables
        self.search_term = ""
        self.search_results = []
        self.current_match = -1
        
        # Set up the display
        self.create_widgets()
        
        # Load first page
        self.display_current_page()
    
    def create_widgets(self):
        """Set up the UI components for the viewer."""
        # Create a canvas with scrollbars
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Horizontal scrollbar
        self.h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Vertical scrollbar
        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas for displaying the PDF
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            background='gray',
            xscrollcommand=self.h_scrollbar.set,
            yscrollcommand=self.v_scrollbar.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Connect scrollbars to canvas
        self.h_scrollbar.config(command=self.canvas.xview)
        self.v_scrollbar.config(command=self.canvas.yview)
        
        # Bind events
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.bind_mouse_events()
    
    def bind_mouse_events(self):
        """Set up mouse event handling for the canvas."""
        # Bind mouse wheel for scrolling
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows/macOS
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)   # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)   # Linux scroll down
        
        # Bind click events (for annotation selection)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Bind drag events (for moving annotations)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
    
    def on_canvas_configure(self, event):
        """Handle canvas resize events."""
        # Update the scroll region when the canvas size changes
        self.update_scroll_region()
        
        # If this is the first resize after loading a page, center it
        if hasattr(self, 'page_image') and hasattr(self, 'page_image_id'):
            self.center_page()
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel events for scrolling."""
        # Determine direction and platform
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            # Scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            # Scroll down
            self.canvas.yview_scroll(1, "units")
    
    def on_canvas_click(self, event):
        """Handle mouse click on canvas."""
        # This will be used for selecting annotations
        # Implemented in the PDFEditor class
        pass
    
    def on_canvas_drag(self, event):
        """Handle mouse drag on canvas."""
        # This will be used for moving annotations
        # Implemented in the PDFEditor class
        pass
    
    def on_canvas_release(self, event):
        """Handle mouse button release on canvas."""
        # This will be used for finalizing annotation moves
        # Implemented in the PDFEditor class
        pass
    
    def display_current_page(self):
        """Render and display the current page."""
        # Clear previous content
        self.canvas.delete("all")
        
        # Render the page at current zoom level
        self.page_image = self.document.render_page(
            self.current_page, 
            scale=self.zoom_level
        )
        
        # Display the image on the canvas
        self.page_image_id = self.canvas.create_image(
            0, 0,  # Position will be adjusted later
            anchor=tk.NW,
            image=self.page_image
        )
        
        # Update scroll region and center the page
        self.update_scroll_region()
        self.center_page()
        
        # Get and display annotations for this page
        self.display_annotations()
    
    def update_scroll_region(self):
        """Update the canvas scroll region based on content size."""
        if hasattr(self, 'page_image'):
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Get image dimensions
            image_width = self.page_image.width()
            image_height = self.page_image.height()
            
            # Set scroll region to the larger of canvas or image
            scroll_width = max(canvas_width, image_width)
            scroll_height = max(canvas_height, image_height)
            
            self.canvas.config(scrollregion=(0, 0, scroll_width, scroll_height))
    
    def center_page(self):
        """Center the page in the canvas."""
        if hasattr(self, 'page_image') and hasattr(self, 'page_image_id'):
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Get image dimensions
            image_width = self.page_image.width()
            image_height = self.page_image.height()
            
            # Calculate centered position
            x_pos = max(0, (canvas_width - image_width) // 2)
            y_pos = max(0, (canvas_height - image_height) // 2)
            
            # Move the image
            self.canvas.coords(self.page_image_id, x_pos, y_pos)
    
    def display_annotations(self):
        """Display annotations for the current page."""
        # Get annotations from the document
        annotations = self.document.get_annotations(self.current_page)
        
        # Display each annotation
        for annotation in annotations:
            annotation_type = annotation['type']
            data = annotation['data']
            annotation_id = annotation['id']
            
            if annotation_type == 'highlight':
                self._display_highlight(data, annotation_id)
            elif annotation_type == 'text':
                self._display_text_box(data, annotation_id)
            elif annotation_type == 'drawing':
                self._display_drawing(data, annotation_id)
            elif annotation_type == 'shape':
                self._display_shape(data, annotation_id)
            elif annotation_type == 'comment':
                self._display_comment(data, annotation_id)
    
    def _display_highlight(self, data, annotation_id):
        """Display a highlight annotation."""
        # Get coordinates and apply zoom
        x1 = data['x1'] * self.zoom_level
        y1 = data['y1'] * self.zoom_level
        x2 = data['x2'] * self.zoom_level
        y2 = data['y2'] * self.zoom_level
        
        # Get any positioning offset from centering
        if hasattr(self, 'page_image_id'):
            x_offset, y_offset = self.canvas.coords(self.page_image_id)
        else:
            x_offset, y_offset = 0, 0
        
        # Create highlight rectangle
        self.canvas.create_rectangle(
            x1 + x_offset, y1 + y_offset, 
            x2 + x_offset, y2 + y_offset,
            fill=data.get('color', 'yellow'),
            stipple='gray25',  # Semi-transparent
            outline='',  # No outline
            tags=(f"annotation:{annotation_id}", 'highlight')
        )
    
    def _display_text_box(self, data, annotation_id):
        """Display a text box annotation."""
        # Get coordinates and apply zoom
        x = data['x'] * self.zoom_level
        y = data['y'] * self.zoom_level
        
        # Get any positioning offset from centering
        if hasattr(self, 'page_image_id'):
            x_offset, y_offset = self.canvas.coords(self.page_image_id)
        else:
            x_offset, y_offset = 0, 0
        
        # Create text box
        self.canvas.create_text(
            x + x_offset, y + y_offset,
            text=data.get('text', ''),
            fill=data.get('color', 'black'),
            font=(data.get('font', 'Arial'), 
                 int(data.get('font_size', 12) * self.zoom_level)),
            anchor=data.get('anchor', tk.NW),
            tags=(f"annotation:{annotation_id}", 'text_box')
        )
    
    def _display_drawing(self, data, annotation_id):
        """Display a freehand drawing annotation."""
        # Get points and apply zoom
        points = data.get('points', [])
        if not points:
            return
            
        # Scale points by zoom level
        scaled_points = []
        for x, y in points:
            scaled_points.extend([x * self.zoom_level, y * self.zoom_level])
        
        # Get any positioning offset from centering
        if hasattr(self, 'page_image_id'):
            x_offset, y_offset = self.canvas.coords(self.page_image_id)
        else:
            x_offset, y_offset = 0, 0
        
        # Apply offset
        for i in range(0, len(scaled_points), 2):
            scaled_points[i] += x_offset
            scaled_points[i+1] += y_offset
        
        # Create line
        self.canvas.create_line(
            scaled_points,
            fill=data.get('color', 'blue'),
            width=data.get('width', 2) * self.zoom_level,
            smooth=data.get('smooth', True),
            tags=(f"annotation:{annotation_id}", 'drawing')
        )
    
    def _display_shape(self, data, annotation_id):
        """Display a shape annotation (rectangle, oval, arrow)."""
        shape_type = data.get('shape_type')
        if not shape_type:
            return
            
        # Get coordinates and apply zoom
        x1 = data.get('x1', 0) * self.zoom_level
        y1 = data.get('y1', 0) * self.zoom_level
        x2 = data.get('x2', 0) * self.zoom_level
        y2 = data.get('y2', 0) * self.zoom_level
        
        # Get any positioning offset from centering
        if hasattr(self, 'page_image_id'):
            x_offset, y_offset = self.canvas.coords(self.page_image_id)
        else:
            x_offset, y_offset = 0, 0
        
        x1 += x_offset
        y1 += y_offset
        x2 += x_offset
        y2 += y_offset
        
        if shape_type == 'rectangle':
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=data.get('color', 'red'),
                width=data.get('line_width', 2) * self.zoom_level,
                tags=(f"annotation:{annotation_id}", 'shape', 'rectangle')
            )
        
        elif shape_type == 'oval':
            self.canvas.create_oval(
                x1, y1, x2, y2,
                outline=data.get('color', 'green'),
                width=data.get('line_width', 2) * self.zoom_level,
                tags=(f"annotation:{annotation_id}", 'shape', 'oval')
            )
        
        elif shape_type == 'arrow':
            # Calculate arrow points 
            # (this is a simplified arrow - in a real app, use proper arrow drawing)
            self.canvas.create_line(
                x1, y1, x2, y2,
                arrow=tk.LAST,  # Arrow at the end
                fill=data.get('color', 'blue'),
                width=data.get('line_width', 2) * self.zoom_level,
                tags=(f"annotation:{annotation_id}", 'shape', 'arrow')
            )
    
    def _display_comment(self, data, annotation_id):
        """Display a sticky note comment."""
        # Get coordinates and apply zoom
        x = data.get('x', 0) * self.zoom_level
        y = data.get('y', 0) * self.zoom_level
        
        # Get any positioning offset from centering
        if hasattr(self, 'page_image_id'):
            x_offset, y_offset = self.canvas.coords(self.page_image_id)
        else:
            x_offset, y_offset = 0, 0
        
        x += x_offset
        y += y_offset
        
        # Create a small rectangle for the sticky note
        note_size = 20 * self.zoom_level
        self.canvas.create_rectangle(
            x, y, x + note_size, y + note_size,
            fill=data.get('color', 'yellow'),
            outline='black',
            tags=(f"annotation:{annotation_id}", 'comment', 'note_icon')
        )
        
        # Add a marker
        self.canvas.create_text(
            x + note_size/2, y + note_size/2,
            text="?",
            fill='black',
            tags=(f"annotation:{annotation_id}", 'comment', 'note_marker')
        )
        
        # Bind click event to show comment text
        self.canvas.tag_bind(
            f"annotation:{annotation_id}", 
            "<Button-1>", 
            lambda e, comment=data.get('text', ''): self.show_comment(e, comment)
        )
    
    def show_comment(self, event, comment_text):
        """Show a popup with the comment text."""
        # Create a toplevel window near the click position
        comment_popup = tk.Toplevel(self)
        comment_popup.title("Comment")
        comment_popup.geometry(f"+{event.x_root}+{event.y_root}")
        
        # Add text display
        text = tk.Text(comment_popup, wrap=tk.WORD, width=40, height=10)
        text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        text.insert(tk.END, comment_text)
        text.config(state=tk.DISABLED)  # Make read-only
        
        # Add close button
        ttk.Button(comment_popup, text="Close", 
                  command=comment_popup.destroy).pack(pady=5)
    
    def previous_page(self):
        """Navigate to the previous page if available."""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()
            # Reset search results when changing pages
            self.search_results = []
            self.current_match = -1
            return True
        return False
    
    def next_page(self):
        """Navigate to the next page if available."""
        if self.current_page < self.document.page_count - 1:
            self.current_page += 1
            self.display_current_page()
            # Reset search results when changing pages
            self.search_results = []
            self.current_match = -1
            return True
        return False
    
    def go_to_page(self, page_num):
        """Go to a specific page number."""
        if 0 <= page_num < self.document.page_count:
            self.current_page = page_num
            self.display_current_page()
            # Reset search results when changing pages
            self.search_results = []
            self.current_match = -1
            return True
        return False
    
    def zoom_in(self):
        """Increase the zoom level."""
        if self.zoom_level < self.max_zoom:
            self.zoom_level = min(self.zoom_level + self.zoom_step, self.max_zoom)
            self.display_current_page()
            return True
        return False
    
    def zoom_out(self):
        """Decrease the zoom level."""
        if self.zoom_level > self.min_zoom:
            self.zoom_level = max(self.zoom_level - self.zoom_step, self.min_zoom)
            self.display_current_page()
            return True
        return False
    
    def set_zoom(self, zoom_level):
        """Set a specific zoom level."""
        if self.min_zoom <= zoom_level <= self.max_zoom:
            self.zoom_level = zoom_level
            self.display_current_page()
            return True
        return False
    
    def fit_to_width(self):
        """Adjust zoom to fit the page width to the canvas."""
        if not hasattr(self, 'page_image'):
            return False
            
        # Get canvas width
        canvas_width = self.canvas.winfo_width()
        
        # Get page original dimensions
        page_width, _ = self.document.get_page_dimensions(self.current_page)
        
        # Calculate zoom factor to fit width (with a small margin)
        zoom = (canvas_width - 20) / page_width
        
        # Apply bounds
        zoom = max(min(zoom, self.max_zoom), self.min_zoom)
        
        # Set zoom and refresh
        return self.set_zoom(zoom)
    
    def actual_size(self):
        """Reset zoom to 100%."""
        return self.set_zoom(1.0)
    
    def search_text(self, search_term):
        """
        Search for text in the current document, starting from the current page.
        
        Args:
            search_term (str): Text to search for
            
        Returns:
            bool: True if any matches found, False otherwise
        """
        self.search_term = search_term
        self.search_results = []
        self.current_match = -1
        
        # Start searching from current page
        current_page = self.current_page
        
        # Search current page first
        if self.document.search_text(current_page, search_term):
            self.search_results.append(current_page)
        
        # Then search remaining pages
        for i in range(self.document.page_count):
            if i != current_page and self.document.search_text(i, search_term):
                self.search_results.append(i)
        
        if self.search_results:
            # Go to first result
            self.next_match()
            return True
        else:
            return False
    
    def next_match(self):
        """Navigate to the next search match."""
        if not self.search_results:
            return False
            
        # Move to next match index
        self.current_match = (self.current_match + 1) % len(self.search_results)
        
        # Go to the page with the match
        page_with_match = self.search_results[self.current_match]
        if page_with_match != self.current_page:
            self.go_to_page(page_with_match)
        
        # In a real implementation, you would highlight the match on the page
        # This would require knowing the exact position of the match
        
        return True
    
    def previous_match(self):
        """Navigate to the previous search match."""
        if not self.search_results:
            return False
            
        # Move to previous match index
        self.current_match = (self.current_match - 1) % len(self.search_results)
        
        # Go to the page with the match
        page_with_match = self.search_results[self.current_match]
        if page_with_match != self.current_page:
            self.go_to_page(page_with_match)
        
        # In a real implementation, you would highlight the match on the page
        # This would require knowing the exact position of the match
        
        return True
