# Weekend Project - Example Journaling App
## Introduction
This is a custom journaling app that I wrote in the span of a weekend. I did some basic scaffolding before my four-day Memorial Weekend, but the bulk of the work was done Friday and Saturday (with light commits Sunday and Monday during testing). This app was primarily written just to keep my python/django skills sharp while I'm not using them in my professional life - not neccessarily for the app's usefulness itself.

This app is trying to solve the following problems:
* Journals should always be private, and never sent off the computer this project runs on.
* Journals can benefit from AI analysis, and, that AI processessing should be done with local models on consumer-grade hardware  (I bought an Arc B280 for this project).
* Journals should be long-lasting

## Future Development
When I'm ready for the next iteration of this project, I'm hoping to incorporate the following:
* Feedback. I think it'd be interesting if after your journal is written, the AI gives you some suggestions for things to do the next day.
* Better sentiment analysis and sentiment-over-time graphs.
* Mobile-responsive templates for phones and tablets.
* Data import from other platforms (Day One, plain text).
* PWA support for offline journaling.

**Already implemented:** Goals journal with AI/manual linking ✅, Mood calendar and trends ✅, Annual reviews ✅, Tag system ✅, Export ✅, Streaks ✅, Templates ✅, and much more. See PLAN.md for the full roadmap.

## Current Features
Right now, the journal app does a lot more than when it started:

### Journaling
* **Create journals** with optional templates (Daily Reflection, Gratitude Journal, Weekly Review, Goal Check-in)
* **View past journals** in a table, timeline, or filtered by search, mood, date range, or tags
* **Edit and delete** journals
* **Bookmark** important entries for quick access
* **Link journals to goals** (automatic with AI, manual without)
* **Word count, character count, and reading time** displayed per entry
* **Draft autosave** — your work is saved to the browser if you get interrupted

### Insights & Analytics
* **Dashboard** with stats: total entries, current/longest streak, most common mood, writing volume
* **Mood Calendar** — a heatmap showing your mood over time
* **Mood Trends** — weekly mood frequency bar charts
* **On This Day** — re-read entries from the same date in previous years
* **Streak tracking** — current streak, longest streak, and all historical streaks

### Goals
* **Set goals** with titles, descriptions, rationale, timeframes (1m/6m/1y/5y), and parent goals
* **Track progress** with a 0-100% progress bar
* **Link journals to goals** to see which entries relate to which goals

### Organization
* **Tags** — create, edit, merge, and delete tags to categorize journals
* **Search & filter** — full-text search across content, reflections, and gratitude
* **Export** — download all journals as JSON or Markdown

### Reports
* **Weekly summaries** — AI or text-based review of your week
* **Monthly reports** — deeper monthly analysis with writing stats and mood breakdowns
* **Annual reviews** — year-in-review with monthly breakdowns, top moods, tags, and streaks
* **Ask a question** — query your journals with AI (when USE_AI=True)

### User Experience
* **Profile management** with password change
* **Dark mode** toggle
* **Responsive navigation bar** across all pages
* **Pagination** on all listing views

> **Note:** Screenshots below are from the original version of the app. The UI has evolved significantly since these were taken. Run the app locally with `./start.sh` to see the current interface.

### Original Screenshots (Outdated)
* You can create a journal
![image](https://github.com/user-attachments/assets/a7c55860-12fe-4b95-9d73-4abe3de6456a)
* You can view past journals
![image](https://github.com/user-attachments/assets/a03b01f2-51bb-497b-9b1e-db6083708c51)

_Note: These journals are example journals I had AI write with the prompt about being a drone operator in a bureaucratic organization._

* It has a Signal integration, meaning you can message the app things to journal about throughout the day and it'll display the messages when you sent them ("blurbs!")
![image](https://github.com/user-attachments/assets/4bcfda9b-b021-47f6-9cf5-b29a29dcbbe8)

* It sends your journals to a local LLM and automatically titles them. Also does mood extraction.
![image](https://github.com/user-attachments/assets/1125ad32-75e8-4ef6-ad44-16faed0e2844)
_Note: The Title and Mood tags are completely AI generated_

* Weekly Summaries - At the end of every week, AI reviews your journal and provides you a weekly summary.
![image](https://github.com/user-attachments/assets/6ddf8922-3c92-4f9c-b7ab-b71ac51638fa)

* You can even ask your journals a question using AI.
![image](https://github.com/user-attachments/assets/5d35288c-ffaf-4859-9447-5c80c5b73d8f)

* And it will give you a response formatted from Markdown!
![image](https://github.com/user-attachments/assets/27730138-17e4-4683-92a9-ac52eef60cef)


## Installation and Usage Instructions
### Running Locally (Development)

#### Quick Start

The easiest way to get up and running is to use the included `start.sh` script. It will automatically:

1. Create a `.env` file with a generated `SECRET_KEY` (if one doesn't exist)
2. Set up a Python virtual environment
3. Install dependencies
4. Run database migrations
5. Prompt you to create an admin user (if none exists)
6. Start the development server

```bash
./start.sh
```

The app will be available at http://localhost:8000/

**Script options:**
- `./start.sh --setup-only` — Perform setup steps without starting the server
- `./start.sh --help` — Show usage information

#### Manual Setup

If you prefer to run each step manually:

##### 1. Set up a virtual environment

```bash
cd Journaling-Application
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

##### 2. Create a .env file

Create a `.env` file in the project root with the following values:

```bash
SECRET_KEY=<a-random-64-character-hex-string>
DEBUG=True
USE_AI=False
WEBAPP_USERNAME=joe
```

- `SECRET_KEY`: Generate one with `python3 -c "import secrets; print(secrets.token_hex(32))"`
- `DEBUG`: Set to `True` for local development
- `USE_AI`: Set to `False` to run without AI/Ollama (default). Set to `True` if you have Ollama running locally.
- `WEBAPP_USERNAME`: The username for your journal account

##### 3. Initialize the database

```bash
cd journal_project
../venv/bin/python manage.py migrate
../venv/bin/python manage.py createsuperuser
```

##### 4. Run the development server

```bash
cd journal_project
../venv/bin/python manage.py runserver
```

##### 5. (Optional) Enable AI features

If you want to use the AI features locally:
1. Install [Ollama](https://ollama.com/) and start it
2. Pull a model: `ollama pull deepseek-r1:14b`
3. Set `USE_AI=True` in your `.env` file
4. The app will connect to Ollama at `http://localhost:11434` by default

### Getting the Ollama API running
#### If you have an Intel GPU
Check out my homelab project. Just copy the docker compose. You'll need the ollama-api, journal, and postgres containers.

#### If you have a Nvidia GPU
NVIDIA users have it the easiest, I recommend checking out [this article](https://gist.github.com/usrbinkat/de44facc683f954bf0cca6c87e2f9f88) as it should give you some helpful information on how to set up the compose.
The broad strokes: You'll need to get an ollama API endpoint listening. From there, the application during initialization should do all of the heavy lifting for you. By default, it'll grab Deepseek's r1-14b.

### Environment Variables

The docker compose references an env file. In the repository, the one that's included has all the ENV values you need, however, you'll need to set them yourself. The following values are required:

* `SECRET_KEY`: The value of the secret key for the Django webapp. Should be set to a random 64 hexadecimal value.
* `DEBUG`: Set to `True` for development, `False` for production.
* `USE_AI`: Set to `True` to enable AI-powered features (title generation, mood extraction, ask-a-question). Defaults to `False`.
* `SIGNAL_NUMBER`: The value of the phone number (including area code) you intend to use for Signal (blurb integration). Example value: +12024566213
* `WEBAPP_USERNAME`: The value of the username you intend to use for your journaling. The blurb integration will attach your blurbs to this user.
* `OLLAMA_API_URL`: The URL of your local Ollama API endpoint (e.g., `http://ollama:11434/api/generate`).
* `OLLAMA_MODEL`: The name of the Ollama model to use for AI processing (e.g., `deepseek-r1:14b`).

### Provisioning the database
The application uses PostgreSQL for data persistence. The database is provisioned automatically when you run `docker compose up`. The docker compose file includes the necessary PostgreSQL container configuration.

---

### Signal Setup
To set up Signal integration for blurbs, you'll need to trust the receiving number and send a test message. Replace the placeholder values with your actual numbers:

```bash
signal-cli --config /home/.local/share/signal-cli -a <number-sending-from> trust -a <number-sending-to>
signal-cli --config /home/.local/share/signal-cli -a <number-sending-from> send <number-to-trust> -m "test"
```

