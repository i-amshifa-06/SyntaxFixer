#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import Listbox, Toplevel
import difflib
import re
import os
import keyword
from datetime import datetime
import sys


PY_KEYWORDS = keyword.kwlist

PY_BUILTINS = [
    'print','input','len','int','float','str','list','dict','set','tuple','range','type','open','abs','sum',
    'min','max','any','all','super','format','enumerate','sorted','map','filter','help','reversed','zip','dir','id',
    'next','iter','isinstance','hasattr','setattr','getattr','delattr','hash','callable','compile','eval','exec',
    'divmod','pow','round','slice','globals','locals','object','classmethod','staticmethod','property','bytes','bytearray',
    'frozenset','memoryview','complex','bin','oct','hex','ord','chr','ascii','repr','breakpoint'
]

PY_LIBRARIES = [
    # Standard libraries
    'os','sys','re','math','random','datetime','time','json','csv','pdb','copy','shutil','itertools','functools',
    'collections','heapq','bisect','array','subprocess','logging','argparse','pickle','traceback','typing','unittest',
    'string','socket','inspect','glob','gzip','tarfile','zipfile','io','uuid','threading','multiprocessing','platform',
    'ctypes','signal','select','asyncio','sqlite3','email','email.mime','email.utils','http','urllib','ssl',
    'concurrent','concurrent.futures','wsgiref','tkinter','tkinter.ttk','tkinter.filedialog','tkinter.messagebox',
    'pathlib','pprint','calendar','getpass','configparser','weakref','warnings',
    # Third-party
    'numpy','np','pandas','pd','matplotlib','plt','scipy','sklearn','sp','seaborn','sns',
    'jupyter','notebook','ipython','ipywidgets','torch','torchvision','cv2','opencv','PIL','Image',
    'tensorflow','keras','flask','django','fastapi','requests','beautifulsoup4','bs4','lxml','pyyaml','yaml','plotly',
    'pytest','nose','sphinx','sqlalchemy','pymysql','psycopg2','tabulate','tqdm','colorama','boto3','discord','pyautogui',
    'pyqt5','mplfinance','pytz','dateutil','fbprophet','xgboost','lightgbm','catboost','statsmodels','sympy','pytorch',
    'pyarrow','openpyxl','xlrd','xlsxwriter','networkx','pillow','scikit-learn','pygments','pyee','pyecharts','requests_html',
    'selenium','webdriver_manager','hyperopt','optuna','pydantic','starlette','gunicorn','uvicorn','joblib',
    'nltk','spacy','gensim','transformers','fairseq','sentence_transformers'
]

ALL_WORDS = set(PY_KEYWORDS + PY_BUILTINS + PY_LIBRARIES)

PY_ALIAS = {
    "dfe":"def", "pritn":"print", "prnit":"print", "improt":"import", "printf":"print",
    "flase":"False", "treu":"True", "nnoe":"None", "clas":"class", "funtion":"function", "contiune":"continue",
    "retun":"return", "wihle":"while", "exepct":"except", "finall":"finally", "fucntion":"function", "lenght":"length",
    "strnig":"string", "dicti":"dict", "tupel":"tuple", "claas":"class", "prnt":"print", "prit":"print", "prnitf":"print",
    "np":"numpy", "nmpy":"numpy", "pd":"pandas", "plt":"matplotlib", "sns":"seaborn", "sp":"scipy", "sk":"sklearn",
    "req":"requests", "bs":"bs4", "tf":"tensorflow", "ss":"sys","is":"os","ps":"os","pt":"pytorch"
}

JAVA_KEYWORDS = {
    "public", "private", "protected", "class", "static", "void", "int", "double", "float", "char", "boolean", "long",
    "short", "byte", "if", "else", "switch", "case", "for", "while", "do", "continue", "break", "return",
    "new", "this", "super", "try", "catch", "finally", "throw", "throws", "extends", "implements", "interface",
    "import", "package", "null", "true", "false", "instanceof"
}
JAVA_BUILTINS = {
    "System", "out", "println", "String", "Math", "Integer", "Double", "List", "ArrayList", "Map", "HashMap", "Scanner"
}
JAVA_ALIAS = {
    "pubic": "public", "pravite": "private", "staic": "static", "pritln": "println", "retrun": "return",
    "Strng": "String", "Sysem": "System", "psvm": "public static void main()", "sop": "System.out.println", "syso": "System.out.println"
}
ALL_WORDS_JAVA = JAVA_KEYWORDS | JAVA_BUILTINS


PAIRS = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}



class SyntaxFixer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SyntaxFixer - Code Editor")
        self.geometry("1200x800")
        self.configure(bg="#2d2d2d")
       
        self.suggestion_box = None
        self.suggestion_words = []

        self.filename = None
        self.unsaved_changes = False
        self.last_save_time = None
        self.language = tk.StringVar(value="Python")
        self.auto_correct_enabled = tk.BooleanVar(value=True)
        self.current_line = 1
        self.current_col = 1
       
       
        self.create_menu()
        self.create_widgets()
        self.create_status_bar()
       
       
        self.bind_shortcuts()
       
       
        self.new_file()
       
       
        self.configure_tags()
       
       
        self.text.focus_set()
       
       
        self.show_welcome()

    def master_key_release_handler(self, event):
    # Hide suggestions only for specific keys:
        if event.keysym in ("Shift", "Control", "Alt", "Caps_Lock", "Tab", "Escape"):
           self.hide_suggestions(event)
           return
        self.show_suggestions(event)
        self.on_key_release(event)
        self.update_line_numbers(event)
        self.update_cursor_position(event)




    def on_language_switch(self):
   
        lang = self.language.get()
        status = "ON" if self.auto_correct_enabled.get() else "OFF"
        self.status_bar.config(
            text=f"Auto-Correction: {status} | Language: {lang} | Line: {self.current_line}, Col: {self.current_col}"
    )

    def show_welcome(self):
        welcome_text = """#Welcome to SyntaxFixer!

#Features:
#• Syntax highlighting for code
#• Auto-correction of common typos
#• Auto-completion of brackets and quotes
#• Smart indentation and colon insertion
#• Function call auto-correction
#• Modern dark theme UI

#Start typing or open a file to begin!\n"""
        self.text.insert("1.0", welcome_text)
        self.text.tag_add("comment", "1.0", "end")
   
    def create_menu(self):
        menubar = tk.Menu(self)
       
       
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)
       
       
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_checkbutton(label="Auto-Correction", variable=self.auto_correct_enabled,
                                command=self.toggle_auto_correct, accelerator="Ctrl+Alt+C")
        edit_menu.add_separator()
        edit_menu.add_radiobutton(label="Python", variable=self.language, value="Python", command=self.on_language_switch)
        edit_menu.add_radiobutton(label="Java", variable=self.language, value="Java", command=self.on_language_switch)

        menubar.add_cascade(label="Edit", menu=edit_menu)
       
       
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Increase Font Size", command=lambda: self.change_font_size(1), accelerator="Ctrl++")
        view_menu.add_command(label="Decrease Font Size", command=lambda: self.change_font_size(-1), accelerator="Ctrl+-")
        menubar.add_cascade(label="View", menu=view_menu)
       
       
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        menubar.add_cascade(label="Help", menu=help_menu)
       
        self.config(menu=menubar)

    def undo(self):
        try:
            self.text.edit_undo()
        except:
            pass

    def redo(self):
        try:
            self.text.edit_redo()
        except:
            pass

    def cut(self):
        self.text.event_generate("<<Cut>>")

    def copy(self):
        self.text.event_generate("<<Copy>>")

    def paste(self):
        self.text.event_generate("<<Paste>>")

    def toggle_auto_correct(self):
        status = "ON" if self.auto_correct_enabled.get() else "OFF"
        self.status_bar.config(text=f"Auto-Correction: {status} | Line: {self.current_line}, Col: {self.current_col}")
   
    def create_widgets(self):
       
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
       
        self.line_numbers = tk.Text(main_frame, width=4, padx=5, pady=5, takefocus=0,
                                  border=0, background="#333333", foreground="#aaaaaa",
                                  font=('Consolas', 12), state='disabled')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
       
       
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
       
        self.text = tk.Text(text_frame, wrap=tk.NONE, undo=True,
                           font=('Consolas', 12), bg="#1e1e1e", fg="#d4d4d4",
                           insertbackground="white", selectbackground="#264f78",
                           border=0, relief=tk.FLAT)
       
       

        y_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
       
        x_scroll = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.text.xview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
       
        self.text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
       
        # Unified KeyRelease handler
        self.text.bind("<KeyRelease>", self.master_key_release_handler)

# Other event bindings remain as single handler each:
        self.text.bind("<FocusOut>", self.hide_suggestions)
        self.text.bind("<Return>", self.on_return_key)
        self.text.bind("<Key>", self.on_key_press)
        self.text.bind("<<Modified>>", self.on_text_modified)
        self.text.bind("<Button-1>", self.update_line_numbers)
        self.text.bind("<MouseWheel>", self.update_line_numbers)
        self.text.bind("<Configure>", self.update_line_numbers)
        self.text.bind("<Motion>", self.update_cursor_position)

   
   
    def show_suggestions(self, event=None):
       cursor_pos = self.text.index(tk.INSERT)
       line_num, col_num = map(int, cursor_pos.split('.'))
       line_start = f"{line_num}.0"
       line_text = self.text.get(line_start, cursor_pos)
       word_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)$', line_text)
       if not word_match:
          self.hide_suggestions()
          return
       prefix = word_match.group(1)
       lang = self.language.get()
       if lang == "Python":
          options = sorted(set(PY_KEYWORDS + PY_BUILTINS + PY_LIBRARIES))
       elif lang == "Java":
          options = sorted(JAVA_KEYWORDS | JAVA_BUILTINS)
       else:
          options = []

    # FIXED: Case-insensitive and fuzzy match, works for 'System', 'println', etc.
       matches = [w for w in options if w.lower().startswith(prefix.lower())]
       if len(matches) < 5:
          import difflib
          extra = difflib.get_close_matches(prefix, options, n=5)
          matches += [m for m in extra if m not in matches]
       matches = matches[:5]

       if not matches:
          self.hide_suggestions()
          return
       if self.suggestion_box:
          self.suggestion_box.destroy()
       try:
          x, y, _, _ = self.text.bbox(tk.INSERT)
          abs_x = self.text.winfo_rootx() + x
          abs_y = self.text.winfo_rooty() + y + 20
       except:
          abs_x, abs_y = 30, 30
       self.suggestion_box = Listbox(self, height=len(matches), font=("Consolas", 11), bg="#23272e", fg="#fafafa", highlightthickness=1, border=1)
       self.suggestion_words = matches
       for m in matches:
         self.suggestion_box.insert(tk.END, m)
       self.suggestion_box.place(x=abs_x, y=abs_y)
       self.suggestion_box.bind("<ButtonRelease-1>", self.suggestion_pick)
       self.suggestion_box.bind("<Return>", self.suggestion_pick)
    # Do NOT set focus to the suggestion_box!







    def hide_suggestions(self, event=None):
        if self.suggestion_box:
           self.suggestion_box.destroy()
           self.suggestion_box = None

    def suggestion_pick(self, event=None):
        if not self.suggestion_box:
          return
        selected = self.suggestion_box.curselection()
        if selected:
           chosen_word = self.suggestion_words[selected[0]]
           cursor_pos = self.text.index(tk.INSERT)
           line_num, col_num = map(int, cursor_pos.split('.'))
           line_start = f"{line_num}.0"
           line_text = self.text.get(line_start, cursor_pos)
           word_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)$', line_text)
           if word_match:
              start = int(word_match.start(1))
              self.text.delete(f"{line_num}.{start}", cursor_pos)
              self.text.insert(f"{line_num}.{start}", chosen_word)
        self.hide_suggestions()
        self.text.focus_set()



    def create_status_bar(self):
        self.status_bar = ttk.Label(self, text="Ready | Auto-Correction: ON | Line: 1, Col: 1",
                                  relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
   
    def bind_shortcuts(self):
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-Shift-S>", lambda e: self.save_file_as())
        self.bind("<Control-q>", lambda e: self.on_close())
        self.bind("<Control-Alt-c>", lambda e: self.toggle_auto_correct())
        self.bind("<Control-plus>", lambda e: self.change_font_size(1))
        self.bind("<Control-minus>", lambda e: self.change_font_size(-1))
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-y>", lambda e: self.redo())
        self.bind("<Control-x>", lambda e: self.cut())
        self.bind("<Control-c>", lambda e: self.copy())
        self.bind("<Control-v>", lambda e: self.paste())
   
    def configure_tags(self):
   
      self.text.tag_configure("keyword", foreground="#569cd6", font=('Consolas', 12, 'bold'))
      self.text.tag_configure("builtin", foreground="#4ec9b0", font=('Consolas', 12))
      self.text.tag_configure("string", foreground="#ce9178", font=('Consolas', 12))
      self.text.tag_configure("number", foreground="#b5cea8", font=('Consolas', 12))
      self.text.tag_configure("comment", foreground="#6a9955", font=('Consolas', 12, 'italic'))
      self.text.tag_configure("library", foreground="#c586c0", font=('Consolas', 12))
      self.text.tag_configure("def", foreground="#dcdcaa", font=('Consolas', 12, 'bold'))
      self.text.tag_configure("import", foreground="#d7ba7d", font=('Consolas', 12))
      self.text.tag_configure("class", foreground="#4ec9b0", font=('Consolas', 12, 'bold'))
   
      self.text.tag_configure("java_keyword", foreground="#d18f36", font=('Consolas', 12, 'bold'))   # Orange-brown for Java keywords
      self.text.tag_configure("java_builtin", foreground="#fff689", font=('Consolas', 12))           # Yellow for built-ins
      self.text.tag_configure("java_type", foreground="#4ec9b0", font=('Consolas', 12, 'bold'))      # Cyan for types/classes
      self.text.tag_configure("java_comment", foreground="#6a9955", font=('Consolas', 12, 'italic')) # Greenish
      self.text.tag_configure("java_string", foreground="#ce9178", font=('Consolas', 12))

   
      self.text.tag_configure("current_line", background="#2a2d2e")
      self.text.tag_configure("found", background="#515151")

    def highlight_syntax(self):
       for tag in self.text.tag_names():
         if tag not in ["current_line", "sel"]:
            self.text.tag_remove(tag, "1.0", tk.END)
       text = self.text.get("1.0", tk.END)
       lines = text.split('\n')
       lang = self.language.get()
       for i, line in enumerate(lines):
         start_line = f"{i + 1}.0"
         end_line = f"{i + 1}.end"
         if lang == "Python":
           
            if '#' in line:
                comment_start = line.find('#')
                self.text.tag_add("comment", f"{i+1}.{comment_start}", end_line)
           
            for quote in ['"', "'"]:
                start = 0
                while True:
                    start = line.find(quote, start)
                    if start == -1:
                        break
                    end = line.find(quote, start + 1)
                    if end == -1:
                        end = len(line)
                    self.text.tag_add("string", f"{i+1}.{start}", f"{i+1}.{end+1}")
                    start = end + 1
           
            for match in re.finditer(r'\b\d+\.?\d*\b', line):
                start, end = match.span()
                self.text.tag_add("number", f"{i+1}.{start}", f"{i+1}.{end}")
           
            for word in re.finditer(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', line):
                start, end = word.span()
                word_text = word.group()
                if word_text in PY_KEYWORDS:
                    if word_text in ("def", "class", "import", "from"):
                        self.text.tag_add(word_text, f"{i+1}.{start}", f"{i+1}.{end}")
                    else:
                        self.text.tag_add("keyword", f"{i+1}.{start}", f"{i+1}.{end}")
                elif word_text in PY_BUILTINS:
                    self.text.tag_add("builtin", f"{i+1}.{start}", f"{i+1}.{end}")
                elif word_text in PY_LIBRARIES:
                    self.text.tag_add("library", f"{i+1}.{start}", f"{i+1}.{end}")
         elif lang == "Java":
           
            if '//' in line:
                comment_start = line.find('//')
                self.text.tag_add("java_comment", f"{i+1}.{comment_start}", end_line)
           
            for quote in ['"', "'"]:
                start = 0
                while True:
                    start = line.find(quote, start)
                    if start == -1:
                        break
                    end = line.find(quote, start + 1)
                    if end == -1:
                        end = len(line)
                    self.text.tag_add("java_string", f"{i+1}.{start}", f"{i+1}.{end+1}")
                    start = end + 1
           
            for match in re.finditer(r'\b\d+\.?\d*\b', line):
                start, end = match.span()
                self.text.tag_add("number", f"{i+1}.{start}", f"{i+1}.{end}")
           
            for word in re.finditer(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', line):
                start, end = word.span()
                word_text = word.group()
                if word_text in JAVA_KEYWORDS:
                    self.text.tag_add("java_keyword", f"{i+1}.{start}", f"{i+1}.{end}")
                elif word_text in JAVA_BUILTINS:
                    self.text.tag_add("java_builtin", f"{i+1}.{start}", f"{i+1}.{end}")
                elif word_text[0].isupper():
                    self.text.tag_add("java_type", f"{i+1}.{start}", f"{i+1}.{end}")

   
    def update_status_bar(self):
        cursor_pos = self.text.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.current_line, self.current_col = int(line), int(col) + 1
       
        if self.filename:
            filename = os.path.basename(self.filename)
            status = f"{filename}"
            if self.unsaved_changes:
                status += " *"
            self.status_bar.config(text=f"{status} | Auto-Correction: {'ON' if self.auto_correct_enabled.get() else 'OFF'} | Line: {self.current_line}, Col: {self.current_col}")
        else:
            self.status_bar.config(text=f"New File | Auto-Correction: {'ON' if self.auto_correct_enabled.get() else 'OFF'} | Line: {self.current_line}, Col: {self.current_col}")
   
    def update_cursor_position(self, event=None):
        self.update_status_bar()
   
    def update_line_numbers(self, event=None):
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete(1.0, tk.END)
       
        line_count = self.text.get(1.0, tk.END).count('\n')
        if not self.text.get(1.0, tk.END).endswith('\n'):
            line_count += 1
       
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
       
        self.line_numbers.config(state=tk.DISABLED)
        self.highlight_current_line()
        self.update_status_bar()
   
    def highlight_current_line(self):
        self.text.tag_remove("current_line", 1.0, tk.END)
        current_line = self.text.index(tk.INSERT).split('.')[0]
        self.text.tag_add("current_line", f"{current_line}.0", f"{current_line}.end")
   
    def on_key_press(self, event):
       
        if event.char in PAIRS:
            self.insert_pair(event.char)
            return "break"
       
       
        if event.keysym == "Tab":
            self.text.insert(tk.INSERT, "    ")
            return "break"
       
       
        if event.keysym == "BackSpace":
            if self.handle_pair_backspace():
                return "break"
   
    def on_key_release(self, event):
      if self.auto_correct_enabled.get():
         if event.keysym == "space":
             self.auto_correct_current_word()
             self.auto_correct_function_calls()
      self.update_line_numbers()
      self.highlight_syntax()



    def on_return_key(self, event):
      lang = self.language.get()
      if self.auto_correct_enabled.get():
        self.auto_correct_current_word()
        self.auto_correct_function_calls()
      cursor_pos = self.text.index(tk.INSERT)
      line_num = int(cursor_pos.split('.')[0])
      line_start = f"{line_num}.0"
      line_end = f"{line_num}.end"
      prev_line = self.text.get(line_start, line_end)
      prev_stripped = prev_line.strip()

      if lang == "Python":
       
        block_starters = (
            "def ", "class ", "if ", "elif ", "else", "for ", "while ", "try", "except", "finally", "with "
        )
        is_starter = any(prev_stripped.startswith(starter) for starter in block_starters)
        needs_colon = is_starter and not prev_line.rstrip().endswith(":")
        if needs_colon:
            self.text.insert(line_end, ":")
            prev_line = self.text.get(line_start, f"{line_end}+1c")
        self.text.mark_set(tk.INSERT, f"{line_num}.end")
        self.text.insert(tk.INSERT, "\n")
        if (is_starter and prev_line.rstrip().endswith(":")):
            indent_in = len(prev_line) - len(prev_line.lstrip())
            indent = indent_in + 4
        else:
            indent_in = len(prev_line) - len(prev_line.lstrip())
            indent = indent_in
        self.text.insert(tk.INSERT, " " * indent)
        self.update_line_numbers()
        self.highlight_syntax()
        return "break"

      if lang == "Java":
       
        block_pattern = (
            r"(class\s+\w+)|(interface\s+\w+)|(^|\s)(public|private|protected)?\s*static\s*void\s+\w+\s*\([^\)]*\)$|"
            r"^\s*(public|private|protected)?\s*\w+\s+\w+\s*\([^\)]*\)$"
        )
       
        if re.match(block_pattern, prev_stripped):
            base_indent = len(prev_line) - len(prev_line.lstrip())
            indent = base_indent + 4
            self.text.mark_set(tk.INSERT, f"{line_num}.end")
            self.text.insert(tk.INSERT, "\n" + " " * base_indent + "{")
            self.text.insert(tk.INSERT, "\n" + " " * indent)
            self.text.insert(tk.INSERT, "\n" + " " * base_indent + "}")
            self.text.mark_set(tk.INSERT, f"{line_num + 2}.{indent}")
            self.update_line_numbers()
            self.highlight_syntax()
            return "break"
       
        if prev_stripped.endswith("{"):
            base_indent = len(prev_line) - len(prev_line.lstrip())
            indent = base_indent + 4
            self.text.mark_set(tk.INSERT, f"{line_num}.end")
            self.text.insert(tk.INSERT, "\n" + " " * indent)
            self.text.insert(tk.INSERT, "\n" + " " * base_indent + "}")
            self.text.mark_set(tk.INSERT, f"{line_num + 1}.{indent}")
            self.update_line_numbers()
            self.highlight_syntax()
            return "break"
       
        if prev_stripped == "}":
            base_indent = len(prev_line) - len(prev_line.lstrip())
            outdent = max(base_indent - 4, 0)
            self.text.delete(line_start, line_start + f"+{base_indent}c")
            self.text.insert(line_start, " " * outdent)
            self.text.mark_set(tk.INSERT, f"{line_num}.end")
            self.text.insert(tk.INSERT, "\n" + " " * outdent)
            self.update_line_numbers()
            self.highlight_syntax()
            return "break"
       
        if prev_stripped.startswith(("case ", "default")) and not prev_stripped.endswith(":"):
            self.text.insert(line_end, ":")
       
       
        needs_semi = (
            prev_stripped and
            not prev_stripped.endswith((';', '{', '}', ':')) and
            not prev_stripped.startswith(('public ', 'private ', 'protected ', 'class ', 'interface ', 'else', 'if(', 'for(', 'while(', 'switch(', '@')) and
            not prev_stripped.startswith('//') and
            not re.match(block_pattern, prev_stripped)
        )
        if needs_semi:
            self.text.insert(line_end, ";")
       
        prev_indent = len(prev_line) - len(prev_line.lstrip())
        self.text.mark_set(tk.INSERT, f"{line_num}.end")
        self.text.insert(tk.INSERT, "\n" + " " * prev_indent)
        self.update_line_numbers()
        self.highlight_syntax()
        return "break"

   
    def is_inside_string(self, line_num, col_num):
        """Check if cursor is inside a string literal"""
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        line_text = self.text.get(line_start, line_end)
       
       
        in_single_quote = False
        in_double_quote = False
        escaped = False
       
        for i, char in enumerate(line_text):
            if i >= col_num:
                break
               
            if escaped:
                escaped = False
                continue
               
            if char == '\\':
                escaped = True
                continue
               
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
       
        return in_single_quote or in_double_quote
   
    def auto_correct_function_calls(self):
        """Auto-correct function names when they're followed by parentheses"""
        if not self.auto_correct_enabled.get():
            return
       
        cursor_pos = self.text.index(tk.INSERT)
        line_num = int(cursor_pos.split('.')[0])
        col_num = int(cursor_pos.split('.')[1])
       
       
        if self.is_inside_string(line_num, col_num):
            return
       
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        line_text = self.text.get(line_start, line_end)
       
       
        matches = list(re.finditer(r'\b([a-zA-Z_][a-zA-Z0-9_]*)(\()', line_text))
        for match in reversed(matches):
            func_name = match.group(1)
            corrected_name = self.autocorrect_word(func_name)
           
            if corrected_name != func_name:
                start = match.start(1)
                end = match.end(1)
                start_pos = f"{line_num}.{start}"
                end_pos = f"{line_num}.{end}"
               
                self.text.delete(start_pos, end_pos)
                self.text.insert(start_pos, corrected_name)
   
    def auto_correct_current_word(self):
        """Auto-correct the word before the cursor when space or enter is pressed"""
        if not self.auto_correct_enabled.get():
            return
       
        cursor_pos = self.text.index(tk.INSERT)
        line_num, col_num = map(int, cursor_pos.split('.'))
       
       
        if self.is_inside_string(line_num, col_num):
            return
       
        line_start = f"{line_num}.0"
        line_text = self.text.get(line_start, cursor_pos)
       
       
        word_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*$', line_text)
        if not word_match:
            return
       
        current_word = word_match.group(1)
        start = word_match.start(1)
        end = word_match.end(1)
       
       
        if line_text[end:].lstrip().startswith('('):
            return
       
        corrected_word = self.autocorrect_word(current_word)
        if corrected_word != current_word:
            start_pos = f"{line_num}.{start}"
            end_pos = f"{line_num}.{end}"
            self.text.delete(start_pos, end_pos)
            self.text.insert(start_pos, corrected_word)
           
           
            if corrected_word in ['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'with']:
                self.text.insert(f"{line_num}.{start + len(corrected_word)}", " ")
                self.text.mark_set(tk.INSERT, f"{line_num}.{start + len(corrected_word) + 1}")
            else:
               
                self.text.mark_set(tk.INSERT, f"{line_num}.{start + len(corrected_word)}")
   
    def autocorrect_word(self, word):
        lang = self.language.get()
        if lang == "Python":
           lw = word.lower()
           if lw in PY_ALIAS:
              return PY_ALIAS[lw]
           if word in ALL_WORDS or not word.isidentifier() or len(word) < 2:
              return word
           matches = difflib.get_close_matches(word, ALL_WORDS, n=1, cutoff=0.7)
           return matches[0] if matches else word
        elif lang == "Java":
             lw = word.lower()
             if lw in JAVA_ALIAS:
                return JAVA_ALIAS[lw]
             if word in ALL_WORDS_JAVA or not word.isidentifier() or len(word) < 2:
                return word
             matches = difflib.get_close_matches(word, ALL_WORDS_JAVA, n=1, cutoff=0.7)
             return matches[0] if matches else word
        return word
   
    def insert_pair(self, char):
        pair = PAIRS[char]
        self.text.insert(tk.INSERT, char + pair)
        self.text.mark_set(tk.INSERT, f"{tk.INSERT}-1c")
   
    def handle_pair_backspace(self):
        cursor_pos = self.text.index(tk.INSERT)
        if cursor_pos == "1.0":
            return False
       
        prev_char_pos = f"{cursor_pos}-1c"
        next_char_pos = f"{cursor_pos}+1c"
       
        prev_char = self.text.get(prev_char_pos, cursor_pos)
        next_char = self.text.get(cursor_pos, next_char_pos)
       
        for open_char, close_char in PAIRS.items():
            if prev_char == open_char and next_char == close_char:
                self.text.delete(cursor_pos, next_char_pos)
                self.text.delete(prev_char_pos, cursor_pos)
                return True
        return False
   
   
   
    def on_text_modified(self, event):
        if self.text.edit_modified():
            self.unsaved_changes = True
            self.update_status_bar()
        self.text.edit_modified(False)
   
    def new_file(self, event=None):
        if self.unsaved_changes and not self.prompt_save():
            return
       
        self.text.delete(1.0, tk.END)
        self.filename = None
        self.unsaved_changes = False
        self.last_save_time = None
        self.title("SyntaxFixer - New File")
        self.update_status_bar()
        self.update_line_numbers()
   
    def open_file(self, event=None):
        if self.unsaved_changes and not self.prompt_save():
            return
       
        filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, content)
                self.filename = filepath
                self.unsaved_changes = False
                self.last_save_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.title(f"SyntaxFixer - {os.path.basename(filepath)}")
                self.update_status_bar()
                self.update_line_numbers()
                self.highlight_syntax()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")
   
    def save_file(self, event=None):
        if not self.filename:
            return self.save_file_as()
        try:
            content = self.text.get(1.0, tk.END)
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write(content)
            self.unsaved_changes = False
            self.last_save_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.update_status_bar()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
            return False
   
    def save_file_as(self, event=None):
        filepath = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if filepath:
            self.filename = filepath
            if self.save_file():
                self.title(f"SyntaxFixer - {os.path.basename(filepath)}")
                return True
        return False
   
    def prompt_save(self):
        if not self.unsaved_changes:
            return True
        response = messagebox.askyesnocancel("Unsaved Changes", "Do you want to save changes before continuing?")
        if response is None:
            return False
        elif response:
            return self.save_file()
        else:
            return True
   
    def change_font_size(self, delta):
        current_size = int(self.text['font'].split()[1])
        new_size = max(8, min(24, current_size + delta))
        self.text.config(font=('Consolas', new_size))
        self.line_numbers.config(font=('Consolas', new_size))
   
    def show_about(self):
        about_text = """SyntaxFixer - Code Editor


Author: Mohiadeen Shifaul Kareem MI
Version: 1.0
Description: A modern programming code editor with advanced
auto-correction, syntax highlighting, and intelligent
code completion features.

Features:
• Smart auto-correction of common typos
• Syntax highlighting for code
• Auto-completion of brackets and quotes
• Intelligent indentation for blocks
• Function call auto-correction
• Modern dark theme interface"""
        messagebox.showinfo("About SyntaxFixer", about_text)
   
    def show_shortcuts(self):
        shortcuts = """Keyboard Shortcuts:

File Operations:
Ctrl+N - New File
Ctrl+O - Open File
Ctrl+S - Save File
Ctrl+Shift+S - Save As
Ctrl+Q - Quit

Editing:
Ctrl+Z - Undo
Ctrl+Y - Redo
Ctrl+X - Cut
Ctrl+C - Copy
Ctrl+V - Paste
Ctrl+Alt+C - Toggle Auto-Correction

View:
Ctrl++ - Increase Font Size
Ctrl+- - Decrease Font Size

Auto-Correction:
Space/Enter - Auto-correct words and function calls"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
   
    def on_close(self, event=None):
        if self.unsaved_changes and not self.prompt_save():
            return
        self.destroy()

if __name__ == "__main__":
    app = SyntaxFixer()
    # If user gave a file name, open it
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                app.text.delete(1.0, tk.END)
                app.text.insert(tk.END, content)
                app.filename = filepath
                app.unsaved_changes = False
                app.title(f"SyntaxFixer - {os.path.basename(filepath)}")
                app.update_status_bar()
                app.update_line_numbers()
                app.highlight_syntax()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open {filepath}:\n{e}")
        else:
            # If file doesn’t exist, set name so saving will create it
            app.filename = filepath
            app.title(f"SyntaxFixer - {os.path.basename(filepath)}")

    app.mainloop()
