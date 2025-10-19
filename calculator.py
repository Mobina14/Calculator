"""
Engineering Calculator - tkinter (updated)
- Display changed to Label (read-only)
- Fixed trigonometric parentheses bug (adds double closing parenthesis automatically when DEG)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math

# --- Helper: safe eval environment ---
ALLOWED_NAMES = {k: getattr(math, k) for k in [
    'sin','cos','tan','asin','acos','atan','sinh','cosh','tanh',
    'log','log10','sqrt','factorial','pi','e','degrees','radians'
]}
ALLOWED_NAMES['ln'] = math.log
ALLOWED_NAMES['pow'] = pow

class CalcApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("ماشین حساب مهندسی")
        self.geometry("420x560")
        self.minsize(380,520)
        self.configure(bg="#f5f7fa")

        self.expr = tk.StringVar()
        self.mode = tk.StringVar(value='DEG')

        self._build_style()
        self._build_ui()

    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', font=('IranSans', 12), padding=8)
        style.configure('Top.TLabel', font=('IranSans', 18, 'bold'))

    def _build_ui(self):
        disp_frame = ttk.Frame(self, padding=(12,12,12,6))
        disp_frame.pack(fill='x')

        self.display_label = ttk.Label(disp_frame, textvariable=self.expr, anchor='e',
                                       background='white', font=('Consolas', 20), relief='solid', padding=10)
        self.display_label.pack(fill='x', ipady=12)

        mode_frame = ttk.Frame(self, padding=(12,0,12,8))
        mode_frame.pack(fill='x')
        self.mode_btn = ttk.Button(mode_frame, text='DEG', command=self.toggle_mode)
        self.mode_btn.pack(side='right')

        btns = [
            ['7','8','9','/','sqrt'],
            ['4','5','6','*','^'],
            ['1','2','3','-','%'],
            ['0','.','+','(',')'],
            ['pi','ln','log','!','ANS'],
            ['sin','cos','tan','BACK','C'],
            ['=']
        ]

        grid_frame = ttk.Frame(self, padding=12)
        grid_frame.pack(expand=True, fill='both')

        for r, row in enumerate(btns):
            for c, label in enumerate(row):
                if label == '=':
                    btn = ttk.Button(grid_frame, text=label, command=self.evaluate)
                    btn.grid(row=r, column=c, columnspan=5, sticky='nsew', padx=6, pady=6)
                else:
                    cmd = lambda x=label: self.on_button(x)
                    btn = ttk.Button(grid_frame, text=label, command=cmd)
                    btn.grid(row=r, column=c, sticky='nsew', padx=6, pady=6)

        for i in range(5):
            grid_frame.columnconfigure(i, weight=1)
        for i in range(len(btns)):
            grid_frame.rowconfigure(i, weight=1)

        self.bind('<Return>', lambda e: self.evaluate())
        self.bind('<BackSpace>', lambda e: self.on_button('BACK'))
        self.last_ans = None

    def toggle_mode(self):
        cur = self.mode.get()
        if cur == 'DEG':
            self.mode.set('RAD')
            self.mode_btn.config(text='RAD')
        else:
            self.mode.set('DEG')
            self.mode_btn.config(text='DEG')

    def on_button(self, label):
        s = self.expr.get()
        if label == 'C':
            self.expr.set('')
            return
        if label == 'BACK':
            self.expr.set(s[:-1])
            return
        if label == 'ANS':
            if self.last_ans is not None:
                self.expr.set(s + str(self.last_ans))
            return
        if label == 'pi':
            self.expr.set(s + 'pi')
            return
        if label == 'sqrt':
            self.expr.set(s + 'sqrt(')
            return
        if label == '^':
            self.expr.set(s + '**')
            return
        if label == '%':
            try:
                import re
                m = re.search(r"(\d+\.?\d*)$", s)
                if m:
                    num = float(m.group(1))
                    start = m.start(1)
                    new = s[:start] + str(num/100)
                    self.expr.set(new)
                else:
                    self.expr.set(s + '/100')
            except Exception:
                self.expr.set(s + '/100')
            return
        if label == '!':
            try:
                import re
                m = re.search(r"(\d+)$", s)
                if m:
                    n = int(m.group(1))
                    val = math.factorial(n)
                    new = s[:m.start(1)] + str(val)
                    self.expr.set(new)
                else:
                    messagebox.showinfo('Error','یک عدد صحیح برای فاکتوریل لازم است')
            except Exception as e:
                messagebox.showinfo('Error', str(e))
            return
        if label in ('sin','cos','tan'):
            self.expr.set(s + label + '(')
            return
        if label in ('ln','log'):
            if label == 'ln':
                self.expr.set(s + 'ln(')
            else:
                self.expr.set(s + 'log10(')
            return
        self.expr.set(s + label)

    def evaluate(self):
        expr = self.expr.get()
        if not expr.strip():
            return
        expr_transformed = expr
        if self.mode.get() == 'DEG':
            for fn in ('sin','cos','tan','asin','acos','atan'):
                expr_transformed = self._wrap_deg(expr_transformed, fn)
        try:
            result = eval(expr_transformed, {"__builtins__":None}, ALLOWED_NAMES)
            if isinstance(result, float) and abs(result - round(result)) < 1e-12:
                result = int(round(result))
            self.last_ans = result
            self.expr.set(str(result))
        except Exception as e:
            messagebox.showerror('Error', f'خطا در محاسبه:\n{e}')

    def _wrap_deg(self, expression, fname):
        import re
        pattern = rf"\b{fname}\((?!radians\()"
        repl = f"{fname}(radians("
        updated = re.sub(pattern, repl, expression)
        # add extra closing parenthesis for each insertion
        count = len(re.findall(pattern, expression))
        updated += ')' * count
        return updated

if __name__ == '__main__':
    app = CalcApp()
    app.mainloop()

