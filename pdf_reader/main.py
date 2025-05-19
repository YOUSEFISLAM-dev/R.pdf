#!/usr/bin/env python3
"""
PDF Reader and Editor Application

A complete PDF viewer and editor with annotation capabilities built with Tkinter.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import application modules
from pdf_reader.viewer.pdf_viewer import PDFViewer
from pdf_reader.editor.pdf_editor import PDFEditor
from pdf_reader.models.document import PDFDocument
from pdf_reader.utils.config import AppConfig
from pdf_reader.utils.recent_files import RecentFiles


class PDFReaderApp(tk.Tk):
    """Main application class for the PDF Reader and Editor."""
    
    def __init__(self):
        """Initialize the application and set up the UI."""
        super().__init__()
        
        # Configure the window
        self.title("PDF Reader & Editor")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Set application icon
        # self.iconphoto(True, tk.PhotoImage(file=os.path.join(
        #     os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.png')))
        
        # Initialize config and recent files
        self.config = AppConfig()
        self.recent_files = RecentFiles()
        
        # Set up the UI theme
        self.style = ttk.Style()
        self.apply_theme(self.config.get('theme', 'light'))
        
        # Create the main menu
        self.create_menu()
        
        # Create the main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Set up the status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize document model
        self.current_document = None
        
        # Initialize PDF viewer and editor components
        self.setup_ui_components()
        
        # Set up keyboard shortcuts
        self.bind_shortcuts()
        
        # Set up drag and drop support
        self.setup_drag_drop()
        
        # Update status
        self.status_var.set("Ready")
    
    def setup_ui_components(self):
        """Set up the main UI components including viewer and editor."""
        # Create PanedWindow for resizable components
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel for thumbnails
        self.thumbnail_frame = ttk.Frame(self.paned_window, width=200)
        self.paned_window.add(self.thumbnail_frame, weight=1)
        
        # Create right panel for main viewer/editor
        self.viewer_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.viewer_frame, weight=4)
        
        # Initialize viewer and editor (they will be properly created when a document is loaded)
        self.viewer = None
        self.editor = None
        
        # Create toolbar
        self.create_toolbar()
        
        # Set up empty state display
        self.setup_empty_state()
    
    def create_toolbar(self):
        """Create the application toolbar with common actions."""
        self.toolbar = ttk.Frame(self.viewer_frame)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Navigation controls
        ttk.Button(self.toolbar, text="⬅", command=self.previous_page).pack(side=tk.LEFT, padx=2)
        self.page_var = tk.StringVar(value="Page: 0 / 0")
        ttk.Label(self.toolbar, textvariable=self.page_var).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.toolbar, text="➡", command=self.next_page).pack(side=tk.LEFT, padx=2)
        
        # Jump to page
        ttk.Label(self.toolbar, text="Go to:").pack(side=tk.LEFT, padx=(10, 2))
        self.goto_entry = ttk.Entry(self.toolbar, width=5)
        self.goto_entry.pack(side=tk.LEFT, padx=2)
        self.goto_entry.bind("<Return>", self.jump_to_page)
        
        # Zoom controls
        ttk.Button(self.toolbar, text="🔍-", command=self.zoom_out).pack(side=tk.LEFT, padx=(10, 2))
        self.zoom_var = tk.StringVar(value="100%")
        ttk.Label(self.toolbar, textvariable=self.zoom_var).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="🔍+", command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        
        # Search
        ttk.Label(self.toolbar, text="Search:").pack(side=tk.LEFT, padx=(20, 2))
        self.search_entry = ttk.Entry(self.toolbar, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=2)
        self.search_entry.bind("<Return>", self.search_text)
        ttk.Button(self.toolbar, text="Find", command=self.search_text).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="▲", command=self.previous_match).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="▼", command=self.next_match).pack(side=tk.LEFT, padx=2)
        
        # Editing tools on the right side
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Tool selection
        self.tool_var = tk.StringVar(value="view")
        ttk.Radiobutton(self.toolbar, text="View", variable=self.tool_var, value="view",
                       command=self.change_tool).pack(side=tk.LEFT)
        ttk.Radiobutton(self.toolbar, text="Highlight", variable=self.tool_var, value="highlight",
                       command=self.change_tool).pack(side=tk.LEFT)
        ttk.Radiobutton(self.toolbar, text="Text", variable=self.tool_var, value="text",
                       command=self.change_tool).pack(side=tk.LEFT)
        ttk.Radiobutton(self.toolbar, text="Draw", variable=self.tool_var, value="draw",
                       command=self.change_tool).pack(side=tk.LEFT)
        ttk.Radiobutton(self.toolbar, text="Shapes", variable=self.tool_var, value="shapes",
                       command=self.change_tool).pack(side=tk.LEFT)
        ttk.Radiobutton(self.toolbar, text="Comment", variable=self.tool_var, value="comment",
                       command=self.change_tool).pack(side=tk.LEFT)
    
    def setup_empty_state(self):
        """Display empty state when no document is loaded."""
        self.empty_frame = ttk.Frame(self.viewer_frame)
        self.empty_frame.pack(fill=tk.BOTH, expand=True)
        
        # Center the empty state message and buttons
        empty_content = ttk.Frame(self.empty_frame)
        empty_content.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        ttk.Label(empty_content, text="Welcome to PDF Reader & Editor", 
                 font=("Arial", 18)).pack(pady=10)
        ttk.Label(empty_content, text="Open a PDF file to get started").pack(pady=5)
        
        button_frame = ttk.Frame(empty_content)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Open File", command=self.open_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Recent Files", command=self.show_recent_files).pack(side=tk.LEFT, padx=5)
    
    def create_menu(self):
        """Create the application main menu."""
        self.menu_bar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        
        # Recent files submenu will be populated dynamically
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.update_recent_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export Page as PDF", command=self.export_page_pdf)
        file_menu.add_command(label="Export Page as PNG", command=self.export_page_png)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Alt+F4")
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Find", command=self.show_search, accelerator="Ctrl+F")
        edit_menu.add_separator()
        edit_menu.add_command(label="Delete Annotation", command=self.delete_annotation)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Fit to Width", command=self.fit_to_width)
        view_menu.add_command(label="Actual Size", command=self.actual_size, accelerator="Ctrl+0")
        view_menu.add_separator()
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        theme_var = tk.StringVar(value=self.config.get('theme', 'light'))
        theme_menu.add_radiobutton(label="Light Mode", variable=theme_var, value="light", 
                                  command=lambda: self.change_theme('light'))
        theme_menu.add_radiobutton(label="Dark Mode", variable=theme_var, value="dark", 
                                  command=lambda: self.change_theme('dark'))
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        
        # Split view toggle
        self.split_view_var = tk.BooleanVar(value=False)
        view_menu.add_checkbutton(label="Split View", variable=self.split_view_var,
                                 command=self.toggle_split_view)
        
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Tools menu
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        tools_menu.add_command(label="OCR Current Page", command=self.ocr_current_page)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=self.menu_bar)
    
    def bind_shortcuts(self):
        """Set up keyboard shortcuts for common actions."""
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-Shift-S>", lambda e: self.save_as())
        self.bind("<Control-f>", lambda e: self.show_search())
        self.bind("<Control-plus>", lambda e: self.zoom_in())
        self.bind("<Control-minus>", lambda e: self.zoom_out())
        self.bind("<Control-0>", lambda e: self.actual_size())
        self.bind("<Left>", lambda e: self.previous_page())
        self.bind("<Right>", lambda e: self.next_page())
        self.bind("<Control-p>", lambda e: self.previous_match())
        self.bind("<Control-n>", lambda e: self.next_match())
    
    def setup_drag_drop(self):
        """Set up drag and drop support for opening files."""
        # This is platform-specific and may require additional libraries
        # like TkinterDnD or windnd depending on the platform
        # For simplicity, we'll include a placeholder implementation
        try:
            self.drop_target_register(self.DND_FILES)
            self.dnd_bind('<<Drop>>', self.handle_drop)
        except:
            print("Drag and drop support not available. Using file dialog only.")
    
    def handle_drop(self, event):
        """Handle files dropped onto the application."""
        # Extract file path from the event
        file_path = event.data
        # Remove any quotes or extra characters the OS might add
        file_path = file_path.strip('"\'')
        self.load_document(file_path)
    
    def open_file(self):
        """Open a file dialog to select and open a PDF document."""
        file_path = filedialog.askopenfilename(
            title="Open PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_document(file_path)
    
    def load_document(self, file_path):
        """Load a PDF document from the given file path."""
        try:
            # Clean up previous components if they exist
            if hasattr(self, 'empty_frame'):
                self.empty_frame.pack_forget()
            
            if self.viewer:
                self.viewer.destroy()
            
            if self.editor:
                self.editor.destroy()
            
            # Create new document model
            self.current_document = PDFDocument(file_path)
            
            # Update window title with file name
            self.title(f"{os.path.basename(file_path)} - PDF Reader & Editor")
            
            # Create viewer and editor components
            self.viewer = PDFViewer(self.viewer_frame, self.current_document)
            self.viewer.pack(fill=tk.BOTH, expand=True)
            
            self.editor = PDFEditor(self.viewer)
            
            # Display thumbnails
            self.setup_thumbnails()
            
            # Update page display
            self.page_var.set(f"Page: 1 / {self.current_document.page_count}")
            
            # Update status bar
            self.status_var.set(f"Opened: {file_path}")
            
            # Add to recent files
            self.recent_files.add(file_path)
            self.update_recent_menu()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF file: {str(e)}")
            self.status_var.set("Error loading document")
    
    def setup_thumbnails(self):
        """Set up the thumbnail sidebar for page navigation."""
        # Clear previous thumbnails if they exist
        for widget in self.thumbnail_frame.winfo_children():
            widget.destroy()
        
        # Create canvas for thumbnails with scrollbar
        self.thumb_canvas = tk.Canvas(self.thumbnail_frame, width=180)
        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        thumb_scrollbar = ttk.Scrollbar(self.thumbnail_frame, orient=tk.VERTICAL, 
                                      command=self.thumb_canvas.yview)
        thumb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.thumb_canvas.configure(yscrollcommand=thumb_scrollbar.set)
        
        # Frame to hold thumbnails
        self.thumb_frame = ttk.Frame(self.thumb_canvas)
        self.thumb_canvas.create_window((0, 0), window=self.thumb_frame, anchor=tk.NW)
        
        # Generate and display thumbnails
        self.thumbnails = []
        for i in range(self.current_document.page_count):
            thumb_frame = ttk.Frame(self.thumb_frame)
            thumb_frame.pack(fill=tk.X, pady=5)
            
            # Thumbnail image (to be generated by the document model)
            thumb = self.current_document.get_thumbnail(i)
            label = ttk.Label(thumb_frame, image=thumb)
            label.image = thumb  # Keep a reference
            label.pack(pady=2)
            
            # Page number
            ttk.Label(thumb_frame, text=f"Page {i+1}").pack()
            
            # Store reference and bind click event
            self.thumbnails.append((thumb_frame, label))
            thumb_frame.bind("<Button-1>", lambda e, page=i: self.go_to_page(page))
        
        # Update scroll region
        self.thumb_frame.update_idletasks()
        self.thumb_canvas.config(scrollregion=self.thumb_canvas.bbox(tk.ALL))
    
    def update_recent_menu(self):
        """Update the recent files menu with the latest files."""
        # Clear existing menu items
        self.recent_menu.delete(0, tk.END)
        
        # Add recent files to menu
        for path in self.recent_files.get_list():
            # Use basename for display but full path for command
            filename = os.path.basename(path)
            self.recent_menu.add_command(
                label=filename,
                command=lambda p=path: self.load_document(p)
            )
        
        # Add menu items even if list is empty
        if not self.recent_files.get_list():
            self.recent_menu.add_command(label="No recent files", state=tk.DISABLED)
    
    def show_recent_files(self):
        """Show a dialog with recent files."""
        if not self.recent_files.get_list():
            messagebox.showinfo("Recent Files", "No recent files found")
            return
            
        # Create a simple dialog to display recent files
        dialog = tk.Toplevel(self)
        dialog.title("Recent Files")
        dialog.geometry("500x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Create a listbox to show files
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Select a file to open:").pack(anchor=tk.W, pady=5)
        
        listbox = tk.Listbox(frame)
        listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add recent files to the listbox
        recent_files = self.recent_files.get_list()
        for path in recent_files:
            listbox.insert(tk.END, path)
            
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame, text="Open Selected", 
            command=lambda: self.open_selected_recent(listbox, recent_files, dialog)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Double-click to select
        listbox.bind("<Double-Button-1>", 
                     lambda e: self.open_selected_recent(listbox, recent_files, dialog))
    
    def open_selected_recent(self, listbox, recent_files, dialog):
        """Open a file selected from the recent files dialog."""
        selection = listbox.curselection()
        if selection:
            index = selection[0]
            self.load_document(recent_files[index])
            dialog.destroy()
    
    def previous_page(self):
        """Navigate to the previous page in the document."""
        if self.current_document and self.viewer:
            self.viewer.previous_page()
            self.update_page_status()
    
    def next_page(self):
        """Navigate to the next page in the document."""
        if self.current_document and self.viewer:
            self.viewer.next_page()
            self.update_page_status()
    
    def jump_to_page(self, event=None):
        """Jump to the specified page number."""
        if not self.current_document or not self.viewer:
            return
            
        try:
            page_num = int(self.goto_entry.get()) - 1  # Convert to 0-based index
            if 0 <= page_num < self.current_document.page_count:
                self.go_to_page(page_num)
            else:
                messagebox.showwarning("Invalid Page", 
                                      f"Please enter a page number between 1 and {self.current_document.page_count}")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid page number")
    
    def go_to_page(self, page_num):
        """Go to the specified page number (0-based index)."""
        if self.current_document and self.viewer:
            self.viewer.go_to_page(page_num)
            self.update_page_status()
    
    def update_page_status(self):
        """Update the page number display in the toolbar."""
        if self.current_document and self.viewer:
            current_page = self.viewer.current_page + 1  # Convert to 1-based index for display
            total_pages = self.current_document.page_count
            self.page_var.set(f"Page: {current_page} / {total_pages}")
    
    def zoom_in(self):
        """Increase the zoom level."""
        if self.viewer:
            self.viewer.zoom_in()
            self.zoom_var.set(f"{int(self.viewer.zoom_level * 100)}%")
    
    def zoom_out(self):
        """Decrease the zoom level."""
        if self.viewer:
            self.viewer.zoom_out()
            self.zoom_var.set(f"{int(self.viewer.zoom_level * 100)}%")
    
    def fit_to_width(self):
        """Adjust zoom to fit the page width."""
        if self.viewer:
            self.viewer.fit_to_width()
            self.zoom_var.set(f"{int(self.viewer.zoom_level * 100)}%")
    
    def actual_size(self):
        """Reset zoom to 100%."""
        if self.viewer:
            self.viewer.actual_size()
            self.zoom_var.set("100%")
    
    def show_search(self):
        """Focus the search entry in the toolbar."""
        if hasattr(self, 'search_entry'):
            self.search_entry.focus_set()
    
    def search_text(self, event=None):
        """Search for text in the current document."""
        if not self.current_document or not self.viewer:
            return
            
        search_term = self.search_entry.get()
        if not search_term:
            return
            
        # Delegate search to the viewer
        found = self.viewer.search_text(search_term)
        
        if found:
            self.status_var.set(f"Found '{search_term}'")
        else:
            self.status_var.set(f"Text '{search_term}' not found")
    
    def previous_match(self):
        """Go to previous search match."""
        if self.viewer:
            self.viewer.previous_match()
    
    def next_match(self):
        """Go to next search match."""
        if self.viewer:
            self.viewer.next_match()
    
    def change_tool(self):
        """Change the current editing tool based on selection."""
        if self.editor:
            tool = self.tool_var.get()
            self.editor.set_tool(tool)
            self.status_var.set(f"Tool: {tool.capitalize()}")
    
    def delete_annotation(self):
        """Delete the selected annotation."""
        if self.editor:
            if self.editor.delete_selected():
                self.status_var.set("Annotation deleted")
            else:
                self.status_var.set("No annotation selected")
    
    def save_file(self):
        """Save changes to the current file."""
        if not self.current_document:
            return
            
        try:
            # If it's a new document without a path, use Save As instead
            if not self.current_document.file_path:
                self.save_as()
                return
                
            self.current_document.save()
            self.status_var.set(f"Saved to {self.current_document.file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save the file: {str(e)}")
    
    def save_as(self):
        """Save the current document to a new file."""
        if not self.current_document:
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_document.save_as(file_path)
                # Update window title with new filename
                self.title(f"{os.path.basename(file_path)} - PDF Reader & Editor")
                self.status_var.set(f"Saved to {file_path}")
                
                # Add to recent files
                self.recent_files.add(file_path)
                self.update_recent_menu()
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save the file: {str(e)}")
    
    def export_page_pdf(self):
        """Export the current page as a PDF file."""
        if not self.current_document or not self.viewer:
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Page as PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            try:
                page_num = self.viewer.current_page
                self.current_document.export_page_as_pdf(page_num, file_path)
                self.status_var.set(f"Page {page_num + 1} exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not export the page: {str(e)}")
    
    def export_page_png(self):
        """Export the current page as a PNG image."""
        if not self.current_document or not self.viewer:
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Page as PNG",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )
        
        if file_path:
            try:
                page_num = self.viewer.current_page
                self.current_document.export_page_as_png(page_num, file_path)
                self.status_var.set(f"Page {page_num + 1} exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not export the page: {str(e)}")
    
    def change_theme(self, theme_name):
        """Change the application theme."""
        self.apply_theme(theme_name)
        self.config.set('theme', theme_name)
        self.config.save()
    
    def apply_theme(self, theme_name):
        """Apply the specified theme to the application."""
        # Configure ttk style based on theme
        if theme_name == 'dark':
            self.style.theme_use('clam')  # Best builtin base for customization
            self.style.configure('TFrame', background='#2E2E2E')
            self.style.configure('TLabel', background='#2E2E2E', foreground='#FFFFFF')
            self.style.configure('TButton', background='#3D3D3D', foreground='#FFFFFF')
            self.style.map('TButton',
                         background=[('active', '#4D4D4D')],
                         foreground=[('active', '#FFFFFF')])
            self.style.configure('TEntry', fieldbackground='#3D3D3D', foreground='#FFFFFF')
            self.style.configure('TRadiobutton', background='#2E2E2E', foreground='#FFFFFF')
            self.style.map('TRadiobutton',
                         background=[('active', '#3D3D3D')],
                         foreground=[('active', '#FFFFFF')])
            # Set main window background
            self.configure(background='#2E2E2E')
            # Set menu colors (using tk menu, not ttk)
            self.menu_bar.configure(bg='#2E2E2E', fg='#FFFFFF', activebackground='#4D4D4D', 
                                   activeforeground='#FFFFFF')
        else:  # Light theme (default)
            self.style.theme_use('clam')
            self.style.configure('TFrame', background='#F0F0F0')
            self.style.configure('TLabel', background='#F0F0F0', foreground='#000000')
            self.style.configure('TButton', background='#E0E0E0', foreground='#000000')
            self.style.map('TButton',
                         background=[('active', '#D0D0D0')],
                         foreground=[('active', '#000000')])
            self.style.configure('TEntry', fieldbackground='#FFFFFF', foreground='#000000')
            self.style.configure('TRadiobutton', background='#F0F0F0', foreground='#000000')
            self.style.map('TRadiobutton',
                         background=[('active', '#E0E0E0')],
                         foreground=[('active', '#000000')])
            # Set main window background
            self.configure(background='#F0F0F0')
            # Set menu colors (using tk menu, not ttk)
            self.menu_bar.configure(bg='#F0F0F0', fg='#000000', activebackground='#D0D0D0', 
                                   activeforeground='#000000')
    
    def toggle_split_view(self):
        """Toggle between single and split view for comparing documents."""
        is_split = self.split_view_var.get()
        
        if is_split:
            # Create split view if not already created
            if not hasattr(self, 'second_viewer_frame'):
                # Create a second viewer pane
                self.second_viewer_frame = ttk.Frame(self.paned_window)
                self.paned_window.add(self.second_viewer_frame, weight=4)
                
                # Add open button to second pane
                self.second_empty_frame = ttk.Frame(self.second_viewer_frame)
                self.second_empty_frame.pack(fill=tk.BOTH, expand=True)
                
                empty_content = ttk.Frame(self.second_empty_frame)
                empty_content.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                
                ttk.Label(empty_content, text="Second View").pack(pady=5)
                ttk.Button(empty_content, text="Open File", 
                          command=self.open_second_file).pack(pady=10)
                
            else:
                # Show the second viewer if it was hidden
                self.second_viewer_frame.pack(fill=tk.BOTH, expand=True)
        else:
            # Hide the second viewer if it exists
            if hasattr(self, 'second_viewer_frame'):
                self.second_viewer_frame.pack_forget()
    
    def open_second_file(self):
        """Open a file in the second viewer pane for comparison."""
        file_path = filedialog.askopenfilename(
            title="Open PDF File for Comparison",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Hide empty frame
                if hasattr(self, 'second_empty_frame'):
                    self.second_empty_frame.pack_forget()
                
                # Clean up previous viewer if it exists
                if hasattr(self, 'second_viewer'):
                    self.second_viewer.destroy()
                
                # Create new document model for second view
                self.second_document = PDFDocument(file_path)
                
                # Create viewer component for second view
                self.second_viewer = PDFViewer(self.second_viewer_frame, self.second_document)
                self.second_viewer.pack(fill=tk.BOTH, expand=True)
                
                # Add a simple toolbar for second viewer
                self.create_second_toolbar()
                
                self.status_var.set(f"Comparison view: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open PDF file: {str(e)}")
    
    def create_second_toolbar(self):
        """Create a minimal toolbar for the second viewer pane."""
        toolbar = ttk.Frame(self.second_viewer_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Add minimal controls
        ttk.Button(toolbar, text="⬅", 
                  command=lambda: self.second_viewer.previous_page()).pack(side=tk.LEFT, padx=2)
        
        self.second_page_var = tk.StringVar(value=f"Page: 1 / {self.second_document.page_count}")
        ttk.Label(toolbar, textvariable=self.second_page_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(toolbar, text="➡", 
                  command=lambda: self.second_viewer.next_page()).pack(side=tk.LEFT, padx=2)
        
        # Add zoom controls
        ttk.Button(toolbar, text="🔍-", 
                  command=lambda: self.second_viewer.zoom_out()).pack(side=tk.LEFT, padx=(10, 2))
        
        self.second_zoom_var = tk.StringVar(value="100%")
        ttk.Label(toolbar, textvariable=self.second_zoom_var).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar, text="🔍+", 
                  command=lambda: self.second_viewer.zoom_in()).pack(side=tk.LEFT, padx=2)
        
        # Add synchronize button
        ttk.Button(toolbar, text="Sync Views", 
                  command=self.sync_views).pack(side=tk.RIGHT, padx=5)
    
    def sync_views(self):
        """Synchronize the page and zoom level between the two viewers."""
        if hasattr(self, 'viewer') and hasattr(self, 'second_viewer'):
            # Sync to the main viewer's page and zoom
            self.second_viewer.go_to_page(self.viewer.current_page)
            self.second_viewer.set_zoom(self.viewer.zoom_level)
            self.second_zoom_var.set(f"{int(self.second_viewer.zoom_level * 100)}%")
            self.second_page_var.set(
                f"Page: {self.second_viewer.current_page + 1} / {self.second_document.page_count}")
    
    def ocr_current_page(self):
        """Perform OCR on the current page."""
        if not self.current_document or not self.viewer:
            return
            
        try:
            page_num = self.viewer.current_page
            self.status_var.set("Processing OCR... This may take a moment")
            self.update()  # Force UI update
            
            # Perform OCR
            text = self.current_document.ocr_page(page_num)
            
            # Show the OCR result in a dialog
            self.show_ocr_result(text)
            
            self.status_var.set("OCR completed")
        except Exception as e:
            messagebox.showerror("OCR Error", f"Could not perform OCR: {str(e)}")
            self.status_var.set("OCR failed")
    
    def show_ocr_result(self, text):
        """Show OCR results in a dialog."""
        dialog = tk.Toplevel(self)
        dialog.title("OCR Results")
        dialog.geometry("600x400")
        dialog.transient(self)
        
        # Create a frame with padding
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Extracted Text:").pack(anchor=tk.W, pady=5)
        
        # Create a scrollable text widget
        text_widget = tk.Text(frame, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(text_widget, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Insert the OCR text
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Add buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame, text="Copy to Clipboard",
            command=lambda: self.copy_to_clipboard(text)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="Close",
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status_var.set("Copied to clipboard")
    
    def show_shortcuts(self):
        """Display a dialog with keyboard shortcuts."""
        shortcuts = [
            ("Ctrl+O", "Open file"),
            ("Ctrl+S", "Save file"),
            ("Ctrl+Shift+S", "Save as"),
            ("Ctrl+F", "Find text"),
            ("Ctrl++", "Zoom in"),
            ("Ctrl+-", "Zoom out"),
            ("Ctrl+0", "Actual size"),
            ("Left Arrow", "Previous page"),
            ("Right Arrow", "Next page"),
            ("Alt+F4", "Exit application")
        ]
        
        dialog = tk.Toplevel(self)
        dialog.title("Keyboard Shortcuts")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Keyboard Shortcuts", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create a table of shortcuts
        for i, (key, desc) in enumerate(shortcuts):
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=2)
            
            ttk.Label(row, text=key, width=15).pack(side=tk.LEFT)
            ttk.Label(row, text=desc).pack(side=tk.LEFT, padx=10)
            
            if i < len(shortcuts) - 1:
                ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=2)
        
        ttk.Button(frame, text="Close", command=dialog.destroy).pack(pady=10)
    
    def show_about(self):
        """Display information about the application."""
        about_text = """PDF Reader & Editor

Version 1.0

A modern PDF viewer and editor with annotation capabilities.
Created as a Python application with Tkinter.

Features:
- View and navigate PDF documents
- Search text with highlighting
- Annotate with highlights, drawings, and notes
- Save edits back to PDF files
- Export pages as PDF or PNG
- OCR support for text extraction

© 2025 PDF Reader Project
"""
        messagebox.showinfo("About PDF Reader & Editor", about_text)


def main():
    """Main function to start the application."""
    app = PDFReaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
