#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# GUI Sublist3r - A clean graphical interface for Sublist3r v2.0

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import sys
import os
import queue
import re
import time

# ── Colour palette ────────────────────────────────────────────────────────────
BG        = "#1e1e1e"   # near-black window bg
PANEL     = "#252525"   # slightly lighter panel
CARD      = "#2c2c2c"   # card / frame bg
BORDER    = "#3a3a3a"   # subtle borders
ACCENT    = "#4a9eff"   # blue accent
ACCENT_H  = "#6ab4ff"   # hover accent
SUCCESS   = "#4caf7d"   # green
WARNING   = "#f0a832"   # amber
ERROR     = "#e05c5c"   # red
TEXT_PRI  = "#e8e8e8"   # primary text
TEXT_SEC  = "#8a8a8a"   # secondary / muted text
TEXT_DIM  = "#555555"   # very muted

FONT_MONO = ("Consolas", 10)
FONT_UI   = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI Semibold", 10)
FONT_HEAD = ("Segoe UI Semibold", 13)
FONT_TINY = ("Segoe UI", 8)


# ── Helper: find sublist3r.py next to this script ─────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
SUBLIST3R_PY = os.path.join(SCRIPT_DIR, "sublist3r.py")


# ══════════════════════════════════════════════════════════════════════════════
class GUISublist3r(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("GUI Sublist3r  ·  v2.0")
        self.geometry("820x680")
        self.minsize(720, 560)
        self.configure(bg=BG)
        self.resizable(True, True)

        self._queue      = queue.Queue()
        self._proc       = None
        self._running    = False
        self._subdomains = []

        self._build_ui()
        self._poll_queue()

    # ── UI construction ────────────────────────────────────────────────────────
    def _build_ui(self):
        # ---- header bar ----
        hdr = tk.Frame(self, bg=PANEL, height=54)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="GUI Sublist3r", font=("Segoe UI Semibold", 14),
                 fg=TEXT_PRI, bg=PANEL).pack(side="left", padx=18, pady=14)
        tk.Label(hdr, text="Subdomain Enumeration Tool  ·  v2.0",
                 font=FONT_TINY, fg=TEXT_SEC, bg=PANEL).pack(side="left", pady=16)

        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x")

        # ---- body (two columns) ----
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=18, pady=14)

        # left  (controls)
        left = tk.Frame(body, bg=BG, width=310)
        left.pack(side="left", fill="y", padx=(0, 14))
        left.pack_propagate(False)

        # right (results)
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self._build_controls(left)
        self._build_results(right)

        # ---- status bar ----
        bar = tk.Frame(self, bg=PANEL, height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._status_var = tk.StringVar(value="Ready")
        tk.Label(bar, textvariable=self._status_var, font=FONT_TINY,
                 fg=TEXT_SEC, bg=PANEL, anchor="w").pack(side="left", padx=10, pady=4)

        self._count_var = tk.StringVar(value="")
        tk.Label(bar, textvariable=self._count_var, font=FONT_TINY,
                 fg=ACCENT, bg=PANEL, anchor="e").pack(side="right", padx=10, pady=4)

    # ── Controls panel ─────────────────────────────────────────────────────────
    def _build_controls(self, parent):
        def section(title):
            tk.Label(parent, text=title, font=FONT_BOLD,
                     fg=TEXT_SEC, bg=BG).pack(anchor="w", pady=(14, 4))

        # --- Domain ---
        section("TARGET DOMAIN")
        dom_frame = tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                             highlightthickness=1)
        dom_frame.pack(fill="x")
        self._domain_var = tk.StringVar()
        dom_entry = tk.Entry(dom_frame, textvariable=self._domain_var,
                             font=FONT_UI, fg=TEXT_PRI, bg=CARD,
                             insertbackground=ACCENT, relief="flat",
                             bd=8, highlightthickness=0)
        dom_entry.pack(fill="x", ipady=6)
        dom_entry.insert(0, "e.g. example.com")
        dom_entry.config(fg=TEXT_DIM)
        dom_entry.bind("<FocusIn>",  lambda e: self._placeholder_clear(dom_entry, "e.g. example.com"))
        dom_entry.bind("<FocusOut>", lambda e: self._placeholder_restore(dom_entry, "e.g. example.com"))
        dom_entry.bind("<Return>",   lambda e: self._start_scan())

        # --- Engines ---
        section("SEARCH ENGINES")
        engine_names = ["Baidu", "Yahoo", "Google", "Bing", "Ask",
                        "Netcraft", "DNSdumpster", "VirusTotal",
                        "ThreatCrowd", "SSL Certs", "PassiveDNS", "ShrewdEye"]
        engine_keys  = ["baidu","yahoo","google","bing","ask",
                        "netcraft","dnsdumpster","virustotal",
                        "threatcrowd","ssl","passivedns","shrewdeye"]
        self._engine_vars = {}
        self._dns_key_var = tk.StringVar()
        self._vt_key_var  = tk.StringVar()

        eng_outer = tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                              highlightthickness=1)
        eng_outer.pack(fill="x")

        for name, key in zip(engine_names, engine_keys):
            var = tk.BooleanVar(value=True)
            self._engine_vars[key] = var
            cb = tk.Checkbutton(eng_outer, text=name, variable=var,
                                font=FONT_TINY, fg=TEXT_PRI, bg=CARD,
                                selectcolor=BORDER, activebackground=CARD,
                                activeforeground=TEXT_PRI, anchor="w",
                                relief="flat", bd=0)
            cb.pack(fill="x", padx=10, pady=1)

            # API key entry under DNSdumpster
            if key == "dnsdumpster":
                dns_row = tk.Frame(eng_outer, bg=CARD)
                dns_row.pack(fill="x", padx=(28, 10), pady=(0, 3))
                tk.Label(dns_row, text="API key:", font=FONT_TINY,
                         fg=TEXT_SEC, bg=CARD, width=7, anchor="w").pack(side="left")
                dns_entry = tk.Entry(dns_row, textvariable=self._dns_key_var,
                                     font=("Consolas", 8), fg=TEXT_PRI, bg=BORDER,
                                     insertbackground=ACCENT, relief="flat",
                                     bd=4, highlightthickness=0)
                dns_entry.pack(side="left", fill="x", expand=True, ipady=2)

            # API key entry under VirusTotal
            if key == "virustotal":
                vt_row = tk.Frame(eng_outer, bg=CARD)
                vt_row.pack(fill="x", padx=(28, 10), pady=(0, 3))
                tk.Label(vt_row, text="API key:", font=FONT_TINY,
                         fg=TEXT_SEC, bg=CARD, width=7, anchor="w").pack(side="left")
                vt_entry = tk.Entry(vt_row, textvariable=self._vt_key_var,
                                    font=("Consolas", 8), fg=TEXT_PRI, bg=BORDER,
                                    insertbackground=ACCENT, relief="flat",
                                    bd=4, highlightthickness=0, show="*")
                vt_entry.pack(side="left", fill="x", expand=True, ipady=2)

        all_frame = tk.Frame(parent, bg=BG)
        all_frame.pack(fill="x", pady=(4, 0))
        tk.Button(all_frame, text="All",  font=FONT_TINY, fg=ACCENT, bg=BG,
                  relief="flat", bd=0, cursor="hand2",
                  command=lambda: [v.set(True)  for v in self._engine_vars.values()]).pack(side="left")
        tk.Label(all_frame, text=" · ", font=FONT_TINY, fg=TEXT_DIM, bg=BG).pack(side="left")
        tk.Button(all_frame, text="None", font=FONT_TINY, fg=ACCENT, bg=BG,
                  relief="flat", bd=0, cursor="hand2",
                  command=lambda: [v.set(False) for v in self._engine_vars.values()]).pack(side="left")

        # --- Options ---
        section("OPTIONS")
        opts = tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                        highlightthickness=1)
        opts.pack(fill="x")

        self._brute_var   = tk.BooleanVar(value=False)
        self._verbose_var = tk.BooleanVar(value=True)

        for text, var in [("Enable bruteforce (slow)", self._brute_var),
                          ("Verbose output",           self._verbose_var)]:
            tk.Checkbutton(opts, text=text, variable=var,
                           font=FONT_TINY, fg=TEXT_PRI, bg=CARD,
                           selectcolor=BORDER, activebackground=CARD,
                           activeforeground=TEXT_PRI, anchor="w",
                           relief="flat", bd=0).pack(fill="x", padx=10, pady=2)

        # threads row
        thr_row = tk.Frame(opts, bg=CARD)
        thr_row.pack(fill="x", padx=10, pady=(2, 6))
        tk.Label(thr_row, text="Threads:", font=FONT_TINY, fg=TEXT_SEC,
                 bg=CARD).pack(side="left")
        self._threads_var = tk.StringVar(value="30")
        thr_spin = tk.Spinbox(thr_row, from_=1, to=200, width=5,
                              textvariable=self._threads_var,
                              font=FONT_TINY, fg=TEXT_PRI, bg=BORDER,
                              buttonbackground=BORDER, relief="flat", bd=4)
        thr_spin.pack(side="left", padx=(8, 0))

        # ---- Run / Stop buttons ----
        btn_frame = tk.Frame(parent, bg=BG)
        btn_frame.pack(fill="x", pady=(16, 0))

        self._run_btn = tk.Button(btn_frame, text="▶  Run Scan",
                                  font=FONT_BOLD, fg="#ffffff",
                                  bg=ACCENT, activebackground=ACCENT_H,
                                  activeforeground="#ffffff",
                                  relief="flat", bd=0, cursor="hand2",
                                  pady=10, command=self._start_scan)
        self._run_btn.pack(fill="x")

        self._stop_btn = tk.Button(btn_frame, text="■  Stop",
                                   font=FONT_BOLD, fg="#ffffff",
                                   bg=ERROR, activebackground="#c04040",
                                   activeforeground="#ffffff",
                                   relief="flat", bd=0, cursor="hand2",
                                   pady=8, command=self._stop_scan,
                                   state="disabled")
        self._stop_btn.pack(fill="x", pady=(6, 0))

        # ---- progress bar ----
        self._progress = ttk.Progressbar(parent, mode="indeterminate",
                                         style="Accent.Horizontal.TProgressbar")
        self._progress.pack(fill="x", pady=(10, 0))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Accent.Horizontal.TProgressbar",
                        troughcolor=BORDER, background=ACCENT,
                        darkcolor=ACCENT, lightcolor=ACCENT, bordercolor=BG)

    # ── Results panel ──────────────────────────────────────────────────────────
    def _build_results(self, parent):
        hdr = tk.Frame(parent, bg=BG)
        hdr.pack(fill="x", pady=(0, 6))
        tk.Label(hdr, text="RESULTS", font=FONT_BOLD,
                 fg=TEXT_SEC, bg=BG).pack(side="left", pady=(14, 0))

        self._export_btn = tk.Button(hdr, text="Export .txt",
                                     font=FONT_TINY, fg=ACCENT, bg=BG,
                                     relief="flat", bd=0, cursor="hand2",
                                     command=self._export_results,
                                     state="disabled")
        self._export_btn.pack(side="right", pady=(14, 0))

        self._clear_btn = tk.Button(hdr, text="Clear",
                                    font=FONT_TINY, fg=TEXT_SEC, bg=BG,
                                    relief="flat", bd=0, cursor="hand2",
                                    command=self._clear_results)
        self._clear_btn.pack(side="right", padx=(0, 12), pady=(14, 0))

        # subdomain list box
        list_frame = tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                              highlightthickness=1)
        list_frame.pack(fill="both", expand=True)

        self._list_box = tk.Listbox(list_frame, font=FONT_MONO,
                                    fg=SUCCESS, bg=CARD, selectbackground=BORDER,
                                    selectforeground=TEXT_PRI,
                                    relief="flat", bd=0,
                                    highlightthickness=0,
                                    activestyle="none")
        sb_y = tk.Scrollbar(list_frame, orient="vertical",
                            command=self._list_box.yview, bg=BORDER,
                            troughcolor=CARD, relief="flat")
        self._list_box.configure(yscrollcommand=sb_y.set)
        sb_y.pack(side="right", fill="y")
        self._list_box.pack(fill="both", expand=True)

        # log output
        tk.Label(parent, text="LOG", font=FONT_BOLD,
                 fg=TEXT_SEC, bg=BG).pack(anchor="w", pady=(10, 4))

        log_frame = tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                             highlightthickness=1, height=130)
        log_frame.pack(fill="x")
        log_frame.pack_propagate(False)

        self._log_text = tk.Text(log_frame, font=("Consolas", 9),
                                 fg=TEXT_SEC, bg=CARD, relief="flat", bd=8,
                                 highlightthickness=0, state="disabled",
                                 wrap="word", cursor="arrow")
        sb_log = tk.Scrollbar(log_frame, orient="vertical",
                              command=self._log_text.yview, bg=BORDER,
                              troughcolor=CARD, relief="flat")
        self._log_text.configure(yscrollcommand=sb_log.set)
        sb_log.pack(side="right", fill="y")
        self._log_text.pack(fill="both", expand=True)

        # colour tags for log
        self._log_text.tag_config("info",    foreground=TEXT_SEC)
        self._log_text.tag_config("success", foreground=SUCCESS)
        self._log_text.tag_config("warning", foreground=WARNING)
        self._log_text.tag_config("error",   foreground=ERROR)
        self._log_text.tag_config("accent",  foreground=ACCENT)

    # ── Placeholder helpers ────────────────────────────────────────────────────
    def _placeholder_clear(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg=TEXT_PRI)

    def _placeholder_restore(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=TEXT_DIM)

    # ── Scan logic ─────────────────────────────────────────────────────────────
    def _start_scan(self):
        if self._running:
            return

        domain = self._domain_var.get().strip()
        if not domain or domain == "e.g. example.com":
            messagebox.showwarning("No domain", "Please enter a target domain.")
            return

        # validate loosely
        if not re.match(r'^[a-zA-Z0-9]+([\-\.][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}$', domain):
            messagebox.showerror("Invalid domain",
                                 "Please enter a valid domain (e.g. example.com).")
            return

        if not os.path.isfile(SUBLIST3R_PY):
            messagebox.showerror("sublist3r.py not found",
                                 f"Could not find sublist3r.py at:\n{SUBLIST3R_PY}\n\n"
                                 "Place gui_sublist3r.py in the same folder as sublist3r.py.")
            return

        self._clear_results()
        self._running = True
        self._run_btn.config(state="disabled")
        self._stop_btn.config(state="normal")
        self._export_btn.config(state="disabled")
        self._progress.start(12)
        self._status_var.set(f"Scanning {domain} …")
        self._log("Starting scan for: " + domain, "accent")

        # build args
        chosen = [k for k, v in self._engine_vars.items() if v.get()]
        engines_str = ",".join(chosen) if chosen else None

        cmd = [sys.executable, SUBLIST3R_PY,
               "-d", domain,
               "-n",                              # no colour codes in output
               "-t", self._threads_var.get()]
        if self._verbose_var.get():
            cmd.append("-v")
        if self._brute_var.get():
            cmd.append("-b")
        if engines_str:
            cmd += ["-e", engines_str]

        # build env with any API keys the user supplied
        env = os.environ.copy()
        dns_key = self._dns_key_var.get().strip()
        vt_key  = self._vt_key_var.get().strip()
        if dns_key:
            env["DNSDUMPSTER_API_KEY"] = dns_key
        if vt_key:
            env["VTAPIKEY"] = vt_key

        threading.Thread(target=self._run_proc, args=(cmd, env), daemon=True).start()

    def _run_proc(self, cmd, env=None):
        try:
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=SCRIPT_DIR,
                env=env
            )
            subdomain_re = re.compile(
                r'^(?!.*[-]\s)([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
            )
            for line in self._proc.stdout:
                line = line.rstrip()
                # strip any residual ANSI
                line_clean = re.sub(r'\x1b\[[0-9;]*m', '', line)
                if not line_clean:
                    continue
                # detect subdomain lines vs log lines
                if subdomain_re.match(line_clean):
                    self._queue.put(("subdomain", line_clean))
                else:
                    tag = "info"
                    low = line_clean.lower()
                    if "error" in low or "invalid" in low:
                        tag = "error"
                    elif "found" in low or "total" in low:
                        tag = "success"
                    elif "start" in low or "enum" in low or "search" in low:
                        tag = "accent"
                    self._queue.put(("log", (line_clean, tag)))

            self._proc.wait()
            rc = self._proc.returncode
            self._queue.put(("done", rc))
        except Exception as ex:
            self._queue.put(("error", str(ex)))

    def _stop_scan(self):
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
        self._queue.put(("done", -1))

    # ── Queue polling (main thread) ────────────────────────────────────────────
    def _poll_queue(self):
        try:
            while True:
                msg_type, payload = self._queue.get_nowait()
                if msg_type == "subdomain":
                    if payload not in self._subdomains:
                        self._subdomains.append(payload)
                        self._list_box.insert("end", payload)
                        self._list_box.yview_moveto(1.0)
                        self._count_var.set(f"{len(self._subdomains)} subdomains found")
                elif msg_type == "log":
                    self._log(*payload)
                elif msg_type == "done":
                    self._scan_finished(payload)
                elif msg_type == "error":
                    self._log("Process error: " + payload, "error")
                    self._scan_finished(-1)
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)

    def _scan_finished(self, rc):
        self._running = False
        self._progress.stop()
        self._run_btn.config(state="normal")
        self._stop_btn.config(state="disabled")
        n = len(self._subdomains)
        if rc == 0:
            self._status_var.set(f"Scan complete  ·  {n} subdomains found")
            self._log(f"Done. {n} unique subdomain(s) found.", "success")
        elif rc == -1:
            self._status_var.set("Scan stopped by user")
            self._log(f"Stopped. {n} subdomain(s) collected so far.", "warning")
        else:
            self._status_var.set(f"Scan finished with errors  ·  {n} found")
            self._log(f"Finished with exit code {rc}. {n} subdomain(s) collected.", "warning")

        if n > 0:
            self._export_btn.config(state="normal")

    # ── Results helpers ────────────────────────────────────────────────────────
    def _clear_results(self):
        self._subdomains = []
        self._list_box.delete(0, "end")
        self._count_var.set("")

    def _export_results(self):
        if not self._subdomains:
            messagebox.showinfo("Nothing to export", "No subdomains to save.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save subdomains",
            initialfile="subdomains.txt"
        )
        if not path:
            return
        try:
            with open(path, "w") as f:
                f.write(os.linesep.join(self._subdomains) + os.linesep)
            self._log(f"Exported {len(self._subdomains)} subdomains to {path}", "success")
            messagebox.showinfo("Exported", f"Saved {len(self._subdomains)} subdomains to:\n{path}")
        except Exception as ex:
            messagebox.showerror("Export failed", str(ex))

    def _log(self, text, tag="info"):
        self._log_text.config(state="normal")
        ts = time.strftime("%H:%M:%S")
        self._log_text.insert("end", f"[{ts}] {text}\n", tag)
        self._log_text.yview_moveto(1.0)
        self._log_text.config(state="disabled")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = GUISublist3r()
    app.mainloop()
