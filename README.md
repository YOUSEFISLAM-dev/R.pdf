# PDF Reader & Editor

A complete Python application that functions as both a PDF reader and a basic PDF editor with a modern graphical user interface built with Tkinter.

## Features

- **PDF Viewing**:
  - Open and render multi-page PDF files
  - Zoom in/out and page navigation (next/previous, jump-to-page)
  - Thumbnail sidebar for quick navigation
  - Text search with highlighting and match navigation

- **Annotation & Editing**:
  - Add, move, and delete text highlights
  - Add freehand ink drawings
  - Insert shapes (rectangles, ovals, arrows)
  - Add text boxes and sticky-note comments

- **File Operations**:
  - Save edits back to the original file or to a new PDF
  - Export selected pages to individual PDF or PNG files
  - Drag-and-drop file opening
  - Recent files list

- **User Experience**:
  - Keyboard shortcuts for common actions
  - Dark/light mode toggle
  - Split view to compare two PDFs side by side
  - OCR functionality for scanned PDFs (requires Tesseract)

## Installation

1. Ensure you have Python 3.7+ installed
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. For OCR functionality, install Tesseract:
   - **Linux**: `apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`
   - **Windows**: Download from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)

## Usage

Run the application:

```bash
python -m pdf_reader.main
```

Or install the package:

```bash
pip install .
pdf_reader
```

### Keyboard Shortcuts

- **Ctrl+O**: Open file
- **Ctrl+S**: Save file
- **Ctrl+Shift+S**: Save as
- **Ctrl+F**: Find text
- **Ctrl++**: Zoom in
- **Ctrl+-**: Zoom out
- **Ctrl+0**: Actual size
- **Left Arrow**: Previous page
- **Right Arrow**: Next page
- **Alt+F4**: Exit application

## Development

### Project Structure

```
pdf_reader/
├── __init__.py
├── main.py                 # Main application entry point
├── editor/                 # PDF editing functionality
│   ├── __init__.py
│   └── pdf_editor.py
├── models/                 # Data models
│   ├── __init__.py  
│   └── document.py
├── viewer/                 # PDF viewing functionality
│   ├── __init__.py
│   └── pdf_viewer.py
├── utils/                  # Utility functions and classes
│   ├── __init__.py
│   ├── config.py
│   └── recent_files.py
└── tests/                  # Unit tests
    ├── __init__.py
    └── test_document.py
```

### Running Tests

```bash
pytest pdf_reader/tests/
```

## License

This project is open source, available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Notes

- This application uses simplified PDF rendering in this demonstration. For a production application, consider using libraries like pdf2image with Poppler for better rendering quality.
- The annotation implementation is a proof-of-concept. In a real-world scenario, you would need to use PyPDF2's annotation features to properly save annotations back to PDF files.