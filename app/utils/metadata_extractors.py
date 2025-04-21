from typing import Dict, Any, Optional
import os
import re
import json
import datetime
from loguru import logger


def extract_metadata_from_filename(filename: str) -> Dict[str, Any]:
    """
    Extract metadata from a filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        Dictionary of extracted metadata
    """
    metadata = {}
    
    # Extract file extension
    _, ext = os.path.splitext(filename)
    if ext:
        metadata["extension"] = ext.lower().lstrip(".")
    
    # Try to extract date from filename
    date_patterns = [
        # YYYY-MM-DD
        (r'(\d{4})[_-](\d{1,2})[_-](\d{1,2})', "%Y-%m-%d"),
        # DD-MM-YYYY
        (r'(\d{1,2})[_-](\d{1,2})[_-](\d{4})', "%d-%m-%Y"),
        # Plain YYYYMMDD
        (r'(\d{4})(\d{2})(\d{2})', "%Y%m%d")
    ]
    
    for pattern, date_format in date_patterns:
        match = re.search(pattern, filename)
        if match:
            try:
                if date_format == "%Y-%m-%d":
                    date_str = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                elif date_format == "%d-%m-%Y":
                    date_str = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                else:  # %Y%m%d
                    date_str = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                metadata["date"] = date_obj.isoformat()
                break
            except ValueError:
                # Invalid date, continue to next pattern
                pass
    
    # Extract PMQA category if present
    category_match = re.search(r'หมวด[_-]?(\d)', filename, re.IGNORECASE)
    if category_match:
        category_num = category_match.group(1)
        metadata["category"] = f"หมวด_{category_num}"
    
    # Extract title
    # Remove extension and clean up
    title = os.path.splitext(filename)[0]
    # Remove date patterns
    for pattern, _ in date_patterns:
        title = re.sub(pattern, "", title)
    # Remove category pattern
    title = re.sub(r'หมวด[_-]?\d', "", title, flags=re.IGNORECASE)
    # Clean up separators and extra spaces
    title = re.sub(r'[_-]+', " ", title)
    title = re.sub(r'\s+', " ", title).strip()
    
    if title:
        metadata["title"] = title
    
    return metadata


def extract_metadata_from_text(text: str) -> Dict[str, Any]:
    """
    Extract metadata from the content of a text document.
    
    Args:
        text: Document text
        
    Returns:
        Dictionary of extracted metadata
    """
    metadata = {}
    
    # Try to extract date
    date_patterns = [
        # Common formats with various separators
        r'วันที่\s*(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})',
        r'(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})',
        r'ลงวันที่\s*(\d{1,2})\s*(มกราคม|กุมภาพันธ์|มีนาคม|เมษายน|พฤษภาคม|มิถุนายน|กรกฎาคม|สิงหาคม|กันยายน|ตุลาคม|พฤศจิกายน|ธันวาคม)\s*(\d{4})'
    ]
    
    # Thai month mapping
    thai_months = {
        "มกราคม": 1, "กุมภาพันธ์": 2, "มีนาคม": 3, "เมษายน": 4,
        "พฤษภาคม": 5, "มิถุนายน": 6, "กรกฎาคม": 7, "สิงหาคม": 8,
        "กันยายน": 9, "ตุลาคม": 10, "พฤศจิกายน": 11, "ธันวาคม": 12
    }
    
    # Check first 2000 characters for date
    text_sample = text[:2000]
    
    for pattern in date_patterns:
        match = re.search(pattern, text_sample)
        if match:
            try:
                if len(match.groups()) == 3 and match.group(2) in thai_months:
                    # Thai format with month name
                    day = int(match.group(1))
                    month = thai_months[match.group(2)]
                    year = int(match.group(3))
                    # Adjust for Thai year if needed
                    if year > 2400:
                        year -= 543
                elif pattern.startswith(r'(\d{4})'):
                    # YYYY-MM-DD format
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                else:
                    # DD-MM-YYYY format
                    day = int(match.group(1))
                    month = int(match.group(2))
                    year = int(match.group(3))
                
                date_obj = datetime.datetime(year, month, day)
                metadata["date"] = date_obj.isoformat()
                break
            except (ValueError, IndexError):
                # Invalid date, continue to next pattern
                pass
    
    # Try to extract title from first non-empty line
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line and len(line) > 5 and len(line) < 200:  # Reasonable title length
            # Check if it's not a date line or other metadata
            if not re.search(r'^\d+[/.-]\d+[/.-]\d+$', line) and not re.search(r'^วันที่', line):
                metadata["title"] = line
                break
    
    # Try to extract author/organization
    org_patterns = [
        r'(?:โดย|จัดทำโดย|จาก|ผู้จัดทำ)[:\s]+([\w\s]+)',
        r'(กรม[\w\s]+|สำนัก[\w\s]+|กระทรวง[\w\s]+)'
    ]
    
    for pattern in org_patterns:
        match = re.search(pattern, text_sample)
        if match:
            author = match.group(1).strip()
            metadata["author"] = author
            break
    
    # Try to extract PMQA category
    pmqa_patterns = [
        r'หมวด\s*(\d)\s*[:-]?\s*([\w\s]+)',
        r'หมวดที่\s*(\d)\s*[:-]?\s*([\w\s]+)'
    ]
    
    for pattern in pmqa_patterns:
        match = re.search(pattern, text_sample)
        if match:
            category_num = match.group(1)
            metadata["category"] = f"หมวด_{category_num}"
            
            # Get category name if available
            if match.group(2):
                metadata["category_name"] = match.group(2).strip()
            
            break
    
    return metadata


def extract_metadata_from_pdf_info(pdf_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from PDF document info.
    
    Args:
        pdf_info: PDF document info dictionary
        
    Returns:
        Dictionary of extracted metadata
    """
    metadata = {}
    
    # Common metadata fields in PDF
    field_mapping = {
        "Title": "title",
        "Author": "author",
        "Subject": "subject",
        "Keywords": "keywords",
        "Creator": "creator",
        "Producer": "producer",
        "ModDate": "modified_date",
        "CreationDate": "creation_date"
    }
    
    for pdf_field, meta_field in field_mapping.items():
        if pdf_field in pdf_info and pdf_info[pdf_field]:
            value = pdf_info[pdf_field]
            
            # Handle dates
            if meta_field.endswith('_date') and isinstance(value, str):
                # Try to parse PDF date format (D:YYYYMMDDHHmmSS)
                date_match = re.match(r'D:(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', value)
                if date_match:
                    try:
                        year = int(date_match.group(1))
                        month = int(date_match.group(2))
                        day = int(date_match.group(3))
                        hour = int(date_match.group(4))
                        minute = int(date_match.group(5))
                        second = int(date_match.group(6))
                        
                        date_obj = datetime.datetime(year, month, day, hour, minute, second)
                        metadata[meta_field] = date_obj.isoformat()
                    except ValueError:
                        metadata[meta_field] = value
                else:
                    metadata[meta_field] = value
            
            # Handle keywords
            elif meta_field == "keywords" and isinstance(value, str):
                # Split keywords string into list
                keywords = [kw.strip() for kw in value.split(",") if kw.strip()]
                if keywords:
                    metadata[meta_field] = keywords
            else:
                metadata[meta_field] = value
    
    return metadata


def extract_metadata_from_frontmatter(text: str) -> Dict[str, Any]:
    """
    Extract metadata from YAML or JSON frontmatter.
    
    Args:
        text: Document text with frontmatter
        
    Returns:
        Dictionary of extracted metadata
    """
    metadata = {}
    
    # Check for YAML frontmatter (---)
    yaml_match = re.match(r'---\s+(.*?)\s+---', text, re.DOTALL)
    if yaml_match:
        try:
            # For proper YAML parsing we would use PyYAML here,
            # but for simplicity we'll just extract key-value pairs
            frontmatter = yaml_match.group(1)
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        metadata[key] = value
            
            return metadata
        except Exception as e:
            logger.error(f"Error parsing YAML frontmatter: {str(e)}")
    
    # Check for JSON frontmatter (```json)
    json_match = re.match(r'```json\s+(.*?)\s+```', text, re.DOTALL)
    if json_match:
        try:
            frontmatter = json_match.group(1)
            metadata = json.loads(frontmatter)
            return metadata
        except Exception as e:
            logger.error(f"Error parsing JSON frontmatter: {str(e)}")
    
    return metadata


def extract_metadata_from_file(
    file_path: str, 
    file_content: str = None
) -> Dict[str, Any]:
    """
    Extract metadata from a file using all available methods.
    
    Args:
        file_path: Path to the file
        file_content: Optional file content (to avoid reading large files multiple times)
        
    Returns:
        Dictionary of extracted metadata
    """
    metadata = {}
    
    try:
        # Get basic file info
        filename = os.path.basename(file_path)
        file_stats = os.stat(file_path)
        
        metadata.update({
            "filename": filename,
            "file_path": file_path,
            "size": file_stats.st_size,
            "created_at": datetime.datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            "modified_at": datetime.datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        })
        
        # Extract metadata from filename
        filename_metadata = extract_metadata_from_filename(filename)
        metadata.update(filename_metadata)
        
        # Get MIME type
        extension = os.path.splitext(filename)[1].lower()
        mime_type = None
        
        if extension in ['.txt', '.md', '.markdown']:
            mime_type = f"text/{extension[1:]}"
        elif extension == '.pdf':
            mime_type = "application/pdf"
        elif extension in ['.docx', '.doc']:
            mime_type = "application/msword"
        elif extension == '.html':
            mime_type = "text/html"
        
        if mime_type:
            metadata["mimetype"] = mime_type
        
        # If content is provided or file is text-based, extract metadata from content
        if file_content is not None or mime_type and mime_type.startswith('text/'):
            # Read content if not provided
            if file_content is None:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                except Exception as e:
                    logger.warning(f"Could not read file content for metadata extraction: {str(e)}")
                    file_content = ""
            
            # Extract metadata from content
            if file_content:
                # Check for frontmatter first
                frontmatter_metadata = extract_metadata_from_frontmatter(file_content)
                if frontmatter_metadata:
                    metadata.update(frontmatter_metadata)
                
                # Extract from text content
                text_metadata = extract_metadata_from_text(file_content)
                
                # Only update metadata if not already set from frontmatter
                for key, value in text_metadata.items():
                    if key not in metadata:
                        metadata[key] = value
        
        # If we have a category but not a title, use the filename as title
        if "category" in metadata and "title" not in metadata:
            title = os.path.splitext(filename)[0]
            # Remove category and date information
            title = re.sub(r'หมวด[_-]?\d', "", title, flags=re.IGNORECASE)
            title = re.sub(r'\d{4}[_-]\d{2}[_-]\d{2}', "", title)
            title = re.sub(r'\d{2}[_-]\d{2}[_-]\d{4}', "", title)
            # Clean up separators and extra spaces
            title = re.sub(r'[_-]+', " ", title)
            title = re.sub(r'\s+', " ", title).strip()
            
            if title:
                metadata["title"] = title
    
    except Exception as e:
        logger.error(f"Error extracting metadata from file {file_path}: {str(e)}")
    
    return metadata
