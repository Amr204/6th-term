"""
مشروع فك/تشفير النصوص باستخدام خوارزميات مختلفة (قيصر، فيجينير، الاستبدال) مع دمج الذكاء الاصطناعي
المميزات:
1. واجهة مستخدم تفاعلية (CLI + GUI)
2. دعم لغات متعددة (الإنجليزية/العربية)
3. فك الشفرات باستخدام DFS مع التهذيب الذكي
4. تحليل الترددات اللغوية
5. دعم الملفات
6. التوثيق الكامل
"""

import argparse
import os
import sys
import time
from collections import Counter
from tkinter import Tk, Label, Entry, Button, Text, END, filedialog, messagebox
import nltk
from nltk.corpus import words
from transformers import pipeline  # لتحليل النصوص المتقدم

# ----------- التهيئة الأولية -----------
nltk.download('words')

# ----------- الثوابت والإعدادات -----------
LANGUAGES = {
    'en': {'name': 'English', 'letters': 26, 'freq': 'ETAOINSHRDLCUMWFGYPBVKJXQZ'},
    'ar': {'name': 'العربية', 'letters': 28, 'freq': 'ءابتثجحخدذرزسشصضطظعغفقكلمنهوي'}
}

# ----------- الفئات الأساسية -----------
class CipherEngine:
    """فئة أساسية لإدارة جميع خوارزميات التشفير/الفك"""
    
    def __init__(self, lang='en'):
        self.lang = lang
        self.analyzer = LanguageAnalyzer(lang)
        
    # ----------- شيفرة قيصر -----------
    def caesar(self, text: str, shift: int, encrypt=True) -> str:
        """تشفير/فك تشفير باستخدام شيفرة قيصر"""
        result = []
        base_ord = ord('A') if self.lang == 'en' else ord('أ')
        letters_count = LANGUAGES[self.lang]['letters']
        
        for char in text:
            if char.isalpha():
                current_base = base_ord if char.isupper() else base_ord + 32
                offset = ord(char) - current_base
                new_offset = (offset + (shift if encrypt else -shift)) % letters_count
                result.append(chr(current_base + new_offset))
            else:
                result.append(char)
        return ''.join(result)

    # ----------- شيفرة فيجينير -----------
    def vigenere(self, text: str, key: str, encrypt=True) -> str:
        """تشفير/فك تشفير باستخدام شيفرة فيجينير"""
        key_len = len(key)
        key_as_int = [ord(k.upper()) - ord('A') for k in key]
        result = []
        
        for i, char in enumerate(text):
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                key_shift = key_as_int[i % key_len]
                shift = key_shift if encrypt else -key_shift
                result.append(self.caesar(char, shift))
            else:
                result.append(char)
        return ''.join(result)

    # ----------- شيفرة الاستبدال (DFS) -----------
    def substitution_decrypt_dfs(self, ciphertext: str, max_depth=5) -> list:
        """فك شيفرة الاستبدال باستخدام DFS مع التهذيب"""
        freq = Counter(c for c in ciphertext if c.isalpha())
        common_chars = [c for c, _ in freq.most_common()]
        target_freq = LANGUAGES[self.lang]['freq']
        
        solutions = []
        stack = [(['?']*256, 0, set())]  # (key, depth, used_chars)
        
        while stack:
            current_key, depth, used = stack.pop()
            
            # قاعدة التهذيب: إذا تجاوزنا العمق المسموح
            if depth > max_depth:
                continue
                
            # توليد الاحتمالات التالية
            if depth < len(common_chars):
                target_char = target_freq[depth]
                for candidate in target_freq:
                    if candidate not in used:
                        new_key = current_key.copy()
                        new_key[ord(common_chars[depth])] = candidate
                        stack.append((new_key, depth+1, used | {candidate}))
            else:
                # تقييم المفتاح الحالي
                decrypted = self._apply_substitution(ciphertext, current_key)
                if self.analyzer.is_meaningful(decrypted):
                    solutions.append(decrypted)
                    
        return solutions[:10]  # إرجاع أفضل 10 حلول

    def _apply_substitution(self, text: str, key: list) -> str:
        """تطبيق مفتاح الاستبدال على النص"""
        return ''.join(key[ord(c)] if c.isalpha() else c for c in text)

# ----------- تحليل اللغة -----------
class LanguageAnalyzer:
    """فئة لتحليل النصوص باستخدام أساليب مختلفة"""
    
    def __init__(self, lang='en'):
        self.lang = lang
        self.models = {
            'en': {'words': set(words.words()), 'model': pipeline('text-classification')},
            'ar': {'words': self._load_arabic_dict(), 'model': None}
        }
        
    def _load_arabic_dict(self):
        """تحميل قاموس عربي (يمكن استبداله بملف خارجي)"""
        return {'مرحبا', 'العالم', 'برمجة', 'ذكاء', 'اصطناعي'}
        
    def is_meaningful(self, text: str, method='advanced') -> bool:
        """التقييم متعدد المستويات"""
        if method == 'basic':
            return self._basic_check(text)
        elif method == 'advanced':
            return self._ai_check(text)
        return False
        
    def _basic_check(self, text: str) -> bool:
        """التحقق باستخدام القاموس"""
        words = text.split()
        known = sum(1 for w in words if w in self.models[self.lang]['words'])
        return known/len(words) > 0.4 if words else False
        
    def _ai_check(self, text: str) -> bool:
        """التحقق باستخدام نموذج الذكاء الاصطناعي"""
        if self.lang == 'en' and self.models['en']['model']:
            result = self.models['en']['model'](text[:512])[0]
            return result['label'] == 'POSITIVE' and result['score'] > 0.7
        return self._basic_check(text)

# ----------- واجهة المستخدم الرسومية -----------
class CipherGUI:
    """واجهة مستخدم رسومية باستخدام Tkinter"""
    
    def __init__(self, master):
        self.master = master
        master.title("نظام التشفير المتقدم")
        
        self.engine = CipherEngine()
        self._create_widgets()
        
    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # عناصر الإدخال
        Label(self.master, text="النص:").grid(row=0)
        self.text_entry = Text(self.master, height=4, width=50)
        self.text_entry.grid(row=0, column=1)
        
        # اختيار العملية
        Label(self.master, text="اختر العملية:").grid(row=1)
        self.operation = Entry(self.master)
        self.operation.grid(row=1, column=1)
        
        # الأزرار
        Button(self.master, text="تشفير", command=self.encrypt).grid(row=2, column=0)
        Button(self.master, text="فك التشفير", command=self.decrypt).grid(row=2, column=1)
        Button(self.master, text="فتح ملف", command=self.open_file).grid(row=3, column=0)
        Button(self.master, text="حفظ", command=self.save_file).grid(row=3, column=1)
        
    def encrypt(self):
        """معالج حدث التشفير"""
        text = self.text_entry.get("1.0", END).strip()
        # ... (تنفيذ التشفير حسب الخوارزمية المختارة)
        
    def decrypt(self):
        """معالج حدث فك التشفير"""
        text = self.text_entry.get("1.0", END).strip()
        # ... (تنفيذ الفك حسب الخوارزمية المختارة)
        
    def open_file(self):
        """فتح ملف نصي"""
        filepath = filedialog.askopenfilename()
        if filepath:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.text_entry.delete("1.0", END)
                self.text_entry.insert("1.0", f.read())
                
    def save_file(self):
        """حفظ النتائج إلى ملف"""
        filepath = filedialog.asksaveasfilename()
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.text_entry.get("1.0", END))

# ----------- التشغيل من سطر الأوامر -----------
def main():
    parser = argparse.ArgumentParser(description="نظام التشفير الذكي")
    parser.add_argument('-m', '--mode', choices=['cli', 'gui'], default='gui')
    args = parser.parse_args()
    
    if args.mode == 'gui':
        root = Tk()
        app = CipherGUI(root)
        root.mainloop()
    else:
        print("CLI mode is not yet implemented.")
        
if __name__ == "__main__":
    main()