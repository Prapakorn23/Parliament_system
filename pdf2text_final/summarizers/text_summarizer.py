import os
import sys
from typing import Optional
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
	from apis.typhoon_client import typhoon_client
	_HAS_TYPHOON = True
except Exception as e:
	print(f"Warning: Could not import Typhoon client: {e}")
	_HAS_TYPHOON = False


def _clean_text_for_summarization(text: str) -> str:
    """Enhanced text cleaning and preparation for better summarization with performance optimization."""
    if not text or len(text.strip()) < 10:
        return text.strip()
    
    # Use more efficient regex patterns and limit processing for very large texts
    text_length = len(text)
    
    # For very large texts, use simpler cleaning to improve performance
    if text_length > 100000:
        # Simplified cleaning for very large texts
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'----- PAGE BREAK -----', '', text)
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        return text.strip()
    
    # Standard cleaning for normal-sized texts
    # Remove excessive whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove page break markers and headers/footers
    text = re.sub(r'----- PAGE BREAK -----', '', text)
    text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)  # Remove standalone page numbers
    
    # Remove common PDF artifacts but keep important punctuation and Thai characters
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'ก-๙]', ' ', text)
    
    # Normalize Thai text spacing (only if Thai characters detected)
    if re.search(r'[ก-๙]', text):
        text = re.sub(r'([ก-๙])\s+([ก-๙])', r'\1\2', text)  # Remove spaces between Thai characters
    
    # Remove repetitive patterns (common in OCR) - limit iterations for performance
    if text_length < 50000:  # Only for smaller texts to avoid performance issues
        text = re.sub(r'(.{2,})\1{2,}', r'\1', text)  # Remove repeated phrases
    
    # Clean up sentence boundaries
    text = re.sub(r'\.\s*\.+', '.', text)  # Multiple periods to single
    text = re.sub(r'([.!?])\s*([a-zA-Zก-๙])', r'\1 \2', text)  # Ensure space after sentence endings
    
    return text.strip()


def _extract_key_sentences(text: str, num_sentences: int = 8) -> list:
    """Enhanced key sentence extraction with improved coverage and clarity with performance optimization."""
    # Optimize for large texts by limiting sentence processing
    text_length = len(text)
    if text_length > 200000:
        # For very large texts, use simplified extraction
        sentences = re.split(r'[.!?]+', text[:100000])  # Process only first 100k characters
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 15]
        return sentences[:min(num_sentences, len(sentences))]
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
    
    if len(sentences) <= num_sentences:
        return sentences
    
    # Enhanced scoring algorithm for better coverage and clarity
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = 0
        
        # Length factor (optimal length for clarity)
        sentence_length = len(sentence)
        if 30 <= sentence_length <= 150:  # Optimal length for clarity
            length_score = 0.3
        elif 20 <= sentence_length <= 200:  # Acceptable length
            length_score = 0.2
        else:
            length_score = 0.1
        score += length_score
        
        # Position factor (balanced coverage across text)
        position_ratio = i / len(sentences)
        if position_ratio < 0.15:  # Beginning - high importance for context
            position_score = 0.4
        elif position_ratio > 0.85:  # End - high importance for conclusions
            position_score = 0.4
        elif 0.25 <= position_ratio <= 0.75:  # Middle - moderate importance
            position_score = 0.2
        else:
            position_score = 0.15
        score += position_score
        
        # Enhanced keyword density factor for better coverage
        sentence_lower = sentence.lower()
        high_importance_words = [
            # Core concepts
            'สำคัญ', 'หลัก', 'สำคัญที่สุด', 'หลักการ', 'แนวทาง', 'วัตถุประสงค์',
            'important', 'main', 'key', 'critical', 'principle', 'objective',
            # Analysis and results
            'วิเคราะห์', 'ประเด็น', 'ผลลัพธ์', 'ข้อสรุป', 'สรุป', 'ผล',
            'analysis', 'issue', 'result', 'conclusion', 'summary', 'outcome',
            # Problem and solution
            'ปัญหา', 'อุปสรรค', 'ข้อจำกัด', 'วิธีแก้', 'การแก้ไข', 'แนวทางแก้',
            'problem', 'obstacle', 'limitation', 'solution', 'resolution', 'approach',
            # Development and improvement
            'การพัฒนา', 'การปรับปรุง', 'การเปลี่ยนแปลง', 'การดำเนินการ',
            'development', 'improvement', 'change', 'implementation',
            # Specific details
            'รายละเอียด', 'ข้อมูล', 'สถิติ', 'ตัวเลข', 'เปอร์เซ็นต์',
            'detail', 'information', 'statistics', 'number', 'percentage'
        ]
        keyword_count = sum(1 for word in high_importance_words if word in sentence_lower)
        keyword_score = min(keyword_count * 0.12, 0.4)
        score += keyword_score
        
        # Topic coverage factor (sentences that introduce new topics)
        topic_indicators = [
            'ในเรื่องของ', 'เกี่ยวกับ', 'ด้าน', 'ส่วน', 'ประเภท', 'รูปแบบ', 'ลักษณะ',
            'regarding', 'concerning', 'aspect', 'section', 'type', 'form', 'feature'
        ]
        topic_count = sum(1 for indicator in topic_indicators if indicator in sentence_lower)
        score += topic_count * 0.08
        
        # Definition and explanation factor (for clarity)
        definition_patterns = [
            'หมายถึง', 'คือ', 'เป็น', 'ได้แก่', 'ประกอบด้วย', 'มีลักษณะ',
            'means', 'is', 'are', 'includes', 'consists', 'features'
        ]
        definition_count = sum(1 for pattern in definition_patterns if pattern in sentence_lower)
        score += definition_count * 0.1
        
        # Numerical and factual data factor
        if re.search(r'\d+', sentence):
            score += 0.15
        if re.search(r'[%]|เปอร์เซ็นต์|percent', sentence_lower):
            score += 0.1
        if re.search(r'[0-9]+[.,][0-9]+', sentence):  # Decimal numbers
            score += 0.08
        
        # Question/answer pattern factor (for context and clarity)
        if sentence.endswith('?'):
            score += 0.05  # Questions provide context
        if sentence.startswith(('ทำไม', 'อย่างไร', 'อะไร', 'เมื่อไหร่', 'ที่ไหน', 'ใคร')):
            score += 0.1
        
        # Transition and connection factor (for flow and clarity)
        transition_words = [
            'นอกจากนี้', 'อีกทั้ง', 'อย่างไรก็ตาม', 'ดังนั้น', 'เพราะฉะนั้น', 'สรุปแล้ว',
            'furthermore', 'however', 'therefore', 'thus', 'moreover', 'in conclusion'
        ]
        transition_count = sum(1 for word in transition_words if word in sentence_lower)
        score += transition_count * 0.06
        
        scored_sentences.append((score, sentence, i))
    
    # Enhanced selection for better coverage
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    
    # Ensure balanced coverage across the text
    selected_sentences = []
    text_sections = 4  # Divide text into 4 sections
    section_size = len(sentences) // text_sections
    section_counts = [0] * text_sections
    
    for score, sentence, position in scored_sentences:
        if len(selected_sentences) >= num_sentences:
            break
        
        # Determine which section this sentence belongs to
        section = min(position // max(1, section_size), text_sections - 1)
        
        # Allow selection if:
        # 1. We haven't reached the target number yet, OR
        # 2. This section is underrepresented, OR
        # 3. We need at least one sentence from each section
        max_per_section = max(1, num_sentences // text_sections)
        if (len(selected_sentences) < num_sentences and 
            (section_counts[section] < max_per_section or 
             len(selected_sentences) < num_sentences // 2)):
            
            selected_sentences.append(sentence)
            section_counts[section] += 1
    
    # Sort back to original order to maintain flow and clarity
    selected_sentences.sort(key=lambda x: sentences.index(x))
    
    return selected_sentences


def _create_enhanced_narrative_summary(sentences: list, is_thai: bool) -> str:
    """Create an enhanced narrative summary with improved coverage, clarity, and organization."""
    if not sentences:
        return ""
    
    if len(sentences) == 1:
        return sentences[0] + "."
    
    # Enhanced sentence processing for better clarity and flow
    processed_sentences = []
    for i, sentence in enumerate(sentences):
        # Clean and enhance each sentence for clarity
        cleaned_sentence = _enhance_sentence_clarity(sentence, is_thai)
        
        # Add appropriate connectors for better narrative flow
        if i == 0:
            processed_sentences.append(cleaned_sentence)
        else:
            # Use smarter connector selection for better flow
            connector = _select_enhanced_connector(cleaned_sentence, i, len(sentences), is_thai)
            processed_sentences.append(f"{connector} {cleaned_sentence}")
    
    # Create organized narrative with enhanced paragraph structure for better clarity
    if len(processed_sentences) > 15:
        # For very long summaries, create four paragraphs for comprehensive coverage
        quarter_point = len(processed_sentences) // 4
        paragraph1 = ". ".join(processed_sentences[:quarter_point]) + "."
        paragraph2 = ". ".join(processed_sentences[quarter_point:quarter_point*2]) + "."
        paragraph3 = ". ".join(processed_sentences[quarter_point*2:quarter_point*3]) + "."
        paragraph4 = ". ".join(processed_sentences[quarter_point*3:]) + "."
        return f"{paragraph1}\n\n{paragraph2}\n\n{paragraph3}\n\n{paragraph4}"
    elif len(processed_sentences) > 10:
        # For long summaries, create three paragraphs
        third_point = len(processed_sentences) // 3
        paragraph1 = ". ".join(processed_sentences[:third_point]) + "."
        paragraph2 = ". ".join(processed_sentences[third_point:third_point*2]) + "."
        paragraph3 = ". ".join(processed_sentences[third_point*2:]) + "."
        return f"{paragraph1}\n\n{paragraph2}\n\n{paragraph3}"
    elif len(processed_sentences) > 6:
        # For medium summaries, create two paragraphs
        mid_point = len(processed_sentences) // 2
        paragraph1 = ". ".join(processed_sentences[:mid_point]) + "."
        paragraph2 = ". ".join(processed_sentences[mid_point:]) + "."
        return f"{paragraph1}\n\n{paragraph2}"
    else:
        # For shorter summaries, create single flowing paragraph
        return ". ".join(processed_sentences) + "."


def _enhance_sentence_clarity(sentence: str, is_thai: bool) -> str:
    """Enhance sentence clarity and readability for better understanding."""
    if not sentence:
        return sentence
    
    # Remove redundant phrases for clarity
    redundant_patterns = []
    if is_thai:
        redundant_patterns = [
            r'ในเรื่องของ\s*',
            r'ในส่วนของ\s*',
            r'สำหรับเรื่อง\s*',
            r'เกี่ยวกับเรื่อง\s*',
            r'ในกรณีของ\s*',
            r'ในเรื่อง\s*',
        ]
    else:
        redundant_patterns = [
            r'in terms of\s*',
            r'with regard to\s*',
            r'regarding\s*',
            r'concerning\s*',
            r'in case of\s*',
            r'as for\s*',
        ]
    
    for pattern in redundant_patterns:
        sentence = re.sub(pattern, '', sentence, flags=re.IGNORECASE)
    
    # Improve sentence structure and clarity
    sentence = re.sub(r'\s+', ' ', sentence.strip())
    
    # Fix common clarity issues
    if is_thai:
        # Thai clarity improvements
        sentence = re.sub(r'\s+([ก-๙])\s+([ก-๙])', r'\1\2', sentence)  # Remove spaces between Thai chars
        sentence = re.sub(r'([ก-๙])\s+([.!?])', r'\1\2', sentence)  # Remove space before punctuation
        sentence = re.sub(r'([ก-๙])\s+([0-9])', r'\1 \2', sentence)  # Ensure space before numbers
    else:
        # English clarity improvements
        sentence = re.sub(r'\s+([.!?])', r'\1', sentence)  # Remove space before punctuation
        sentence = re.sub(r'([a-zA-Z])\s+([a-zA-Z])', r'\1 \2', sentence)  # Ensure space between words
    
    # Ensure proper capitalization for clarity
    if sentence and sentence[0].islower():
        sentence = sentence[0].upper() + sentence[1:]
    
    # Add clarity markers for important statements
    if is_thai:
        if any(word in sentence for word in ['สำคัญ', 'หลัก', 'ผล']):
            if not sentence.startswith('สิ่งที่'):
                sentence = sentence  # Keep as is for clarity
    else:
        if any(word in sentence.lower() for word in ['important', 'key', 'result']):
            sentence = sentence  # Keep as is for clarity
    
    return sentence


def _select_enhanced_connector(sentence: str, position: int, total: int, is_thai: bool) -> str:
    """Select enhanced connector based on content, position, and language for better clarity and organization."""
    if is_thai:
        # Thai connectors with improved clarity and organization
        sentence_lower = sentence.lower()
        
        # Position-based connectors for better organization
        if position == 1:
            return "นอกจากนี้"
        elif position == total - 1:
            return "สุดท้าย"
        elif position == total // 2:
            return "ในขณะเดียวกัน"
        
        # Content-based connectors for better clarity
        if any(word in sentence_lower for word in ["ผล", "ผลลัพธ์", "ผลที่ได้", "ผลกระทบ"]):
            return "ผลที่ได้คือ"
        elif any(word in sentence_lower for word in ["ปัญหา", "อุปสรรค", "ข้อจำกัด", "ความยาก"]):
            return "อย่างไรก็ตาม"
        elif any(word in sentence_lower for word in ["วิธี", "แนวทาง", "การแก้ไข", "การพัฒนา"]):
            return "โดยวิธีการ"
        elif any(word in sentence_lower for word in ["ข้อมูล", "รายละเอียด", "สถิติ", "ตัวเลข"]):
            return "ข้อมูลแสดงให้เห็นว่า"
        elif any(word in sentence_lower for word in ["สรุป", "ข้อสรุป", "สรุปแล้ว"]):
            return "สรุปแล้ว"
        elif any(word in sentence_lower for word in ["เป้าหมาย", "วัตถุประสงค์", "จุดประสงค์"]):
            return "เพื่อให้บรรลุ"
        else:
            # Default connectors based on position for better flow
            if position < total // 3:
                return "อีกทั้ง"
            elif position < 2 * total // 3:
                return "นอกจากนั้น"
            else:
                return "อีกประการหนึ่ง"
    else:
        # English connectors with improved clarity and organization
        sentence_lower = sentence.lower()
        
        # Position-based connectors for better organization
        if position == 1:
            return "Additionally"
        elif position == total - 1:
            return "Finally"
        elif position == total // 2:
            return "Meanwhile"
        
        # Content-based connectors for better clarity
        if any(word in sentence_lower for word in ["result", "outcome", "impact", "effect"]):
            return "As a result"
        elif any(word in sentence_lower for word in ["problem", "issue", "limitation", "challenge"]):
            return "However"
        elif any(word in sentence_lower for word in ["method", "approach", "solution", "development"]):
            return "Through the method"
        elif any(word in sentence_lower for word in ["data", "information", "statistics", "number"]):
            return "The data shows that"
        elif any(word in sentence_lower for word in ["summary", "conclusion", "conclude"]):
            return "In conclusion"
        elif any(word in sentence_lower for word in ["goal", "objective", "purpose", "aim"]):
            return "To achieve"
        else:
            # Default connectors based on position for better flow
            if position < total // 3:
                return "Furthermore"
            elif position < 2 * total // 3:
                return "Moreover"
            else:
                return "In addition"


# Removed: All ThaiBERT-related functions - using only Typhoon API now
# Functions removed: _summarize_with_ai, _summarize_large_text_with_ai, _hierarchical_summarization,
# _section_based_summarization, _direct_summarization, _extract_key_themes, _get_transformer_summarizer,
# _try_thaibert_summarizer

def _split_text_into_sections(text: str) -> list:
    """Enhanced text splitting into logical sections for better summarization."""
    # First try to split by major structural markers
    major_breaks = re.split(r'\n\s*[-=*]{3,}\s*\n', text)
    if len(major_breaks) > 1:
        return [section.strip() for section in major_breaks if section.strip()]
    
    # Try to split by paragraph breaks
    paragraphs = text.split('\n\n')
    if len(paragraphs) >= 2:
        # Filter out very short paragraphs and combine small ones
        filtered_paragraphs = []
        current_section = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            if len(paragraph) < 100 and current_section:
                # Combine short paragraphs
                current_section += " " + paragraph
            else:
                if current_section:
                    filtered_paragraphs.append(current_section)
                current_section = paragraph
        
        if current_section:
            filtered_paragraphs.append(current_section)
            
        return filtered_paragraphs
    
    # Fallback: Split by sentences with smart grouping
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
    
    if len(sentences) <= 3:
        return [text]
    
    # Smart sentence grouping based on content similarity
    sections = []
    current_section = []
    target_section_size = max(3, len(sentences) // 4)
    
    for i, sentence in enumerate(sentences):
        current_section.append(sentence)
        
        # Check if we should end this section
        should_end = (
            len(current_section) >= target_section_size or
            i == len(sentences) - 1 or
            _is_section_boundary(sentence, sentences[i+1] if i+1 < len(sentences) else "")
        )
        
        if should_end:
            section_text = '. '.join(current_section)
            if section_text:
                sections.append(section_text + '.')
            current_section = []
    
    return sections if sections else [text]


def _is_section_boundary(current_sentence: str, next_sentence: str) -> bool:
    """Determine if there's a logical section boundary between sentences."""
    if not next_sentence:
        return True
    
    # Look for transition words that indicate section boundaries
    transition_words = [
        'ต่อไป', 'ต่อมา', 'ในส่วนต่อไป', 'ในเรื่องของ', 'ในขณะเดียวกัน',
        'อย่างไรก็ตาม', 'นอกจากนี้', 'อีกทั้ง', 'สรุปแล้ว', 'โดยรวม',
        'next', 'furthermore', 'however', 'moreover', 'in conclusion'
    ]
    
    current_lower = current_sentence.lower()
    next_lower = next_sentence.lower()
    
    # Check if next sentence starts with transition word
    for word in transition_words:
        if next_lower.startswith(word):
            return True
    
    # Check for topic shifts (simple keyword-based)
    current_keywords = _extract_sentence_keywords(current_sentence)
    next_keywords = _extract_sentence_keywords(next_sentence)
    
    # If keywords are very different, it might be a section boundary
    if current_keywords and next_keywords:
        overlap = len(current_keywords.intersection(next_keywords))
        total = len(current_keywords.union(next_keywords))
        similarity = overlap / total if total > 0 else 0
        return similarity < 0.2  # Low similarity suggests section boundary
    
    return False


def _extract_sentence_keywords(sentence: str) -> set:
    """Extract meaningful keywords from a sentence."""
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'ที่', 'ของ', 'ใน', 'กับ', 'และ', 'หรือ', 'แต่', 'เพื่อ', 'จาก', 'โดย', 'ด้วย'
    }
    
    # Extract words (simple approach)
    words = re.findall(r'\b\w+\b', sentence.lower())
    keywords = {word for word in words if word not in stop_words and len(word) > 2}
    
    return keywords


def _contains_thai(text: str) -> bool:
    return re.search(r"[\u0E00-\u0E7F]", text) is not None


# Removed: _get_transformer_summarizer and _try_thaibert_summarizer
# Using only Typhoon API for summarization


def summarize_text(text: str, lang: str = 'auto', provider: str = 'auto', max_length: int = None, min_length: int = None) -> str:
    """
    Enhanced text summarization with improved analysis and processing for large texts.
    Includes robust error handling and fallback mechanisms with optimized performance.
    
    Creates a comprehensive, flowing summary that captures key information
    while maintaining readability and coherence for texts of any size.
    
    Args:
        text: Input text to summarize
        lang: Language preference ('th' for Thai, 'auto' for auto-detection)
        provider: Summarization provider ('typhoon', 'auto', 'local')
        max_length: Maximum summary length (auto-calculated if None)
        min_length: Minimum summary length (auto-calculated if None)
    
    Returns:
        Enhanced summary text optimized for readability and coverage
    """
    try:
        # Enhanced text preprocessing with error handling
        cleaned_text = _clean_text_for_summarization(text)
        if len(cleaned_text) < 50:
            return cleaned_text

        # Analyze text characteristics
        text_length = len(cleaned_text)
        is_thai = _contains_thai(cleaned_text)
        
        # Calculate optimal summary lengths based on text size
        if max_length is None:
            if text_length > 50000:  # Very large texts
                max_length = min(2000, text_length // 25)
            elif text_length > 20000:  # Large texts
                max_length = min(1500, text_length // 15)
            elif text_length > 10000:  # Medium-large texts
                max_length = min(1000, text_length // 12)
            elif text_length > 5000:   # Medium texts
                max_length = min(800, text_length // 8)
            else:  # Smaller texts
                max_length = min(600, text_length // 4)
        
        if min_length is None:
            min_length = max(100, max_length // 3)
        
        # Determine optimal summarization strategy
        use_typhoon = provider in ('typhoon', 'auto') and _HAS_TYPHOON
        
        print(f"Processing text of length: {text_length} characters, target summary: {min_length}-{max_length} chars")
        
    except Exception as e:
        print(f"Error in text preprocessing: {e}")
        # Fallback to basic text processing
        try:
            cleaned_text = text.strip()
            if len(cleaned_text) < 50:
                return cleaned_text
            text_length = len(cleaned_text)
            is_thai = _contains_thai(cleaned_text)
            use_typhoon = False  # Disable Typhoon for error recovery
            max_length = min(600, text_length // 4)
            min_length = max(100, max_length // 3)
        except:
            return "ไม่สามารถประมวลผลข้อความได้"
    
    if use_typhoon:
        try:
            if typhoon_client.is_ready():
                # Use Typhoon with optimized parameters for large data processing
                if text_length > 50000:
                    # For very large texts, use advanced hierarchical approach
                    try:
                        return typhoon_client.summarize_long_text(
                            cleaned_text, 
                            max_chunk_size=6000,  # Larger chunk size for efficiency
                            max_length=max_length,
                            min_length=min_length,
                            lang=lang
                        )
                    except Exception as e:
                        print(f"Very large text processing failed, trying smaller chunks: {e}")
                        return typhoon_client.summarize_long_text(
                            cleaned_text, 
                            max_chunk_size=4000,
                            max_length=max_length * 2 // 3,
                            min_length=min_length * 2 // 3,
                            lang=lang
                        )
                elif text_length > 20000:
                    # For large texts, use hierarchical approach
                    try:
                        return typhoon_client.summarize_long_text(
                            cleaned_text, 
                            max_chunk_size=5000,
                            max_length=max_length,
                            min_length=min_length,
                            lang=lang
                        )
                    except Exception as e:
                        print(f"Large text processing failed, trying smaller chunks: {e}")
                        return typhoon_client.summarize_long_text(
                            cleaned_text, 
                            max_chunk_size=3000,
                            max_length=max_length * 3 // 4,
                            min_length=min_length * 3 // 4,
                            lang=lang
                        )
                elif text_length > 10000:
                    # For medium-large texts, use hierarchical approach
                    try:
                        return typhoon_client.summarize_long_text(
                            cleaned_text, 
                            max_chunk_size=4000,
                            max_length=max_length,
                            min_length=min_length,
                            lang=lang
                        )
                    except Exception as e:
                        print(f"Medium-large text processing failed, trying direct: {e}")
                        return typhoon_client.summarize(
                            cleaned_text,
                            max_length=max_length,
                            min_length=min_length,
                            do_sample=True,
                            lang=lang
                        )
                elif text_length > 3000:
                    # For medium texts, use direct or hierarchical approach
                    try:
                        if text_length > 5000:
                            return typhoon_client.summarize_long_text(
                                cleaned_text, 
                                max_chunk_size=3000,
                                max_length=max_length,
                                min_length=min_length,
                                lang=lang
                            )
                        else:
                            return typhoon_client.summarize(
                                cleaned_text,
                                max_length=max_length,
                                min_length=min_length,
                                do_sample=True,
                                lang=lang
                            )
                    except Exception as e:
                        print(f"Medium text processing failed, trying direct: {e}")
                        return typhoon_client.summarize(
                            cleaned_text,
                            max_length=max_length,
                            min_length=min_length,
                            do_sample=False,
                            lang=lang
                        )
                else:
                    # For shorter texts, use direct summarization with optimized parameters
                    try:
                        return typhoon_client.summarize(
                            cleaned_text,
                            max_length=max_length,
                            min_length=min_length,
                            do_sample=True,  # Enable sampling for better quality
                            lang=lang
                        )
                    except Exception as e:
                        print(f"Direct summarization failed: {e}")
                        # Fallback to local summarizer
                        pass
            
            if provider == 'typhoon':
                return "ไม่สามารถเรียกใช้บริการสรุปด้วย Typhoon ได้ โปรดตรวจสอบ Typhoon API service แล้วลองใหม่อีกครั้ง"
                
        except Exception as e:
            print(f"Typhoon summarization failed completely: {e}")
            if provider == 'typhoon':
                return "ไม่สามารถเรียกใช้บริการสรุปด้วย Typhoon ได้ โปรดตรวจสอบ Typhoon API service แล้วลองใหม่อีกครั้ง"
            # Fall through to local summarizer

    # Removed: ThaiBERT and local transformer model support
    # Using only Typhoon API - fall through to extractive summarization if Typhoon fails

    # Enhanced fallback to extractive summarization
    try:
        # Adjust number of sentences based on text length with enhanced scaling for large data
        if text_length > 50000:
            num_sentences = min(50, max(25, text_length // 80))  # Even more sentences for very large texts
        elif text_length > 30000:
            num_sentences = min(45, max(20, text_length // 90))  # More sentences for very large texts
        elif text_length > 15000:
            num_sentences = min(40, max(18, text_length // 100))  # Much more sentences for very large texts
        elif text_length > 8000:
            num_sentences = min(35, max(15, text_length // 120))  # More sentences for large texts
        elif text_length > 5000:
            num_sentences = min(30, max(12, text_length // 140))  # More sentences for medium-large texts
        elif text_length > 2000:
            num_sentences = min(25, max(10, text_length // 160))
        else:
            num_sentences = min(20, max(8, text_length // 180))
            
        key_sentences = _extract_key_sentences(cleaned_text, num_sentences)
        
        if key_sentences:
            # Use enhanced narrative creation for better flow
            narrative_summary = _create_enhanced_narrative_summary(key_sentences, is_thai)
            processed_summary = _post_process_summary(narrative_summary, is_thai).strip()
            
            # Ensure summary meets minimum length requirements
            if len(processed_summary) < min_length and len(key_sentences) < num_sentences * 1.5:
                # Try to get more sentences if summary is too short
                try:
                    more_sentences = _extract_key_sentences(cleaned_text, min(num_sentences * 2, 60))
                    if len(more_sentences) > len(key_sentences):
                        extended_summary = _create_enhanced_narrative_summary(more_sentences, is_thai)
                        processed_summary = _post_process_summary(extended_summary, is_thai).strip()
                except:
                    pass
            
            return processed_summary
    except Exception as e:
        print(f"Extractive summarization failed: {e}")
    
    # Final fallback: return cleaned text if all else fails with enhanced large data handling and error recovery
    try:
        if len(cleaned_text) > 10000:
            # For very large texts, use sophisticated extractive summarization with error handling
            try:
                sentences = re.split(r'[.!?]+', cleaned_text)
                sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
                
                if len(sentences) > 50:
                    # For very large texts, take more sentences for better coverage
                    key_sentences = (sentences[:8] + 
                                   sentences[len(sentences)//4:len(sentences)//4+6] + 
                                   sentences[len(sentences)//2:len(sentences)//2+6] + 
                                   sentences[3*len(sentences)//4:3*len(sentences)//4+6] + 
                                   sentences[-8:])
                    return ". ".join(key_sentences) + "."
                elif len(sentences) > 30:
                    # For large texts, take more sentences
                    key_sentences = (sentences[:6] + 
                                   sentences[len(sentences)//3:len(sentences)//3+4] + 
                                   sentences[2*len(sentences)//3:2*len(sentences)//3+4] + 
                                   sentences[-6:])
                    return ". ".join(key_sentences) + "."
                elif len(sentences) > 15:
                    # For medium-large texts, take first, middle, and last sentences
                    key_sentences = sentences[:5] + sentences[len(sentences)//2:len(sentences)//2+3] + sentences[-5:]
                    return ". ".join(key_sentences) + "."
                else:
                    # If not enough sentences, take what we have
                    return ". ".join(sentences) + "."
            except Exception as e:
                print(f"Sophisticated extraction failed: {e}")
                # Fallback to simple truncation with better coverage
                return cleaned_text[:min_length] + "..."
        elif len(cleaned_text) > 3000:
            # For large texts, try basic extractive summarization with error handling
            try:
                sentences = re.split(r'[.!?]+', cleaned_text)
                sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
                if len(sentences) > 15:
                    # Take more sentences for better coverage
                    key_sentences = sentences[:4] + sentences[len(sentences)//2:len(sentences)//2+3] + sentences[-4:]
                    return ". ".join(key_sentences) + "."
                else:
                    return ". ".join(sentences) + "."
            except Exception as e:
                print(f"Basic extraction failed: {e}")
                # Fallback to simple truncation
                return cleaned_text[:min_length] + "..."
        elif len(cleaned_text) > 1000:
            # For medium texts, try basic extractive summarization with error handling
            try:
                sentences = re.split(r'[.!?]+', cleaned_text)
                sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
                if len(sentences) > 8:
                    # Take first few sentences and last few sentences
                    key_sentences = sentences[:3] + sentences[-3:]
                    return ". ".join(key_sentences) + "."
                else:
                    return ". ".join(sentences) + "."
            except Exception as e:
                print(f"Basic extraction failed: {e}")
                # Fallback to simple truncation
                return cleaned_text[:800] + "..."
        else:
            return cleaned_text
    except Exception as e:
        print(f"All fallback methods failed: {e}")
        # Ultimate fallback - return truncated original text
        try:
            return text[:min_length] + "..." if len(text) > min_length else text
        except:
            return "ไม่สามารถประมวลผลข้อความได้"


def _post_process_summary(summary: str, is_thai: bool) -> str:
    """Enhanced post-process summary for better paraphrasing quality."""
    if not summary:
        return summary
    
    # Remove excessive whitespace
    summary = re.sub(r'\s+', ' ', summary.strip())
    
    # Fix common issues
    summary = re.sub(r'\.\s*\.+', '.', summary)  # Multiple periods
    summary = re.sub(r'\s+([.!?])', r'\1', summary)  # Space before punctuation
    
    # Ensure proper sentence endings
    if not summary.endswith(('.', '!', '?')):
        summary += '.'
    
    # Fix Thai text spacing issues
    if is_thai:
        summary = re.sub(r'([ก-๙])\s+([ก-๙])', r'\1\2', summary)
        summary = re.sub(r'([ก-๙])\s+([.!?])', r'\1\2', summary)
    
    # Enhanced paraphrasing improvements
    summary = _improve_paraphrasing_quality(summary, is_thai)
    
    # Remove repetitive phrases
    summary = re.sub(r'\b(\w+)\s+\1\b', r'\1', summary)
    
    # Ensure reasonable length
    if len(summary) > 1000:
        sentences = re.split(r'[.!?]+', summary)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) > 8:
            summary = '. '.join(sentences[:8]) + '.'
    
    # Apply enhanced formatting
    summary = _apply_enhanced_formatting(summary, is_thai)
    
    return summary.strip()


def _improve_paraphrasing_quality(summary: str, is_thai: bool) -> str:
    """Improve paraphrasing quality by fixing common issues."""
    if not summary:
        return summary
    
    # Split into sentences for analysis
    sentences = re.split(r'[.!?]+', summary)
    improved_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Fix common paraphrasing issues
        improved_sentence = _fix_paraphrasing_issues(sentence, is_thai)
        improved_sentences.append(improved_sentence)
    
    # Rejoin sentences
    result = '. '.join(improved_sentences)
    if result and not result.endswith(('.', '!', '?')):
        result += '.'
    
    return result


def _fix_paraphrasing_issues(sentence: str, is_thai: bool) -> str:
    """Fix common paraphrasing issues in a sentence."""
    if not sentence:
        return sentence
    
    if is_thai:
        # Thai-specific paraphrasing improvements
        redundant_patterns = [
            r'กล่าวว่า\s*',  # Remove "กล่าวว่า" (said that)
            r'ตามที่\s*',   # Remove "ตามที่" (according to)
            r'ในเรื่องของ\s*',  # Remove "ในเรื่องของ" (in terms of)
            r'เป็นที่ทราบกันว่า\s*',  # Remove "เป็นที่ทราบกันว่า" (it is known that)
            r'นอกจากนี้\s*แล้ว\s*',  # Remove redundant "นอกจากนี้แล้ว"
            r'อีกทั้ง\s*ยัง\s*',  # Remove redundant "อีกทั้งยัง"
            r'โดยเฉพาะอย่างยิ่ง\s*',  # Remove "โดยเฉพาะอย่างยิ่ง" (especially)
        ]
        
        for pattern in redundant_patterns:
            sentence = re.sub(pattern, '', sentence, flags=re.IGNORECASE)
        
        # Improve sentence flow by removing unnecessary connectors
        flow_improvements = [
            (r'และ\s*ยัง\s*', 'และ'),
            (r'แต่\s*ก็\s*', 'แต่'),
            (r'เพราะ\s*ว่า\s*', 'เพราะ'),
            (r'เนื่องจาก\s*ว่า\s*', 'เนื่องจาก'),
            (r'ในขณะที่\s*', 'ขณะที่'),
            (r'ในกรณีที่\s*', 'กรณีที่'),
        ]
        
        for old_pattern, new_pattern in flow_improvements:
            sentence = re.sub(old_pattern, new_pattern, sentence, flags=re.IGNORECASE)
    else:
        # English-specific paraphrasing improvements
        redundant_patterns = [
            r'it is known that\s*',
            r'according to\s*',
            r'it should be noted that\s*',
            r'it is important to note that\s*',
            r'in terms of\s*',
            r'with regard to\s*',
        ]
        
        for pattern in redundant_patterns:
            sentence = re.sub(pattern, '', sentence, flags=re.IGNORECASE)
        
        # Improve sentence flow
        flow_improvements = [
            (r'and also\s*', 'and '),
            (r'but also\s*', 'but '),
            (r'due to the fact that\s*', 'because '),
            (r'in order to\s*', 'to '),
        ]
        
        for old_pattern, new_pattern in flow_improvements:
            sentence = re.sub(old_pattern, new_pattern, sentence, flags=re.IGNORECASE)
    
    # Ensure sentence starts with proper capitalization
    if sentence and sentence[0].islower():
        sentence = sentence[0].upper() + sentence[1:]
    
    return sentence.strip()


def _apply_enhanced_formatting(summary: str, is_thai: bool) -> str:
    """Apply enhanced formatting with improved clarity and organization."""
    if not summary:
        return summary
    
    # Check numerical consistency first
    summary = _check_and_fix_numerical_consistency(summary, is_thai)
    
    # Split into sentences for better analysis
    sentences = re.split(r'[.!?]+', summary)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= 2:
        return summary  # Too short to format
    
    # Apply enhanced structured formatting for better clarity and organization
    return _format_as_enhanced_structured_paragraphs(sentences, is_thai)


def _check_and_fix_numerical_consistency(summary: str, is_thai: bool) -> str:
    """Check and fix numerical consistency in the summary."""
    if not summary:
        return summary
    
    # Common numerical patterns to preserve
    numerical_patterns = [
        # Thai patterns
        (r'(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*(กก\.?|กิโลกรัม|kg|สัปดาห์|week|เดือน|month|ปี|year|บาท|baht|เปอร์เซ็นต์|%|ร้อยละ)',
         r'\1–\2 \3'),  # Fix dash formatting for ranges
        (r'(\d+(?:\.\d+)?)\s*(กก\.?|กิโลกรัม|kg|สัปดาห์|week|เดือน|month|ปี|year|บาท|baht)',
         r'\1 \2'),  # Ensure space before units
        # English patterns  
        (r'(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*(kg|week|month|year|baht|%)',
         r'\1–\2 \3'),
        (r'(\d+(?:\.\d+)?)\s*(kg|week|month|year|baht)',
         r'\1 \2'),
    ]
    
    for pattern, replacement in numerical_patterns:
        summary = re.sub(pattern, replacement, summary, flags=re.IGNORECASE)
    
    # Fix common numerical inconsistencies
    fixes = [
        # Fix missing units
        (r'(\d+(?:\.\d+)?)\s*ก\.', r'\1 กก.'),  # Fix incomplete "ก." to "กก."
        (r'(\d+(?:\.\d+)?)\s*เปอร์เซ็นต์', r'\1%'),  # Standardize percentage
        (r'(\d+(?:\.\d+)?)\s*ร้อยละ', r'\1%'),  # Standardize percentage
        # Fix spacing issues
        (r'(\d+)\s*%', r'\1%'),  # Remove space before %
        (r'(\d+(?:\.\d+)?)\s*%', r'\1%'),  # Ensure no space before %
    ]
    
    for pattern, replacement in fixes:
        summary = re.sub(pattern, replacement, summary)
    
    return summary


def _should_use_bullet_formatting(sentences: list, is_thai: bool) -> bool:
    """Determine if content should be formatted as bullet points."""
    if len(sentences) < 3:
        return False
    
    # Check for list-like indicators
    list_indicators = []
    if is_thai:
        list_indicators = [
            r'^\d+\.',  # Numbered lists
            r'^[-•*]\s*',  # Bullet points
            r'^[\u2022\u2023\u25E6\u2043]',  # Unicode bullets
            r'ประการที่\s*\d+',  # Thai enumeration
            r'ข้อ\s*\d+',  # Thai item numbering
        ]
    else:
        list_indicators = [
            r'^\d+\.',  # Numbered lists
            r'^[-•*]\s*',  # Bullet points
            r'^[\u2022\u2023\u25E6\u2043]',  # Unicode bullets
            r'^[a-zA-Z]\.',  # Lettered lists
        ]
    
    # Count how many sentences look like list items
    list_like_count = 0
    for sentence in sentences:
        for pattern in list_indicators:
            if re.match(pattern, sentence.strip()):
                list_like_count += 1
                break
    
    # Also check for content that naturally forms lists
    content_indicators = []
    if is_thai:
        content_indicators = [
            r'ประกอบด้วย', r'มีดังนี้', r'คือ', r'ได้แก่', r'สาเหตุ', r'ปัจจัย',
            r'ข้อดี', r'ข้อเสีย', r'ขั้นตอน', r'วิธีการ', r'ลักษณะ'
        ]
    else:
        content_indicators = [
            r'consists of', r'includes', r'such as', r'factors', r'steps',
            r'methods', r'characteristics', r'advantages', r'disadvantages'
        ]
    
    content_list_count = 0
    for sentence in sentences:
        sentence_lower = sentence.lower()
        for indicator in content_indicators:
            if indicator in sentence_lower:
                content_list_count += 1
                break
    
    # Use bullet formatting if more than 40% of sentences are list-like
    # or if there are content indicators suggesting lists
    return (list_like_count / len(sentences) > 0.4) or (content_list_count > 0)


def _format_as_bullet_points(sentences: list, is_thai: bool) -> str:
    """Format sentences as bullet points."""
    formatted_points = []
    bullet_char = "•" if is_thai else "•"
    
    for i, sentence in enumerate(sentences):
        # Clean up the sentence
        sentence = sentence.strip()
        
        # Remove existing list markers
        sentence = re.sub(r'^\d+\.\s*', '', sentence)
        sentence = re.sub(r'^[-•*]\s*', '', sentence)
        sentence = re.sub(r'^[\u2022\u2023\u25E6\u2043]\s*', '', sentence)
        
        # Capitalize first letter
        if sentence and sentence[0].islower():
            sentence = sentence[0].upper() + sentence[1:]
        
        # Add bullet point
        formatted_points.append(f"{bullet_char} {sentence}")
    
    return "\n".join(formatted_points)


def _format_as_structured_paragraphs(sentences: list, is_thai: bool) -> str:
    """Format sentences as structured paragraphs with better flow."""
    if len(sentences) <= 3:
        return ". ".join(sentences) + "."
    
    # Group sentences into logical paragraphs
    paragraphs = []
    current_paragraph = []
    
    for i, sentence in enumerate(sentences):
        current_paragraph.append(sentence)
        
        # Determine if we should start a new paragraph
        should_break = (
            i == len(sentences) - 1 or  # Last sentence
            len(current_paragraph) >= 3 or  # Paragraph getting long
            _is_paragraph_break(sentence, sentences[i + 1] if i + 1 < len(sentences) else "", is_thai)
        )
        
        if should_break:
            if current_paragraph:
                paragraph_text = _create_flowing_paragraph(current_paragraph, is_thai)
                paragraphs.append(paragraph_text)
                current_paragraph = []
    
    return "\n\n".join(paragraphs)


def _format_as_enhanced_structured_paragraphs(sentences: list, is_thai: bool) -> str:
    """Format sentences as enhanced structured paragraphs with improved clarity and organization."""
    if len(sentences) <= 3:
        return ". ".join(sentences) + "."
    
    # Enhanced paragraph organization for better clarity
    paragraphs = []
    current_paragraph = []
    
    # Group sentences into logical paragraphs with better organization
    for i, sentence in enumerate(sentences):
        current_paragraph.append(sentence)
        
        # Determine if we should start a new paragraph for better organization
        should_break = (
            i == len(sentences) - 1 or  # Last sentence
            len(current_paragraph) >= 3 or  # Paragraph getting long
            _is_enhanced_paragraph_break(sentence, sentences[i + 1] if i + 1 < len(sentences) else "", is_thai)
        )
        
        if should_break:
            if current_paragraph:
                paragraph_text = _create_enhanced_flowing_paragraph(current_paragraph, is_thai)
                paragraphs.append(paragraph_text)
                current_paragraph = []
    
    # If there are remaining sentences, create final paragraph
    if current_paragraph:
        paragraph_text = _create_enhanced_flowing_paragraph(current_paragraph, is_thai)
        paragraphs.append(paragraph_text)
    
    return "\n\n".join(paragraphs)


def _is_enhanced_paragraph_break(current_sentence: str, next_sentence: str, is_thai: bool) -> bool:
    """Determine if there should be a paragraph break between sentences for better organization."""
    if not next_sentence:
        return False
    
    # Look for enhanced topic shift indicators for better coverage
    topic_shift_indicators = []
    if is_thai:
        topic_shift_indicators = [
            r'ในเรื่องของ', r'ในส่วนของ', r'ต่อไป', r'ต่อมา', r'อย่างไรก็ตาม',
            r'นอกจากนี้', r'อีกทั้ง', r'สรุปแล้ว', r'โดยรวม', r'ในขณะเดียวกัน',
            r'ในทางกลับกัน', r'ในทำนองเดียวกัน', r'ในกรณีที่', r'สำหรับเรื่อง',
            r'เกี่ยวกับ', r'ด้าน', r'ส่วน', r'ประเภท', r'รูปแบบ'
        ]
    else:
        topic_shift_indicators = [
            r'in terms of', r'regarding', r'furthermore', r'however', r'moreover',
            r'in addition', r'in conclusion', r'overall', r'meanwhile', r'on the other hand',
            r'similarly', r'in case of', r'concerning', r'aspect', r'section',
            r'type', r'form', r'pattern'
        ]
    
    for indicator in topic_shift_indicators:
        if re.search(indicator, next_sentence.lower()):
            return True
    
    return False


def _create_enhanced_flowing_paragraph(sentences: list, is_thai: bool) -> str:
    """Create an enhanced flowing paragraph from sentences with improved clarity and connectors."""
    if not sentences:
        return ""
    
    if len(sentences) == 1:
        return sentences[0] + "."
    
    # Start with the first sentence
    paragraph = sentences[0]
    
    # Add remaining sentences with enhanced appropriate connectors for better clarity
    for i, sentence in enumerate(sentences[1:], 1):
        connector = _get_enhanced_paragraph_connector(sentence, i, len(sentences), is_thai)
        paragraph += f" {connector} {sentence}"
    
    return paragraph + "."


def _get_enhanced_paragraph_connector(sentence: str, position: int, total: int, is_thai: bool) -> str:
    """Get enhanced connector for paragraph flow with improved clarity."""
    if is_thai:
        # Thai connectors with enhanced clarity
        sentence_lower = sentence.lower()
        
        if position == total - 1:
            return "และ"
        elif any(word in sentence_lower for word in ["ผล", "ผลลัพธ์", "ผลที่ได้"]):
            return "ซึ่งทำให้"
        elif any(word in sentence_lower for word in ["ปัญหา", "อุปสรรค", "ข้อจำกัด"]):
            return "อย่างไรก็ตาม"
        elif any(word in sentence_lower for word in ["วิธี", "แนวทาง", "การแก้ไข"]):
            return "โดยวิธีการ"
        elif any(word in sentence_lower for word in ["ข้อมูล", "รายละเอียด", "สถิติ"]):
            return "ข้อมูลแสดงให้เห็นว่า"
        else:
            return "อีกทั้ง"
    else:
        # English connectors with enhanced clarity
        sentence_lower = sentence.lower()
        
        if position == total - 1:
            return "and"
        elif any(word in sentence_lower for word in ["result", "outcome", "effect"]):
            return "which results in"
        elif any(word in sentence_lower for word in ["problem", "issue", "limitation"]):
            return "however"
        elif any(word in sentence_lower for word in ["method", "approach", "solution"]):
            return "through the method"
        elif any(word in sentence_lower for word in ["data", "information", "statistics"]):
            return "the data shows that"
        else:
            return "furthermore"


def _is_paragraph_break(current_sentence: str, next_sentence: str, is_thai: bool) -> bool:
    """Determine if there should be a paragraph break between sentences."""
    if not next_sentence:
        return False
    
    # Look for topic shift indicators
    topic_shift_indicators = []
    if is_thai:
        topic_shift_indicators = [
            r'ในเรื่องของ', r'ในส่วนของ', r'ต่อไป', r'ต่อมา', r'อย่างไรก็ตาม',
            r'นอกจากนี้', r'อีกทั้ง', r'สรุปแล้ว', r'โดยรวม'
        ]
    else:
        topic_shift_indicators = [
            r'in terms of', r'regarding', r'furthermore', r'however', r'moreover',
            r'in addition', r'in conclusion', r'overall'
        ]
    
    for indicator in topic_shift_indicators:
        if indicator in next_sentence.lower():
            return True
    
    return False


def _create_flowing_paragraph(sentences: list, is_thai: bool) -> str:
    """Create a flowing paragraph from sentences with improved connectors."""
    if not sentences:
        return ""
    
    if len(sentences) == 1:
        return sentences[0] + "."
    
    # Start with the first sentence
    paragraph = sentences[0]
    
    # Add remaining sentences with appropriate connectors
    for i, sentence in enumerate(sentences[1:], 1):
        connector = _get_improved_connector(sentence, i, len(sentences), is_thai)
        paragraph += f" {connector} {sentence}"
    
    return paragraph + "."


def _get_improved_connector(sentence: str, position: int, total: int, is_thai: bool) -> str:
    """Get improved connector based on sentence content and position."""
    sentence_lower = sentence.lower()
    
    if is_thai:
        # Smart Thai connector selection
        if any(word in sentence_lower for word in ['หลังจาก', 'ต่อมา', 'ในที่สุด', 'finally', 'then', 'after']):
            return "ต่อมา"
        
        if any(word in sentence_lower for word in ['แต่', 'อย่างไรก็ตาม', 'อย่างไรก็ดี', 'however', 'but', 'although']):
            return "อย่างไรก็ตาม"
        
        if any(word in sentence_lower for word in ['นอกจากนี้', 'อีกทั้ง', 'เพิ่มเติม', 'moreover', 'additionally', 'furthermore']):
            return "นอกจากนี้"
        
        if any(word in sentence_lower for word in ['เพราะ', 'เนื่องจาก', 'เพราะฉะนั้น', 'therefore', 'because', 'thus']):
            return "เพราะฉะนั้น"
        
        # Position-based connectors with variety
        if position < total * 0.3:  # Early
            connectors = ["นอกจากนี้", "อีกทั้ง", "ในส่วนนี้"]
        elif position < total * 0.7:  # Middle
            connectors = ["ในขณะเดียวกัน", "ต่อมา", "ในเรื่องของ"]
        else:  # Late
            connectors = ["ในที่สุด", "สรุปแล้ว", "โดยรวม"]
        
        return connectors[position % len(connectors)]
    else:
        # Smart English connector selection
        if any(word in sentence_lower for word in ['after', 'then', 'finally', 'subsequently']):
            return "then"
        
        if any(word in sentence_lower for word in ['but', 'however', 'although', 'despite']):
            return "however"
        
        if any(word in sentence_lower for word in ['moreover', 'additionally', 'furthermore', 'also']):
            return "moreover"
        
        if any(word in sentence_lower for word in ['because', 'therefore', 'thus', 'hence']):
            return "therefore"
        
        # Position-based connectors with variety
        if position < total * 0.3:  # Early
            connectors = ["moreover", "additionally", "furthermore"]
        elif position < total * 0.7:  # Middle
            connectors = ["meanwhile", "then", "regarding"]
        else:  # Late
            connectors = ["finally", "in conclusion", "overall"]
        
        return connectors[position % len(connectors)]