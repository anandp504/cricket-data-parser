import pytest
from datetime import datetime
from cricket_parser.parser import CricketParser
import json
from pathlib import Path

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

def test_match_metadata_extraction(parser, sample_data):
    """Test extraction of match metadata."""
    result = parser._parse_data(sample_data)
    assert len(result) > 0
    
    # Check first record has correct metadata
    first_record = result[0]
    assert first_record["match_date"] == "2025-05-12"
    assert first_record["match_type"] == "T20"
    assert first_record["venue"] == "Terdthai Cricket Ground, Bangkok"
    assert first_record["city"] == "Bangkok"

def test_team_information_extraction(parser, sample_data):
    """Test extraction of team information."""
    result = parser._parse_data(sample_data)
    assert len(result) > 0
    
    # Check first record has correct team information
    first_record = result[0]
    assert set(first_record["teams"]) == {"Kuwait", "Bhutan"}
    assert first_record["batting_team"] in {"Kuwait", "Bhutan"}
    assert first_record["bowling_team"] in {"Kuwait", "Bhutan"}

def test_match_result_extraction(parser, sample_data):
    """Test extraction of match result information."""
    result = parser._parse_data(sample_data)
    assert len(result) > 0
    
    # Check first record has correct result information
    first_record = result[0]
    assert first_record["winner"] == "Kuwait"
    assert first_record["win_margin"] == 35
    assert first_record["win_margin_type"] == "runs"

def test_toss_information_extraction(parser, sample_data):
    """Test extraction of toss information."""
    result = parser._parse_data(sample_data)
    assert len(result) > 0
    
    # Check first record has correct toss information
    first_record = result[0]
    assert first_record["toss_winner"] == "Bhutan"
    assert first_record["toss_decision"] == "field" 