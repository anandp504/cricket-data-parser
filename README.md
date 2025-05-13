 # Cricket Data Parser

A Python-based parser for cricket match data that transforms ball-by-ball data from cricsheet.org JSON format into a structure suitable for Apache Druid ingestion.

## Features

- Parses cricket match data from cricsheet.org JSON format
- Transforms data into a flattened format suitable for Druid ingestion
- Handles T20, ODI, and Test match formats
- Provides detailed ball-by-ball information
- Supports batch processing of multiple matches
- Optimized for performance and large files

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd cricket-data-parser
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Parse a single match file and write output
```python
from cricket_parser.parser import CricketParser
import json

parser = CricketParser()
with open('src/conf/sample_data.json') as f:
    match_data = json.load(f)
parser.write_output(match_data, 'output.json')
```

### Batch process multiple files
```python
from cricket_parser.parser import CricketParser

parser = CricketParser()
input_files = ['match1.json', 'match2.json', 'match3.json']
parser.process_batch(input_files, 'batch_output.json')
```

### Streaming and parallel options for large datasets
```python
from cricket_parser.output import OutputGenerator

generator = OutputGenerator()
generator.process_batch(input_files, 'large_output.json', parallel=True, stream=True)
```

## API Documentation

### `CricketParser`
- `parse_file(file_path)`: Parse a single match file and return a list of delivery records.
- `parse_directory(directory_path)`: Parse all match files in a directory.
- `write_output(data, output_path)`: Parse and write output to a JSON file.
- `process_batch(input_files, output_path)`: Batch process multiple files and write combined output.

### `OutputGenerator`
- `write_output(data, output_path, stream=False)`: Write records to a JSON file, optionally streaming for large files.
- `process_batch(input_files, output_path, parallel=True, stream=False)`: Batch process with parallel and streaming options.

## Configuration Guide
- Place your input JSON files in a directory (e.g., `src/conf/`).
- Use the parser methods to process and output data as needed.
- For large datasets, use `stream=True` and `parallel=True` for best performance.

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black src tests
```

4. Type checking:
```bash
mypy src
```

## License

MIT License 
