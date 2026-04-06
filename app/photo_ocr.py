import json
import os
import re
from typing import List, Dict

QUESTION_START_RE = re.compile(r'^\s*(\d+[\.)、)]|[一二三四五六七八九十]+[\.、])')
CHOICE_RE = re.compile(r'^\s*([A-D])[\.、\)]\s*(.+)')
TRUE_FALSE_RE = re.compile(r'\b(True|False|正确|错误|对|错)\b', re.I)

def _load_paddleocr():
    try:
        from paddleocr import PaddleOCR
        return PaddleOCR
    except Exception as e:
        raise RuntimeError(
            "当前环境没有安装 PaddleOCR。请先按 README 里的说明安装 paddlepaddle 和 paddleocr。"
        ) from e

def _result_item_to_dict(item):
    if isinstance(item, dict):
        return item

    # PaddleOCR v3 Result object often exposes json / res
    if hasattr(item, "json"):
        try:
            data = item.json
            if callable(data):
                data = data()
            if isinstance(data, str):
                return json.loads(data)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    if hasattr(item, "res"):
        try:
            res = item.res
            if isinstance(res, dict):
                return {"res": res}
        except Exception:
            pass

    # Last resort
    try:
        return json.loads(str(item))
    except Exception:
        return {}

def extract_text_lines(image_path: str) -> List[str]:
    PaddleOCR = _load_paddleocr()

    # PaddleOCR 3.x official API uses predict(), not ocr(..., cls=...).
    # Disable optional preprocessing modules for speed and compatibility.
    ocr = PaddleOCR(
        lang="ch",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    result = ocr.predict(
        image_path,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    lines: List[str] = []
    if not result:
        return lines

    try:
        items = list(result)
    except Exception:
        items = [result]

    for item in items:
        data = _result_item_to_dict(item)
        res = data.get("res", {}) if isinstance(data, dict) else {}

        # PaddleOCR 3.x documented field
        rec_texts = res.get("rec_texts", []) if isinstance(res, dict) else []
        if isinstance(rec_texts, list) and rec_texts:
            for text in rec_texts:
                if text and str(text).strip():
                    lines.append(str(text).strip())
            continue

        # Fallback for older nested structure
        if isinstance(item, list):
            for sub in item:
                try:
                    text = sub[1][0]
                    if text and str(text).strip():
                        lines.append(str(text).strip())
                except Exception:
                    continue

    return lines

def split_questions(lines: List[str]) -> List[Dict]:
    blocks = []
    current = []
    for line in lines:
        if QUESTION_START_RE.search(line) and current:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)

    questions = []
    for i, block in enumerate(blocks, start=1):
        text = " ".join(block).strip()
        if not text:
            continue
        choices = []
        type_guess = "written"
        for line in block:
            m = CHOICE_RE.search(line)
            if m:
                choices.append(f"{m.group(1)}. {m.group(2)}")
        if choices:
            type_guess = "multiple_choice"
        elif TRUE_FALSE_RE.search(text):
            type_guess = "true_false"
        questions.append({
            "number": str(i),
            "raw_lines": block,
            "question": text,
            "type": type_guess,
            "choices": choices,
        })
    return questions

def keyword_explanation(question_text: str, subject: str) -> str:
    q = question_text.lower()
    if subject.lower() == "math":
        if "slope" in q or "斜率" in q:
            return "这题和斜率有关。先找出两个点，再用斜率公式：(y2-y1)/(x2-x1)。如果题目给的是 y=mx+b，那么 m 就是斜率。"
        if "vertex" in q or "顶点" in q or "parabola" in q:
            return "这题和二次函数图像有关。若是 y=(x-h)^2+k，顶点就是 (h,k)。再结合开口方向、对称轴和零点来分析。"
        if "sin" in q or "cos" in q or "tan" in q or "三角" in q:
            return "这题和三角函数有关。直角三角形里：sin=对边/斜边，cos=邻边/斜边，tan=对边/邻边。"
        return "这是一道数学题。先找题目给出的已知量，再判断属于哪个单元：函数、方程、三角、数列或统计，然后一步一步列式求解。"
    if subject.lower() == "chemistry":
        if "proton" in q or "electron" in q or "atomic" in q or "原子" in q:
            return "这题和原子结构有关。原子序数决定质子数，中性原子里电子数等于质子数，中子数=质量数-原子序数。"
        if "bond" in q or "ionic" in q or "covalent" in q or "化学键" in q:
            return "这题和化学键有关。离子键通常是电子转移，共价键通常是电子共享。"
        if "acid" in q or "base" in q or "ph" in q or "酸" in q or "碱" in q:
            return "这题和酸碱有关。先看 pH 判断酸碱性：小于 7 通常偏酸，大于 7 通常偏碱。"
        return "这是一道化学题。先判断属于原子结构、周期表、化学键、化学反应还是酸碱溶液，再用粒子观点解释。"
    if subject.lower() == "physics":
        if "velocity" in q or "acceleration" in q or "speed" in q or "速度" in q or "加速度" in q:
            return "这题和运动学有关。先分清 speed、velocity、acceleration，再看题目给的是路程、位移还是时间。"
        if "force" in q or "newton" in q or "力" in q:
            return "这题和力学有关。先画受力分析，再判断合力是否为零。若涉及牛顿第二定律，可用 F=ma。"
        if "circuit" in q or "current" in q or "voltage" in q or "电流" in q or "电压" in q:
            return "这题和电路有关。先判断是串联还是并联，再分析电流、电压和电阻之间的关系。"
        return "这是一道物理题。先看属于运动学、动力学、能量、波还是电学，再把物理量和单位列清楚。"
    return "这是基础 OCR 讲解版本。先找出题目中的已知条件，再判断题型和所属单元，然后分步骤求解。"

def infer_answer(question: str, choices: List[str], qtype: str) -> str:
    if qtype == "true_false":
        if any(x in question for x in ["不是", "不等于", "错误", "false"]):
            return "False"
        return "True"
    if qtype == "multiple_choice":
        return "A"
    return "请结合题目条件作答"

def analyze_question_page(image_path: str, subject: str) -> Dict:
    lines = extract_text_lines(image_path)
    if not lines:
        return {"questions": []}
    questions = split_questions(lines)
    final = []
    for i, q in enumerate(questions, start=1):
        final.append({
            "number": q["number"] or str(i),
            "question": q["question"],
            "type": q["type"],
            "choices": q["choices"],
            "answer": infer_answer(q["question"], q["choices"], q["type"]),
            "explanation": keyword_explanation(q["question"], subject),
            "unit_guess": "",
            "difficulty": "medium",
        })
    return {"questions": final}
