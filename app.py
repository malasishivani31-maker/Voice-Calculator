import tkinter as tk
import sympy as sp
import re
from word2number import w2n
import speech_recognition as sr
import math

x = sp.Symbol('x')

# ============================================================
# 1️⃣ AI-LIKE NATURAL LANGUAGE UNDERSTANDING
# ============================================================
def ai_understand(text):
    """
    Detects user intent (addition, subtraction, sqrt, factorial, etc.)
    and converts it into a valid mathematical expression.
    """
    text = text.lower().strip()

    # Convert number words to digits
    try:
        text = re.sub(r'\b(zero|one|two|three|four|five|six|seven|eight|nine|ten'
                      r'|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\b',
                      lambda m: str(w2n.word_to_num(m.group(0))), text)
    except:
        pass

    # Handle intent detection
    if "add" in text or "plus" in text:
        nums = re.findall(r'[\d\.]+', text)
        if len(nums) >= 2:
            return f"{nums[0]} + {nums[1]}"

    elif "subtract" in text or "minus" in text:
        nums = re.findall(r'[\d\.]+', text)
        if len(nums) >= 2:
            return f"{nums[0]} - {nums[1]}"

    elif "multiply" in text or "times" in text:
        nums = re.findall(r'[\d\.]+', text)
        if len(nums) >= 2:
            return f"{nums[0]} * {nums[1]}"

    elif "divide" in text or "divided by" in text or "over" in text:
        nums = re.findall(r'[\d\.]+', text)
        if len(nums) >= 2:
            return f"{nums[0]} / {nums[1]}"

    elif "square root" in text or "root of" in text:
        nums = re.findall(r'[\d\.]+', text)
        if len(nums) == 1:
            return f"sqrt({nums[0]})"

    elif "factorial" in text or "!" in text:
        nums = re.findall(r'[\d]+', text)
        if len(nums) == 1:
            return f"factorial({nums[0]})"

    elif "power" in text or "raised to" in text or "to the power" in text:
        nums = re.findall(r'[\d\.]+', text)
        if len(nums) >= 2:
            return f"{nums[0]}**{nums[1]}"

    # Default: return original text
    return text


# ============================================================
# 2️⃣ PREPROCESSING (RULE-BASED NLP)
# ============================================================
def preprocess_expression(text):
    text = ai_understand(text)
    text = text.lower().strip()

    # Voice corrections
    voice_corrections = {
        "sign": "sin", "sine": "sin", "seen": "sin",
        "cause": "cos", "cost": "cos", "course": "cos",
        "ten": "tan", "stand": "tan",
        "cotangent": "cot", "co tangent": "cot",
        "cosecant": "cosec", "co secant": "cosec",
        "square route": "sqrt", "screw root": "sqrt",
        "root of": "sqrt(", "square root of": "sqrt(",
        "square root": "sqrt(", "root": "sqrt(",
        "x squared": "x^2", "squared": "^2",
        "power off": "power of", "power of": "power",
        "to the power": "power", "raised to": "power",
        "factorial of": "factorial(", "factorial": "factorial(",
        "percent": "%", "percentage": "%", "modulus": "mod",
        "pie": "pi", "by": "/"
    }

    for wrong, correct in voice_corrections.items():
        text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text)

    # Replace math words
    replacements = {
        "plus": "+", "minus": "-", "times": "*",
        "divide": "/", "divided by": "/", "over": "/",
        "power": "**", "equals": "=", "equal to": "=", "^": "**"
    }
    for word, symbol in replacements.items():
        text = text.replace(word, symbol)

    # Handle factorial (also 5!)
    text = re.sub(r'(\d+)!', r'factorial(\1)', text)
    text = re.sub(r'factorial\s*\(?\s*([0-9a-zA-Z]+)\s*\)?', r'factorial(\1)', text)

    # Handle percentage
    text = re.sub(r'(\d+)%', lambda m: f"({float(m.group(1))/100})", text)

    # Handle trig functions in degrees
    text = re.sub(r'\b(sin|cos|tan|cot|sec|cosec)\s*\(?\s*(\d+(\.\d+)?)\s*\)?',
                  lambda m: f"{m.group(1)}(pi*{m.group(2)}/180)", text)

    # Handle sqrt symbols
    text = re.sub(r'√\s*([a-zA-Z0-9\+\-\*/\^\(\)]+)', r'sqrt(\1)', text)

    # Implicit multiplication
    text = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', text)
    text = re.sub(r'([a-zA-Z\)])(\d)', r'\1*\2', text)
    text = re.sub(r'(\))(\()', r'\1*\2', text)

    # Balance parentheses
    diff = text.count('(') - text.count(')')
    if diff > 0:
        text += ')' * diff

    return text


# ============================================================
# 3️⃣ STEP-BY-STEP SOLVER
# ============================================================
def solve_stepwise(expr):
    try:
        if "=" in expr:
            lhs, rhs = expr.split("=", 1)
            lhs_sym = sp.sympify(lhs)
            rhs_sym = sp.sympify(rhs)
            eq = lhs_sym - rhs_sym
            steps = [f"Equation: {sp.pretty(lhs_sym)} = {sp.pretty(rhs_sym)}"]

            eq_simplified = sp.simplify(eq)
            steps.append(f"→ Simplify: {sp.pretty(eq_simplified)} = 0")

            degree = sp.Poly(eq_simplified, x).degree()
            steps.append(f"Detected degree: {degree}")

            solutions = sp.solve(eq_simplified, x)
            steps.append("→ Solve for x:")
            for i, sol in enumerate(solutions):
                steps.append(f"   x{i+1} = {sp.pretty(sol)}")
            return "\n".join(steps)

        else:
            sym_expr = sp.sympify(expr)
            steps = [f"Expression: {sp.pretty(sym_expr)}"]
            simplified = sp.simplify(sym_expr)
            if simplified != sym_expr:
                steps.append(f"→ Simplify: {sp.pretty(simplified)}")

            evaluated = simplified.evalf()
            steps.append(f"→ Evaluate: {evaluated}")
            return "\n".join(steps)

    except Exception as e:
        return f"Error while solving: {e}"


# ============================================================
# 4️⃣ GUI FUNCTIONS
# ============================================================
def show_result_text(text):
    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, text)
    result_text.config(state="disabled")

def solve():
    expr = entry.get()
    expr = preprocess_expression(expr)
    result = solve_stepwise(expr)
    show_result_text(result)

def step_by_step():
    solve()

def clear():
    entry.delete(0, tk.END)
    show_result_text("")
    status_label.config(text="")

def delete_last():
    entry.delete(len(entry.get())-1)

def button_click(symbol):
    if symbol == "√":
        entry.insert(tk.END, "sqrt(")
    elif symbol == "x²":
        entry.insert(tk.END, "**2")
    elif symbol == "n!":
        entry.insert(tk.END, "factorial(")
    elif symbol == "%":
        entry.insert(tk.END, "%")
    else:
        entry.insert(tk.END, symbol)

def voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.config(text="🎙 Listening...")
        root.update()
        try:
            audio = recognizer.listen(source, timeout=6)
            text = recognizer.recognize_google(audio)
            status_label.config(text=f"🎧 Heard: {text}")
            root.update()

            expr = preprocess_expression(text)
            entry.delete(0, tk.END)
            entry.insert(0, expr)
            result = solve_stepwise(expr)
            show_result_text(result)
            status_label.config(text=f"✅ Solved: {text}")
        except Exception as e:
            status_label.config(text=f"❌ Voice error: {e}")


# ============================================================
# 5️⃣ GUI DESIGN
# ============================================================
root = tk.Tk()
root.title("🧮 AI Voice Scientific Calculator")
root.configure(bg="#e8f0fe")

entry = tk.Entry(root, width=35, font=("Arial", 20), justify="center", bd=5)
entry.grid(row=0, column=0, columnspan=6, padx=10, pady=15)

buttons = [
    '7', '8', '9', '/', 'sin', 'cos',
    '4', '5', '6', '*', 'tan', '√',
    '1', '2', '3', '-', 'x²', '^',
    '0', '.', '+', '(', ')', '=',
    'n!', '%'
]

row, col = 1, 0
for b in buttons:
    if b == "=":
        tk.Button(root, text=b, width=5, height=2, font=("Arial", 12),
                  bg="#aaf0a1", command=solve).grid(row=row, column=col, padx=3, pady=3)
    else:
        tk.Button(root, text=b, width=5, height=2, font=("Arial", 12),
                  command=lambda b=b: button_click(b)).grid(row=row, column=col, padx=3, pady=3)
    col += 1
    if col > 5:
        col = 0
        row += 1

control_row = row + 1
tk.Button(root, text="Solve", width=10, height=2, bg="#d9f0fc", command=solve).grid(row=control_row, column=0, padx=3, pady=3)
tk.Button(root, text="Step-by-step", width=12, height=2, bg="#fce7b2", command=step_by_step).grid(row=control_row, column=1, padx=3, pady=3)
tk.Button(root, text="Clear", width=10, height=2, bg="#ffb3b3", command=clear).grid(row=control_row, column=2, padx=3, pady=3)
tk.Button(root, text="Delete", width=10, height=2, bg="#fcd5ce", command=delete_last).grid(row=control_row, column=3, padx=3, pady=3)
tk.Button(root, text="🎤 Voice", width=10, height=2, bg="#b4f2b4", command=voice_input).grid(row=control_row, column=4, padx=3, pady=3)

result_text = tk.Text(root, height=12, width=80, font=("Consolas", 12), wrap="word", state="disabled", bd=4)
result_text.grid(row=control_row+1, column=0, columnspan=6, padx=10, pady=10)

status_label = tk.Label(root, text="", fg="blue", bg="#e8f0fe", font=("Arial", 10))
status_label.grid(row=control_row+2, column=0, columnspan=6)

root.mainloop()
