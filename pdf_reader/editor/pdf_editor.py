"""
PDF Editor Component

This module provides the PDFEditor class for annotating and editing PDF documents.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, colorchooser


class PDFEditor:
    """
    Class for editing and annotating PDF documents displayed in a PDFViewer.
    """
    
    def __init__(self, viewer):
        """
        Initialize the PDF editor.
        
        Args:
            viewer (PDFViewer): The PDF viewer component to attach to
        """
        self.viewer = viewer
        self.document = viewer.document
        self.canvas = viewer.canvas
        
        # Current tool and state
        self.current_tool = "view"  # Default tool is view mode
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.temp_item = None
        self.current_annotation = None
        self.selected_annotation = None
        self.color = "#FF0000"  # Default red color
        
        # Bind canvas events for editing
        self.bind_editor_events()
    
    def bind_editor_events(self):
        """Set up event bindings for the editor."""
        # Override viewer's canvas event bindings
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        
        # Additional bindings for keyboard shortcuts
        self.viewer.bind("<Delete>", self.delete_selected)
        self.viewer.bind("<Escape>", self.cancel_current_action)
    
    def set_tool(self, tool_name):
        """
        Set the current editing tool.
        
        Args:
            tool_name (str): One of 'view', 'highlight', 'text', 'draw', 'shapes', 'comment'
        """
        self.current_tool = tool_name
        
        # Clear any selection when changing tools
        self.clear_selection()
        
        # Update cursor based on tool
        if tool_name == "view":
            self.canvas.config(cursor="arrow")
        elif tool_name in ["highlight", "text", "comment"]:
            self.canvas.config(cursor="cross")
        elif tool_name == "draw":
            self.canvas.config(cursor="pencil")
        elif tool_name == "shapes":
            self.canvas.config(cursor="crosshair")
        else:
            self.canvas.config(cursor="arrow")
    
    def get_page_coordinates(self, event):
        """
        Convert canvas coordinates to page coordinates.
        
        Args:
            event: The event with x, y coordinates
            
        Returns:
            tuple: (x, y) coordinates relative to the page
        """
        # Get the page image position
        if hasattr(self.viewer, 'page_image_id'):
            x_offset, y_offset = self.canvas.coords(self.viewer.page_image_id)
        else:
            x_offset, y_offset = 0, 0
            
        # Convert to page coordinates
        page_x = (event.x - x_offset) / self.viewer.zoom_level
        page_y = (event.y - y_offset) / self.viewer.zoom_level
        
        return (page_x, page_y)
    
    def on_mouse_down(self, event):
        """Handle mouse button press events."""
        if self.current_tool == "view":
            # In view mode, check if we clicked on an annotation
            self.select_annotation_at(event.x, event.y)
        
        elif self.current_tool == "highlight":
            # Start creating a highlight
            self.clear_selection()
            self.drawing = True
            self.start_x, self.start_y = self.get_page_coordinates(event)
            
            # Create a temporary rectangle to show the highlight
            x_offset, y_offset = self.canvas.coords(self.viewer.page_image_id)
            self.temp_item = self.canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                fill="yellow",
                stipple='gray25',  # Semi-transparent
                outline='',
                tags=("temp_annotation")
            )
        
        elif self.current_tool == "text":
            # Place a text box at the click position
            self.clear_selection()
            page_x, page_y = self.get_page_coordinates(event)
            
            # Ask for text content 
            text = simpledialog.askstring("Text Annotation", "Enter text:")
            if text:
                # Create the text annotation
                self.add_text_annotation(page_x, page_y, text)
        
        elif self.current_tool == "draw":
            # Start a freehand drawing
            self.clear_selection()
            self.drawing = True
            
            # Initialize points list for the drawing
            page_x, page_y = self.get_page_coordinates(event)
            self.drawing_points = [(page_x, page_y)]
            
            # Create a temporary line for the drawing
            x_offset, y_offset = self.canvas.coords(self.viewer.page_image_id)
            scaled_x = page_x * self.viewer.zoom_level + x_offset
            scaled_y = page_y * self.viewer.zoom_level + y_offset
            self.temp_item = self.canvas.create_line(
                scaled_x, scaled_y, scaled_x, scaled_y,
                fill=self.color,
                width=2 * self.viewer.zoom_level,
                tags=("temp_annotation")
            )
        
        elif self.current_tool == "shapes":
            # Start creating a shape (rectangle by default)
            self.clear_selection()
            self.drawing = True
            self.start_x, self.start_y = self.get_page_coordinates(event)
            
            # Create a temporary shape
            x_offset, y_offset = self.canvas.coords(self.viewer.page_image_id)
            self.temp_item = self.canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                outline=self.color,
                width=2 * self.viewer.zoom_level,
                tags=("temp_annotation")
            )
        
        elif self.current_tool == "comment":
            # Place a comment at the click position
            self.clear_selection()
            page_x, page_y = self.get_page_coordinates(event)
            
            # Ask for comment text
            comment = simpledialog.askstring("Comment", "Enter comment:")
            if comment:
                # Create the comment annotation
                self.add_comment_annotation(page_x, page_y, comment)
    
    def on_mouse_drag(self, event):
        """Handle mouse drag events."""
        if not self.drawing:
            # If we're not drawing but have a selection, move it
            if self.selected_annotation:
                self.move_selected_annotation(event)
            return
        
        if self.current_tool == "highlight":
            # Update the temporary highlight
            current_x, current_y = self.get_page_coordinates(event)
            
            # Update the temporary rectangle
            x_offset, y_offset = self.canvas.coords(self.viewer.page_image_id)
            x1 = self.start_x * self.viewer.zoom_level + x_offset
            y1 = self.start_y * self.viewer.zoom_level + y_offset
            x2 = current_x * self.viewer.zoom_level + x_offset
            y2 = current_y * self.viewer.zoom_level + y_offset
            
            self.canvas.coords(self.temp_item, x1, y1, x2, y2)
        
        elif self.current_tool == "draw":
            # Add point to the drawing
            page_x, page_y = self.get_page_coordinates(event)
            self.drawing_points.append((page_x, page_y))
            
            # Update the temporary line
            x_offset, y_offset = self.canvas.coords(self.viewer.page_image_id)
            
            # Create a list of scaled points
            scaled_points = []
            for x, y in self.drawing_points:
                scaled_points.extend([
                    x * self.viewer.zoom_level + x_offset,
                    y * self.viewer.zoom_level + y_offset
                ])
            
            # Update the line
            self.canvas.delete(self.temp_item)
            self.temp_item = self.canvas.create_line(
                scaled_points,
                fill=self.color,
                width=2 * self.viewer.zoom_level,
                smooth=True,
                tags=("temp_annotation")
            )
        
        elif self.current_tool == "shapes":
            # Update the temporary shape
            current_x, current_y = self.get_page_coordinates(event)
            
            # Update the temporary rectangle
            x_offset, y_offset = self.canvas.coords(self.viewer.page_image_id)
            x1 = self.start_x * self.viewer.zoom_level + x_offset
            y1 = self.start_y * self.viewer.zoom_level + y_offset
            x2 = current_x * self.viewer.zoom_level + x_offset
            y2 = current_y * self.viewer.zoom_level + y_offset
            
            self.canvas.coords(self.temp_item, x1, y1, x2, y2)
    
    def on_mouse_up(self, event):
        """Handle mouse button release events."""
        if not self.drawing:
            return
            
        if self.current_tool == "highlight":
            # Finalize the highlight
            current_x, current_y = self.get_page_coordinates(event)
            
            # Delete the temporary rectangle
            self.canvas.delete(self.temp_item)
            self.temp_item = None
            
            # Make sure start coordinates are smaller than end coordinates
            x1, x2 = sorted([self.start_x, current_x])
            y1, y2 = sorted([self.start_y, current_y])
            
            # Add the highlight annotation
            self.add_highlight_annotation(x1, y1, x2, y2)
        
        elif self.current_tool == "draw":
            # Finalize the drawing
            self.canvas.delete(self.temp_item)
            self.temp_item = None
            
            # Add the drawing annotation if it has more than one point
            if len(self.drawing_points) > 1:
                self.add_drawing_annotation(self.drawing_points)
        
        elif self.current_tool == "shapes":
            # Finalize the shape
            current_x, current_y = self.get_page_coordinates(event)
            
            # Delete the temporary shape
            self.canvas.delete(self.temp_item)
            self.temp_item = None
            
            # Make sure coordinates are properly ordered
            x1, x2 = sorted([self.start_x, current_x])
            y1, y2 = sorted([self.start_y, current_y])
            
            # Add the shape annotation
            self.add_shape_annotation(x1, y1, x2, y2, 'rectangle')
        
        self.drawing = False
    
    def on_mouse_move(self, event):
        """Handle mouse movement events (without button press)."""
        # Update cursor if hovering over an annotation in view mode
        if self.current_tool == "view":
            if self.is_over_annotation(event.x, event.y):
                self.canvas.config(cursor="hand2")
            else:
                self.canvas.config(cursor="arrow")
    
    def is_over_annotation(self, x, y):
        """
        Check if the cursor is over an annotation.
        
        Args:
            x, y: Canvas coordinates
            
        Returns:
            bool: True if cursor is over an annotation
        """
        # Get items at cursor position
        items = self.canvas.find_overlapping(x-2, y-2, x+2, y+2)
        
        for item in items:
            # Get tags for the item
            tags = self.canvas.gettags(item)
            
            # Check if any tag starts with 'annotation:'
            for tag in tags:
                if tag.startswith("annotation:"):
                    return True
        
        return False
    
    def select_annotation_at(self, x, y):
        """
        Select an annotation at the given canvas coordinates.
        
        Args:
            x, y: Canvas coordinates
            
        Returns:
            bool: True if an annotation was selected
        """
        # Clear any existing selection
        self.clear_selection()
        
        # Get items at cursor position
        items = self.canvas.find_overlapping(x-2, y-2, x+2, y+2)
        
        for item in items:
            # Get tags for the item
            tags = self.canvas.gettags(item)
            
            # Find annotation tag
            annotation_id = None
            for tag in tags:
                if tag.startswith("annotation:"):
                    annotation_id = tag.split(":", 1)[1]
                    break
            
            if annotation_id:
                # Found an annotation, mark it as selected
                self.selected_annotation = {
                    'id': annotation_id,
                    'item': item,
                    'tags': tags
                }
                
                # Highlight the selected annotation
                self.canvas.itemconfig(item, width=2 * self.viewer.zoom_level)
                
                # If it's a rectangle, add a selection border
                if 'rectangle' in tags or 'highlight' in tags:
                    coords = self.canvas.coords(item)
                    self.selection_outline = self.canvas.create_rectangle(
                        coords,
                        outline='blue',
                        width=2,
                        dash=(4, 4),
                        tags=('selection_marker')
                    )
                # If it's a text or comment, add a selection border
                elif 'text_box' in tags or 'comment' in tags:
                    bbox = self.canvas.bbox(item)
                    self.selection_outline = self.canvas.create_rectangle(
                        bbox,
                        outline='blue',
                        width=2,
                        dash=(4, 4),
                        tags=('selection_marker')
                    )
                
                return True
        
        return False
    
    def clear_selection(self):
        """Clear the current annotation selection."""
        if self.selected_annotation:
            # Restore original appearance
            self.canvas.itemconfig(
                self.selected_annotation['item'], 
                width=1 * self.viewer.zoom_level
            )
            self.selected_annotation = None
        
        # Remove selection outline if it exists
        if hasattr(self, 'selection_outline') and self.selection_outline:
            self.canvas.delete(self.selection_outline)
            self.selection_outline = None
    
    def move_selected_annotation(self, event):
        """
        Move the selected annotation based on mouse drag.
        
        Args:
            event: Mouse event with x, y coordinates
        """
        if not self.selected_annotation:
            return
            
        # Get annotation ID and page number
        annotation_id = self.selected_annotation['id']
        page_num = self.viewer.current_page
        
        # Find annotation in document
        annotations = self.document.get_annotations(page_num)
        target_annotation = None
        
        for annotation in annotations:
            if annotation['id'] == annotation_id:
                target_annotation = annotation
                break
        
        if not target_annotation:
            return
            
        # Get current page coordinates
        page_x, page_y = self.get_page_coordinates(event)
        
        # Update annotation position based on type
        annotation_type = target_annotation['type']
        
        if annotation_type == 'highlight':
            # Highlights typically don't move, but we could implement it
            pass
            
        elif annotation_type == 'text':
            # Update text position
            target_annotation['data']['x'] = page_x
            target_annotation['data']['y'] = page_y
            
        elif annotation_type == 'comment':
            # Update comment position
            target_annotation['data']['x'] = page_x
            target_annotation['data']['y'] = page_y
            
        elif annotation_type == 'shape':
            # Shapes could be moved or resized
            # For simplicity, we'll just move them
            width = target_annotation['data']['x2'] - target_annotation['data']['x1']
            height = target_annotation['data']['y2'] - target_annotation['data']['y1']
            
            target_annotation['data']['x1'] = page_x
            target_annotation['data']['y1'] = page_y
            target_annotation['data']['x2'] = page_x + width
            target_annotation['data']['y2'] = page_y + height
            
        # Redisplay the current page to reflect changes
        self.viewer.display_current_page()
        
        # Mark document as changed
        self.document.has_changes = True
    
    def delete_selected(self, event=None):
        """
        Delete the currently selected annotation.
        
        Returns:
            bool: True if an annotation was deleted
        """
        if not self.selected_annotation:
            return False
            
        # Get annotation ID and page number
        annotation_id = self.selected_annotation['id']
        page_num = self.viewer.current_page
        
        # Delete the annotation
        result = self.document.delete_annotation(page_num, annotation_id)
        
        # Clear selection
        self.clear_selection()
        
        # Redisplay the page to reflect changes
        if result:
            self.viewer.display_current_page()
        
        return result
    
    def cancel_current_action(self, event=None):
        """Cancel the current drawing action."""
        # Clear any temporary items
        if self.temp_item:
            self.canvas.delete(self.temp_item)
            self.temp_item = None
        
        # Reset drawing state
        self.drawing = False
        
        # Clear selection
        self.clear_selection()
        
        # Reset to view tool
        self.set_tool("view")
        
        return True
    
    def add_highlight_annotation(self, x1, y1, x2, y2):
        """
        Add a highlight annotation to the current page.
        
        Args:
            x1, y1, x2, y2: Coordinates in page space
            
        Returns:
            str: ID of the created annotation
        """
        # Check if the highlight has a minimum size
        if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
            return None
            
        # Create annotation data
        data = {
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'color': 'yellow'  # Default color for highlights
        }
        
        # Add to document
        page_num = self.viewer.current_page
        annotation_id = self.document.add_annotation(page_num, 'highlight', data)
        
        # Update the display
        self.viewer.display_current_page()
        
        return annotation_id
    
    def add_text_annotation(self, x, y, text):
        """
        Add a text box annotation to the current page.
        
        Args:
            x, y: Position in page space
            text: Text content
            
        Returns:
            str: ID of the created annotation
        """
        # Create annotation data
        data = {
            'x': x,
            'y': y,
            'text': text,
            'color': 'black',
            'font': 'Arial',
            'font_size': 12,
            'anchor': tk.NW
        }
        
        # Add to document
        page_num = self.viewer.current_page
        annotation_id = self.document.add_annotation(page_num, 'text', data)
        
        # Update the display
        self.viewer.display_current_page()
        
        return annotation_id
    
    def add_drawing_annotation(self, points):
        """
        Add a freehand drawing annotation to the current page.
        
        Args:
            points: List of (x, y) coordinates in page space
            
        Returns:
            str: ID of the created annotation
        """
        # Create annotation data
        data = {
            'points': points,
            'color': self.color,
            'width': 2,
            'smooth': True
        }
        
        # Add to document
        page_num = self.viewer.current_page
        annotation_id = self.document.add_annotation(page_num, 'drawing', data)
        
        # Update the display
        self.viewer.display_current_page()
        
        return annotation_id
    
    def add_shape_annotation(self, x1, y1, x2, y2, shape_type):
        """
        Add a shape annotation to the current page.
        
        Args:
            x1, y1, x2, y2: Coordinates in page space
            shape_type: Type of shape ('rectangle', 'oval', 'arrow')
            
        Returns:
            str: ID of the created annotation
        """
        # Check if the shape has a minimum size (except for arrows)
        if shape_type != 'arrow' and (abs(x2 - x1) < 5 or abs(y2 - y1) < 5):
            return None
            
        # Create annotation data
        data = {
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'shape_type': shape_type,
            'color': self.color,
            'line_width': 2
        }
        
        # Add to document
        page_num = self.viewer.current_page
        annotation_id = self.document.add_annotation(page_num, 'shape', data)
        
        # Update the display
        self.viewer.display_current_page()
        
        return annotation_id
    
    def add_comment_annotation(self, x, y, text):
        """
        Add a comment annotation to the current page.
        
        Args:
            x, y: Position in page space
            text: Comment text
            
        Returns:
            str: ID of the created annotation
        """
        # Create annotation data
        data = {
            'x': x,
            'y': y,
            'text': text,
            'color': 'yellow'  # Default color for comments
        }
        
        # Add to document
        page_num = self.viewer.current_page
        annotation_id = self.document.add_annotation(page_num, 'comment', data)
        
        # Update the display
        self.viewer.display_current_page()
        
        return annotation_id
    
    def choose_color(self):
        """
        Open a color chooser dialog.
        
        Returns:
            str: Hex color code or None if canceled
        """
        color = colorchooser.askcolor(self.color, title="Choose Color")[1]
        if color:
            self.color = color
            return color
        return None
