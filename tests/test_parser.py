import json
import pytest
from pathlib import Path
from cricket_parser.parser import CricketParser

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

def test_json_loading(parser, sample_data):
    """Test that the parser can load JSON data correctly."""
    # This test will be implemented once we have the parser class
    pass

def test_schema_validation(parser, sample_data):
    """Test that the parser validates the input schema correctly."""
    # This test will be implemented once we have the parser class
    pass

def test_basic_field_extraction(parser, sample_data):
    """Test that the parser can extract basic fields from the data."""
    # This test will be implemented once we have the parser class
    pass 