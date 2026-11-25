import http.server
import socketserver
import os
import markdown # Requires: pip install markdown

PORT = 8000
NOTES_DIR = "notes"

# Ensure the notes directory exists and create a sample note if it doesn't
if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)
    with open(os.path.join(NOTES_DIR, "welcome.md"), "w", encoding="utf-8") as f:
        f.write("# Welcome to Your Notes App!\n\nThis is your first note, written in **Markdown**.\n\n- You can create new `.md` files in the `notes/` directory.\n- Each file will be accessible as a separate note.\n\nEnjoy your database-free note-taking experience!")

class MarkdownNotesHandler(http.server.SimpleHTTPRequestHandler):
    def _send_html_response(self, content, title="Notes"):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html_template = f"""
        <html>
        <head>
            <title>{title}</title>
            <style>
                body { font-family: sans-serif; margin: 2em; line-height: 1.6; max-width: 800px; margin-left: auto; margin-right: auto; }
                pre { background-color: #f4f4f4; padding: 1em; border-radius: 5px; overflow-x: auto; }
                code { font-family: monospace; }
                a { text-decoration: none; color: #007bff; } a:hover { text-decoration: underline; }
                nav { margin-bottom: 2em; }
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
        self.wfile.write(html_template.encode("utf-8"))

    def do_GET(self):
        if self.path == '/':
            # Generate an index page listing all markdown files in the notes directory
            notes_files = [f for f in os.listdir(NOTES_DIR) if f.endswith(".md")]
            list_items = ""
            for note_file in sorted(notes_files):
                note_name = os.path.splitext(note_file)[0].replace('_', ' ').title()
                list_items += f'<li><a href="/note/{note_file}">{note_name}</a></li>'
            
            content = f"""
            <h1>My Database-Free Notes</h1>
            <p>Click on a note to view its content:</p>
            <ul>{list_items}</ul>
            """
            self._send_html_response(content, "My Notes")
            return
        
        if self.path.startswith('/note/') and self.path.endswith('.md'):
            note_filename = os.path.basename(self.path)
            note_filepath = os.path.join(NOTES_DIR, note_filename)

            if os.path.exists(note_filepath) and os.path.isfile(note_filepath):
                try:
                    with open(note_filepath, "r", encoding="utf-8") as f:
                        markdown_content = f.read()
                    
                    # Core concept: Convert Markdown content to HTML using the markdown library
                    html_content = markdown.markdown(markdown_content) 

                    note_title = os.path.splitext(note_filename)[0].replace('_', ' ').title()
                    content = f"""
                    <nav><a href="/">← Back to Notes List</a></nav>
                    {html_content}
                    """
                    self._send_html_response(content, note_title)
                except Exception as e:
                    self.send_error(500, f"Error reading or processing note: {e}")
            else:
                self.send_error(404, "Note not found")
            return
        
        self.send_error(404, "Not Found")

# Set up the server
with socketserver.TCPServer(('', PORT), MarkdownNotesHandler) as httpd:
    print(f"Serving notes from '{NOTES_DIR}' at http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server.")
    httpd.serve_forever()
