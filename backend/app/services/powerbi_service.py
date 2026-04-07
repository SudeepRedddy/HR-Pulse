import os
import tempfile
import zipfile

def generate_pbix() -> str:
    """
    Generates a dummy .pbix file.
    In reality, .pbix is a ZIP archive containing specific Power BI XML/JSON schemas.
    We just mock a zip file here for the user to download as fallback validation.
    """
    fd, path = tempfile.mkstemp(suffix=".pbix")
    with os.fdopen(fd, 'wb') as f:
        with zipfile.ZipFile(f, 'w') as zf:
            zf.writestr("Content_Types.xml", "<Types xmlns='...'><Default Extension='xml' ContentType='application/xml'/></Types>")
            zf.writestr("DataModel", "MOCK DATA MODEL BYTES")
    return path
