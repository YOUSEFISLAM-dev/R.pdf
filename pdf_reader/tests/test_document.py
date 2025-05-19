"""
Unit tests for the PDF Document model
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
import io
from PIL import Image

# Import the module to test
from pdf_reader.models.document import PDFDocument


class TestPDFDocument(unittest.TestCase):
    """Test cases for the PDFDocument class."""
    
    @patch('PyPDF2.PdfReader')
    def setUp(self, mock_pdf_reader):
        """Set up test environment before each test."""
        # Create mock pages
        mock_page1 = MagicMock()
        mock_page1.mediabox.width = 612
        mock_page1.mediabox.height = 792
        
        mock_page2 = MagicMock()
        mock_page2.mediabox.width = 612
        mock_page2.mediabox.height = 792
        
        # Configure mock reader
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Create a temporary file to use as a test PDF
        self.test_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        self.test_file.write(b'%PDF-1.7\nMock PDF content\n%%EOF')
        self.test_file.close()
        
        # Create the document
        self.document = PDFDocument(self.test_file.name)
    
    def tearDown(self):
        """Clean up after each test."""
        os.unlink(self.test_file.name)
    
    def test_initialization(self):
        """Test that the document initializes correctly."""
        self.assertEqual(self.document.page_count, 2)
        self.assertEqual(self.document.file_path, self.test_file.name)
        self.assertFalse(self.document.has_changes)
    
    def test_get_page_dimensions(self):
        """Test getting page dimensions."""
        width, height = self.document.get_page_dimensions(0)
        self.assertEqual(width, 612)
        self.assertEqual(height, 792)
        
        # Test with invalid page number
        width, height = self.document.get_page_dimensions(999)
        self.assertEqual(width, 612)  # Should return default letter size
        self.assertEqual(height, 792)
    
    def test_annotations(self):
        """Test adding, retrieving and deleting annotations."""
        # Add an annotation
        annotation_id = self.document.add_annotation(0, 'highlight', {
            'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200, 'color': 'yellow'
        })
        
        # Check that it was added
        self.assertIsNotNone(annotation_id)
        self.assertTrue(self.document.has_changes)
        
        # Get annotations for the page
        annotations = self.document.get_annotations(0)
        self.assertEqual(len(annotations), 1)
        self.assertEqual(annotations[0]['type'], 'highlight')
        
        # Update the annotation
        self.document.update_annotation(0, annotation_id, {'color': 'blue'})
        annotations = self.document.get_annotations(0)
        self.assertEqual(annotations[0]['data']['color'], 'blue')
        
        # Delete the annotation
        result = self.document.delete_annotation(0, annotation_id)
        self.assertTrue(result)
        
        # Check that it was deleted
        annotations = self.document.get_annotations(0)
        self.assertEqual(len(annotations), 0)
    
    def test_export_page_as_pdf(self):
        """Test exporting a single page as PDF."""
        with patch('PyPDF2.PdfWriter') as mock_writer:
            # Create a temporary file for the export
            with tempfile.NamedTemporaryFile(suffix='.pdf') as output_file:
                result = self.document.export_page_as_pdf(0, output_file.name)
                self.assertTrue(result)
                
                # Verify the writer was called correctly
                mock_writer.assert_called_once()
                mock_writer.return_value.add_page.assert_called_once()
                mock_writer.return_value.write.assert_called_once()
    
    def test_export_page_as_png(self):
        """Test exporting a single page as PNG."""
        with patch('PIL.Image.new') as mock_image_new:
            # Mock the Image creation
            mock_image = MagicMock()
            mock_image_new.return_value = mock_image
            
            # Create a temporary file for the export
            with tempfile.NamedTemporaryFile(suffix='.png') as output_file:
                result = self.document.export_page_as_png(0, output_file.name)
                self.assertTrue(result)
                
                # Verify the image was created and saved
                mock_image_new.assert_called_once()
                mock_image.save.assert_called_once()
    
    def test_search_text(self):
        """Test text search functionality."""
        # Mock extract_text to return some text
        self.document.pdf_reader.pages[0].extract_text = MagicMock(
            return_value="This is a test document with searchable text."
        )
        
        # Test search that should match
        result = self.document.search_text(0, "test")
        self.assertTrue(result)
        
        # Test search that shouldn't match
        result = self.document.search_text(0, "xyz123")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
