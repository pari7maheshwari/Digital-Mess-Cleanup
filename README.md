# Digital Mess Cleanup

A modular Streamlit app for organizing files, identifying exact duplicates and similar images, and optionally classifying images with CLIP. It combines several text prompts per category to make image classification more robust. Original files are preserved; the app organizes copies.

## Agent workflow

1. Enter a cleanup goal, such as `Organize my photos and documents`.
2. Enter the destination path once. The local planner inspects the source,
   reports the recognized file-type scope, and presents the files and actions
   it proposes.
3. Review and approve the plan. The organizer prepares and verifies the
   organized files in a temporary staging folder; it does not yet create a
   folder at the selected destination.
4. Click **Download folder** to copy the prepared folder to the selected
   destination. If that folder already exists, the app creates a sibling with
   `_1`, `_2`, etc. Original files are preserved.

The planner currently recognizes file-type keywords (images/photos, documents,
spreadsheets, presentations, videos, audio, archives, code, and other files).
Unknown goals include all file types and are labeled as such. This is a local,
transparent planning workflow—not a general-purpose conversational LLM. CLIP
provides AI image classification. The app never moves or deletes originals.

The selected destination is shown again in the results, and the folder is
created there only after clicking **Download folder**. No ZIP is created.
Because browsers cannot write a directory to an arbitrary local path, this
copy is made by the Streamlit process and works on the machine running the app.
A redirected Windows Desktop is detected via the system's configured Desktop
folder.

The AI model menu defaults to CLIP ViT-B/32 for faster scans, particularly on
CPU-only computers. ViT-B/16 provides a balanced option; choose ViT-L/14 when
higher classification accuracy is more important than speed. The selected
model downloads on first use; supported CUDA GPUs are used automatically.

## Project structure

```text
DigitalMessCleanup/
├── app.py                         # Streamlit entry point
├── requirements.txt               # Python dependencies
├── README.md
└── digital_mess_cleanup/
    ├── __init__.py
    ├── config.py                  # Categories, AI labels, model settings
    ├── file_utils.py              # Hashing, safe copy, folder helpers
    ├── ai_classifier.py           # Cached CLIP model and image inference
    ├── planning.py                # Goal scope, approval snapshot, verification
    ├── organizer.py               # Scan and organize workflow
    ├── styles.py                  # Existing green/black/white CSS theme
    └── ui.py                      # Sidebar, controls, dashboard, report
```

## Run on Windows

Activate your existing virtual environment, then from this project folder run:

```powershell
python -m streamlit run app.py
```

If creating a new environment, install dependencies with `pip install -r requirements.txt`. PyTorch installation can vary by platform; use the official PyTorch installer instructions if the generic install does not work. The first AI-enabled scan downloads the selected CLIP model and its processor.
