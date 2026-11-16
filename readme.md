# Around the Globe Quiz

Around the Globe Quiz is a geography game built with Python and Streamlit.

The player chooses a difficulty and answers 15 multiple-choice questions:
five about capitals, five about flags and five about neighbouring countries.
The topics and answer options appear in a random order.

## How the game works

1. Choose easy, medium or hard.
2. Click Start quiz.
3. Select an answer and submit it.
4. Read the feedback and continue to the next question.
5. At the end, view the score, accuracy and performance charts.
6. Click Play again to start a new game.

Each question has four distinct answer labels and one stored correct answer.
The app requires a selection before submission and locks the answer afterward.

The same country cannot be used twice as a target within the same topic.
It can appear in different topics during one game.

## Data

The country records and SVG flag files come from
[World Countries by mledoze](https://github.com/mledoze/countries).

The JSON file contains country names, codes, capitals, regions,
subregions and land-border codes. The dataset also includes territories,
so not every record represents an independent country.

The application reads the data locally:

- Country records: `data/countries.json`
- Flag images: `data/flags/`

Flag filenames use lowercase three-letter country codes, such as `ita.svg`.

The World Bank API is not used in this version.

### Attribution

The World Countries database uses the
[Open Database License, ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
See the original repository's
[LICENSE](https://github.com/mledoze/countries/blob/master/LICENSE).

The source repository states that flag images are not covered by ODbL.
Its README provides separate information about rights in flag images.

## Preparing the data

The program prepares records separately for each topic:

- Capitals: keep countries with exactly one nonblank capital.
- Flags: keep records explicitly marked as UN members with an available
  SVG file. Indonesia and Monaco are excluded because both use red-over-white
  horizontal bands. Romania and Chad are excluded because both use
  blue-yellow-red vertical bands with subtle colour differences.
  These exclusions avoid relying on small visual differences.
- Neighbours: keep targets with at least one listed land neighbour,
  where every border code can be matched to a country name.

Prepared records require a nonempty country name and country code.
Regions and subregions are retained for selecting wrong answers.

## Difficulty

Difficulty is based on geographic similarity.

| Level | Rule for wrong answers | Points for a correct answer |
|---|---|---:|
| Easy | Countries in different regions from the target | 1 |
| Medium | Countries in the same region as the target | 2 |
| Hard | Countries in the same subregion as the target | 3 |

For capital questions, the options are the capitals associated with
those countries. For flag and neighbour questions, the options are
country names.

Neighbour questions exclude the target and all its listed neighbours
from the wrong-answer pool. One actual listed neighbour is selected
as the correct answer.

The generators remove repeated answer labels without distinguishing
capitalization. A target needs at least three suitable wrong answers.
If a valid quiz cannot be generated, the app displays an error.

Geography is a difficulty heuristic. For flags, it does not measure
similarity in colours, symbols or shapes.

## Scoring and analysis

Incorrect answers earn zero points. Correct answers earn the point
value of the selected difficulty.

The maximum scores are:

- Easy: 15 points.
- Medium: 30 points.
- Hard: 45 points.

Accuracy is `correct answers / answered questions × 100`.

The results page shows overall performance, a bar chart of accuracy
by topic and a pie chart of correct and incorrect answers.

It also compares the game with independent random guessing.
With four options and one correct answer, the guessing probability
is 0.25 per question.

For question point values `w`, the calculations are:

- Expected correct answers: `number of questions × 0.25`
- Expected score: `0.25 × sum(w)`
- Score variance: `0.25 × 0.75 × sum(w²)`
- Score standard deviation: square root of the variance

These are averages and variation across hypothetical guessing games,
not guaranteed outcomes or measurements of the player's knowledge.

## Libraries

| Library | Use |
|---|---|
| Streamlit | Display the game and handle player interaction. |
| pandas | Convert answer records into a table and group results by topic. |
| NumPy | Calculate the random-guessing comparison. |
| Matplotlib | Create the performance charts. |

Exact installed versions are recorded in `requirements.txt`.

## Files

| File | Purpose |
|---|---|
| `data_loader.py` | Load JSON and prepare country records. |
| `question_generator.py` | Generate individual questions and options. |
| `quiz_logic.py` | Assemble the quiz, check answers and calculate totals. |
| `analysis.py` | Summarize results and create charts and numerical comparisons. |
| `app.py` | Display the game and manage its session state. |
| `.streamlit/config.toml` | Set the application theme. |
| `.gitignore` | Exclude the environment and generated files from Git. |

The app imports the project's functions instead of duplicating their code.

## Setup and run

The project was developed with Python 3.15. Compatibility with other
Python versions has not yet been verified.

### 1. Download the project

Clone the repository:

```powershell
git clone https://github.com/budnikovateya/around-the-globe-quiz.git
cd around-the-globe-quiz
```

Alternatively, download and extract the repository ZIP and open its
project folder in VS Code.

### 2. Create a virtual environment

Run from the project folder:

```powershell
python -m venv .venv
```

### 3. Install the libraries

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Start the app

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the Local URL printed in the terminal, usually
`http://localhost:8501`.

Keep the terminal running while playing.
Press `Ctrl + C` in the terminal to stop the app.

## Course materials

The project uses programming patterns from:

- [Montanelli's L1.py](https://github.com/montanelli/dsecoding2627/blob/master/PY/L1.py):
  functions, loops, conditions, lists and return values.
- [Picascia's lectures](https://github.com/sergiopicascia/codingdse-py/tree/main/lectures):
  project organization, JSON input, error handling, pandas, NumPy,
  Matplotlib and Streamlit.

The quiz rules are project-specific. Some presentation features,
including CSS and theme configuration, extend beyond the lecture
examples reviewed.

## Limitations

- Facts and border relationships follow the dataset snapshot and may
  be incomplete, disputed or outdated.
- A single listed capital does not resolve every distinction between
  a constitutional capital and a seat of government.
- Geographic similarity does not guarantee greater difficulty.
- The flag pool excludes non-UN-member records and two known confusing
  flag pairs. These are manual safeguards, not an automated visual
  comparison of every flag.
- Five questions per topic provide only a small sample of performance.
- Results remain in the current browser session; permanent game history
  is not implemented.
- A fresh-environment installation check remains to be completed.