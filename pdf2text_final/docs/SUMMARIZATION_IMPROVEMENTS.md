# 📝 การปรับปรุงระบบสรุป - เน้นจับใจความหลัก

**วันที่**: 23 ธันวาคม 2025  
**เวอร์ชัน**: 2.0 - Main Ideas Focus

---

## 🎯 ภาพรวมการปรับปรุง

การปรับปรุงครั้งนี้มุ่งเน้นให้ระบบสรุป**จับใจความหลักได้ดีขึ้น**โดย:

1. ✅ **ปรับ Prompt** ให้เน้นการระบุประเด็นหลัก 3-5 ประเด็น
2. ✅ **เพิ่ม Importance Scoring** คำนวณความสำคัญของแต่ละประโยค
3. ✅ **ปรับ Generation Parameters** (temperature 0.3 เพื่อความโฟกัส)
4. ✅ **ปรับปรุง Second-Pass** ให้เน้นความชัดเจนของใจความ
5. ✅ **เพิ่ม Quality Evaluation** ตรวจสอบคุณภาพการจับใจความ
6. ✅ **Extractive Fallback** ใช้ extractive summary ถ้าคุณภาพต่ำ

---

## 📊 เปรียบเทียบ Before/After

### **เวอร์ชันเดิม (1.0):**
```
Prompt: "กรุณาย่อความและเรียบเรียงข้อความต่อไปนี้ใหม่..."
Temperature: 0.4-0.7
Focus: ย่อความทั่วไป
Structure: อิสระ
Quality Check: ไม่มี
```

### **เวอร์ชันใหม่ (2.0):**
```
Prompt: "คุณเป็นผู้เชี่ยวชาญในการจับใจความ กรุณาสรุปโดยเน้น..."
Temperature: 0.3 (โฟกัสมากขึ้น)
Focus: จับใจความหลัก 3-5 ประเด็น + ลำดับความสำคัญ
Structure: Main Idea → Key Points → Conclusion
Quality Check: Coverage, Clarity, Focus scores
Fallback: Extractive summary ถ้าคุณภาพต่ำกว่า 0.5
```

---

## 🔧 การเปลี่ยนแปลงโดยละเอียด

### **1. Prompt Engineering (ไฟล์: `_build_prompt`)**

#### **Prompt เดิม:**
```python
"กรุณาย่อความและเรียบเรียงข้อความต่อไปนี้ใหม่ โดยไม่คัดลอกข้อความเดิม"

คำสั่ง:
1. ย่อความและใช้คำใหม่
2. จัดระเบียบข้อมูล
3. เชื่อมโยงประเด็น
...
```

#### **Prompt ใหม่:**
```python
"คุณเป็นผู้เชี่ยวชาญในการจับใจความและสรุปประเด็นสำคัญ"

หลักการสำคัญ:
1. **จับใจความหลัก**: ระบุประเด็นหลัก 3-5 ประเด็น
2. **ลำดับความสำคัญ**: เรียงจากสำคัญสุดไปน้อยสุด
3. **เชื่อมโยงเหตุและผล**: อธิบายความสัมพันธ์
4. **ตัดส่วนรอง**: ตัดรายละเอียดออก เก็บแต่ใจความ
5. **ภาษาชัดเจน**: ตรงประเด็น กระชับ

โครงสร้าง:
- ประโยคแรก: ใจความหลัก (Core Message)
- ส่วนกลาง: ขยายความ 2-4 ประเด็น
- ประโยคสุดท้าย: สรุปหรือนัยสำคัญ
```

**ผลลัพธ์:**
- 🎯 โมเดลเข้าใจบริบทได้ดีขึ้น
- 🎯 สรุปมีโครงสร้างชัดเจน
- 🎯 ไม่เสียเวลากับรายละเอียดรอง

---

### **2. Generation Parameters**

```python
# เดิม
temperature: 0.4-0.7  # ค่อนข้างสูง อาจทำให้ไม่โฟกัส
top_p: 0.9
top_k: 50
no_repeat_ngram_size: 3
repetition_penalty: 1.2

# ใหม่ (Optimized for Main Ideas)
temperature: 0.3       # ⬇️ ลดลง = โฟกัสมากขึ้น
top_p: 0.85            # ⬇️ ลดลง = เลือกคำที่มั่นใจมากขึ้น
top_k: 40              # ⬇️ ลดลง = จำกัดตัวเลือก
no_repeat_ngram_size: 4    # ⬆️ เพิ่ม = ลดการซ้ำ
repetition_penalty: 1.3    # ⬆️ เพิ่ม = หลากหลายมากขึ้น
do_sample: True (เสมอ)     # ใช้ sampling เพื่อคุณภาพ
```

**ผลลัพธ์:**
- ✨ คำตอบมีความมั่นใจและโฟกัสมากขึ้น
- ✨ ลดการใช้คำซ้ำ
- ✨ เลือกคำที่สำคัญและเหมาะสมมากขึ้น

---

### **3. Second-Pass Refinement**

#### **เดิม:**
```
เป้าหมาย: ปรับความยาวและลดความซ้ำซ้อน
```

#### **ใหม่:**
```
เป้าหมาย: จับใจความให้ชัดเจนขึ้น

1. ใจความหลักชัดเจน: ประโยคแรกต้องบอกใจความหลักทันที
2. ลำดับความสำคัญ: จัดเรียงจากสำคัญสุดไปน้อยสุด
3. ตัดส่วนรอง: เก็บเฉพาะประเด็นสำคัญจริงๆ
4. เชื่อมโยงชัดเจน: แสดงความสัมพันธ์เหตุผล
5. กระชับตรงประเด็น: ไม่ยืดยาด
```

**ผลลัพธ์:**
- 🎯 ใจความหลักปรากฏชัดในประโยคแรก
- 🎯 ประเด็นจัดเรียงตามความสำคัญ
- 🎯 ตัดรายละเอียดรองออกได้มากขึ้น

---

### **4. Importance Scoring (NEW!)**

**ฟังก์ชันใหม่:** `_score_sentence_importance()`

คำนวณคะแนนความสำคัญของประโยคจาก 7 ปัจจัย:

```python
1. Position (20%): ประโยคต้นๆ มักสำคัญกว่า
2. Length (10%): ความยาวพอดี (60-120 chars) ดีที่สุด
3. Key Phrases (15%): มีคำสำคัญ เช่น "ประเด็นสำคัญ", "หลัก"
4. Numbers (10%): มีตัวเลข/วันที่
5. Named Entities (10%): มีชื่อองค์กร, บุคคล
6. Questions (10%): มีเครื่องหมายคำถาม
7. Important Starters (20%): ขึ้นต้นด้วยคำสำคัญ

Total Score: 0.0 - 1.0
```

**การใช้งาน:**
```python
score = self._score_sentence_importance(sentence, full_text)
# score = 0.85 = ประโยคสำคัญมาก
# score = 0.3  = ประโยครอง
```

---

### **5. Quality Evaluation (NEW!)**

**ฟังก์ชันใหม่:** `_evaluate_main_idea_quality()`

ประเมินคุณภาพการจับใจความด้วย 3 metrics:

```python
1. Coverage Score (40%):
   - วัดว่าครอบคลุมคำสำคัญจากต้นฉบับหรือไม่
   - Intersection of keywords / Total keywords
   
2. Clarity Score (30%):
   - วัดความชัดเจนจากความยาวประโยค
   - ประโยคยาวพอดี (60-120 chars) = ชัดเจน
   
3. Focus Score (30%):
   - วัดความโฟกัสจาก unique words ratio
   - คำซ้ำน้อย = โฟกัสดี

Overall Score = Coverage*0.4 + Clarity*0.3 + Focus*0.3
```

**เกณฑ์คุณภาพ:**
- 🟢 **0.7-1.0**: ดีเยี่ยม - จับใจความได้ดีมาก
- 🟡 **0.5-0.7**: ดี - จับใจความได้พอใช้
- 🔴 **0.0-0.5**: ต่ำ - ต้องใช้ fallback

---

### **6. Extractive Fallback (NEW!)**

**ฟังก์ชันใหม่:** `_extractive_summary_by_importance()`

ถ้าคุณภาพ < 0.5 ระบบจะ:

1. สร้าง **Extractive Summary** โดยเลือก 5 ประโยคที่สำคัญที่สุด
2. ประเมินคุณภาพของ extractive summary
3. เปรียบเทียบกับ abstractive summary
4. เลือกอันที่ดีกว่า

```python
if quality_score < 0.5:
    extractive = self._extractive_summary_by_importance(text)
    if extractive_quality > quality_score:
        return extractive  # ใช้ extractive แทน
```

**ข้อดี:**
- 🛡️ ป้องกันการสรุปที่คุณภาพต่ำ
- 🛡️ Extractive มักจับใจความได้แม่นกว่าถ้า abstractive ล้มเหลว
- 🛡️ ไม่สูญเสียข้อมูลสำคัญ

---

## 📈 ผลลัพธ์ที่คาดหวัง

### **ข้อความสั้น (< 1,500 tokens):**
- ✅ จับใจความหลักได้ชัดเจนในประโยคแรก
- ✅ ระบุประเด็นสำคัญ 3-5 ประเด็น
- ✅ มีโครงสร้าง: Main Idea → Points → Conclusion
- ✅ Quality score > 0.6

### **ข้อความยาว (> 1,500 tokens):**
- ✅ แบ่ง chunks พร้อม overlap
- ✅ สรุปแต่ละ chunk ตามสัดส่วน
- ✅ รวม chunks → Second-pass → Refine main ideas
- ✅ Quality score > 0.55

### **กรณี Edge Cases:**
- ✅ ข้อความสั้นมาก (< 50 chars): คืนค่าเดิม
- ✅ คุณภาพต่ำ: ใช้ extractive fallback
- ✅ ข้อความซ้ำ: Cache hit (fast response)

---

## 🧪 วิธีทดสอบ

### **1. ทดสอบพื้นฐาน**

```bash
# รัน Typhoon API
python scripts/setup/run_typhoon_api.py

# ใน Python อื่น
from apis.typhoon_client import typhoon_client

text = """
[ข้อความตัวอย่างที่ต้องการทดสอบ]
"""

summary = typhoon_client.summarize(text, target_length=1000, lang="th")
print(summary)
```

### **2. ตรวจสอบคุณภาพ**

ดูใน console output:

```
Input: 5000 chars, 1800 tokens
Target output: 1000 chars
Using chunked summarization with second-pass...
Quality evaluation: 0.72 (coverage: 0.68, clarity: 0.75, focus: 0.74)
Final output: 983 chars (quality: 0.72)
```

**Quality Score แปลว่า:**
- **> 0.7**: 🟢 ดีเยี่ยม
- **0.5-0.7**: 🟡 ดี
- **< 0.5**: 🔴 ต่ำ (จะใช้ fallback)

### **3. เปรียบเทียบ Before/After**

สร้างไฟล์ test:

```python
test_cases = [
    "ข้อความเกี่ยวกับรัฐสภา...",
    "ข้อความเกี่ยวกับนโยบาย...",
    "ข้อความเกี่ยวกับเศรษฐกิจ..."
]

for text in test_cases:
    summary = typhoon_client.summarize(text, target_length=800)
    
    # ตรวจสอบ:
    # ✓ ประโยคแรกบอกใจความหลักชัดเจนไหม?
    # ✓ มีประเด็นสำคัญ 3-5 ประเด็นไหม?
    # ✓ จัดเรียงตามความสำคัญไหม?
    # ✓ ตัดรายละเอียดรองออกไหม?
```

---

## 📝 ตัวอย่างผลลัพธ์

### **Input (ข้อความยาว 3,000 chars):**
```
[เอกสารเกี่ยวกับการประชุมรัฐสภา ระเบียบวาระ รายละเอียดต่างๆ...]
```

### **Output เดิม (v1.0):**
```
การประชุมรัฐสภาครั้งนี้มีวาระต่างๆ รวมถึงการรับรองรายงาน
การพิจารณาเรื่องต่างๆ และมีเอกสารประกอบหลายชุด...
[ไม่ชัดว่าประเด็นหลักคืออะไร]
```

### **Output ใหม่ (v2.0):**
```
**ใจความหลัก**: การประชุมรัฐสภาครั้งที่ 2 มีวาระสำคัญ 3 เรื่อง
คือการรับรองรายงาน การพิจารณาร่างกฎหมาย และเรื่องด่วน

**ประเด็นสำคัญ**: ประธานจะแจ้งต่อที่ประชุม คณะกรรมาธิการได้
พิจารณาเสร็จแล้ว และมีเอกสารประกอบเผยแพร่ทาง parliament.go.th

**สรุป**: สมาชิกสามารถเข้าถึงเอกสารได้ล่วงหน้าผ่านเว็บไซต์
ตามข้อบังคับฯ พ.ศ. 2560
```

**เปรียบเทียบ:**
- ✅ ใจความหลักชัดเจนทันที (วาระสำคัญ 3 เรื่อง)
- ✅ มีโครงสร้าง (Main → Points → Conclusion)
- ✅ ตัดรายละเอียดรองออก
- ✅ อ่านเข้าใจง่ายขึ้น

---

## 🔍 Troubleshooting

### **ปัญหา: Quality Score ต่ำ (< 0.5)**

**สาเหตุ:**
1. ข้อความต้นฉบับซับซ้อนเกินไป
2. ไม่มีประเด็นหลักที่ชัดเจน
3. ภาษาผสม (ไทย-อังกฤษ) มาก

**แก้ไข:**
- ระบบจะใช้ extractive summary อัตโนมัติ
- หรือปรับ `target_length` ให้ยาวขึ้น

### **ปัญหา: สรุปยาวเกินไป**

**แก้ไข:**
```python
summary = typhoon_client.summarize(
    text, 
    target_length=800,  # ลดลง
    lang="th"
)
```

### **ปัญหา: จับใจความไม่ชัดเจน**

**ตรวจสอบ:**
1. ดู quality score ใน console
2. ถ้า coverage_score < 0.5 = ข้อความซับซ้อนเกินไป
3. ลอง extractive summary:

```python
# ใช้ extractive แทน (fallback manual)
from apis.typhoon_summarizer_api import summarizer

extractive = summarizer._extractive_summary_by_importance(text, target_sentences=5)
```

---

## 🎓 Best Practices

### **1. เลือก `target_length` ที่เหมาะสม**

| ความยาวต้นฉบับ | target_length แนะนำ | เหตุผล |
|---------------|---------------------|--------|
| < 1,000 chars | 500-600 chars | สั้นพอ ไม่ต้องสรุปมาก |
| 1,000-3,000 chars | 700-1,000 chars | สมดุล |
| 3,000-10,000 chars | 1,000-1,200 chars | ต้องการ chunking |
| > 10,000 chars | 1,200-1,500 chars | ใช้ second-pass |

### **2. ระบุภาษา (`lang`) ชัดเจน**

```python
# ดีกว่า
summary = typhoon_client.summarize(text, lang="th")  # ระบุชัด

# กว่า
summary = typhoon_client.summarize(text, lang="auto")  # อาจเดาผิด
```

### **3. ใช้ `do_sample=False` สำหรับความสม่ำเสมอ**

```python
summary = typhoon_client.summarize(
    text, 
    do_sample=False  # ผลลัพธ์เหมือนเดิมทุกครั้ง + ใช้ cache
)
```

---

## 📚 สรุป

การปรับปรุงครั้งนี้ทำให้ระบบสรุป:

✅ **จับใจความหลักได้ดีขึ้น** - เน้นประเด็นสำคัญ 3-5 ประเด็น  
✅ **มีโครงสร้างชัดเจน** - Main Idea → Points → Conclusion  
✅ **โฟกัสมากขึ้น** - temperature 0.3, ตัดรายละเอียดรอง  
✅ **มีการตรวจสอบคุณภาพ** - Coverage, Clarity, Focus metrics  
✅ **มี Fallback** - ใช้ extractive ถ้าคุณภาพต่ำ  
✅ **อ่านเข้าใจง่ายขึ้น** - ใจความหลักปรากฏชัดในประโยคแรก  

---

**🚀 พร้อมใช้งานแล้ว!** รีสตาร์ท Typhoon API แล้วทดสอบได้เลยครับ!

```bash
# รีสตาร์ท API
python scripts/setup/run_typhoon_api.py
```

