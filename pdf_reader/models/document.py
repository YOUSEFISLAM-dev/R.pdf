"""
PDF Document Model

This module provides the PDFDocument class for representing and manipulating PDF files.
"""

import os
import io
from PIL import Image, ImageTk
import PyPDF2
import pytesseract


class PDFDocument:
    """
    Class representing a PDF document with methods for viewing, editing, and exporting.
    """
    
    def __init__(self, file_path):
        """
        Initialize a PDF document from a file path.
        
        Args:
            file_path (str): Path to the PDF file
        
        Raises:
            FileNotFoundError: If the file does not exist
            PyPDF2.errors.PdfReadError: If the file is not a valid PDF
        """
        self.file_path = file_path
        
        # Open and read the PDF file
        with open(file_path, 'rb') as file:
            self.pdf_reader = PyPDF2.PdfReader(file)
            self.page_count = len(self.pdf_reader.pages)
        
        # Initialize writer for making changes
        self.pdf_writer = None
        
        # Cache for rendered pages and thumbnails
        self.page_cache = {}
        self.thumbnail_cache = {}
        
        # Track annotations and changes
        self.annotations = {i: [] for i in range(self.page_count)}
        self.has_changes = False
    
    def get_page_dimensions(self, page_num):
        """
        Get the dimensions of a page.
        
        Args:
            page_num (int): Page number (0-based index)
            
        Returns:
            tuple: (width, height) in points
        """
        if 0 <= page_num < self.page_count:
            page = self.pdf_reader.pages[page_num]
            media_box = page.mediabox
            width = float(media_box.width)
            height = float(media_box.height)
            return (width, height)
        return (612, 792)  # Default letter size
    
    def render_page(self, page_num, scale=1.0, dpi=150):
        """
        Render a page as a Pillow Image.
        
        Args:
            page_num (int): Page number (0-based index)
            scale (float): Scale factor for rendering (default: 1.0)
            dpi (int): DPI for rendering (default: 150)
            
        Returns:
            PIL.ImageTk.PhotoImage: Rendered page as a PhotoImage
        """
        # Check if we already have this page cached at this scale
        cache_key = (page_num, scale, dpi)
        if cache_key in self.page_cache:
            return self.page_cache[cache_key]
        
        if 0 <= page_num < self.page_count:
            # Convert PDF page to image
            # This is a simplified approach - in a real app, you might use a
            # library like pdf2image which uses Poppler/MuPDF for better quality
            try:
                # Extract page as bytes
                page = self.pdf_reader.pages[page_num]
                
                # Convert to a temporary PDF
                temp_writer = PyPDF2.PdfWriter()
                temp_writer.add_page(page)
                
                # Save to bytes buffer
                pdf_bytes = io.BytesIO()
                temp_writer.write(pdf_bytes)
                pdf_bytes.seek(0)
                
                # Use PIL to convert from PDF to image 
                # Note: In a real implementation, you'd use a more robust PDF renderer
                # like pdf2image (with poppler) or a similar library
                # This is a placeholder for the concept
                image = Image.new('RGB', [int(dim * scale) for dim in self.get_page_dimensions(page_num)])
                
                # Display a placeholder with page number
                # (In a real implementation, you'd render the actual PDF content)
                from PIL import ImageDraw
                draw = ImageDraw.Draw(image)
                draw.rectangle([0, 0, image.width, image.height], fill='white', outline='black')
                draw.text((image.width//2, image.height//2), f"Page {page_num+1}", fill='black')
                
                # Convert to PhotoImage for Tkinter
                photo = ImageTk.PhotoImage(image)
                
                # Cache the result
                self.page_cache[cache_key] = photo
                
                return photo
            except Exception as e:
                print(f"Error rendering page {page_num}: {e}")
                # Return an error image
                error_img = Image.new('RGB', (500, 700), color='white')
                from PIL import ImageDraw
                draw = ImageDraw.Draw(error_img)
                draw.text((250, 350), f"Error rendering page {page_num+1}", fill='red')
                return ImageTk.PhotoImage(error_img)
        else:
            # Return a blank image for invalid page number
            blank_img = Image.new('RGB', (500, 700), color='white')
            return ImageTk.PhotoImage(blank_img)
    
    def get_thumbnail(self, page_num, size=(150, 200)):
        """
        Get a thumbnail image for the page.
        
        Args:
            page_num (int): Page number (0-based index)
            size (tuple): Thumbnail size as (width, height)
            
        Returns:
            PIL.ImageTk.PhotoImage: Thumbnail image
        """
        if page_num in self.thumbnail_cache:
            return self.thumbnail_cache[page_num]
            
        if 0 <= page_num < self.page_count:
            # Create a smaller rendering of the page
            # For simplicity, we'll create a placeholder
            # In a real implementation, you would render a smaller version of the actual page
            thumb_img = Image.new('RGB', size, color='white')
            from PIL import ImageDraw
            draw = ImageDraw.Draw(thumb_img)
            draw.rectangle([0, 0, size[0], size[1]], outline='black')
            draw.text((size[0]//2, size[1]//2), f"Page {page_num+1}", fill='black')
            
            photo = ImageTk.PhotoImage(thumb_img)
            self.thumbnail_cache[page_num] = photo
            return photo
        else:
            # Return a blank thumbnail for invalid page
            blank = Image.new('RGB', size, color='gray')
            return ImageTk.PhotoImage(blank)
    
    def add_annotation(self, page_num, annotation_type, data):
        """
        Add an annotation to a page.
        
        Args:
            page_num (int): Page number (0-based index)
            annotation_type (str): Type of annotation ('highlight', 'text', 'drawing', etc.)
            data (dict): Annotation data including coordinates and properties
            
        Returns:
            str: ID of the created annotation
        """
        if 0 <= page_num < self.page_count:
            # Generate a unique ID for the annotation
            annotation_id = f"annot_{page_num}_{len(self.annotations[page_num])}"
            
            # Create the annotation object
            annotation = {
                'id': annotation_id,
                'type': annotation_type,
                'data': data
            }
            
            # Add to the annotations dictionary
            self.annotations[page_num].append(annotation)
            self.has_changes = True
            
            return annotation_id
        
        return None
    
    def update_annotation(self, page_num, annotation_id, data):
        """
        Update an existing annotation.
        
        Args:
            page_num (int): Page number (0-based index)
            annotation_id (str): ID of the annotation to update
            data (dict): New annotation data
            
        Returns:
            bool: True if annotation was updated, False otherwise
        """
        if 0 <= page_num < self.page_count:
            for annotation in self.annotations[page_num]:
                if annotation['id'] == annotation_id:
                    annotation['data'].update(data)
                    self.has_changes = True
                    return True
        
        return False
    
    def delete_annotation(self, page_num, annotation_id):
        """
        Delete an annotation.
        
        Args:
            page_num (int): Page number (0-based index)
            annotation_id (str): ID of the annotation to delete
            
        Returns:
            bool: True if annotation was deleted, False otherwise
        """
        if 0 <= page_num < self.page_count:
            for i, annotation in enumerate(self.annotations[page_num]):
                if annotation['id'] == annotation_id:
                    self.annotations[page_num].pop(i)
                    self.has_changes = True
                    return True
        
        return False
    
    def get_annotations(self, page_num):
        """
        Get all annotations for a page.
        
        Args:
            page_num (int): Page number (0-based index)
            
        Returns:
            list: List of annotation objects
        """
        if 0 <= page_num < self.page_count:
            return self.annotations[page_num]
        return []
    
    def save(self):
        """
        Save changes back to the original file.
        
        Raises:
            IOError: If the file cannot be written
            PermissionError: If the user doesn't have permission to write to the file
        """
        if not self.has_changes:
            return  # No changes to save
        
        self._apply_annotations()
        
        # Save the modified PDF back to the original file
        with open(self.file_path, 'wb') as output_file:
            self.pdf_writer.write(output_file)
    
    def save_as(self, output_path):
        """
        Save changes to a new file.
        
        Args:
            output_path (str): Path where the new file will be saved
            
        Raises:
            IOError: If the file cannot be written
        """
        self._apply_annotations()
        
        # Save the modified PDF to the specified path
        with open(output_path, 'wb') as output_file:
            self.pdf_writer.write(output_file)
        
        # Update file path and reset changes flag
        self.file_path = output_path
        self.has_changes = False
    
    def _apply_annotations(self):
        """
        Apply all annotations to the PDF.
        This internal method creates a new PDF writer with all annotations applied.
        """
        # Create a new PDF writer
        self.pdf_writer = PyPDF2.PdfWriter()
        
        # Copy all pages and apply annotations
        for i in range(self.page_count):
            # Get original page
            page = self.pdf_reader.pages[i]
            
            # Apply annotations for this page
            # In a real implementation, this would add annotations to the page
            # using PyPDF2 or another PDF library's annotation features
            
            # Add the modified page to the writer
            self.pdf_writer.add_page(page)
    
    def export_page_as_pdf(self, page_num, output_path):
        """
        Export a single page as a new PDF file.
        
        Args:
            page_num (int): Page number (0-based index)
            output_path (str): Path where the new PDF will be saved
            
        Returns:
            bool: True if successful, False otherwise
        """
        if 0 <= page_num < self.page_count:
            try:
                # Create a new PDF writer
                writer = PyPDF2.PdfWriter()
                
                # Add the page
                writer.add_page(self.pdf_reader.pages[page_num])
                
                # Write to file
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                return True
            except Exception as e:
                print(f"Error exporting page as PDF: {e}")
                return False
        
        return False
    
    def export_page_as_png(self, page_num, output_path, dpi=300):
        """
        Export a single page as a PNG image.
        
        Args:
            page_num (int): Page number (0-based index)
            output_path (str): Path where the PNG will be saved
            dpi (int): Resolution for the exported image
            
        Returns:
            bool: True if successful, False otherwise
        """
        if 0 <= page_num < self.page_count:
            try:
                # Get the page dimensions
                width, height = self.get_page_dimensions(page_num)
                
                # Create a high-resolution image
                # In a real implementation, you would render the actual PDF content
                image = Image.new('RGB', 
                                 (int(width * dpi / 72), int(height * dpi / 72)), 
                                 color='white')
                
                # Draw a placeholder (in a real app, render the actual PDF content)
                from PIL import ImageDraw
                draw = ImageDraw.Draw(image)
                draw.rectangle([0, 0, image.width-1, image.height-1], outline='black')
                draw.text((image.width//2, image.height//2), f"Page {page_num+1}", fill='black')
                
                # Save the image
                image.save(output_path, format='PNG')
                
                return True
            except Exception as e:
                print(f"Error exporting page as PNG: {e}")
                return False
        
        return False
    
    def ocr_page(self, page_num):
        """
        Perform OCR on a page to extract text.
        
        Args:
            page_num (int): Page number (0-based index)
            
        Returns:
            str: Extracted text or empty string if OCR failed
        """
        if 0 <= page_num < self.page_count:
            try:
                # Render the page at high resolution for OCR
                # In a real implementation, use a proper PDF renderer 
                # like pdf2image with Poppler for better quality
                width, height = self.get_page_dimensions(page_num)
                image = Image.new('RGB', 
                                 (int(width * 3), int(height * 3)), 
                                 color='white')
                
                # Draw a placeholder (in real app, use the actual PDF content)
                from PIL import ImageDraw
                draw = ImageDraw.Draw(image)
                draw.text((image.width//2, image.height//2), 
                         f"This is sample text on page {page_num+1} for OCR testing.", fill='black')
                
                # Use pytesseract to extract text
                text = pytesseract.image_to_string(image)
                
                return text
            except Exception as e:
                print(f"Error performing OCR: {e}")
                return f"OCR Error: {str(e)}"
        
        return ""
    
    def search_text(self, page_num, search_term):
        """
        Search for text on a specific page.
        
        Args:
            page_num (int): Page number (0-based index)
            search_term (str): Text to search for
            
        Returns:
            list: List of matches with positions (in a real implementation)
                 For this simplified example, just returns True/False
        """
        if 0 <= page_num < self.page_count:
            try:
                # Extract text from the page
                page = self.pdf_reader.pages[page_num]
                text = page.extract_text()
                
                # Check if search term is in the text
                if search_term.lower() in text.lower():
                    # In a real implementation, return positions of matches
                    return True
            except Exception as e:
                print(f"Error searching text: {e}")
        
        return False
