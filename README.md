# usgs_timeslice_downloader

A Docker image and associated Python script for CIROH's NextGen Research Datastream to download USGS timeslices from the NWM operational NOMADS data.

## Installation

### Docker installation

You will need [Docker Desktop](https://docs.docker.com/desktop/) to build the Docker image locally.

```bash
git clone https://github.com/quinnylee/usgs_timeslice_downloader.git
cd usgs_timeslice_downloader
docker build -t [name_of_image] .
```

### Local installation

Clone the repository and install the Python package. We recommend using [Astral UV](https://docs.astral.sh/uv/getting-started/installation/) as the package manager.

```bash
git clone https://github.com/quinnylee/usgs_timeslice_downloader.git
cd usgs_timeslice_downloader
uv venv
source .venv/bin/activate
uv pip install -e .
```

Without Astral UV, you will need a local [Python](https://www.python.org/downloads/) installation and the [pip](https://pypi.org/project/pip/) package manager.

```bash
git clone https://github.com/quinnylee/usgs_timeslice_downloader.git
cd usgs_timeslice_downloader
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

### Docker

You will need a local directory where you want the timeslices and output log to be stored. This will be mounted to the Docker image as a volume. Additionally, you will need `--start` and `--end` datetimes. Note that NOMADS only keeps data from the current day and the previous day.

```bash
docker run --rm -v "[absolute/path/to/timeslice/dir]:/app/usgs_timeslices" [name-of-image] --start "YYYY-MM-DD_HH:MM:SS" --end "YYYY-MM-DD_HH:MM:SS"
```

### Python

USGS timeslices will get downloaded into a directory named `usgs_timeslices`. You will need `--start` and `--end` datetimes. Note that NOMADS only keeps data from the current day and the previous day.

```bash
python scripts/download_timeslices.py --start "YYYY-MM-DD_HH:MM:SS" --end "YYYY-MM-DD_HH:MM:SS"
```

## Contributing

Pull requests are welcome.

## License

MIT
