from typing import List, Optional
import re


def split_text_by_chunk(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separator: str = "\n",
) -> List[str]:
    """
    Split text into chunks of approximately chunk_size characters with overlap.
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        separator: String to split on to ensure chunks don't break in the middle of a word or sentence
        
    Returns:
        List of text chunks
    """
    # Ensure the chunk_size is reasonable
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")
    
    # If the text is short enough, return it as a single chunk
    if len(text) <= chunk_size:
        return [text]
    
    # Split text by separator
    splits = text.split(separator)
    
    # Initialize chunks
    chunks = []
    current_chunk = []
    current_length = 0
    
    for split in splits:
        # Add separator back to the split except for the first one
        if current_length > 0:
            split_with_separator = separator + split
        else:
            split_with_separator = split
        
        split_length = len(split_with_separator)
        
        # If adding this split would exceed the chunk size and we already have content,
        # finish the current chunk and start a new one
        if current_length + split_length > chunk_size and current_length > 0:
            chunks.append(separator.join(current_chunk))
            
            # If we have overlap, keep some of the current chunk for the next one
            if chunk_overlap > 0:
                # Find where to start the next chunk by figuring out which splits to keep
                overlap_length = 0
                overlap_splits = []
                
                for i in range(len(current_chunk) - 1, -1, -1):
                    split_text = current_chunk[i]
                    if i > 0:  # Add separator for all except the first split
                        split_text = separator + split_text
                    
                    overlap_length += len(split_text)
                    
                    if overlap_length > chunk_overlap:
                        # We've reached our overlap target
                        overlap_splits = current_chunk[i:]
                        break
                    
                    overlap_splits.insert(0, current_chunk[i])
                
                current_chunk = overlap_splits
                current_length = sum(len(s) + len(separator) for s in current_chunk[:-1]) + len(current_chunk[-1])
            else:
                current_chunk = []
                current_length = 0
        
        # Add the current split to the chunk
        current_chunk.append(split)
        current_length += split_length
    
    # Add the final chunk if there's anything left
    if current_chunk:
        chunks.append(separator.join(current_chunk))
    
    return chunks


def split_text_by_sentence(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    min_sentences: int = 1
) -> List[str]:
    """
    Split text into chunks trying to keep sentences intact.
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        min_sentences: Minimum number of sentences per chunk
        
    Returns:
        List of text chunks
    """
    # Simple sentence splitter pattern
    sentence_endings = r'(?<=[.!?])\s+'
    sentences = re.split(sentence_endings, text)
    
    # Remove empty sentences
    sentences = [s for s in sentences if s.strip()]
    
    # If the text is short enough, return it as a single chunk
    if len(text) <= chunk_size:
        return [text]
    
    # Initialize chunks
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        
        # If a single sentence is longer than chunk_size, split it
        if sentence_length > chunk_size:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
            
            # Split the long sentence
            sentence_chunks = split_text_by_chunk(
                sentence, 
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap, 
                separator=" "
            )
            
            chunks.extend(sentence_chunks)
            continue
        
        # If adding this sentence would exceed the chunk size and we have at least min_sentences,
        # finish the current chunk and start a new one
        if current_length + sentence_length > chunk_size and len(current_chunk) >= min_sentences:
            chunks.append(" ".join(current_chunk))
            
            # If we have overlap, keep some sentences for the next chunk
            if chunk_overlap > 0:
                # Keep sentences until we reach the desired overlap
                overlap_length = 0
                overlap_sentences = []
                
                for i in range(len(current_chunk) - 1, -1, -1):
                    overlap_length += len(current_chunk[i])
                    
                    if overlap_length > chunk_overlap:
                        # We've reached our overlap target
                        overlap_sentences = current_chunk[i:]
                        break
                    
                    overlap_sentences.insert(0, current_chunk[i])
                
                current_chunk = overlap_sentences
                current_length = sum(len(s) for s in current_chunk)
            else:
                current_chunk = []
                current_length = 0
        
        # Add the current sentence to the chunk
        current_chunk.append(sentence)
        current_length += sentence_length
    
    # Add the final chunk if there's anything left
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


def split_text_semantic(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    embedding_service = None
) -> List[str]:
    """
    Split text into semantically meaningful chunks.
    This is a placeholder for a more sophisticated implementation that would
    use embeddings to ensure similar content stays together.
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        embedding_service: Optional embedding service for semantic splitting
        
    Returns:
        List of text chunks
    """
    # If no embedding service is provided, fall back to sentence splitting
    if embedding_service is None:
        return split_text_by_sentence(text, chunk_size, chunk_overlap)
    
    # For now, just use sentence splitting
    # In a future implementation, this would use embeddings to
    # determine semantic boundaries
    return split_text_by_sentence(text, chunk_size, chunk_overlap)


def split_markdown(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[str]:
    """
    Split markdown text, trying to preserve the structure.
    
    Args:
        text: Markdown text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of markdown chunks
    """
    # Try to split at heading boundaries first
    heading_pattern = r'(^|\n)(#{1,6} .+?(?:\n|$))'
    sections = re.split(heading_pattern, text)
    
    # Recombine the separated headings with their content
    chunks = []
    current_chunk = ""
    heading = ""
    
    for i, section in enumerate(sections):
        # Skip empty sections
        if not section.strip():
            continue
        
        # Check if this is a heading (starts with #)
        if re.match(r'^#{1,6} ', section.strip()):
            heading = section
            continue
        
        # If this is content and we have a heading, combine them
        if heading and i > 0:
            section_with_heading = heading + section
            heading = ""
        else:
            section_with_heading = section
        
        # If adding this section would exceed the chunk size and we already have content,
        # finish the current chunk and start a new one
        if len(current_chunk) + len(section_with_heading) > chunk_size and current_chunk:
            chunks.append(current_chunk)
            
            # Calculate overlap
            if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                # Try to find paragraph breaks for cleaner overlap
                overlap_text = current_chunk[-chunk_overlap:]
                paragraph_match = re.search(r'\n\n', overlap_text)
                
                if paragraph_match:
                    overlap_start = len(overlap_text) - paragraph_match.start()
                    current_chunk = current_chunk[-overlap_start:]
                else:
                    current_chunk = current_chunk[-chunk_overlap:]
            else:
                current_chunk = ""
        
        # Add the current section to the chunk
        current_chunk += section_with_heading
        
        # If the current chunk is already over the chunk size, finish it
        if len(current_chunk) > chunk_size:
            chunks.append(current_chunk)
            current_chunk = ""
    
    # Add the final chunk if there's anything left
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks
