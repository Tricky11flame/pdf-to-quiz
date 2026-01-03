
## 🧠 **The Simple PDF-to-Quiz Pipeline**

This system takes your PDFs and turns them into study quizzes using **Gemini.** 
Follow these steps to *set up* everything up correctly.

---
### 📂 **Step 0: Folder Structure**

Your folders must look exactly like this for the scripts to work:

```text
Project_Root/
├── [SUBJECT1]/            # Subject Folder
│   ├── pdf/               # 📥 INPUT: Put your PDFs/PPTs here
│   ├── text/              # 📝 AUTO: Extracted text goes here
│   └── quizes/            # 📤 OUTPUT: AI Quizzes go here
├── [SUBJECT2]/            # Another Subject...
├── .env.local             # 🔐 Your API Key & Settings
├── convert.sh         # ⚙️ PDF-to-Text Script
└── script.py              # 🤖 AI Quiz Script

```

---

### 🛠️ **Setup & Tools**

**Create a Virtual Environment** 🛡️
Keep your project clean. Run this in your terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# OR: .\.venv\Scripts\Activate.ps1 (Windows)

```

**Install Libraries** 📦

```bash
pip install google-genai python-dotenv

```

*Note: You must have `poppler` installed on your computer for `pdftotext` to work.*

**Set your Secrets** 🔑
Create a file named `.env.local` and paste this:

```env
API_KEY=your_key_here
SUBJECTS=Architecture,CN,DBMS,OS
MODEL_ID=gemini-3-flash-preview
MIN_QUESTION_THRESHOLD=5

```

---

### ⚡ **Extract Text from PDFs**

We need to turn the PDFs into text files so the AI can read them.

**How to run:**

```bash
chmod +x convert.sh
cd ./SUBJECT1
./convert.sh

```

**The Code (`convert.sh`):**

```bash
#!/bin/bash
SUBJECTS=("Architecture" "CN" "DBMS" "OS")

for sub in "${SUBJECTS[@]}"; do
    echo "📂 Processing: $sub"
    mkdir -p "./$sub/text"
    for file in "./$sub/pdf"/*.pdf; do
        [ -e "$file" ] || continue
        name=$(basename "$file" .pdf)
        output="./$sub/text/$name.txt"
        if [ ! -f "$output" ]; then
            pdftotext -layout -enc UTF-8 "$file" "$output"
        fi
    done
done

```

---

### 🤖 **Generate the Quizzes**

Now, run the AI script to create your JSON quizzes.

**How to run:**

```bash
python3 script.py

```

**What the AI script does:**

* **Smart Skip:** It won't waste your API limit on files already done.
* **Auto-Wait:** If you hit the limit, it sees the "Retry in X seconds" message and waits for you.
* **Unify:** It puts every quiz into one big `fullQuiz.json` for each subject.

---

### ⚠️ **Important Notes**

* **Blank Files?** If a text file is empty, your PDF is likely a scanned image. You’ll need an OCR tool for those.
* **Quota Error?** If the script stops with a "429" error, just leave it running. It is programmed to wait and resume automatically when Google allows it.

Would you like me to help you create a **study interface** to actually take these quizzes?