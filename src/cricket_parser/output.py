import json
from pathlib import Path
from typing import List, Dict, Any, Union, Iterator
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

logger = logging.getLogger(__name__)

class OutputGenerator:
    """
    Handles generation of output files for cricket match data.
    Provides methods for writing output in JSONL format (one JSON object per line).
    """

    def __init__(self):
        """
        Initialize the output generator.
        """
        pass

    def write_output(self, data: List[Dict[str, Any]], output_path: Union[str, Path], stream: bool = False) -> None:
        """
        Write parsed data to a JSONL file (one JSON object per line).
        Args:
            data: List of records
            output_path: Path to write the output file
            stream: If True, write records one by one (streaming)
        Raises:
            Exception: If output path is invalid or file cannot be written
        """
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            raise Exception(f"Output directory does not exist: {output_dir}")
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                for record in data:
                    json.dump(record, f)
                    f.write('\n')
            logger.info(f"Successfully wrote output to {output_path}")
        except Exception as e:
            logger.error(f"Error writing output to {output_path}: {str(e)}")
            raise

    def process_batch(self, input_files: List[Union[str, Path]], output_path: Union[str, Path], parallel: bool = True, stream: bool = False) -> None:
        """
        Process multiple input files and write combined output in JSONL format.
        Args:
            input_files: List of paths to input files
            output_path: Path to write the combined output file
            parallel: If True, process files in parallel
            stream: If True, write output in streaming mode
        Raises:
            Exception: If files cannot be read or written
        """
        try:
            all_records = []
            if parallel:
                with ThreadPoolExecutor() as executor:
                    futures = {executor.submit(self._load_file, f): f for f in input_files}
                    for future in as_completed(futures):
                        all_records.extend(future.result())
            else:
                for input_file in input_files:
                    all_records.extend(self._load_file(input_file))
            self.write_output(all_records, output_path, stream=stream)
            logger.info(f"Successfully processed {len(input_files)} files to {output_path}")
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            raise

    @staticmethod
    def _load_file(input_file: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Load a single input file and return its data as a list of records.
        Supports both JSON array and JSONL formats.
        Args:
            input_file: Path to the input file
        Returns:
            List of records loaded from the file
        """
        records = []
        with open(input_file) as f:
            # Try reading as JSON array first
            try:
                data = json.load(f)
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass
            
            # If not a JSON array, try reading as JSONL
            f.seek(0)
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        record = json.loads(line)
                        records.append(record)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse line as JSON: {line}")
                        continue
        return records 