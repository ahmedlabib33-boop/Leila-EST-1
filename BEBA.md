# SAT Quiz App

Leila EST Prep is a Streamlit learning and quiz application for Math and English EST preparation. It combines lesson browsing, math visualizations, mock exams, mistake review, progress tracking, and optional local AI explanations through Ollama.

## Program Design

The application is organized as a small Streamlit multi-page style app, with one main entry file and page modules.

```text
app.py
  -> initialize_session()
  -> top slide navigation
  -> selected page renderer

pages/
  home.py                    -> welcome screen
  learning.py                -> Math and English learning mode
  mock_exam.py               -> mock exam form, grading, result storage
  live_call.py               -> persistent remote audio/video call launcher
  review.py                  -> saved mistake review
  progress.py                -> score history and progress chart

loaders/
  learning_loader.py -> reads learning Excel files
  mock_loader.py     -> reads mock exam Excel files

ai/
  ai_engine.py        -> calls Ollama model with built-in fallback text
  prompts/            -> prompt builders
  course_generator/   -> math/english AI explanation wrappers

shared_session.py             -> shared selected-page and shared-notes sync files
```

## User Flow

```text
Start app
  -> Home
  -> Learning Mode
       -> choose Math or English
       -> choose topic
       -> choose lesson
       -> view formula, examples, explanations, and visuals
       -> optionally generate AI explanation
  -> Mock Exam
       -> choose subject
       -> choose exam
       -> answer questions
       -> submit
       -> grade result
       -> save progress and mistakes in session state
  -> Music Player
       -> floating global player available across all sections
       -> paste a supported YouTube, YouTube Music, Spotify, or SoundCloud link
       -> player stays minimized by default and does not require a separate Music slide
  -> Floating Explanation Pad
       -> movable and resizable drawing pad available across all sections
       -> pen, colors, eraser, undo, clear, grid, and download
  -> Shared Classroom
       -> floating live call available across all sections
       -> shared selected-section sync between both browsers
       -> shared typed explanation notes
  -> Review Mistakes
       -> filter saved mistakes by subject
       -> review question, user answer, correct answer, explanation
  -> Progress
       -> view latest, best, and average score
       -> view attempt history table
       -> view score chart after at least two attempts
```

## Page Behavior

### Home

File: `pages/home.py`

Shows the app title, target date, welcome message, and developer credit.

### Learning Mode

File: `pages/learning.py`

Subject options:

- `Math`
- `English`

Math learning uses `data/learning_math_content.xlsx`.

Math page features:

- Topic selector by `domain`
- Lesson selector by `lesson_title`
- Formula display
- Example display
- Explanation split by `|`
- Topic metrics
- Lessons-per-domain chart
- Difficulty chart
- Lesson map table
- Equation plots for selected graphable lessons
- Triangle area diagram for `Triangle Area`
- Optional AI explanation using Ollama

Current math visual rules:

| Lesson/formula keyword | Visualization |
| --- | --- |
| `slope`, `linear`, `y=mx+b`, `ax+b` | Line plot for `y = 2x + 1` |
| `quadratic`, `vertex`, `x2`, `x^2` | Parabola plot for `y = x^2 - 2x - 3` |
| `absolute value`, `\|x\|` | V-shaped plot for `y = \|x\|` |
| `exponential`, `growth`, `a(b)^x` | Growth plot for `y = 2^x` |
| `circle` | Circle plot for `x^2 + y^2 = 25` |
| `triangle` + `area` or `surface` | Triangle base/height SVG diagram |

English learning uses `data/learning_english_content.xlsx`.

English page features:

- Topic selector by `lesson_title`
- Rule title display
- Beginner-to-expert explanation structure for each rule
- Example display
- Expert tip and common EST trap display
- Two practice questions for every English rule from `data/learning_english_questions.xlsx`
- Answer feedback appears only after Leila chooses an option
- Optional AI explanation using Ollama, with built-in fallback if Ollama is unavailable

### Mock Exam

File: `pages/mock_exam.py`

Data files:

- English: `data/mock_english.xlsx`
- Math: `data/mock_math.xlsx`

Mock exam behavior:

1. User selects subject: `English` or `Math`.
2. App loads the matching workbook.
3. User selects an `exam_id`.
4. Questions are grouped by `section`.
5. Each question displays options A-D plus `Not answered`.
6. On submit, `_grade_exam()` compares the selected letter with `correct_answer`.
7. Result is stored in `st.session_state.last_exam_result`.
8. Attempt summary is appended to `st.session_state.progress_history`.
9. Wrong answers are appended to `st.session_state.mistakes`.

### Persistent Live Call

File: `pages/live_call.py`

Provides a global persistent remote audio/video call launcher using Jitsi Meet.

Persistent call behavior:

1. A minimized `Live Call` panel appears globally.
2. User presses `Open` to expand the embedded call while staying inside the app.
3. User presses `Tab` only if the browser requires a separate call tab for camera or microphone permissions.
4. The app remains free for Home, Learning, Mock Exam, Review, Progress, and IPTVSmartersPro.
5. Browser camera and microphone permissions must be allowed.

Important: use the Cloudflare HTTPS public app link for remote access. Camera and microphone permissions can fail on plain HTTP depending on browser settings.

### Shared Classroom Sync

Files: `shared_session.py`, `data/shared_session.json`, `data/shared_explanation_notes.txt`

Shared classroom behavior:

- When either side changes the selected app section, the selected page is written to `data/shared_session.json`.
- The other browser follows the shared page through the automatic refresh cycle.
- `Shared classroom notes` stores typed explanations in `data/shared_explanation_notes.txt`.
- The floating drawing pad is browser-local. For live pen drawings, use the embedded Jitsi call screen-share feature or write typed notes in the shared notes panel.

### Floating Explanation Pad

File: `app.py`

The app injects a floating explanation pad globally, so it is available across Home, Learning, Mock Exam, Review, Progress, and Music.

Pad features:

- Move by dragging the pad header
- Resize from the pad corner
- Minimize or hide
- Reopen with `Open Pad`
- Pen mode
- Auto Text mode for clean medium-size typed placement when text is provided, with browser handwriting-recognition fallback where supported
- Keyboard Text mode: type in the pad text box, then tap/click the pad to place clean typed text
- Stronger Eraser mode with a larger effective erase area
- Color picker
- Brush size control
- Undo
- Clear
- Grid background toggle
- Download drawing as PNG
- Browser local storage persistence while navigating between sections

### Music Player

File: `app.py`

The separate Music slide was removed. Music is now handled by a compact global floating player.

Music Player behavior:

- Minimized by default
- Positioned at the bottom-right of the screen
- `Open Pad` is positioned above it to avoid overlap
- Accepts supported YouTube, YouTube Music, Spotify, and SoundCloud links
- Plays embedded music inside the program where the platform allows embedding
- Persists while moving through Home, Learning, Mock Exam, Review, and Progress
- Stores the last link in browser local storage

### Review Mistakes

File: `pages/review.py`

Reads `st.session_state.mistakes`.

Features:

- Subject filter: `All`, `English`, `Math`
- Saved mistakes count
- Expandable mistake review cards
- Clear all saved mistakes button

### Progress

File: `pages/progress.py`

Reads `st.session_state.progress_history`.

Features:

- Latest score metric
- Best score metric
- Average score metric
- Subject filter
- Attempt history table
- Bar chart by `exam_id` after at least two filtered attempts

## Data Flow

### Learning Data Flow

```text
Excel workbook in data/
  -> loaders/learning_loader.py
  -> pandas DataFrame
  -> pages/learning.py
  -> Streamlit controls and visualizations
  -> optional AI prompt
  -> ai/course_generator/*
  -> ai/ai_engine.py
  -> Ollama tinyllama response or built-in fallback lesson
  -> Streamlit output
```

### Mock Exam Data Flow

```text
mock_english.xlsx or mock_math.xlsx
  -> loaders/mock_loader.py
  -> pandas DataFrame
  -> pages/mock_exam.py
  -> Streamlit form
  -> _grade_exam()
  -> result dictionary
  -> st.session_state.last_exam_result
  -> st.session_state.progress_history
  -> st.session_state.mistakes
  -> Progress and Review pages
```

## Data Schema

All main content is stored in Excel files inside `data/`.

### `data/learning_math_topics.xlsx`

Rows: 5

| Column | Meaning |
| --- | --- |
| `subject` | Subject name, currently `Math` |
| `topic_id` | Topic identifier, such as `MATH-01` |
| `topic_name` | Display name for the topic |
| `order` | Topic ordering number |

### `data/learning_math_content.xlsx`

Rows: 159

| Column | Meaning |
| --- | --- |
| `topic_id` | Links lesson to a math topic |
| `domain` | Topic/domain displayed in the Math topic selector |
| `lesson_title` | Lesson name displayed in the lesson selector |
| `formula` | Formula shown in the lesson page |
| `example` | Example problem text |
| `explanation` | Explanation text; `|` is used to split into multiple visual blocks |
| `difficulty` | Difficulty label: `Easy`, `Medium`, or `Hard` |
| `arabic` | Arabic explanation/translation helper |

Example rows include:

- `Algebra` / `Addition` / `a+b`
- `Algebra` / `Slope Intercept Form` / `y=mx+b`
- `Geometry` / `Triangle Area` / `1/2bh`
- `Geometry` / `Circle Equation` / `(x-h)^2+(y-k)^2=r^2`

### `data/learning_english_topics.xlsx`

Rows: 12

| Column | Meaning |
| --- | --- |
| `subject` | Subject name, currently `english` |
| `topic_id` | Topic identifier, such as `eng-01` |
| `topic_name` | Display name for the English topic |
| `order` | Topic ordering number |

### `data/learning_english_content.xlsx`

Rows: 157

| Column | Meaning |
| --- | --- |
| `topic_id` | Links rule to an English topic |
| `lesson_title` | Main English topic shown in the selector |
| `rule_title` | Individual rule shown inside the selected topic |
| `explanation` | Rule explanation; `|` can split text into multiple blocks |
| `example` | Example sentence or usage |
| `tip` | Study tip shown with success styling |

### `data/learning_english_questions.xlsx`

Rows: 314

| Column | Meaning |
| --- | --- |
| `topic_id` | Links question to an English topic |
| `lesson_title` | Main English topic |
| `rule_title` | Individual English rule |
| `difficulty` | `Easy` or `Medium` |
| `question` | Practice question text |
| `option_a` | Answer choice A |
| `option_b` | Answer choice B |
| `option_c` | Answer choice C |
| `option_d` | Answer choice D |
| `correct_answer` | Correct letter: `A`, `B`, `C`, or `D` |
| `explanation` | Explanation shown after Leila chooses an answer |

### `data/mock_english.xlsx`

Rows: 850

| Column | Meaning |
| --- | --- |
| `exam_id` | Exam name, such as `English Exam 1` |
| `subject` | `English` |
| `section` | Exam section/module name |
| `question_number` | Question number used for sorting and display |
| `skill` | Skill tested |
| `difficulty` | Difficulty label |
| `passage` | Optional reading passage |
| `question` | Question text |
| `option_a` | Answer choice A |
| `option_b` | Answer choice B |
| `option_c` | Answer choice C |
| `option_d` | Answer choice D |
| `correct_answer` | Correct letter: `A`, `B`, `C`, or `D` |
| `explanation` | Explanation displayed after grading |

### `data/mock_math.xlsx`

Rows: 500

Uses the same schema as `mock_english.xlsx`, with `subject` set to `Math`.

## Session State Schema

Initialized in `session.py`.

| Key | Type | Purpose |
| --- | --- | --- |
| `score` | number | Legacy score holder |
| `wrong_answers` | list | Legacy wrong-answer holder |
| `completed_topics` | list | Legacy completed-topic holder |
| `current_question` | number | Legacy current-question holder |
| `progress_history` | list of dictionaries | Stores submitted mock exam summaries |
| `mistakes` | list of dictionaries | Stores missed questions for review |
| `last_exam_result` | dictionary | Created after mock exam submission |

### `progress_history` Item Schema

Created in `pages/mock_exam.py`.

| Key | Meaning |
| --- | --- |
| `date` | Submission date/time as `YYYY-MM-DD HH:MM` |
| `subject` | `English` or `Math` |
| `exam_id` | Selected exam |
| `score` | Number of correct answers |
| `total` | Number of questions in the selected exam |
| `percent` | Score percentage rounded to one decimal |
| `mistakes` | Number of missed questions |

### `mistakes` Item Schema

Created in `_grade_exam()` inside `pages/mock_exam.py`.

| Key | Meaning |
| --- | --- |
| `date` | Submission date/time |
| `subject` | `English` or `Math` |
| `exam_id` | Selected exam |
| `section` | Exam section/module |
| `question_number` | Question number |
| `skill` | Tested skill |
| `passage` | Optional passage |
| `question` | Question text |
| `your_answer` | User-selected answer text or `Not answered` |
| `correct_answer` | Correct answer letter and text |
| `explanation` | Explanation from workbook |

## AI Explanation Flow

AI explanations try Ollama first. If Ollama or the selected model is unavailable, the app shows a built-in structured explanation instead of failing.

```text
Learning page button
  -> generate_math_course(topic) or generate_english_course(topic)
  -> prompt builder in ai/prompts/
  -> generate_text(prompt)
  -> ollama.chat(model=OLLAMA_MODEL or "qwen2.5-coder:7b") or built-in fallback
  -> displayed in Streamlit
```

The AI model and timeout are configured in `ai/ai_engine.py` and can be overridden with environment variables:

```python
DEFAULT_OLLAMA_MODEL = "qwen2.5-coder:7b"
OLLAMA_TIMEOUT_SECONDS = 25
```

## Requirements

Install dependencies from `requirements.txt`:

```text
streamlit
streamlit-autorefresh
pandas
openpyxl
ollama
```

## Setup

Run these commands once from the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
ollama pull qwen2.5-coder:7b
```

## Run The App

Activate the virtual environment if it is not already active:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start Ollama in a separate terminal to enable AI-generated explanations:

```powershell
ollama serve
```

Start the Streamlit application:

```powershell
streamlit run app.py
```

The local app will normally open at:

```text
http://localhost:8501
```

## Cloudflare Public Link

Follow these exact steps to create a public Cloudflare link from the beginning.

### 1. Open PowerShell In The Project Folder

```powershell
cd C:\Users\pc\OneDrive\Desktop\leila\SAT_Quiz_App
```

### 2. Allow Virtual Environment Activation For This PowerShell Window

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### 3. Create And Activate The Virtual Environment

If `.venv` does not exist yet, create it:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install The App Requirements

```powershell
python -m pip install -r requirements.txt
```

### 5. Start The Streamlit App

Keep this terminal open:

```powershell
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

The local app should show:

```text
http://127.0.0.1:8501
```

### 6. Open A Second PowerShell Terminal

Go to the same project folder again:

```powershell
cd C:\Users\pc\OneDrive\Desktop\leila\SAT_Quiz_App
```

### 7. Start The Cloudflare Tunnel

Run:

```powershell
cloudflared tunnel --url http://localhost:8501
```

Cloudflare will print a public link like this:

```text
https://example-words-here.trycloudflare.com
```

Copy that `trycloudflare.com` link and share it.

Important: keep both terminals open. If you close Streamlit or Cloudflare, the public link will stop working.

## Remote Audio / Video Call Workflow

Use this when you want to explain to Leila remotely.

1. Start the app with Streamlit.
2. Start the Cloudflare tunnel.
3. Send Leila the Cloudflare public link.
4. Both you and Leila open the app link.
5. Both press `Open Persistent Call`.
6. Both keep the same room name, for example:

```text
LeilaESTPrepLiveClass
```

7. Both press allow for camera and microphone permissions.
8. Keep the call tab open.
9. Return to the app tab and move through Learning, Exams, Review, or Progress while the call continues.

## Quick Run Files

You can also use the included batch files.

Start the app:

```powershell
.\RUN_APP.bat
```

Start the Cloudflare tunnel in another terminal:

```powershell
.\RUN_TUNNEL.bat
```

## Notes And Constraints

- Progress and mistakes are stored only in Streamlit session state, so they reset when the browser session/app session resets.
- Excel column names must stay exactly as listed in the schemas above.
- `correct_answer` must be one of `A`, `B`, `C`, or `D`.
- Math and English learning explanations use `|` as a delimiter for separate display blocks.
- Cloudflare quick tunnel links are temporary and change each time a new tunnel is created.
- The Live Call room is public to anyone who has the room link/name. Use a unique room name if privacy matters.
