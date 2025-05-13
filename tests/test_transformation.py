import pytest
from pathlib import Path
import json
from cricket_parser.parser import CricketParser
from cricket_parser.transformer import CricketDataTransformer

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

def test_record_generation(parser, sample_data):
    """Test that records are generated correctly."""
    result = parser._parse_data(sample_data)
    assert len(result) > 0
    
    # Check that each record has all required fields
    required_fields = {
        "match_date", "match_type", "venue", "city", "teams",
        "innings_number", "batting_team", "bowling_team",
        "over_number", "ball_number", "batter", "non_striker",
        "bowler", "runs_batter", "runs_extras", "runs_total"
    }
    
    for record in result:
        assert all(field in record for field in required_fields)

def test_field_mapping(parser, sample_data):
    """Test that fields are mapped correctly to Druid schema."""
    result = parser._parse_data(sample_data)
    assert len(result) > 0
    
    # Check that all fields have appropriate types
    for record in result:
        assert isinstance(record["match_date"], str)
        assert isinstance(record["match_type"], str)
        assert isinstance(record["venue"], str)
        assert isinstance(record["city"], str)
        assert isinstance(record["teams"], list)
        assert isinstance(record["innings_number"], int)
        assert isinstance(record["batting_team"], str)
        assert isinstance(record["bowling_team"], str)
        assert isinstance(record["over_number"], int)
        assert isinstance(record["ball_number"], int)
        assert isinstance(record["batter"], str)
        assert isinstance(record["non_striker"], str)
        assert isinstance(record["bowler"], str)
        assert isinstance(record["runs_batter"], int)
        assert isinstance(record["runs_extras"], int)
        assert isinstance(record["runs_total"], int)

def test_data_type_conversion(parser, sample_data):
    """Test that data types are converted correctly."""
    result = parser._parse_data(sample_data)
    assert len(result) > 0
    
    # Check numeric fields
    for record in result:
        assert record["runs_total"] == record["runs_batter"] + record["runs_extras"]
        assert record["over_number"] >= 0
        assert 1 <= record["ball_number"] <= 6
        assert record["innings_number"] in {1, 2}

def test_null_handling(parser, sample_data):
    """Test that null values are handled correctly."""
    result = parser._parse_data(sample_data)
    assert len(result) > 0
    
    # Check optional fields
    for record in result:
        # Optional fields should be None if not present
        if record["runs_extras"] == 0:
            assert record["extras_type"] is None
        
        if "wicket_type" in record:
            if record["wicket_type"] is None:
                assert record["wicket_player_out"] is None
                assert record["wicket_fielders"] == [] 