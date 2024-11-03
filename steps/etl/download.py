import io
import zipfile
from typing import List, Dict, Any
import requests
from loguru import logger
from urllib.parse import parse_qs, urlparse
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_content: bytes) -> Dict[str, Any]:
    """Extract text content from PDF bytes."""
    try:
        # Create a memory buffer for the PDF
        pdf_buffer = io.BytesIO(pdf_content)
        
        # Initialize document structure
        document = {
            "content": "",
            "pages": [],
            "metadata": {}
        }
        
        # Open PDF with PyMuPDF
        with fitz.open(stream=pdf_buffer, filetype="pdf") as doc:
            full_text = []
            
            # Get document metadata
            document["metadata"] = {
                "page_count": len(doc),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", "")
            }
            
            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get text blocks with their coordinates
                blocks = page.get_text("blocks")
                
                # Sort blocks top to bottom, left to right
                blocks.sort(key=lambda b: (b[1], b[0]))  # Sort by y-coordinate, then x-coordinate
                
                # Extract text from blocks
                page_text = "\n".join(block[4] for block in blocks if block[4].strip())
                
                if page_text.strip():
                    document["pages"].append({
                        "page": page_num + 1,
                        "text": page_text.strip()
                    })
                    full_text.append(page_text)
            
            # Combine all text
            document["content"] = "\n".join(full_text)
            
            logger.info(f"Extracted {len(document['pages'])} pages with content")
            
            return document
            
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise

def download_zip(zip_url: str) -> List[Dict[str, Any]]:
    """Download and extract documents from zip file."""
    try:
        # Handle Google redirect URLs
        if "google.com/url" in zip_url:
            parsed = urlparse(zip_url)
            query_params = parse_qs(parsed.query)
            if 'q' in query_params:
                zip_url = query_params['q'][0]
                logger.info(f"Extracted actual URL from Google redirect: {zip_url}")

        # Download the file
        logger.info(f"Downloading zip file from: {zip_url}")
        response = requests.get(zip_url, verify=False)  # Added verify=False for testing
        response.raise_for_status()
        
        logger.info(f"Downloaded {len(response.content)} bytes")

        documents = []
        try:
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                # Filter out macOS metadata and non-PDF files
                pdf_files = [
                    f for f in zip_ref.namelist() 
                    if f.lower().endswith('.pdf') 
                    and not f.startswith('__MACOSX') 
                    and not f.startswith('.')
                    and not f.endswith('/')
                ]
                
                logger.info(f"Found {len(pdf_files)} PDF files in zip")
                
                for file_name in pdf_files:
                    logger.info(f"Processing PDF: {file_name}")
                    
                    # Extract PDF content
                    with zip_ref.open(file_name) as pdf_file:
                        pdf_content = pdf_file.read()
                        logger.info(f"Read {len(pdf_content)} bytes from {file_name}")
                        
                        try:
                            # Extract text from PDF
                            doc = extract_text_from_pdf(pdf_content)
                            
                            # Add source information
                            doc["source"] = file_name
                            doc["type"] = "earnings_call"
                            
                            if doc["content"].strip():
                                documents.append(doc)
                                logger.info(f"Successfully extracted text from {file_name}: "
                                          f"{len(doc['content'])} chars, "
                                          f"{len(doc['pages'])} pages")
                            else:
                                logger.warning(f"No text content found in {file_name}")
                                
                        except Exception as e:
                            logger.error(f"Error processing PDF {file_name}: {str(e)}")
                            continue
                            
                logger.info(f"Successfully processed {len(documents)} documents from zip file")
                
        except zipfile.BadZipFile as e:
            logger.error(f"Error extracting zip file: {str(e)}")
            logger.error(f"Response content type: {response.headers.get('content-type')}")
            logger.error(f"Response status code: {response.status_code}")
            raise

        return documents

    except Exception as e:
        logger.error(f"Error downloading/extracting zip file: {str(e)}")
        raise