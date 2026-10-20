"""
Create list of URLs for USGS timeslices from NWM operational databased on user-input time and date
and download the files.
Written by Quinn Lee Russell (qylee@ua.edu)
"""

import argparse
from datetime import datetime, timezone, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import time
import requests

TIMESLICE_DIR = Path("usgs_timeslices")


def parse_arguments() -> argparse.Namespace:
    """Parse input arguments.

    Returns:
        argparse.Namespace
    """

    parser = argparse.ArgumentParser(description="Download USGS timeslices")
    parser.add_argument(
        "--start",
        type=lambda s: datetime.strptime(
            s, "%Y-%m-%d_%H:%M:%S"
        ),  # TODO: make timezone aware
        help="UTC start date and time (inclusive) in YYYY-MM-DD_HH:MM:SS",
        required=True,
    )

    parser.add_argument(
        "--end",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d_%H:%M:%S"),
        help="UTC end date and time (inclusive) in YYYY-MM-DD_HH:MM:SS",
        required=True,
    )

    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> None:
    """Validates datetime arguments by checking basic requirements for availability in NOMADS.
    NOMADS only contains data from the current day and the past day.

    Args:
        args (argparse.Namespace): Input arguments

    Raises:
        ValueError: End time is later than the current time
        ValueError: Start date is earlier than what is currently stored in NOMADS
    """

    current_time = datetime.now(timezone.utc)
    yesterday = current_time.date() - timedelta(days=1)

    end_time = args.end.replace(tzinfo=timezone.utc)
    start_date = args.start.replace(tzinfo=timezone.utc).date()

    if end_time > current_time:
        logging.error("End time is later than the current time")
        raise ValueError("End time is later than the current time")
    if start_date < yesterday:
        logging.error("Start date is earlier than what is currently stored in NOMADS")
        raise ValueError(
            "Start date is earlier than what is currently stored in NOMADS"
        )


def generate_dates(args: argparse.Namespace) -> list[datetime]:
    """Generate list of dates spaced 15 minutes apart given a start and end datetime (inclusive).
    USGS reports streamflow at 15-minute intervals.

    Args:
        args (argparse.Namespace): Input arguments

    Returns:
        list[datetime]: List of datetimes in 15-minute intervals
    """

    datetimes = []

    current_date = args.start
    while current_date <= args.end:
        datetimes.append(current_date)
        current_date += timedelta(minutes=15)

    return datetimes


def generate_urls(datetimes: list[datetime]) -> list[str]:
    """Generate NOMADS URLs for USGS timeslices given a list of datetimes.

    Args:
        datetimes (list[datetime]): List of datetimes for which timeslices should be downloaded.

    Returns:
        list[str]: List of URLs pointing to the USGS timeslices.
    """

    urls = []
    for dt in datetimes:
        day = dt.strftime("%Y%m%d")
        filename = dt.strftime("%Y-%m-%d_%H:%M:%S")

        url = (
            f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/nwm.{day}"
            + f"/usgs_timeslices/{filename}.15min.usgsTimeSlice.ncdf"
        )

        urls.append(url)

    return urls


def download_file(url: str) -> None:
    """Download timeslice files given a URL.

    Args:
        url (str): URL to USGS timeslice
    """

    local_filename = os.path.join(TIMESLICE_DIR, url.split("/")[-1])

    try:
        with requests.get(url, timeout=10) as response:
            response.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.info("Error downloading %s: %s", url, e)


def main() -> None:
    """Download USGS timeslice files in parallel, based on user inputted start and end datetimes."""
    start_time = time.perf_counter()

    if not TIMESLICE_DIR.exists():
        TIMESLICE_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H:%M:%S")
    logging.basicConfig(
        filename=f"{TIMESLICE_DIR}/usgs_timeslice_download_{now}.log",
        filemode="a",
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    logging.info("starting")
    args = parse_arguments()
    validate_arguments(args)
    datetimes = generate_dates(args)
    urls = generate_urls(datetimes)

    cpu_count = os.cpu_count()
    if cpu_count is None:
        cpu_count = 1
    elif cpu_count > 1:
        cpu_count -= 1
    else:
        pass

    # parallel download
    with ThreadPoolExecutor(max_workers=cpu_count) as executor:
        executor.map(download_file, urls)

    downloaded = [str(file) for file in TIMESLICE_DIR.glob("*.ncdf") if file.is_file()]
    num_downloaded = len(downloaded)
    num_urls = len(urls)
    total_size = sum(os.path.getsize(f) for f in downloaded)

    logging.info(
        "Successfully downloaded %d USGS timeslices out of %d", num_downloaded, num_urls
    )
    logging.info(
        "Total size of all downloaded timeslices: %d bytes", total_size
    )

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    logging.info(
        "Code took %.6f seconds to execute.", execution_time
    )

if __name__ == "__main__":
    main()
