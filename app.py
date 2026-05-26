import tkinter as tk
import sympy as sp
from sympy import sin, cos, tan, log, sqrt, pi, E, factorial
import speech_recognition as sr

x = sp.Symbol('x')

# =========================
# STATE
# =========================
dark_mode = False
history = []


# =========================
# SAFE STRING CONVERTER (IMPORTANT FIX)
# =========================
def safe_str(obj):
    try:
        return str(obj)
    except:
        return repr(obj)


# =========================
# SOLVER
# =========================
def solve_expr(expr):
    try:
        expr = expr.replace("^", "**")

        if "=" in expr:
            lhs, rhs = expr.split("=")
            lhs = sp.sympify(lhs)
            rhs = sp.sympify(rhs)

            eq = lhs - rhs
            sol = sp.solve(eq, x)

            return f"{safe_str(lhs)} = {safe_str(rhs)}\n\nSolution:\n{safe_str(sol)}"

        else:
            expr_sym = sp.sympify(expr)
            simplified = sp.simplify(expr_sym)
            result = simplified.evalf()

            return f"Expression:\n{safe_str(expr_sym)}\n\nResult:\n{safe_str(result)}"

    except Exception as e:
        return f"Error: {e}"


# =========================
# RESULT BOX
# =========================
def show_result(text):
    result_box.config(state="normal")
    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, safe_str(text))
    result_box.config(state="disabled")


# =========================
# 🔥 FIXED HISTORY (GUARANTEED WORKING)
# =========================
def update_history(expr, result):
    history.append((safe_str(expr), safe_str(result)))

    history_box.config(state="normal")
    history_box.delete("1.0", tk.END)

    if len(history) == 0:
        history_box.insert(tk.END, "No history yet")
    else:
        for i, (e, r) in enumerate(history[-20:], start=1):
            history_box.insert(tk.END, f"{i}. {e}\n→ {r}\n\n")

    history_box.see("end")
    history_box.config(state="disabled")


# =========================
# ACTIONS
# =========================
def solve():
    expr = entry.get()
    result = solve_expr(expr)

    show_result(result)
    update_history(expr, result)


def clear():
    entry.delete(0, tk.END)
    show_result("")


def delete():
    entry.delete(len(entry.get()) - 1)


# =========================
# INSERT
# =========================
def insert(val):
    mapping = {
        "sin": "sin(",
        "cos": "cos(",
        "tan": "tan(",
        "log": "log(",
        "ln": "log(",
        "√": "sqrt(",
        "x²": "**2",
        "x³": "**3",
        "xʸ": "**",
        "π": "pi",
        "e": "E",
        "n!": "factorial("
    }

    entry.insert(tk.END, mapping.get(val, val))


# =========================
# VOICE
# =========================
def voice():
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            status.config(text="🎤 Listening...")
            root.update()

            audio = r.listen(source, timeout=6)
            text = r.recognize_google(audio)

            entry.delete(0, tk.END)
            entry.insert(0, text)

            solve()

            status.config(text="Done")

    except Exception as e:
        status.config(text=f"Voice error: {e}")


# =========================
# THEME
# =========================
def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode

    if dark_mode:
        bg, fg, box, btn = "#121212", "white", "#1e1e1e", "#2a2a2a"
    else:
        bg, fg, box, btn = "#e8f0fe", "black", "white", "#f0f0f0"

    root.configure(bg=bg)
    entry.configure(bg=box, fg=fg, insertbackground=fg)
    result_box.configure(bg=box, fg=fg)
    history_box.configure(bg=box, fg=fg)
    status.configure(bg=bg, fg=fg)

    for w in btn_frame.winfo_children():
        w.configure(bg=btn, fg=fg)

    for w in ctrl_frame.winfo_children():
        w.configure(bg=btn, fg=fg)

    theme_btn.configure(bg=btn, fg=fg)


# =========================
# UI
# =========================
root = tk.Tk()
root.title("AI Scientific Calculator Pro")
root.geometry("900x600")
root.minsize(900, 600)
root.configure(bg="#e8f0fe")


# ENTRY
entry = tk.Entry(root, font=("Arial", 22), justify="center")
entry.pack(fill="x", padx=10, pady=10)


# BUTTONS
btn_frame = tk.Frame(root, bg="#e8f0fe")
btn_frame.pack()

buttons = [
    "sin","cos","tan","log",
    "ln","√","x²","x³",
    "xʸ","π","e","n!",
    "7","8","9","/",
    "4","5","6","*",
    "1","2","3","-",
    "0",".","(",")",
    "+"
]

r = 0
c = 0

for b in buttons:
    tk.Button(
        btn_frame,
        text=b,
        width=6,
        command=lambda b=b: insert(b)
    ).grid(row=r, column=c, padx=3, pady=3)

    c += 1
    if c > 3:
        c = 0
        r += 1


# CONTROLS
ctrl_frame = tk.Frame(root, bg="#e8f0fe")
ctrl_frame.pack(pady=10)

tk.Button(ctrl_frame, text="Solve", command=solve, width=8).grid(row=0, column=0)
tk.Button(ctrl_frame, text="Clear", command=clear, width=8).grid(row=0, column=1)
tk.Button(ctrl_frame, text="Delete", command=delete, width=8).grid(row=0, column=2)
tk.Button(ctrl_frame, text="🎤 Voice", command=voice, width=8).grid(row=0, column=3)

theme_btn = tk.Button(ctrl_frame, text="🌙 Theme", command=toggle_theme, width=8)
theme_btn.grid(row=0, column=4)


# RESULT
result_box = tk.Text(root, height=10, font=("Consolas", 12))
result_box.pack(fill="both", expand=True, padx=10, pady=10)
result_box.config(state="disabled")


# HISTORY
tk.Label(root, text="📜 History", font=("Arial", 14)).pack()

history_box = tk.Text(root, height=8, font=("Consolas", 10))
history_box.pack(fill="both", expand=True, padx=10, pady=5)
history_box.config(state="disabled")


# STATUS
status = tk.Label(root, text="", bg="#e8f0fe", fg="blue")
status.pack()


root.mainloop()