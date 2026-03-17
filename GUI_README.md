# GUI Sublist3r

A clean, dark graphical interface for Sublist3r v2.0.  
No command line needed — just double-click and go.

---

## Installation

1. **Place all files in the same folder** as your existing Sublist3r v2.0 files:
   ```
   your-folder/
   ├── sublist3r.py          ← original tool
   ├── subbrute/             ← original subbrute folder
   ├── gui_sublist3r.py      ← GUI application  ✓ new
   ├── GUISublist3r.bat      ← Windows launcher ✓ new
   └── launch_guisublist3r.sh← macOS/Linux launcher ✓ new
   ```

2. **Install dependencies** (if you haven't already):
   ```
   pip install -r requirements.txt
   ```

---

## How to launch (double-click)

### Windows
Double-click **`GUISublist3r.bat`**

> If Windows asks "How do you want to open this?", choose to run it anyway.  
> You may need to right-click → *Run as administrator* on first use.

### macOS / Linux
1. Make the script executable **once**:
   ```bash
   chmod +x launch_guisublist3r.sh
   ```
2. Double-click **`launch_guisublist3r.sh`** in Finder / Files.  
   (On macOS you may need to right-click → *Open* the first time.)

### Any platform (fallback)
```bash
python gui_sublist3r.py
```

---

## Usage

| Step | Action |
|------|--------|
| 1 | Type the target domain in the **Target Domain** box |
| 2 | Tick/untick the **Search Engines** you want to use |
| 3 | Optionally enable **bruteforce** or change the thread count |
| 4 | Click **▶ Run Scan** |
| 5 | Watch subdomains appear in the results box in real time |
| 6 | Click **Export .txt** to save results to a file of your choice |

---

## Notes

- The **VirusTotal** engine requires a `VTAPIKEY` environment variable to be set.  
  See the main Sublist3r README for instructions.
- Bruteforce mode is slow by design — it performs DNS brute-forcing against a large wordlist.
- The GUI runs `sublist3r.py` as a subprocess so all original functionality is preserved.
