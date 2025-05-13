import json
import os
import pytest
from pathlib import Path
import tempfile
from cricket_parser.parser import CricketParser
from cricket_parser.output import OutputGenerator

@pytest.fixture
def sample_data():
    """Load sample cricket match data for testing."""
    data_path = Path(__file__).parent.parent / "src" / "conf" / "sample_data.json"
    with open(data_path) as f:
        return json.load(f)

@pytest.fixture
def parser():
    """Create a parser instance for testing."""
    return CricketParser()

def test_json_output_format(parser, sample_data):
    """Test that output is generated in correct JSON format."""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json') as temp_file:
        # Write output to temporary file
        parser.write_output(sample_data, temp_file.name)
        
        # Read back and validate
        with open(temp_file.name) as f:
            output_data = json.load(f)
        
        # Check that output is a list of records
        assert isinstance(output_data, list)
        assert len(output_data) > 0
        
        # Check first record structure
        first_record = output_data[0]
        assert isinstance(first_record, dict)
        assert all((v is None) or isinstance(v, (str, int, list)) for v in first_record.values())

def test_file_writing(parser, sample_data):
    """Test that files are written correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "output.json"
        
        # Write output
        parser.write_output(sample_data, str(output_path))
        
        # Check file exists and is readable
        assert output_path.exists()
        assert output_path.is_file()
        
        # Check file content
        with open(output_path) as f:
            output_data = json.load(f)
        assert len(output_data) > 0

def test_batch_processing(parser, sample_data):
    """Test batch processing of multiple files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple input files
        input_files = []
        for i in range(3):
            file_path = Path(temp_dir) / f"match_{i}.json"
            with open(file_path, 'w') as f:
                json.dump(sample_data, f)
            input_files.append(file_path)
        
        # Process all files
        output_path = Path(temp_dir) / "batch_output.json"
        parser.process_batch([str(f) for f in input_files], str(output_path))
        
        # Check output
        assert output_path.exists()
        with open(output_path) as f:
            output_data = json.load(f)
        assert len(output_data) > 0

def test_error_handling(parser, sample_data):
    """Test error handling during output generation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test invalid output path
        invalid_path = Path(temp_dir) / "nonexistent" / "output.json"
        with pytest.raises(Exception):
            parser.write_output(sample_data, str(invalid_path))
        
        # Test invalid input data
        invalid_data = {"invalid": "data"}
        output_path = Path(temp_dir) / "output.json"
        with pytest.raises(Exception):
            parser.write_output(invalid_data, str(output_path)) 