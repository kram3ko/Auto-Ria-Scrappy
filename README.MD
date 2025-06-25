# Auto-![scrap1](https://github.com/user-attachments/assets/45aaeb6a-e56b-49aa-900f-f1d3aec9fe7f)

Ria Scraping

This project is designed for automated data collection from the Auto.ria website.
It allows you to get up-to-date information about vehicles, analyze listings,
and manage collected data for further use.

## Quick Start

1. Clone the repository:

```bash
git clone git@github.com:kram3ko/Auto-Ria-Scrappy.git
cd auto-ria-scrap
```

2. Install dependencies using [uv](https://github.com/astral-sh/uv):

```bash
pip install uv
uv sync
# Or use pip
pip install -r requirements.txt
```

3. Run the project with Docker Compose:

```bash
docker compose up --build
```

## Description

Automated data collection from Auto.ria for analysis and storage of vehicle information.

async def fetch_all(start_page: int = 0, max_pages: int | None = None):
    """
     Executes the main asynchronous function.

     This function serves as the entry point for running the asynchronous
     fetch operation with specified parameters.

     :param start_page: The page number to start parsing from (default: 0)
     :type start_page: int
     :param max_pages: The maximum number of pages to parse (default: all)
     :type max_pages: int
     :returns: None
     :rtype: None

     You can specify the starting page and the number of pages to parse.
     Example:
         await main(start_page=5, max_pages=10)
     """

## Database Dump Scheduler

This project includes an automatic database dump scheduler. The scheduler creates a backup (dump) of your PostgreSQL database every day at a specified time and saves it in the `dumps` directory.

- **How it works:**
    - The scheduler runs in parallel with the main parser inside the Docker container.
    - It uses the time specified in the `.env` file (variable `DUMP_TIME`, format `HH:MM`, e.g., `12:00`).
    - Dumps are saved as SQL files in the `dumps` folder with a timestamp in the filename.

- **Configuration:**
    - Set the desired dump time in your `.env` file:
      ```env
      DUMP_TIME=12:00
      ```
    - By default, the time zone is set to `Europe/Kiev` (can be changed in `src/db_dump_scheduler.py`).

- **How to run:**
    - The scheduler starts automatically when you run the project with Docker Compose. No additional actions are required.
    - If you want to run the scheduler manually, use:
      ```bash
      python src/db_dump_scheduler.py
      ```

---

> Make sure you have Docker and Python 3.12+ installed for proper operation.
