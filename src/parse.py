import asyncio
import logging
import random
import re
from dataclasses import dataclass
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.dialects.postgresql import insert

from src.config.settings import get_settings
from src.database.postgres_db import get_postgresql_db_contextmanager
from src.models.models import ParseCarModel

BASE_URL = "https://auto.ria.com/uk/search/?indexName=auto&abroad=2&custom=3&page={page}&countpage=100"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


@dataclass
class ParseCar:
    url: str
    title: str
    price_usd: int
    odometer: int
    username: str
    phone_number: int
    image_url: str
    images_count: int
    car_number: str
    car_vin: str
    datetime_found: datetime


def safe_int(val, default=None):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


async def get_rates() -> tuple[float, float]:
    url = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
        usd = None
        eur = None
        for rate in data:
            if rate["ccy"] == "USD":
                usd = float(rate["sale"])
            elif rate["ccy"] == "EUR":
                eur = float(rate["sale"])
        if usd is None or eur is None:
            raise ValueError("Rates not found")
        return usd, eur


async def fix_price(price: str, usd_rate: float, eur_rate: float) -> int:
    price = price.replace(" ", "")
    if "$" in price:
        return int(re.search(r"(\d+)", price).group(1))
    elif "€" in price:
        eur = int(re.search(r"(\d+)", price).group(1))
        return int(eur * eur_rate / usd_rate)
    elif "грн" in price:
        uah = int(re.search(r"(\d+)", price).group(1))
        return int(uah / usd_rate)
    else:
        raise ValueError("unexpected price format")


def parse_phone_meta(soup):
    car_id_ul = soup.find("ul", class_="mb-10-list unstyle size13 mb-15")
    if not car_id_ul:
        return "Unknown", "", ""

    car_id = next(
        (
            li.find("span", class_="bold").text.strip()
            for li in car_id_ul.find_all("li")
            if li.text and "ID авто" in li.text
        ),
        "Unknown",
    )

    script = soup.find("script", class_=re.compile(r"js-user-secure-\d+"))
    if not script:
        return car_id, "", ""

    hash_value = script.get("data-hash", "")
    expires = script.get("data-expires", "")
    return car_id, hash_value, expires


async def fetch_phone(client: httpx.AsyncClient, car_id: str, hash_: str, expires: str) -> int | str | None:
    if not hash_ or not expires:
        return ""

    url = f"https://auto.ria.com/users/phones/{car_id}?hash={hash_}&expires={expires}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-Requested-With": "XMLHttpRequest",
    }

    max_retries = 10
    attempt = 0
    while attempt < max_retries:
        try:
            resp = await client.get(url, headers=headers)

            if resp.status_code == 429:
                attempt += 1
                await asyncio.sleep(random.randint(5, 10))
                continue

            if resp.status_code != 200:
                print(f"Phone fetch failed with status {resp.status_code} for car_id {car_id}")
                return ""

            data = resp.json()

            raw_phone = data.get("formattedPhoneNumber", "")
            digits = re.sub(r"\D", "", raw_phone)
            if len(digits) == 10:
                digits = "38" + digits
            phone_number = int(digits) if digits else 0
            return phone_number

        except httpx.RequestError as e:
            print(f"Request error when fetching phone for car_id {car_id}: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error when fetching phone for car_id {car_id}: {e}")
            return ""

    print(f"Max retries exceeded for car_id {car_id}")
    return ""


async def fetch_car(client: httpx.AsyncClient, car_url: str, usd_rate: float, eur_rate: float):  # noqa
    logger.debug(f"Parsing car: {car_url}")
    response = await client.get(car_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    title = soup.find("h1", class_="head").text
    price_text = soup.find("div", class_="price_value").find("strong").text
    price_usd = await fix_price(price_text, usd_rate, eur_rate)
    odometer_text = soup.find("div", class_="base-information bold").find("span", class_="size18").text
    odometer = (safe_int(odometer_text) * 1000) if safe_int(odometer_text) is not None else None
    username_tag = soup.select_one("div.seller_info_name.bold a.sellerPro")
    username = username_tag.text.strip() if username_tag else ""
    car_id, hash_value, expires = parse_phone_meta(soup)
    # phone_number_raw = await fetch_phone(client, car_id, hash_value, expires)
    # phone_number = safe_int(phone_number_raw)
    phone_number = 123
    img_tag = soup.find("img", class_="outline m-auto")
    image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""

    show_all_elem = soup.find("div", class_="preview-gallery mhide")
    images_count = None
    if show_all_elem:
        show_all_link = show_all_elem.find("a", class_="show-all link-dotted")
        if show_all_link and re.search(r"\d+", show_all_link.text):
            images_count = safe_int(re.search(r"\d+", show_all_link.text).group())

    car_vin_car_number = soup.find("div", class_="t-check")
    car_number = ""
    car_vin = ""

    if car_vin_car_number:
        car_number_tag = car_vin_car_number.find("span", class_="state-num ua")
        if car_number_tag and car_number_tag.contents:
            car_number = car_number_tag.contents[0].strip()

        car_vin_element = car_vin_car_number.find("span", class_="label-vin") or car_vin_car_number.find(
            "span", class_="vin-code"
        )
        if car_vin_element:
            car_vin = car_vin_element.text.strip()

    return ParseCarModel(
        url=car_url,
        title=title,
        price_usd=price_usd,
        odometer=odometer,
        username=username,
        phone_number=phone_number,
        image_url=image_url,
        images_count=images_count,
        car_number=car_number,
        car_vin=car_vin,
    )


async def save_cars(cars: list[ParseCarModel], session):
    """
    Save a list of car models to the database, ignoring duplicates.

    This function uses a PostgreSQL-specific 'INSERT ... ON CONFLICT DO NOTHING'
    to efficiently bulk-insert new cars while skipping ones that already exist
    based on the 'uq_car_number_url' unique constraint.
    """
    if not cars:
        return

    car_data = [
        {
            "url": car.url,
            "title": car.title,
            "price_usd": car.price_usd,
            "odometer": car.odometer,
            "username": car.username,
            "phone_number": car.phone_number,
            "image_url": car.image_url,
            "images_count": car.images_count,
            "car_number": car.car_number,
            "car_vin": car.car_vin,
        }
        for car in cars
    ]
    stmt = insert(ParseCarModel).values(car_data)
    stmt = stmt.on_conflict_do_nothing(index_elements=["car_number", "url"])
    await session.execute(stmt)
    await session.commit()


async def fetch_page(client: httpx.AsyncClient, url: str, usd_rate: float, eur_rate: float):
    response = await client.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")
    car_block = soup.find("div", class_="span8 box-panel") or soup.find("div", class_="result-explore fl-r m-view")
    if not car_block:
        logger.warning("Car block not found on the page")
        return []
    car_urls = [a["href"] for a in car_block.find_all("a", class_="m-link-ticket") if a.has_attr("href")]
    if not car_urls:
        logger.warning("No car URLs found")
        return []
    results = await asyncio.gather(
        *(fetch_car(client, car_url, usd_rate, eur_rate) for car_url in car_urls),
        return_exceptions=True,
    )
    return results


async def fetch_all(start_page: int = 0, max_pages: int | None = None):
    settings = get_settings()
    logger.info(f"Settings loaded successfully. Connecting to DB: '{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}'")
    logger.info(
        f"Starting parser: start_page={start_page}, max_pages={max_pages if max_pages is not None else 'no limit'}"
    )

    try:
        usd_rate, eur_rate = await get_rates()
        logger.info(f"Current rates: USD={usd_rate}, EUR={eur_rate}")
    except Exception as e:
        logger.error(f"Could not fetch currency rates. Aborting. Error: {e}")
        return

    page_count = 0
    total_processed_count = 0
    page_num = start_page

    async with (
        httpx.AsyncClient(timeout=30.0) as client,
        get_postgresql_db_contextmanager() as session,
    ):
        while True:
            if max_pages is not None and page_count >= max_pages:
                logger.info(f"Reached page limit of {max_pages}.")
                break

            url = BASE_URL.format(page=page_num)
            page_count += 1

            try:
                logger.info(f"Fetching page_num: {page_num} (url: {url})")
                results = await fetch_page(client, url, usd_rate, eur_rate)
                valid_cars = [car for car in results if isinstance(car, ParseCarModel)]
                errors = [e for e in results if isinstance(e, Exception)]

                logger.info(f"Page #{page_count}: Found {len(valid_cars)} cars. Encountered {len(errors)} errors.")

                if errors:
                    for error in errors:
                        logger.debug(f"Page #{page_count} parsing error: {error}")

                if valid_cars:
                    await save_cars(valid_cars, session)
                    logger.info(f"Page #{page_count}: Sent {len(valid_cars)} cars to be saved in the database.")
                    total_processed_count += len(valid_cars)

                if not valid_cars:
                    logger.info("No more cars found, stopping.")
                    break

                page_num += 1

            except Exception as e:
                logger.error(f"A critical error occurred while processing page {url}: {e}")
                break

    logger.info(f"Parsing finished. Total cars processed and sent to DB: {total_processed_count}.")


async def main():
    await fetch_all(10, 3)


if __name__ == "__main__":
    asyncio.run(main())
