import pytest
from pathlib import Path
import json
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

def test_innings_structure_validation(parser, sample_data):
    """Test that innings structure is validated correctly."""
    result = parser._parse_data(sample_data)
    assert len(result) > 0
    
    # Check that we have records from both innings
    innings_numbers = {record["innings_number"] for record in result}
    assert innings_numbers == {1, 2}

def test_over_extraction(parser, sample_data):
    """Test extraction of over information."""
    result = parser._parse_data(sample_data)
    assert len(result) > 0
    
    # Check first record has correct over information
    first_record = result[0]
    assert first_record["over_number"] == 0
    assert first_record["ball_number"] == 1

def test_delivery_extraction(parser, sample_data):
    """Test extraction of delivery information."""
    result = parser._parse_data(sample_data)
    assert len(result) > 0
    
    # Check first record has correct delivery information
    first_record = result[0]
    assert first_record["batter"] == "Priyada Murali"
    assert first_record["non_striker"] == "Zeefa Jilani"
    assert first_record["bowler"] == "A Gurung"
    assert first_record["runs_batter"] == 0
    assert first_record["runs_extras"] == 1
    assert first_record["runs_total"] == 1

def test_runs_calculation(parser, sample_data):
    """Test calculation of runs from deliveries."""
    result = parser._parse_data(sample_data)
    assert len(result) > 0
    
    # Find a delivery with runs
    runs_delivery = next(
        record for record in result 
        if record["runs_batter"] > 0 or record["runs_extras"] > 0
    )
    assert runs_delivery["runs_total"] == runs_delivery["runs_batter"] + runs_delivery["runs_extras"]

def test_extras_handling(parser, sample_data):
    """Test handling of extras in deliveries."""
    result = parser._parse_data(sample_data)
    assert len(result) > 0
    
    # Find a delivery with extras
    extras_delivery = next(
        record for record in result 
        if record["runs_extras"] > 0
    )
    assert extras_delivery["extras_type"] is not None
    assert extras_delivery["runs_extras"] > 0

def test_wicket_information_extraction(parser, sample_data):
    """Test extraction of wicket information."""
    result = parser._parse_data(sample_data)
    
    # Find a delivery with a wicket if any
    wicket_delivery = next(
        (record for record in result if record["wicket_type"] is not None),
        None
    )
    
    if wicket_delivery:
        assert wicket_delivery["wicket_player_out"] is not None
        assert wicket_delivery["wicket_type"] is not None 