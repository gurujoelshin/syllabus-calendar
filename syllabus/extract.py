"""
Turn an uploaded syllabus file (PDF or DOCX) into plain text.

The AI only ever sees the text this file produces, so if the AI misses
something, a good first check is to print what extract_text() returned.
"""

from pathlib import Path

from docx import Document
from pypdf import PdfReader
from pypdf.errors import PdfReadError

ALLOWED_EXTENSIONS = [".pdf", ".docx"]

# A syllabus with less text than this is almost certainly a scanned
# image (a picture of the pages) rather than real text.
MINIMUM_TEXT_LENGTH = 50


class ExtractionError(Exception):
    """Raised when we can't get usable text out of a file.

    The message is written so it can be shown directly to the user.
    """


def extract_text(uploaded_file):
    """Return the text inside a .pdf or .docx file.

    uploaded_file is the file object Django gives us from the upload
    form. It has a .name (like "CS101_syllabus.pdf") and can be read
    like a normal file.
    """
    extension = Path(uploaded_file.name).suffix.lower()

    if extension == ".pdf":
        text = extract_pdf_text(uploaded_file)
    elif extension == ".docx":
        text = extract_docx_text(uploaded_file)
    else:
        raise ExtractionError("Please upload a .pdf or .docx file.")

    if len(text.strip()) < MINIMUM_TEXT_LENGTH:
        raise ExtractionError(
            "We couldn't find any text in that file. If it's a scanned "
            "copy (a picture of the pages), try a text-based PDF or a "
            "Word version of the syllabus instead."
        )
    return text


def extract_pdf_text(file):
    """Read every page of a PDF and join the text together."""
    try:
        reader = PdfReader(file)

        # Some PDFs are "encrypted" with a blank password and open fine;
        # decrypt("") returns 0 only if a real password is needed.
        if reader.is_encrypted and reader.decrypt("") == 0:
            raise ExtractionError("That PDF is password-protected.")

        pages = []
        for number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            # Page markers help the AI (and you) see where text came from.
            pages.append(f"--- Page {number} ---\n{page_text}")
        return "\n\n".join(pages)

    except PdfReadError:
        raise ExtractionError("That PDF couldn't be read. It may be damaged.")


def extract_docx_text(file):
    """Read the paragraphs and tables of a Word document."""
    try:
        document = Document(file)
    except Exception:
        # python-docx raises several different errors for files that
        # aren't really .docx files, so we catch them all here.
        raise ExtractionError("That Word file couldn't be read. It may be damaged.")

    lines = [paragraph.text for paragraph in document.paragraphs]

    # Course schedules are usually tables, and Word stores tables
    # separately from normal paragraphs, so we read them too. Each row
    # becomes one line with " | " between the cells.
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            lines.append(" | ".join(cells))

    return "\n".join(lines)
