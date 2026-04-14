import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import fitz
import re


# -------- TEXT EXTRACT (PDF) --------
def extract_text_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# -------- EXTRACT IP + HOSTNAME --------
def extract_entities(text):
    ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
    hosts = re.findall(r'\b[A-Z]{2,}-\d+\b', text.upper())
    return list(set(ips + hosts))


# -------- LOAD CMDB (CTRL+F STYLE) --------
def load_cmdb_searchable(excel_path):
    df = pd.read_excel(excel_path)
    search_map = {}

    for idx, row in df.iterrows():
        row_number = idx + 2
        for cell in row:
            if pd.notna(cell):
                value = str(cell).strip().upper()
                if value:
                    search_map[value] = row_number

    return search_map


# -------- VALIDATION --------
def validate_entities(entities, cmdb_map):
    results = []
    for item in entities:
        key = item.strip().upper()
        if key in cmdb_map:
            results.append(f"{item} -> [OK] Found at Row {cmdb_map[key]}")
        else:
            results.append(f"{item} -> [X] Not Found")
    return results


# -------- MANUAL SEARCH --------
def manual_search(cmdb_map, output_box):
    while True:
        user_input = simpledialog.askstring(
            "Manual Search",
            "Enter Hostname / IP (Cancel to stop):"
        )

        if user_input is None:
            break

        key = user_input.strip().upper()

        if key in cmdb_map:
            result = f"{user_input} -> [OK] Found at Row {cmdb_map[key]}"
        else:
            result = f"{user_input} -> [X] Not Found"

        output_box.insert(tk.END, result + "\n")
        output_box.see(tk.END)


# -------- GUI --------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 CMDB Validator (Auto + Manual)")

        self.file_path = ""
        self.cmdb_map = {}

        tk.Button(root, text="📄 Select PDF", command=self.load_pdf).pack(pady=5)
        tk.Button(root, text="📊 Load CMDB Excel", command=self.load_excel).pack(pady=5)

        tk.Button(root, text="🚀 Run Auto Validation", command=self.run_auto).pack(pady=5)
        tk.Button(root, text="🔍 Manual Search Mode", command=self.run_manual).pack(pady=5)

        self.output = tk.Text(root, height=25, width=80)
        self.output.pack()

    def load_pdf(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if self.file_path:
            messagebox.showinfo("Selected PDF", self.file_path)

    def load_excel(self):
        excel_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if excel_path:
            self.cmdb_map = load_cmdb_searchable(excel_path)
            messagebox.showinfo("Success", "CMDB Loaded ✅")

    def run_auto(self):
        if not self.file_path or not self.cmdb_map:
            messagebox.showerror("Error", "Select PDF and CMDB first")
            return

        text = extract_text_pdf(self.file_path)
        entities = extract_entities(text)
        results = validate_entities(entities, self.cmdb_map)

        self.output.delete(1.0, tk.END)

        self.output.insert(tk.END, "🔍 Extracted (IP + Hostname):\n\n")
        for e in entities:
            self.output.insert(tk.END, e + "\n")

        self.output.insert(tk.END, "\n📊 Validation Results:\n\n")
        for r in results:
            self.output.insert(tk.END, r + "\n")

    def run_manual(self):
        if not self.cmdb_map:
            messagebox.showerror("Error", "Load CMDB first")
            return

        manual_search(self.cmdb_map, self.output)


# -------- RUN --------
root = tk.Tk()
root.geometry("750x600")
App(root)
root.mainloop()