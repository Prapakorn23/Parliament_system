import os
import sys
import re
import hashlib
from typing import List, Dict, Optional, Tuple
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


class SimpleCache:
    """Simple LRU cache for summarization results."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache = {}
        self.access_order = []
    
    def _generate_key(self, text: str, target_length: int, lang: str) -> str:
        """Generate cache key from parameters."""
        content = f"{text[:500]}_{target_length}_{lang}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, text: str, target_length: int, lang: str) -> Optional[str]:
        """Get cached result if available."""
        key = self._generate_key(text, target_length, lang)
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, text: str, target_length: int, lang: str, result: str):
        """Store result in cache."""
        key = self._generate_key(text, target_length, lang)
        
        # Remove oldest if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[key] = result
        self.access_order.append(key)
    
    def clear(self):
        """Clear all cached results."""
        self.cache.clear()
        self.access_order.clear()


class SummarizeRequest(BaseModel):
    text: str
    target_length: Optional[int] = 1000  # Target character length for final summary (500-1500 recommended)
    do_sample: Optional[bool] = False
    lang: Optional[str] = "auto"


class SummarizeResponse(BaseModel):
    summary: str
    model: str
    input_length: int
    output_length: int
    processing_time: float
    compression_ratio: float


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    do_sample: Optional[bool] = True


class GenerateResponse(BaseModel):
    response: str
    model: str
    input_length: int
    output_length: int


class TyphoonSummarizer:
    """FastAPI-based summarizer using SCB10X/typhoon-7b model with caching."""

    def __init__(self, model_name: str | None = None):
        # Use SCB10X/typhoon-7b model
        self.model_name = model_name or os.environ.get("TYPHOON_MODEL_NAME", "scb10x/typhoon-7b")
        self.tokenizer = None
        self.model = None
        self.cache = SimpleCache(max_size=200)  # Cache for summarization results
        self._load_model()

    def _load_model(self):
        """Load the Typhoon model and tokenizer."""
        try:
            print(f"Loading {self.model_name} model...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            if torch.cuda.is_available():
                print("Model loaded on GPU")
            else:
                print("Model loaded on CPU")
                
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
        except Exception as e:
            print(f"Error loading model: {e}")
            raise RuntimeError(f"Failed to load {self.model_name}: {e}")

    def is_ready(self) -> bool:
        return self.tokenizer is not None and self.model is not None

    def _contains_thai(self, text: str) -> bool:
        return any("\u0E00" <= ch <= "\u0E7F" for ch in text)
    
    def _score_sentence_importance(self, sentence: str, full_text: str) -> float:
        """
        NEW: Score how important a sentence is based on various factors.
        Returns score from 0.0 to 1.0
        """
        score = 0.0
        sentence_lower = sentence.lower()
        text_lower = full_text.lower()
        
        # Factor 1: Position (earlier sentences often more important)
        position_in_text = text_lower.find(sentence_lower)
        if position_in_text != -1:
            position_score = 1.0 - (position_in_text / len(text_lower))
            score += position_score * 0.2
        
        # Factor 2: Length (moderate length = good, too short/long = less important)
        length_score = 1.0 - abs(len(sentence) - 100) / 200
        length_score = max(0, min(1, length_score))
        score += length_score * 0.1
        
        # Factor 3: Key phrases indicating importance
        key_phrases_thai = ['สำคัญ', 'หลัก', 'ประเด็น', 'เหตุผล', 'ผลกระทบ', 'สรุป', 'ข้อสรุป', 'เป้าหมาย', 'วัตถุประสงค์', 'ปัญหา']
        key_phrases_en = ['important', 'main', 'key', 'significant', 'critical', 'essential', 'primary', 'objective', 'goal', 'problem', 'issue']
        
        key_phrases = key_phrases_thai + key_phrases_en
        for phrase in key_phrases:
            if phrase in sentence_lower:
                score += 0.15
                break
        
        # Factor 4: Numbers/dates (often important for specificity)
        if re.search(r'\d+', sentence):
            score += 0.1
        
        # Factor 5: Named entities (organizations, ministries, etc.)
        if re.search(r'(คุณ|นาย|นาง|บริษัท|กระทรวง|กรม|องค์กร|สำนัก)', sentence):
            score += 0.1
        
        # Factor 6: Question marks (highlight important issues)
        if '?' in sentence or '?' in sentence:
            score += 0.1
        
        # Factor 7: Sentence starters that indicate importance
        important_starters = ['ประเด็นสำคัญ', 'ข้อสำคัญ', 'สิ่งสำคัญ', 'ปัญหาหลัก', 'the main', 'importantly', 'significantly', 'the key']
        for starter in important_starters:
            if sentence_lower.startswith(starter):
                score += 0.2
                break
        
        return min(score, 1.0)
    
    def _extractive_summary_by_importance(self, text: str, target_sentences: int = 5) -> str:
        """
        NEW: Create extractive summary by selecting most important sentences.
        Use as fallback or quality baseline.
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
        
        if len(sentences) <= target_sentences:
            return '. '.join(sentences) + '.'
        
        # Score each sentence
        scored_sentences = []
        for sentence in sentences:
            score = self._score_sentence_importance(sentence, text)
            scored_sentences.append((score, sentence))
        
        # Sort by score (highest first)
        scored_sentences.sort(key=lambda x: -x[0])
        
        # Select top sentences
        top_sentences = [sent for score, sent in scored_sentences[:target_sentences]]
        
        # Reorder by original position to maintain flow
        ordered_summary = []
        for sentence in sentences:
            if sentence in top_sentences:
                ordered_summary.append(sentence)
        
        return '. '.join(ordered_summary) + '.'
    
    def _evaluate_main_idea_quality(self, original: str, summary: str) -> dict:
        """
        NEW: Evaluate how well the summary captures main ideas.
        Returns quality metrics.
        """
        metrics = {
            'coverage_score': 0.0,   # ครอบคลุมประเด็นสำคัญ
            'clarity_score': 0.0,     # ความชัดเจน
            'focus_score': 0.0,       # โฟกัสที่ใจความหลัก
            'overall_score': 0.0
        }
        
        # 1. Coverage: Check if key terms from original are in summary
        original_words = set(re.findall(r'\w+', original.lower()))
        summary_words = set(re.findall(r'\w+', summary.lower()))
        
        # Remove common stop words
        stopwords = {'และ', 'หรือ', 'ที่', 'ใน', 'จาก', 'เป็น', 'มี', 'ได้', 'ของ', 'กับ', 'โดย',
                     'the', 'is', 'are', 'of', 'in', 'to', 'a', 'an', 'and', 'or', 'for', 'with', 'by'}
        original_words -= stopwords
        summary_words -= stopwords
        
        if original_words:
            coverage = len(original_words.intersection(summary_words)) / len(original_words)
            metrics['coverage_score'] = min(coverage * 2, 1.0)  # Scale up, cap at 1.0
        
        # 2. Clarity: Check sentence structure
        sentences = re.split(r'[.!?]+', summary)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_length = sum(len(s) for s in sentences) / len(sentences)
            # Ideal length: 60-120 chars per sentence
            clarity = 1.0 - abs(avg_length - 90) / 90
            metrics['clarity_score'] = max(0, min(1, clarity))
        
        # 3. Focus: Check for repetition (unique words ratio)
        words = re.findall(r'\w+', summary.lower())
        if words:
            unique_ratio = len(set(words)) / len(words)
            metrics['focus_score'] = unique_ratio
        
        # Overall score (weighted average)
        metrics['overall_score'] = (
            metrics['coverage_score'] * 0.4 +
            metrics['clarity_score'] * 0.3 +
            metrics['focus_score'] * 0.3
        )
        
        return metrics

    def _build_prompt(self, text: str, lang: str) -> str:
        """Build enhanced prompt focusing on MAIN IDEAS extraction and key points."""
        is_thai = (lang == "th") or (lang == "auto" and self._contains_thai(text))
        text_length = len(text)
        
        # Analyze text characteristics for better prompting
        has_numbers = bool(re.search(r'\d+', text))
        has_questions = bool(re.search(r'[?？]', text))
        is_long_text = text_length > 2000
        
        if is_thai:
            # NEW: Enhanced Thai prompt focusing on MAIN IDEAS and key points
            base_instruction = "คุณเป็นผู้เชี่ยวชาญในการจับใจความและสรุปประเด็นสำคัญ กรุณาสรุปข้อความต่อไปนี้โดยเน้น"
            
            core_principles = [
                "## หลักการสำคัญ:",
                "1. **จับใจความหลัก**: ระบุประเด็นหลักที่สำคัญที่สุด 3-5 ประเด็น",
                "2. **ลำดับความสำคัญ**: เรียงลำดับจากสำคัญที่สุดไปน้อยสุด",
                "3. **เชื่อมโยงเหตุและผล**: อธิบายความสัมพันธ์ระหว่างประเด็น",
                "4. **ตัดส่วนรอง**: ตัดรายละเอียดที่ไม่สำคัญออก เก็บแต่ใจความหลัก",
                "5. **ภาษาที่เข้าใจง่าย**: ใช้ภาษาชัดเจน ตรงประเด็น กระชับ",
            ]
            
            if is_long_text:
                core_principles.append("6. **โครงสร้างชัดเจน**: จัดหมวดหมู่ประเด็นให้เป็นระบบ")
            
            if has_numbers:
                core_principles.append("7. **ข้อมูลเชิงตัวเลข**: นำเสนอสถิติสำคัญอย่างกระชับและแม่นยำ")
            
            structure_guide = [
                "",
                "## โครงสร้างที่ต้องการ:",
                "- **ประโยคแรก**: ระบุใจความหลัก (Core Message) ที่สำคัญที่สุด",
                "- **ส่วนกลาง**: ขยายความประเด็นสำคัญ 2-4 ประเด็น พร้อมเชื่อมโยง",
                "- **ประโยคสุดท้าย**: สรุปหรือนัยสำคัญ (ถ้ามี)"
            ]
            
            if has_questions:
                structure_guide.append("- **ตอบคำถาม**: ตอบคำถามที่ปรากฏในข้อความด้วยการจับใจความ")
            
            instructions_text = "\n".join(core_principles + structure_guide)
            
            prompt = f"""<|im_start|>user
{base_instruction}:

{instructions_text}

## ข้อความต้นฉบับ:
{text}<|im_end|>
<|im_start|>assistant
บทสรุปที่จับใจความหลัก:

**ใจความหลัก**: """
        else:
            # NEW: Enhanced English prompt focusing on MAIN IDEAS extraction
            base_instruction = "You are an expert in identifying main ideas and summarizing key points. Please summarize the following text"
            
            core_principles = [
                "## Key Principles:",
                "1. **Extract Main Ideas**: Identify the 3-5 most important main points",
                "2. **Prioritize**: Order from most to least important",
                "3. **Show Relationships**: Explain connections and cause-effect relationships",
                "4. **Cut Secondary Details**: Remove less important details, keep only main ideas",
                "5. **Clear Language**: Use clear, concise, direct language"
            ]
            
            if is_long_text:
                core_principles.append("6. **Clear Structure**: Organize topics systematically")
            
            if has_numbers:
                core_principles.append("7. **Numerical Data**: Present key statistics concisely and accurately")
            
            structure_guide = [
                "",
                "## Desired Structure:",
                "- **First sentence**: State the core message (most important idea)",
                "- **Middle section**: Expand on 2-4 key points with connections",
                "- **Last sentence**: Conclusion or implications (if any)"
            ]
            
            if has_questions:
                structure_guide.append("- **Answer questions**: Address questions that appear by capturing main ideas")
            
            instructions_text = "\n".join(core_principles + structure_guide)
            
            prompt = f"""<|im_start|>user
{base_instruction} by focusing on:

{instructions_text}

## Original Text:
{text}<|im_end|>
<|im_start|>assistant
Summary capturing main ideas:

**Core Message**: """
        
        return prompt

    def _generate_summary(
        self, 
        prompt: str, 
        max_new_tokens: int, 
        min_new_tokens: int, 
        do_sample: bool,
        suppress_warnings: bool = True
    ) -> str:
        """
        Generate enhanced summary using optimized model parameters with dynamic token limits.
        
        Args:
            prompt: Input prompt for generation
            max_new_tokens: Maximum number of NEW tokens to generate
            min_new_tokens: Minimum number of NEW tokens to generate
            do_sample: Whether to use sampling
            suppress_warnings: Whether to suppress model warnings
            
        Returns:
            Generated summary text
        """
        # Suppress warnings if requested
        if suppress_warnings:
            import warnings
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", message=".*Using the model-agnostic.*")
        
        # Optimize input processing based on prompt length
        prompt_tokens = self.tokenizer.encode(prompt, add_special_tokens=False)
        prompt_length = len(prompt_tokens)
        
        # Reserve space for generation (model context limit - prompt - buffer)
        max_input_length = min(2048 - max_new_tokens - 50, prompt_length)
        
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_input_length,
            padding=False
        )
        
        if torch.cuda.is_available():
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Ensure min_new_tokens is valid
        min_new_tokens = min(min_new_tokens, max_new_tokens - 10)
        min_new_tokens = max(10, min_new_tokens)  # At least 10 tokens
        
        # OPTIMIZED generation parameters for main idea extraction
        generation_params = {
            "max_new_tokens": max_new_tokens,
            "min_new_tokens": min_new_tokens,
            "do_sample": True,  # Always use sampling for better quality
            "pad_token_id": self.tokenizer.eos_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
            "early_stopping": True,
            "no_repeat_ngram_size": 4,  # Increased to avoid repetition
            "repetition_penalty": 1.3,  # Increased for more diverse vocabulary
        }
        
        if do_sample:
            # Sampling parameters optimized for focused main idea extraction
            generation_params.update({
                "temperature": 0.3,  # LOWERED: More focused on main ideas
                "top_p": 0.85,       # Nucleus sampling - focus on high probability
                "top_k": 40,         # Limit to top 40 tokens for clarity
            })
        else:
            # Even deterministic mode uses light sampling for better quality
            generation_params.update({
                "temperature": 0.25,  # Very focused
                "top_p": 0.8,
                "top_k": 30,
            })
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                attention_mask=inputs.get("attention_mask"),
                **generation_params
            )
        
        # Decode only the generated part (excluding the input prompt)
        generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        summary = self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        # Post-process the generated summary
        summary = self._post_process_generated_summary(summary)
        
        return summary
    
    def _post_process_generated_summary(self, summary: str) -> str:
        """Post-process generated summary for better paraphrasing quality."""
        if not summary:
            return summary
        
        # Remove common generation artifacts
        summary = re.sub(r'^[:\-\s]+', '', summary)  # Remove leading colons/dashes
        summary = re.sub(r'\s+', ' ', summary)       # Normalize whitespace
        
        # Ensure proper sentence structure
        if not summary.endswith(('.', '!', '?')):
            summary += '.'
        
        # Remove incomplete sentences at the end
        sentences = re.split(r'[.!?]+', summary)
        if len(sentences) > 1:
            last_sentence = sentences[-1].strip()
            if len(last_sentence) < 10:  # Very short last sentence might be incomplete
                summary = '. '.join(sentences[:-1]) + '.'
        
        # Enhanced paraphrasing quality check
        summary = self._improve_paraphrasing_quality(summary)
        
        # Apply enhanced formatting
        is_thai = self._contains_thai(summary)
        summary = self._apply_enhanced_formatting(summary, is_thai)
        
        return summary.strip()
    
    def _improve_paraphrasing_quality(self, summary: str) -> str:
        """Improve paraphrasing quality by detecting and fixing common issues."""
        if not summary:
            return summary
        
        # Split into sentences for analysis
        sentences = re.split(r'[.!?]+', summary)
        improved_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check for common paraphrasing issues
            improved_sentence = self._fix_paraphrasing_issues(sentence)
            improved_sentences.append(improved_sentence)
        
        # Rejoin sentences
        result = '. '.join(improved_sentences)
        if result and not result.endswith(('.', '!', '?')):
            result += '.'
        
        return result
    
    def _fix_paraphrasing_issues(self, sentence: str) -> str:
        """Fix common paraphrasing issues in a sentence."""
        if not sentence:
            return sentence
        
        # Remove redundant phrases that indicate poor paraphrasing
        redundant_patterns = [
            r'กล่าวว่า\s*',  # Remove "กล่าวว่า" (said that)
            r'ตามที่\s*',   # Remove "ตามที่" (according to)
            r'ในเรื่องของ\s*',  # Remove "ในเรื่องของ" (in terms of)
            r'เป็นที่ทราบกันว่า\s*',  # Remove "เป็นที่ทราบกันว่า" (it is known that)
            r'นอกจากนี้\s*แล้ว\s*',  # Remove redundant "นอกจากนี้แล้ว"
            r'อีกทั้ง\s*ยัง\s*',  # Remove redundant "อีกทั้งยัง"
        ]
        
        for pattern in redundant_patterns:
            sentence = re.sub(pattern, '', sentence, flags=re.IGNORECASE)
        
        # Improve sentence flow by removing unnecessary connectors
        flow_improvements = [
            (r'และ\s*ยัง\s*', 'และ'),
            (r'แต่\s*ก็\s*', 'แต่'),
            (r'เพราะ\s*ว่า\s*', 'เพราะ'),
            (r'เนื่องจาก\s*ว่า\s*', 'เนื่องจาก'),
        ]
        
        for old_pattern, new_pattern in flow_improvements:
            sentence = re.sub(old_pattern, new_pattern, sentence, flags=re.IGNORECASE)
        
        # Ensure sentence starts with proper capitalization
        if sentence and sentence[0].islower():
            sentence = sentence[0].upper() + sentence[1:]
        
        return sentence.strip()
    
    def _check_paraphrasing_quality(self, original_text: str, summary: str) -> dict:
        """Check the quality of paraphrasing between original and summary."""
        if not original_text or not summary:
            return {"quality_score": 0, "issues": []}
        
        issues = []
        quality_score = 100
        
        # Check for direct copying (word-for-word matches)
        original_words = set(re.findall(r'\b\w+\b', original_text.lower()))
        summary_words = set(re.findall(r'\b\w+\b', summary.lower()))
        
        # Calculate overlap ratio
        overlap = len(original_words.intersection(summary_words))
        total_words = len(original_words.union(summary_words))
        overlap_ratio = overlap / total_words if total_words > 0 else 0
        
        if overlap_ratio > 0.8:
            issues.append("Too much direct copying from original text")
            quality_score -= 30
        elif overlap_ratio > 0.6:
            issues.append("Moderate direct copying detected")
            quality_score -= 15
        
        # Check for repetitive phrases
        repetitive_patterns = [
            r'(\b\w+\b)\s+\1\b',  # Repeated words
            r'(\b\w+\s+\w+\b)\s+\1\b',  # Repeated phrases
        ]
        
        for pattern in repetitive_patterns:
            if re.search(pattern, summary, re.IGNORECASE):
                issues.append("Repetitive phrases detected")
                quality_score -= 10
        
        # Check for proper sentence structure
        sentences = re.split(r'[.!?]+', summary)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                issues.append("Very short sentences detected")
                quality_score -= 5
            elif len(sentence) > 200:
                issues.append("Very long sentences detected")
                quality_score -= 5
        
        return {
            "quality_score": max(0, quality_score),
            "issues": issues,
            "overlap_ratio": overlap_ratio,
            "sentence_count": len([s for s in sentences if s.strip()])
        }

    def _calculate_dynamic_token_quota(self, input_tokens: int, target_chars: int) -> Tuple[int, int]:
        """
        Calculate dynamic max_new_tokens and min_new_tokens based on input size and target output.
        
        Args:
            input_tokens: Number of input tokens
            target_chars: Target character length for output
            
        Returns:
            Tuple of (max_new_tokens, min_new_tokens)
        """
        # Estimate tokens from target characters (Thai: ~1.5 chars/token, English: ~4 chars/token)
        # Use conservative estimate of 2 chars/token for mixed content
        estimated_target_tokens = target_chars // 2
        
        # Calculate compression ratio (aim for 20-40% of input)
        compression_ratio = 0.3  # Default 30% compression
        
        # Calculate tokens based on compression
        base_tokens = int(input_tokens * compression_ratio)
        
        # Adjust based on target length
        if estimated_target_tokens < base_tokens:
            max_tokens = estimated_target_tokens
        else:
            max_tokens = min(base_tokens, estimated_target_tokens)
        
        # Ensure minimum viable summary
        max_tokens = max(50, max_tokens)
        
        # Min tokens should be 50-70% of max
        min_tokens = max(30, int(max_tokens * 0.6))
        
        # Cap at reasonable limits
        max_tokens = min(max_tokens, 512)
        min_tokens = min(min_tokens, max_tokens - 20)
        
        return max_tokens, min_tokens
    
    def _chunk_text_by_tokens(
        self, 
        text: str, 
        max_chunk_tokens: int = 1000, 
        overlap_tokens: int = 100,
        min_chunk_tokens: int = 100
    ) -> List[Dict[str, any]]:
        """
        Split text into chunks based on token count with overlap and metadata.
        
        Args:
            text: Input text to chunk
            max_chunk_tokens: Maximum tokens per chunk
            overlap_tokens: Number of overlapping tokens between chunks
            min_chunk_tokens: Minimum tokens for a valid chunk
            
        Returns:
            List of chunk dictionaries with text, token_count, and skip flag
        """
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = min(start + max_chunk_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_token_count = len(chunk_tokens)
            
            # Decode chunk
            chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            
            # Determine if chunk should be skipped (too short)
            should_skip = chunk_token_count < min_chunk_tokens
            
            chunks.append({
                'text': chunk_text,
                'token_count': chunk_token_count,
                'start_pos': start,
                'end_pos': end,
                'skip': should_skip
            })
            
            if end == len(tokens):
                break
            
            # Move start position with overlap
            start = end - overlap_tokens
        
        # Merge very short chunks with next chunk
        merged_chunks = []
        i = 0
        while i < len(chunks):
            current_chunk = chunks[i]
            
            # If current chunk is too short and not the last one, merge with next
            if current_chunk['skip'] and i < len(chunks) - 1:
                next_chunk = chunks[i + 1]
                # Merge the two chunks
                merged_text = current_chunk['text'] + " " + next_chunk['text']
                merged_tokens = self.tokenizer.encode(merged_text, add_special_tokens=False)
                
                merged_chunks.append({
                    'text': merged_text,
                    'token_count': len(merged_tokens),
                    'start_pos': current_chunk['start_pos'],
                    'end_pos': next_chunk['end_pos'],
                    'skip': len(merged_tokens) < min_chunk_tokens
                })
                i += 2  # Skip next chunk as it's merged
            else:
                merged_chunks.append(current_chunk)
                i += 1
        
        return merged_chunks

    def summarize(
        self,
        text: str,
        target_length: int = 1000,
        do_sample: bool = False,
        lang: str = "auto"
    ) -> str:
        """
        ENHANCED: Summarization focusing on MAIN IDEAS extraction with quality evaluation.
        
        Pipeline:
        1. Analyze text and extract importance
        2. Generate summary focused on main ideas (with improved prompt)
        3. Second-pass refinement for clarity
        4. Evaluate quality
        5. Fallback to extractive if quality too low
        
        Args:
            text: Input text to summarize
            target_length: Target character length for final summary (500-1500 recommended)
            do_sample: Whether to use sampling for generation
            lang: Language code ('auto', 'th', 'en')
            
        Returns:
            Final summary capturing main ideas clearly
        """
        if not self.is_ready():
            raise RuntimeError("Model is not ready. Please check model loading.")
        
        if not text or len(text.strip()) < 50:
            return text.strip()

        # Ensure target_length is within reasonable bounds
        target_length = max(500, min(target_length, 1500))

        # Check cache first (only for deterministic results)
        if not do_sample:
            cached_result = self.cache.get(text, target_length, lang)
            if cached_result:
                print("[Cache] Using cached result")
                return cached_result

        try:
            # Tokenize input to get accurate token count
            input_tokens = self.tokenizer.encode(text, add_special_tokens=False)
            input_token_count = len(input_tokens)
            
            print(f"Input: {len(text)} chars, {input_token_count} tokens")
            print(f"Target output: {target_length} chars")
            
            # Determine strategy based on input size
            if input_token_count <= 1500:
                # Direct summarization for short texts
                result = self._summarize_with_dynamic_tokens(
                    text, target_length, do_sample, lang
                )
            else:
                # Chunked summarization with second-pass for long texts
                result = self._chunked_summarization_with_second_pass(
                    text, input_token_count, target_length, do_sample, lang
                )
            
            # Ensure result meets target length (within tolerance)
            result = self._adjust_summary_to_target_length(result, target_length, lang)
            
            # NEW: Evaluate quality of main idea extraction
            quality_metrics = self._evaluate_main_idea_quality(text, result)
            quality_score = quality_metrics['overall_score']
            
            print(f"Quality evaluation: {quality_score:.2f} (coverage: {quality_metrics['coverage_score']:.2f}, clarity: {quality_metrics['clarity_score']:.2f}, focus: {quality_metrics['focus_score']:.2f})")
            
            # NEW: If quality is too low, try hybrid approach with extractive summary
            if quality_score < 0.5 and len(text) < 5000:
                print(f"[Warning] Quality score {quality_score:.2f} is low, trying extractive fallback...")
                extractive = self._extractive_summary_by_importance(text, target_sentences=5)
                
                # Use extractive as baseline - if it's better, use it
                extractive_quality = self._evaluate_main_idea_quality(text, extractive)
                if extractive_quality['overall_score'] > quality_score:
                    print(f"[Fallback] Using extractive summary (quality: {extractive_quality['overall_score']:.2f})")
                    result = extractive
                    quality_score = extractive_quality['overall_score']
            
            # Cache the result if deterministic and quality is acceptable
            if not do_sample and result and quality_score >= 0.5:
                self.cache.put(text, target_length, lang, result)
            
            print(f"Final output: {len(result)} chars (quality: {quality_score:.2f})")
            return result
                
        except Exception as e:
            raise RuntimeError(f"Summarization failed: {e}")
    
    def _summarize_with_dynamic_tokens(
        self,
        text: str,
        target_chars: int,
        do_sample: bool,
        lang: str
    ) -> str:
        """Summarize text with dynamically calculated token limits."""
        # Calculate token quota
        input_tokens = len(self.tokenizer.encode(text, add_special_tokens=False))
        max_new_tokens, min_new_tokens = self._calculate_dynamic_token_quota(
            input_tokens, target_chars
        )
        
        print(f"  Token quota: {min_new_tokens}-{max_new_tokens} tokens")
        
        # Build prompt and generate
        prompt = self._build_prompt(text, lang)
        summary = self._generate_summary(
            prompt, max_new_tokens, min_new_tokens, do_sample
        )
        
        return summary
    
    def _chunked_summarization_with_second_pass(
        self,
        text: str,
        input_token_count: int,
        target_chars: int,
        do_sample: bool,
        lang: str
    ) -> str:
        """
        Perform chunked summarization followed by second-pass refinement.
        
        This is the complete solution implementing:
        1. Token-based chunking with overlap
        2. Dynamic token quota per chunk
        3. Skip very short chunks
        4. Second-pass summarization to reach target length
        """
        print("Using chunked summarization with second-pass...")
        
        # Calculate optimal chunk size based on input
        # Aim for 3-8 chunks for good coverage
        target_chunks = min(8, max(3, input_token_count // 1000))
        chunk_size = input_token_count // target_chunks
        chunk_size = max(500, min(chunk_size, 1200))  # Keep chunks manageable
        overlap_size = int(chunk_size * 0.1)  # 10% overlap
        min_chunk_size = 100  # Skip chunks smaller than this
        
        print(f"  Chunking: {chunk_size} tokens/chunk, {overlap_size} overlap, min {min_chunk_size}")
        
        # Chunk the text
        chunks = self._chunk_text_by_tokens(
            text,
            max_chunk_tokens=chunk_size,
            overlap_tokens=overlap_size,
            min_chunk_tokens=min_chunk_size
        )
        
        # Filter out chunks marked for skipping
        valid_chunks = [c for c in chunks if not c['skip']]
        print(f"  Created {len(chunks)} chunks, {len(valid_chunks)} valid")
        
        if len(valid_chunks) == 0:
            # Fallback to direct summarization
            return self._summarize_with_dynamic_tokens(text, target_chars, do_sample, lang)
        
        # Calculate token quota per chunk (proportional to chunk size)
        total_chunk_tokens = sum(c['token_count'] for c in valid_chunks)
        
        # First pass: Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(valid_chunks):
            # Calculate proportional token quota for this chunk
            chunk_proportion = chunk['token_count'] / total_chunk_tokens
            chunk_target_chars = int(target_chars * 0.7 * chunk_proportion)  # Use 70% for first pass
            
            max_new_tokens, min_new_tokens = self._calculate_dynamic_token_quota(
                chunk['token_count'], chunk_target_chars
            )
            
            print(f"  Chunk {i+1}/{len(valid_chunks)}: {chunk['token_count']} tokens -> {min_new_tokens}-{max_new_tokens} tokens")
            
            # Generate chunk summary
            prompt = self._build_prompt(chunk['text'], lang)
            chunk_summary = self._generate_summary(
                prompt, max_new_tokens, min_new_tokens, do_sample
            )
            
            if chunk_summary and len(chunk_summary.strip()) > 20:
                chunk_summaries.append(chunk_summary)
        
        if not chunk_summaries:
            # Fallback
            return self._summarize_with_dynamic_tokens(text, target_chars, do_sample, lang)
        
        # Combine all chunk summaries
        combined_summary = " ".join(chunk_summaries)
        print(f"  First pass complete: {len(combined_summary)} chars from {len(chunk_summaries)} chunks")
        
        # Second pass: Refine to target length
        if len(combined_summary) > target_chars * 1.5 or len(combined_summary) < target_chars * 0.5:
            print(f"  Second pass: refining to target {target_chars} chars...")
            final_summary = self._second_pass_summarization(
                combined_summary, target_chars, lang
            )
        else:
            final_summary = combined_summary
        
        return final_summary
    
    def _second_pass_summarization(
        self,
        first_pass_summary: str,
        target_chars: int,
        lang: str
    ) -> str:
        """
        ENHANCED second-pass: Focus on clarifying MAIN IDEAS and importance hierarchy.
        
        Args:
            first_pass_summary: Combined summary from first pass
            target_chars: Target character length (500-1500)
            lang: Language code
            
        Returns:
            Refined summary with clearer main ideas
        """
        is_thai = self._contains_thai(first_pass_summary)
        
        # Build enhanced second-pass prompt focusing on MAIN IDEAS
        if is_thai:
            prompt = f"""<|im_start|>user
กรุณาปรับปรุงบทสรุปต่อไปนี้ให้ **จับใจความได้ชัดเจนขึ้น** โดย:

## เป้าหมายหลัก:
1. **ใจความหลักชัดเจน**: ประโยคแรกต้องบอกใจความหลักได้ชัดเจนทันที
2. **ลำดับความสำคัญ**: จัดเรียงประเด็นจากสำคัญที่สุดไปน้อยสุด
3. **ตัดส่วนรอง**: เก็บเฉพาะประเด็นที่สำคัญจริงๆ ตัดรายละเอียดออก
4. **เชื่อมโยงชัดเจน**: แสดงความสัมพันธ์เหตุผลระหว่างประเด็น
5. **กระชับและตรงประเด็น**: ใช้ภาษาที่เข้าใจง่าย ไม่ยืดยาด
6. **ความยาวเหมาะสม**: ประมาณ {target_chars} อักขระ

บทสรุปจากรอบแรก:
{first_pass_summary}<|im_end|>
<|im_start|>assistant
บทสรุปที่จับใจความชัดเจน:

**ใจความหลัก**: """
        else:
            prompt = f"""<|im_start|>user
Please refine the following summary to **capture main ideas more clearly** by:

## Main Goals:
1. **Clear Core Message**: First sentence must clearly state the main idea immediately
2. **Importance Hierarchy**: Order points from most to least important
3. **Remove Secondary Details**: Keep only truly important points, cut details
4. **Clear Connections**: Show logical relationships between points
5. **Concise and Focused**: Use clear language, avoid verbosity
6. **Appropriate Length**: Approximately {target_chars} characters

First-pass summary:
{first_pass_summary}<|im_end|>
<|im_start|>assistant
Refined summary with clear main ideas:

**Core Message**: """
        
        # Calculate token quota for second pass
        input_tokens = len(self.tokenizer.encode(first_pass_summary, add_special_tokens=False))
        max_new_tokens, min_new_tokens = self._calculate_dynamic_token_quota(
            input_tokens, target_chars
        )
        
        # Generate refined summary
        refined_summary = self._generate_summary(
            prompt, max_new_tokens, min_new_tokens, False
        )
        
        return refined_summary
    
    def _adjust_summary_to_target_length(
        self,
        summary: str,
        target_chars: int,
        lang: str,
        tolerance: float = 0.2
    ) -> str:
        """
        Adjust summary length to be within target range.
        
        Args:
            summary: Input summary
            target_chars: Target character length
            lang: Language code
            tolerance: Acceptable deviation (0.2 = ±20%)
            
        Returns:
            Adjusted summary
        """
        current_length = len(summary)
        min_acceptable = int(target_chars * (1 - tolerance))
        max_acceptable = int(target_chars * (1 + tolerance))
        
        # If within acceptable range, return as-is
        if min_acceptable <= current_length <= max_acceptable:
            return summary
        
        # If too long, truncate intelligently at sentence boundary
        if current_length > max_acceptable:
            sentences = re.split(r'[.!?]+', summary)
            truncated = []
            char_count = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                if char_count + len(sentence) + 2 <= target_chars:
                    truncated.append(sentence)
                    char_count += len(sentence) + 2
                else:
                    break
            
            if truncated:
                result = '. '.join(truncated) + '.'
                return result
        
        # If too short, return as-is (better than padding with nonsense)
        return summary
    
    def _refine_summary_for_paraphrasing(self, original_text: str, summary: str, lang: str) -> str:
        """Refine summary to improve paraphrasing quality."""
        if not summary:
            return summary
        
        # Check paraphrasing quality
        quality_check = self._check_paraphrasing_quality(original_text, summary)
        
        # If quality is low, try to improve it
        if quality_check["quality_score"] < 70:
            # Try to improve the summary
            improved_summary = self._attempt_summary_improvement(original_text, summary, lang)
            if improved_summary:
                # Check if improvement is better
                improved_quality = self._check_paraphrasing_quality(original_text, improved_summary)
                if improved_quality["quality_score"] > quality_check["quality_score"]:
                    return improved_summary
        
        return summary
    
    def _attempt_summary_improvement(self, original_text: str, summary: str, lang: str) -> str:
        """Attempt to improve summary paraphrasing quality."""
        try:
            # Create a refinement prompt
            is_thai = self._contains_thai(summary)
            
            # Calculate token quota
            input_tokens = len(self.tokenizer.encode(summary, add_special_tokens=False))
            target_chars = len(summary) + 50
            max_new_tokens, min_new_tokens = self._calculate_dynamic_token_quota(
                input_tokens, target_chars
            )
            
            if is_thai:
                refinement_prompt = f"""<|im_start|>user
กรุณาปรับปรุงบทสรุปต่อไปนี้ให้มีการย่อความและเรียบเรียงใหม่ที่ดีขึ้น โดย:

1. หลีกเลี่ยงการคัดลอกข้อความเดิม
2. ใช้คำและโครงสร้างประโยคใหม่
3. ทำให้อ่านง่ายและเข้าใจได้ทันที
4. รักษาความหมายเดิมไว้

บทสรุปเดิม:
{summary}<|im_end|>
<|im_start|>assistant
บทสรุปที่ปรับปรุงแล้ว:"""
            else:
                refinement_prompt = f"""<|im_start|>user
Please improve the following summary to have better paraphrasing and restructuring by:

1. Avoiding copying original text
2. Using new words and sentence structures
3. Making it easy to read and immediately understandable
4. Preserving the original meaning

Original summary:
{summary}<|im_end|>
<|im_start|>assistant
Improved summary:"""
            
            # Generate improved summary
            improved_summary = self._generate_summary(
                refinement_prompt,
                max_new_tokens,
                min_new_tokens,
                do_sample=False
            )
            
            return improved_summary
            
        except Exception as e:
            print(f"Summary improvement failed: {e}")
            return None

    def _apply_enhanced_formatting(self, summary: str, is_thai: bool) -> str:
        """Apply enhanced formatting including bullet points and better structure."""
        if not summary:
            return summary
        
        # Check numerical consistency first
        summary = self._check_and_fix_numerical_consistency(summary, is_thai)
        
        # Split into sentences for better analysis
        sentences = re.split(r'[.!?]+', summary)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 2:
            return summary  # Too short to format
        
        # Always use structured paragraphs instead of bullet points
        return self._format_as_structured_paragraphs(sentences, is_thai)

    def _check_and_fix_numerical_consistency(self, summary: str, is_thai: bool) -> str:
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

    def _should_use_bullet_formatting(self, sentences: list, is_thai: bool) -> bool:
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

    def _format_as_bullet_points(self, sentences: list, is_thai: bool) -> str:
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

    def _format_as_structured_paragraphs(self, sentences: list, is_thai: bool) -> str:
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
                self._is_paragraph_break(sentence, sentences[i + 1] if i + 1 < len(sentences) else "", is_thai)
            )
            
            if should_break:
                if current_paragraph:
                    paragraph_text = self._create_flowing_paragraph(current_paragraph, is_thai)
                    paragraphs.append(paragraph_text)
                    current_paragraph = []
        
        return "\n\n".join(paragraphs)

    def _is_paragraph_break(self, current_sentence: str, next_sentence: str, is_thai: bool) -> bool:
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

    def _create_flowing_paragraph(self, sentences: list, is_thai: bool) -> str:
        """Create a flowing paragraph from sentences with improved connectors."""
        if not sentences:
            return ""
        
        if len(sentences) == 1:
            return sentences[0] + "."
        
        # Start with the first sentence
        paragraph = sentences[0]
        
        # Add remaining sentences with appropriate connectors
        for i, sentence in enumerate(sentences[1:], 1):
            connector = self._get_improved_connector(sentence, i, len(sentences), is_thai)
            paragraph += f" {connector} {sentence}"
        
        return paragraph + "."

    def _get_improved_connector(self, sentence: str, position: int, total: int, is_thai: bool) -> str:
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

    def _build_key_points_prompt(self, text: str, lang: str) -> str:
        """Build prompt specifically for extracting key points."""
        is_thai = (lang == "th") or (lang == "auto" and self._contains_thai(text))
        
        if is_thai:
            prompt = f"""<|im_start|>user
กรุณาแยกประเด็นสำคัญ 5-8 ประเด็นจากข้อความต่อไปนี้ โดยเน้น:
- ข้อเท็จจริงหลัก
- ข้อมูลสำคัญ
- การวิเคราะห์ที่สำคัญ
- ข้อสรุปที่เกี่ยวข้อง

ข้อความ:
{text}<|im_end|>
<|im_start|>assistant
ประเด็นสำคัญ:"""
        else:
            prompt = f"""<|im_start|>user
Please extract 5-8 key points from the following text, focusing on:
- Main facts
- Important data
- Critical analysis
- Relevant conclusions

Text:
{text}<|im_end|>
<|im_start|>assistant
Key Points:"""
        
        return prompt

    def get_model_info(self) -> Dict[str, str]:
        return {
            "model_name": self.model_name,
            "model_type": "Typhoon-7B",
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "ready": str(self.is_ready())
        }


# Global summarizer instance
summarizer = TyphoonSummarizer()

# FastAPI app
app = FastAPI(
    title="Typhoon Text Summarizer API",
    description="FastAPI service for text summarization using SCB10X/typhoon-7b",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "message": "Typhoon Text Summarizer API",
        "version": "1.0.0",
        "model_info": summarizer.get_model_info()
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_ready": summarizer.is_ready(),
        "model_info": summarizer.get_model_info()
    }


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """
    Summarize text with dynamic token allocation and second-pass refinement.
    
    Parameters:
    - text: Input text to summarize
    - target_length: Target character length for summary (500-1500 recommended, default 1000)
    - do_sample: Whether to use sampling (default False for consistent results)
    - lang: Language code ('auto', 'th', 'en')
    
    The system will:
    1. Automatically chunk long texts with overlap
    2. Calculate proportional token quotas per chunk
    3. Skip chunks that are too short
    4. Perform second-pass summarization to reach target length
    """
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Start timing
        import time
        start_time = time.time()
        
        input_length = len(request.text)
        summary = summarizer.summarize(
            text=request.text,
            target_length=request.target_length,
            do_sample=request.do_sample,
            lang=request.lang
        )
        
        # Calculate timing and statistics
        end_time = time.time()
        processing_time = end_time - start_time
        output_length = len(summary)
        compression_ratio = (1 - output_length / input_length) * 100 if input_length > 0 else 0
        
        return SummarizeResponse(
            summary=summary,
            model=summarizer.model_name,
            input_length=input_length,
            output_length=output_length,
            processing_time=processing_time,
            compression_ratio=compression_ratio
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model-info")
async def get_model_info():
    return summarizer.get_model_info()


@app.get("/cache-info")
async def get_cache_info():
    """Get cache statistics."""
    return {
        "cache_size": len(summarizer.cache.cache),
        "max_size": summarizer.cache.max_size,
        "hit_ratio": "N/A"  # Could be implemented with hit/miss counters
    }


@app.post("/clear-cache")
async def clear_cache():
    """Clear the summarization cache."""
    summarizer.cache.clear()
    return {"message": "Cache cleared successfully"}


@app.post("/check-paraphrasing-quality")
async def check_paraphrasing_quality(request: dict):
    """Check the paraphrasing quality between original text and summary."""
    try:
        original_text = request.get("original_text", "")
        summary = request.get("summary", "")
        
        if not original_text or not summary:
            raise HTTPException(status_code=400, detail="Both original_text and summary are required")
        
        quality_check = summarizer._check_paraphrasing_quality(original_text, summary)
        
        return {
            "quality_score": quality_check["quality_score"],
            "issues": quality_check["issues"],
            "overlap_ratio": quality_check["overlap_ratio"],
            "sentence_count": quality_check["sentence_count"],
            "recommendations": _get_quality_recommendations(quality_check)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _get_quality_recommendations(quality_check: dict) -> list:
    """Get recommendations based on quality check results."""
    recommendations = []
    
    if quality_check["quality_score"] < 50:
        recommendations.append("Consider using a different summarization approach")
        recommendations.append("Try increasing max_length parameter")
    elif quality_check["quality_score"] < 70:
        recommendations.append("Summary could benefit from better paraphrasing")
        recommendations.append("Consider using do_sample=True for more creative output")
    
    if quality_check["overlap_ratio"] > 0.6:
        recommendations.append("High overlap detected - try to use more diverse vocabulary")
    
    if "Repetitive phrases detected" in quality_check["issues"]:
        recommendations.append("Remove repetitive phrases for better flow")
    
    if quality_check["sentence_count"] < 3:
        recommendations.append("Consider adding more sentences for better detail")
    elif quality_check["sentence_count"] > 8:
        recommendations.append("Consider reducing sentence count for better conciseness")
    
    return recommendations


@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """
    Generate text completion using Typhoon model.
    Useful for chatbot and general text generation.
    """
    import time
    
    if not summarizer.model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        start_time = time.time()
        
        # Tokenize input
        inputs = summarizer.tokenizer(
            request.prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        )
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = summarizer.model.generate(
                **inputs,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature,
                do_sample=request.do_sample,
                top_p=0.95,
                repetition_penalty=1.1,
                pad_token_id=summarizer.tokenizer.pad_token_id,
                eos_token_id=summarizer.tokenizer.eos_token_id
            )
        
        # Decode
        full_response = summarizer.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the generated part (after the prompt)
        response = full_response[len(request.prompt):].strip()
        
        processing_time = time.time() - start_time
        
        print(f"Generated {len(response)} chars in {processing_time:.2f}s")
        
        return GenerateResponse(
            response=response,
            model=summarizer.model_name,
            input_length=len(request.prompt),
            output_length=len(response)
        )
    
    except Exception as e:
        print(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
