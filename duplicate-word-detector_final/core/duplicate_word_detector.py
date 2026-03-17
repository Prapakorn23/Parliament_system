"""
โมเดลตรวจจับคำซ้ำจากข้อความภาษาไทย (Enhanced v2)
ใช้ PyThaiNLP สำหรับการวิเคราะห์ Part-of-Speech และการนับความถี่ของคำ
ปรับปรุงประสิทธิภาพด้วย:
- Similarity-based word grouping (รวมคำที่คล้ายกัน)
- N-gram phrase detection (ตรวจจับวลีซ้ำ)
- Duplicate scoring & threshold (ให้คะแนนและจัดอันดับคำซ้ำ)
- Enhanced preprocessing & stopwords
- Caching และ parallel processing
"""

import re
import math
import pandas as pd
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional, Any, Set
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.graph_objects as go
import time
from concurrent.futures import ThreadPoolExecutor
import threading

# PyThaiNLP imports
import pythainlp
from pythainlp.tokenize import word_tokenize
from pythainlp.tag import pos_tag
from pythainlp.corpus import thai_stopwords
from pythainlp.util import normalize

# Import performance utilities
from .performance_utils import (
    PerformanceTracker, CacheManager, ParallelProcessor,
    timing_decorator, get_performance_summary
)


# --- Parliament-specific stopwords ---
PARLIAMENT_STOPWORDS = {
    'ที่', 'ของ', 'ใน', 'เป็น', 'และ', 'มี', 'ได้', 'จะ', 'ให้', 'กับ',
    'จาก', 'โดย', 'แล้ว', 'ไม่', 'ว่า', 'ก็', 'ยัง', 'กัน', 'ซึ่ง', 'ด้วย',
    'หรือ', 'อยู่', 'แต่', 'นั้น', 'นี้', 'ไป', 'มา', 'เพื่อ', 'ถึง', 'แม้',
    'ทั้ง', 'เมื่อ', 'ต่อ', 'ตาม', 'ผ่าน', 'ขึ้น', 'ลง', 'ออก', 'คือ', 'อัน',
    'บ้าง', 'ครับ', 'ค่ะ', 'ครั้ง', 'อีก', 'ทำ', 'เรา', 'ท่าน', 'เรียน',
    'กราบเรียน', 'ประธาน', 'สมาชิก', 'ผม', 'ดิฉัน', 'ขอ', 'ขอบคุณ',
    'เพราะ', 'เพราะว่า', 'ดัง', 'เช่น', 'อย่าง', 'เลย', 'ต้อง', 'ควร',
    'อาจ', 'คง', 'น่า', 'แค่', 'เฉพาะ', 'ถ้า', 'หาก', 'แม้ว่า',
    'ระหว่าง', 'ภายใน', 'ภายนอก', 'ข้าง', 'บน', 'ล่าง', 'หน้า', 'หลัง',
    'ทุก', 'ทั้งหมด', 'บาง', 'หลาย', 'มาก', 'น้อย', 'เท่า', 'ประมาณ',
    'ฉะนั้น', 'ดังนั้น', 'เพราะฉะนั้น', 'อย่างไรก็ตาม', 'อย่างไรก็ดี',
    'สำหรับ', 'เกี่ยวกับ', 'เนื่องจาก', 'พร้อม', 'รวม', 'แยก',
}


class ThaiDuplicateWordDetector:
    """
    คลาสสำหรับตรวจจับคำซ้ำในข้อความภาษาไทย (Enhanced v2)
    
    คุณสมบัติใหม่:
    - Similarity grouping: รวมคำที่เป็น substring ของกัน เช่น "การศึกษา" + "การศึกษาขั้นพื้นฐาน"
    - N-gram detection: ตรวจจับวลีซ้ำ (bigram, trigram, 4-gram)
    - Duplicate scoring: ให้คะแนนความสำคัญของคำซ้ำจาก frequency, spread, word length
    - Threshold filtering: กำหนดขั้นต่ำของความถี่ที่จะถือว่าเป็น "คำซ้ำ"
    - Enhanced stopwords: เพิ่ม stopwords สำหรับบริบทรัฐสภา
    """

    def __init__(self, tokenize_engine='long',
                 duplicate_threshold=2,
                 enable_ngram=True,
                 ngram_min=2, ngram_max=4, ngram_min_freq=2,
                 enable_similarity=True,
                 similarity_threshold=0.6,
                 score_weights=None):
        self.stopwords = set(thai_stopwords()) | PARLIAMENT_STOPWORDS
        self.word_frequency = Counter()
        self.pos_frequency = defaultdict(Counter)
        self.processed_texts = []
        self.tokenize_engine = tokenize_engine

        # Enhanced detection settings
        self.duplicate_threshold = duplicate_threshold
        self.enable_ngram = enable_ngram
        self.ngram_min = ngram_min
        self.ngram_max = ngram_max
        self.ngram_min_freq = ngram_min_freq
        self.enable_similarity = enable_similarity
        self.similarity_threshold = similarity_threshold
        self.score_weights = score_weights or {
            'frequency': 0.4, 'spread': 0.3, 'length': 0.3
        }

        self.performance_tracker = PerformanceTracker()
        self.cache_manager = CacheManager()
        self.parallel_processor = ParallelProcessor()
        self._lock = threading.Lock()

    # ================================================================
    # Preprocessing
    # ================================================================

    @timing_decorator("preprocess_text")
    def preprocess_text(self, text: str) -> str:
        """ทำความสะอาดข้อความก่อนการประมวลผล"""
        cache_key = f"preprocess_{hash(text)}"
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Normalize Thai characters (sara am, repeated marks, etc.)
        text = normalize(text)

        # แทนที่เครื่องหมายขีดกลาง/ขีดล่างด้วยช่องว่าง เพื่อไม่สูญเสียข้อมูล
        text = re.sub(r'[-_/\\]+', ' ', text)

        # ลบตัวเลขที่อยู่โดดๆ แต่เก็บตัวเลขที่ติดกับตัวอักษร (เช่น "5G", "PM2.5")
        text = re.sub(r'(?<![a-zA-Z\u0E00-\u0E7F])\d+(?![a-zA-Z\u0E00-\u0E7F])', '', text)

        # ลบเครื่องหมายวรรคตอนและอักขระพิเศษ (เก็บไทย, อังกฤษ, ช่องว่าง)
        text = re.sub(r'[^\u0E00-\u0E7Fa-zA-Z\s]', '', text)

        # ลบช่องว่างที่เกิน
        text = re.sub(r'\s+', ' ', text)

        result = text.strip()
        self.cache_manager.set(cache_key, result)
        return result

    # ================================================================
    # Tokenization & POS Tagging
    # ================================================================

    @timing_decorator("tokenize_and_tag")
    def tokenize_and_tag(self, text: str) -> List[Tuple[str, str]]:
        """แยกคำและติดแท็ก Part-of-Speech"""
        cache_key = f"tokenize_{hash(text)}"
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            tokens = word_tokenize(text, engine=self.tokenize_engine)
        except Exception as e:
            print(f"Warning: Tokenize engine '{self.tokenize_engine}' not available, using 'newmm': {e}")
            tokens = word_tokenize(text, engine='newmm')

        pos_tags = pos_tag(tokens, engine='perceptron')

        enhanced_pos_tags = []
        for token, pos in pos_tags:
            token_stripped = token.strip()
            if not token_stripped:
                continue

            if re.match(r'^[a-zA-Z]+$', token_stripped):
                tag = 'NCMN' if len(token_stripped) > 3 else 'VACT'
                enhanced_pos_tags.append((token_stripped.lower(), tag))
            elif re.match(r'^[^\u0E00-\u0E7Fa-zA-Z]+$', token_stripped):
                continue
            elif len(token_stripped) == 1 and pos not in ['NCMN', 'NOUN', 'VACT', 'VERB', 'PROP']:
                continue
            else:
                enhanced_pos_tags.append((token_stripped, pos))

        self.cache_manager.set(cache_key, enhanced_pos_tags)
        return enhanced_pos_tags

    # ================================================================
    # POS Filtering
    # ================================================================

    def filter_by_pos(self, pos_tags: List[Tuple[str, str]],
                      target_pos: List[str] = None) -> List[Tuple[str, str]]:
        """กรองคำตาม Part-of-Speech พร้อม enhanced stopwords"""
        if target_pos is None:
            target_pos = ['NOUN', 'VERB', 'NCMN', 'VACT', 'VSTA', 'PROP', 'ADJ', 'ADVN']

        filtered = []
        for word, pos in pos_tags:
            if word in self.stopwords:
                continue

            is_important = (
                len(word) > 2
                or pos in ('NCMN', 'NOUN', 'VACT', 'VERB', 'PROP')
            )
            if is_important and any(tag in pos for tag in target_pos):
                filtered.append((word, pos))

        return filtered

    # ================================================================
    # Word Normalization (ช่วย group คำรูปแบบต่างๆ)
    # ================================================================

    @staticmethod
    def _normalize_word(word: str) -> str:
        """ลด variation ของคำให้เป็นรูปมาตรฐาน"""
        w = word.strip()
        w = re.sub(r'[\u0E31\u0E34-\u0E3A\u0E47-\u0E4E]+', '', w)  # strip vowels & tone marks for comparison
        return w.lower()

    # ================================================================
    # Similarity Grouping
    # ================================================================

    def _group_similar_words(self, word_counts: Counter) -> Dict[str, Dict]:
        """
        รวมกลุ่มคำที่มีลักษณะคล้ายกัน:
        1. Substring match: "การศึกษา" ⊂ "การศึกษาขั้นพื้นฐาน"
        2. Normalized match: คำที่ต่างกันแค่สระ/วรรณยุกต์
        
        Returns dict ที่ key = representative word, value = {
            'members': [(word, freq), ...],
            'total_frequency': int,
            'representative': str
        }
        """
        if not self.enable_similarity:
            return {
                w: {'members': [(w, c)], 'total_frequency': c, 'representative': w}
                for w, c in word_counts.items()
            }

        words = sorted(word_counts.keys(), key=lambda w: (-word_counts[w], -len(w)))
        assigned: Dict[str, str] = {}
        groups: Dict[str, Dict] = {}

        for word in words:
            if word in assigned:
                continue

            group_key = word
            groups[group_key] = {
                'members': [(word, word_counts[word])],
                'total_frequency': word_counts[word],
                'representative': word
            }
            assigned[word] = group_key

            for other in words:
                if other in assigned or other == word:
                    continue

                sim = self._word_similarity(word, other)
                if sim >= self.similarity_threshold:
                    groups[group_key]['members'].append((other, word_counts[other]))
                    groups[group_key]['total_frequency'] += word_counts[other]
                    assigned[other] = group_key

        return groups

    def _word_similarity(self, a: str, b: str) -> float:
        """
        คำนวณความคล้ายกันระหว่างคำสองคำ (0.0 - 1.0)
        ใช้ผสมระหว่าง substring match + character overlap
        """
        if a == b:
            return 1.0

        shorter, longer = (a, b) if len(a) <= len(b) else (b, a)

        # Substring match (ถ้า shorter อยู่ใน longer ทั้งคำ)
        if len(shorter) >= 3 and shorter in longer:
            return len(shorter) / len(longer)

        # Character-level Jaccard similarity
        set_a = set(a)
        set_b = set(b)
        intersection = set_a & set_b
        union = set_a | set_b
        if not union:
            return 0.0

        jaccard = len(intersection) / len(union)

        # Prefix bonus: คำที่ขึ้นต้นเหมือนกัน
        common_prefix = 0
        for ca, cb in zip(a, b):
            if ca == cb:
                common_prefix += 1
            else:
                break
        prefix_ratio = common_prefix / max(len(a), len(b)) if max(len(a), len(b)) > 0 else 0

        return 0.5 * jaccard + 0.5 * prefix_ratio

    # ================================================================
    # N-gram Phrase Detection
    # ================================================================

    def _detect_ngram_duplicates(self, tokens: List[str]) -> Dict[str, int]:
        """
        ตรวจจับวลีซ้ำ (n-gram) จาก token list
        
        Returns: dict ของ { "วลี": frequency } เฉพาะที่ frequency >= ngram_min_freq
        """
        if not self.enable_ngram:
            return {}

        ngram_counts: Counter = Counter()

        for n in range(self.ngram_min, self.ngram_max + 1):
            for i in range(len(tokens) - n + 1):
                gram = tokens[i:i + n]
                # กรองถ้า gram มีแต่ stopwords
                meaningful = [w for w in gram if w not in self.stopwords and len(w) > 1]
                if len(meaningful) < max(1, n // 2):
                    continue
                phrase = ' '.join(gram)
                ngram_counts[phrase] += 1

        return {
            phrase: count
            for phrase, count in ngram_counts.items()
            if count >= self.ngram_min_freq
        }

    # ================================================================
    # Duplicate Scoring
    # ================================================================

    def _calculate_duplicate_scores(self, word_counts: Counter,
                                     token_positions: Dict[str, List[int]],
                                     total_tokens: int) -> Dict[str, Dict]:
        """
        ให้คะแนนความสำคัญของคำซ้ำ โดยพิจารณาจาก:
        - frequency: ความถี่สัมพัทธ์
        - spread: การกระจายตัวในข้อความ (ซ้ำทั่วข้อความ vs กระจุกตัว)
        - length: ความยาวของคำ (คำยาว = สำคัญกว่า)
        """
        if total_tokens == 0:
            return {}

        max_freq = max(word_counts.values()) if word_counts else 1
        max_len = max((len(w) for w in word_counts), default=1)
        scores = {}

        for word, freq in word_counts.items():
            if freq < self.duplicate_threshold:
                continue

            # Frequency score (normalized)
            freq_score = freq / max_freq

            # Spread score: วัดจาก standard deviation ของตำแหน่ง
            positions = token_positions.get(word, [])
            if len(positions) >= 2:
                mean_pos = sum(positions) / len(positions)
                variance = sum((p - mean_pos) ** 2 for p in positions) / len(positions)
                std = math.sqrt(variance)
                spread_score = min(1.0, std / (total_tokens / 2)) if total_tokens > 0 else 0
            else:
                spread_score = 0.0

            # Length score (normalized)
            length_score = len(word) / max_len

            w = self.score_weights
            composite = (
                w['frequency'] * freq_score
                + w['spread'] * spread_score
                + w['length'] * length_score
            )

            scores[word] = {
                'frequency': freq,
                'score': round(composite, 4),
                'freq_score': round(freq_score, 4),
                'spread_score': round(spread_score, 4),
                'length_score': round(length_score, 4),
            }

        return dict(sorted(scores.items(), key=lambda x: -x[1]['score']))

    # ================================================================
    # Main Analysis (Enhanced)
    # ================================================================

    def analyze_text(self, text: str,
                     filter_pos: bool = True,
                     target_pos: List[str] = None,
                     track_time: bool = True) -> Dict:
        """
        วิเคราะห์ข้อความและนับความถี่ของคำ (Enhanced v2)
        
        ผลลัพธ์ใหม่ที่เพิ่มเข้ามา:
        - duplicate_scores: คะแนนความสำคัญของคำซ้ำ
        - similar_groups: กลุ่มคำที่คล้ายกัน
        - ngram_duplicates: วลีซ้ำ (bigram, trigram, ...)
        - flagged_duplicates: คำที่ frequency >= threshold
        """
        if track_time:
            self.performance_tracker.start_timing("analyze_text")

        cleaned_text = self.preprocess_text(text)
        pos_tags = self.tokenize_and_tag(cleaned_text)

        if filter_pos:
            pos_tags = self.filter_by_pos(pos_tags, target_pos)

        # นับความถี่
        word_counts = Counter([word for word, pos in pos_tags])
        pos_counts = Counter([pos for word, pos in pos_tags])

        # จัดเก็บตำแหน่งของแต่ละคำ (สำหรับ spread scoring)
        token_positions: Dict[str, List[int]] = defaultdict(list)
        for idx, (word, pos) in enumerate(pos_tags):
            token_positions[word].append(idx)

        total_tokens = len(pos_tags)

        # --- Enhanced features ---

        # 1. Duplicate scoring
        duplicate_scores = self._calculate_duplicate_scores(
            word_counts, token_positions, total_tokens
        )

        # 2. Similarity grouping
        similar_groups = self._group_similar_words(word_counts)

        # 3. N-gram detection
        token_list = [word for word, pos in pos_tags]
        ngram_duplicates = self._detect_ngram_duplicates(token_list)

        # 4. Flagged duplicates (ผ่าน threshold)
        flagged = {
            w: c for w, c in word_counts.items()
            if c >= self.duplicate_threshold
        }

        # บันทึกข้อมูล
        with self._lock:
            self.word_frequency.update(word_counts)
            for word, pos in pos_tags:
                self.pos_frequency[word][pos] += 1

            self.processed_texts.append({
                'original_text': text,
                'cleaned_text': cleaned_text,
                'word_count': len(word_counts),
                'total_words': total_tokens,
                'word_frequency': word_counts,
                'pos_frequency': pos_counts,
                'filtered_words': pos_tags,
                'analysis_time': time.time()
            })

        result = {
            # Original fields (backward-compatible)
            'word_frequency': word_counts,
            'pos_frequency': pos_counts,
            'total_words': total_tokens,
            'unique_words': len(word_counts),
            'filtered_words': pos_tags,

            # Enhanced fields
            'duplicate_scores': duplicate_scores,
            'similar_groups': {
                k: {
                    'members': v['members'],
                    'total_frequency': v['total_frequency'],
                    'representative': v['representative']
                }
                for k, v in similar_groups.items()
                if v['total_frequency'] >= self.duplicate_threshold
            },
            'ngram_duplicates': dict(
                sorted(ngram_duplicates.items(), key=lambda x: -x[1])[:50]
            ),
            'flagged_duplicates': flagged,
            'duplicate_count': len(flagged),
            'duplicate_threshold': self.duplicate_threshold,
        }

        if track_time:
            duration = self.performance_tracker.end_timing("analyze_text")
            result['processing_time'] = duration

        return result

    # ================================================================
    # Duplicate Report
    # ================================================================

    def get_duplicate_report(self, result: Dict, top_n: int = 20) -> Dict:
        """
        สร้างรายงานสรุปคำซ้ำอย่างละเอียด
        
        Returns:
            Dict ที่มี:
            - top_duplicates: คำซ้ำ top-N พร้อมคะแนน
            - grouped_duplicates: กลุ่มคำที่คล้ายกัน
            - phrase_duplicates: วลีซ้ำ top-N
            - summary: สรุปภาพรวม
        """
        scores = result.get('duplicate_scores', {})
        groups = result.get('similar_groups', {})
        ngrams = result.get('ngram_duplicates', {})

        top_duplicates = list(scores.items())[:top_n]

        phrase_list = sorted(ngrams.items(), key=lambda x: -x[1])[:top_n]

        multi_member_groups = {
            k: v for k, v in groups.items()
            if len(v.get('members', [])) > 1
        }

        total_words = result.get('total_words', 0)
        dup_count = result.get('duplicate_count', 0)
        unique = result.get('unique_words', 0)
        dup_ratio = dup_count / unique if unique > 0 else 0

        return {
            'top_duplicates': [
                {'word': w, **info} for w, info in top_duplicates
            ],
            'grouped_duplicates': multi_member_groups,
            'phrase_duplicates': [
                {'phrase': p, 'frequency': f} for p, f in phrase_list
            ],
            'summary': {
                'total_words': total_words,
                'unique_words': unique,
                'duplicate_count': dup_count,
                'duplicate_ratio': round(dup_ratio, 4),
                'threshold_used': self.duplicate_threshold,
                'total_phrase_duplicates': len(ngrams),
                'total_similar_groups': len(multi_member_groups),
            }
        }
    
    def get_most_frequent_words(self, n: int = 20) -> List[Tuple[str, int]]:
        """
        ดึงคำที่มีความถี่สูงสุด
        
        Args:
            n (int): จำนวนคำที่ต้องการ
            
        Returns:
            List[Tuple[str, int]]: รายการคำและความถี่
        """
        return self.word_frequency.most_common(n)
    
    def get_word_pos_distribution(self, word: str) -> Dict[str, int]:
        """
        ดึงการกระจายของ POS tags สำหรับคำที่กำหนด
        
        Args:
            word (str): คำที่ต้องการดูการกระจาย
            
        Returns:
            Dict[str, int]: การกระจายของ POS tags
        """
        return dict(self.pos_frequency[word])
    
    def create_word_frequency_chart(self, n: int = 20, 
                                  figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
        """
        สร้างกราฟแสดงความถี่ของคำ
        
        Args:
            n (int): จำนวนคำที่ต้องการแสดง
            figsize (Tuple[int, int]): ขนาดของกราฟ
            
        Returns:
            plt.Figure: กราฟที่สร้างแล้ว
        """
        top_words = self.get_most_frequent_words(n)
        
        if not top_words:
            print("ไม่มีข้อมูลคำที่พบ")
            return None
        
        words, frequencies = zip(*top_words)
        
        plt.figure(figsize=figsize)
        plt.barh(range(len(words)), frequencies)
        plt.yticks(range(len(words)), words)
        plt.xlabel('ความถี่')
        plt.title(f'คำที่มีความถี่สูงสุด {n} คำ')
        plt.gca().invert_yaxis()
        
        # แก้ไขแกน X ให้แสดงจำนวนเต็ม
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        
        plt.tight_layout()
        
        return plt.gcf()
    
    def create_wordcloud(self, max_words: int = 100, 
                        figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
        """
        สร้าง Word Cloud
        
        Args:
            max_words (int): จำนวนคำสูงสุดใน Word Cloud
            figsize (Tuple[int, int]): ขนาดของกราฟ
            
        Returns:
            plt.Figure: Word Cloud ที่สร้างแล้ว
        """
        if not self.word_frequency:
            print("ไม่มีข้อมูลคำที่พบ")
            return None
        
        try:
            # สร้าง Word Cloud โดยไม่ใช้ฟอนต์เฉพาะ
            wordcloud = WordCloud(
                width=figsize[0]*100,
                height=figsize[1]*100,
                background_color='white',
                max_words=max_words,
                colormap='viridis',
                font_step=1,
                relative_scaling=0.5
            ).generate_from_frequencies(self.word_frequency)
            
            plt.figure(figsize=figsize)
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Word Cloud ของคำที่พบ')
            
        except Exception as e:
            print(f"Error creating wordcloud: {e}")
            # สร้างกราฟแทน Word Cloud
            top_words = self.get_most_frequent_words(20)
            if top_words:
                words, frequencies = zip(*top_words)
                plt.figure(figsize=figsize)
                plt.barh(range(len(words)), frequencies)
                plt.yticks(range(len(words)), words)
                plt.xlabel('ความถี่')
                plt.title('คำที่มีความถี่สูงสุด (แทน Word Cloud)')
                plt.gca().invert_yaxis()
                
                # แก้ไขแกน X ให้แสดงจำนวนเต็ม
                plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
            else:
                plt.figure(figsize=figsize)
                plt.text(0.5, 0.5, 'ไม่มีข้อมูลคำ', ha='center', va='center', fontsize=16)
                plt.axis('off')
                plt.title('ไม่มีข้อมูลคำ')
        
        return plt.gcf()
    
    def create_interactive_chart(self, n: int = 20) -> go.Figure:
        """
        สร้างกราฟแบบ Interactive ด้วย Plotly
        
        Args:
            n (int): จำนวนคำที่ต้องการแสดง
            
        Returns:
            go.Figure: กราฟ Interactive
        """
        top_words = self.get_most_frequent_words(n)
        
        if not top_words:
            print("ไม่มีข้อมูลคำที่พบ")
            return None
        
        words, frequencies = zip(*top_words)
        
        fig = go.Figure(data=[
            go.Bar(
                x=frequencies,
                y=words,
                orientation='h',
                text=frequencies,
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>ความถี่: %{x}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=f'คำที่มีความถี่สูงสุด {n} คำ',
            xaxis_title='ความถี่',
            yaxis_title='คำ',
            height=600,
            showlegend=False
        )
        
        return fig
    
    def export_results(self, filename: str = 'word_analysis_results.xlsx', language: str = 'mixed'):
        """
        ส่งออกผลการวิเคราะห์เป็นไฟล์ Excel
        
        Args:
            filename (str): ชื่อไฟล์ที่ต้องการบันทึก
            language (str): ภาษาสำหรับการส่งออก ('mixed' = ทั้งไทยและอังกฤษ)
        """
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # แผ่นข้อมูลความถี่ของคำ (ภาษาไทย)
            word_freq_df_thai = pd.DataFrame(
                self.word_frequency.most_common(),
                columns=['คำ', 'ความถี่']
            )
            word_freq_df_thai.to_excel(writer, sheet_name='ความถี่คำ', index=False)
            
            # แผ่นข้อมูลความถี่ของคำ (ภาษาอังกฤษ)
            word_freq_df_eng = pd.DataFrame(
                self.word_frequency.most_common(),
                columns=['Word', 'Frequency']
            )
            word_freq_df_eng.to_excel(writer, sheet_name='Word Frequency', index=False)
            
            # แผ่นข้อมูลสรุปการวิเคราะห์ (ภาษาไทย)
            summary_data_thai = []
            for i, text_data in enumerate(self.processed_texts):
                summary_data_thai.append({
                    'ข้อความที่': i+1,
                    'จำนวนคำทั้งหมด': text_data['total_words'],
                    'จำนวนคำเฉพาะ': text_data['word_count'],
                    'คำที่ซ้ำมากที่สุด': text_data['word_frequency'].most_common(1)[0][0] if text_data['word_frequency'] else 'ไม่มี',
                    'ความถี่สูงสุด': text_data['word_frequency'].most_common(1)[0][1] if text_data['word_frequency'] else 0
                })
            
            summary_df_thai = pd.DataFrame(summary_data_thai)
            summary_df_thai.to_excel(writer, sheet_name='สรุปการวิเคราะห์', index=False)
            
            # แผ่นข้อมูลสรุปการวิเคราะห์ (ภาษาอังกฤษ)
            summary_data_eng = []
            for i, text_data in enumerate(self.processed_texts):
                summary_data_eng.append({
                    'Text #': i+1,
                    'Total Words': text_data['total_words'],
                    'Unique Words': text_data['word_count'],
                    'Most Frequent Word': text_data['word_frequency'].most_common(1)[0][0] if text_data['word_frequency'] else 'None',
                    'Max Frequency': text_data['word_frequency'].most_common(1)[0][1] if text_data['word_frequency'] else 0
                })
            
            summary_df_eng = pd.DataFrame(summary_data_eng)
            summary_df_eng.to_excel(writer, sheet_name='Analysis Summary', index=False)
    
    def analyze_multiple_texts(self, texts: List[str], 
                              filter_pos: bool = True,
                              target_pos: List[str] = None,
                              parallel: bool = True) -> List[Dict]:
        """
        วิเคราะห์ข้อความหลายข้อความแบบขนาน
        
        Args:
            texts (List[str]): รายการข้อความที่ต้องการวิเคราะห์
            filter_pos (bool): ต้องการกรองตาม POS หรือไม่
            target_pos (List[str]): รายการ POS tags ที่ต้องการ
            parallel (bool): ใช้การประมวลผลแบบขนานหรือไม่
            
        Returns:
            List[Dict]: รายการผลการวิเคราะห์
        """
        if parallel and len(texts) > 1:
            # ใช้การประมวลผลแบบขนาน
            def analyze_single_text(text):
                return self.analyze_text(text, filter_pos, target_pos, track_time=False)
            
            results = self.parallel_processor.process_texts_parallel(texts, analyze_single_text)
        else:
            # ใช้การประมวลผลแบบปกติ
            results = []
            for text in texts:
                result = self.analyze_text(text, filter_pos, target_pos, track_time=False)
                results.append(result)
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """ดึงสถิติประสิทธิภาพ"""
        return {
            'performance_tracker': self.performance_tracker.get_stats(),
            'cache_stats': self.cache_manager.get_stats(),
            'total_texts_processed': len(self.processed_texts),
            'total_words_processed': sum(text_data['total_words'] for text_data in self.processed_texts),
            'average_processing_time': self.performance_tracker.get_average_timing("analyze_text")
        }
    
    def clear_cache(self):
        """ล้าง cache"""
        self.cache_manager.clear()
    
    def reset(self):
        """รีเซ็ตข้อมูลทั้งหมด"""
        with self._lock:
            self.word_frequency.clear()
            self.pos_frequency.clear()
            self.processed_texts.clear()
            self.performance_tracker = PerformanceTracker()
            self.cache_manager.clear()


def main():
    """ฟังก์ชันหลักสำหรับการทดสอบ Enhanced v2"""
    detector = ThaiDuplicateWordDetector(
        duplicate_threshold=2,
        enable_ngram=True,
        enable_similarity=True,
        similarity_threshold=0.6,
    )

    sample_text = (
        "ประเทศไทยเป็นประเทศที่สวยงาม ประเทศไทยมีวัฒนธรรมที่หลากหลาย "
        "ประเทศไทยมีอาหารที่อร่อย การศึกษาขั้นพื้นฐานเป็นสิ่งสำคัญ "
        "การศึกษามีบทบาทในการพัฒนาประเทศ กระทรวงศึกษาธิการดูแลการศึกษา "
        "เทคโนโลยีใหม่ช่วยเพิ่มคุณภาพการศึกษา เทคโนโลยีช่วยในการทำงาน "
        "เทคโนโลยีมีประโยชน์มาก งบประมาณด้านการศึกษาเพิ่มขึ้น "
        "งบประมาณของกระทรวงศึกษาธิการถูกจัดสรรมาก"
    )

    print("=" * 70)
    print(" Enhanced Duplicate Word Detector v2 — Demo")
    print("=" * 70)

    result = detector.analyze_text(sample_text)

    print(f"\n📊 สรุปพื้นฐาน:")
    print(f"   คำทั้งหมด: {result['total_words']}")
    print(f"   คำไม่ซ้ำ: {result['unique_words']}")
    print(f"   คำซ้ำ (≥{result['duplicate_threshold']}): {result['duplicate_count']}")

    print(f"\n🏆 คำซ้ำ Top-10 (เรียงตามคะแนน):")
    for word, info in list(result['duplicate_scores'].items())[:10]:
        print(f"   {word:20s} freq={info['frequency']:3d}  score={info['score']:.3f}")

    groups = result.get('similar_groups', {})
    multi = {k: v for k, v in groups.items() if len(v['members']) > 1}
    if multi:
        print(f"\n🔗 กลุ่มคำที่คล้ายกัน ({len(multi)} กลุ่ม):")
        for rep, g in list(multi.items())[:5]:
            members_str = ', '.join(f"{w}({c})" for w, c in g['members'])
            print(f"   [{rep}] total={g['total_frequency']}: {members_str}")

    ngrams = result.get('ngram_duplicates', {})
    if ngrams:
        print(f"\n📝 วลีซ้ำ ({len(ngrams)} วลี):")
        for phrase, freq in list(ngrams.items())[:10]:
            print(f"   \"{phrase}\" × {freq}")

    report = detector.get_duplicate_report(result)
    print(f"\n📋 สรุปรายงาน:")
    for k, v in report['summary'].items():
        print(f"   {k}: {v}")


if __name__ == "__main__":
    main()
