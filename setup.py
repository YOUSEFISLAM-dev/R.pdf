from setuptools import setup, find_packages

setup(
    name="pdf_reader",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyPDF2>=3.0.0",
        "Pillow>=9.0.0",
        "pytesseract>=0.3.9",
    ],
    entry_points={
        "console_scripts": [
            "pdf_reader=pdf_reader.main:main",
        ],
    },
    author="PDF Reader Project",
    description="A modern PDF reader and editor with annotation capabilities",
    keywords="pdf, reader, editor, annotation",
    python_requires=">=3.7",
)
