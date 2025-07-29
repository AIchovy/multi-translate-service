"""
File utilities for the Multi Translate Service
"""
import requests
import tempfile
import os
from typing import Optional
from urllib.parse import urlparse


# Download url file to temp file, return temp file path
def download_url_to_temp_file(url: str, suffix: Optional[str] = None) -> str:
    """
    Download a file from URL to a temporary file.
    
    Args:
        url: The URL to download from
        suffix: Optional file suffix/extension for the temp file
        
    Returns:
        str: Path to the temporary file
        
    Raises:
        requests.RequestException: If download fails
        IOError: If file writing fails
    """
    try:
        # Parse URL to get filename if suffix not provided
        if suffix is None:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if '.' in filename:
                suffix = '.' + filename.split('.')[-1]
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file_path = temp_file.name
        
        # Download file with streaming to handle large files
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Write content to temporary file
        with open(temp_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return temp_file_path
        
    except requests.RequestException as e:
        # Clean up temp file if it was created
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise requests.RequestException(f"Failed to download file from URL: {str(e)}")
    
    except IOError as e:
        # Clean up temp file if it was created
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise IOError(f"Failed to write downloaded file: {str(e)}")


def cleanup_temp_file(file_path: str) -> None:
    """
    Clean up temporary file.
    
    Args:
        file_path: Path to the temporary file to delete
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except OSError:
        # Ignore errors when cleaning up temp files
        pass

if __name__ == "__main__":
    url = "https://tensorbounce-prod.oss-cn-shenzhen.aliyuncs.com/youxue/1.mp3"
    temp_file_path = download_url_to_temp_file(url)
    print(temp_file_path)
  