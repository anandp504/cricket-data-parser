import pytest
from pathlib import Path
import json
from cricket_parser.parser import CricketParser
from cricket_parser.transformer import CricketDataTransformer
from cricket_parser.models import MatchInfo, DeliveryInfo

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

@pytest.fixture
def sample_match_info():
    """Create sample match info for testing."""
    return MatchInfo(
        match_date="2024-01-01",
        match_type="T20",
        venue="Test Stadium",
        city="Test City",
        teams=["Team A", "Team B"],
        winner="Team A",
        win_margin=10,
        win_margin_type="runs",
        toss_winner="Team A",
        toss_decision="bat",
        gender="men",
        event={
            "name": "Test Series",
            "type": "bilateral",
            "season": "2024"
        }
    )

@pytest.fixture
def sample_delivery_info():
    """Create sample delivery info for testing."""
    return DeliveryInfo(
        innings_number=1,
        batting_team="Team A",
        bowling_team="Team B",
        over_number=1,
        ball_number=1,
        batter="Batsman 1",
        non_striker="Batsman 2",
        bowler="Bowler 1",
        runs_batter=4,
        runs_extras=0,
        runs_total=4
    )

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

def test_record_generation(sample_match_info, sample_delivery_info):
    """Test that records are generated correctly with all required fields."""
    transformer = CricketDataTransformer()
    record = transformer.transform_record(sample_match_info, sample_delivery_info)
    
    # Check required fields
    assert "match_date" in record
    assert "match_type" in record
    assert "venue" in record
    assert "city" in record
    assert "teams" in record
    assert "innings_number" in record
    assert "batting_team" in record
    assert "bowling_team" in record
    assert "over_number" in record
    assert "ball_number" in record
    assert "batter" in record
    assert "non_striker" in record
    assert "bowler" in record
    assert "runs_batter" in record
    assert "runs_extras" in record
    assert "runs_total" in record
    assert "gender" in record
    assert "event" in record
    
    # Check values
    assert record["gender"] == "men"
    assert isinstance(record["event"], dict)
    assert record["event"]["name"] == "Test Series"
    assert record["event"]["type"] == "bilateral"
    assert record["event"]["season"] == "2024"

def test_field_mapping(sample_match_info, sample_delivery_info):
    """Test that fields are mapped correctly from input to output."""
    transformer = CricketDataTransformer()
    record = transformer.transform_record(sample_match_info, sample_delivery_info)
    
    # Check field values
    assert record["match_date"] == "2024-01-01"
    assert record["match_type"] == "T20"
    assert record["venue"] == "Test Stadium"
    assert record["city"] == "Test City"
    assert record["teams"] == ["Team A", "Team B"]
    assert record["innings_number"] == 1
    assert record["batting_team"] == "Team A"
    assert record["bowling_team"] == "Team B"
    assert record["over_number"] == 1
    assert record["ball_number"] == 1
    assert record["batter"] == "Batsman 1"
    assert record["non_striker"] == "Batsman 2"
    assert record["bowler"] == "Bowler 1"
    assert record["runs_batter"] == 4
    assert record["runs_extras"] == 0
    assert record["runs_total"] == 4
    assert record["gender"] == "men"
    assert record["event"]["name"] == "Test Series"

def test_data_type_conversion(sample_match_info, sample_delivery_info):
    """Test that data types are converted correctly."""
    transformer = CricketDataTransformer()
    record = transformer.transform_record(sample_match_info, sample_delivery_info)
    
    # Check data types
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
    assert isinstance(record["gender"], str)
    assert isinstance(record["event"], dict)

def test_null_handling(sample_match_info, sample_delivery_info):
    """Test handling of null/optional fields."""
    # Set optional fields to None
    sample_match_info.winner = None
    sample_match_info.win_margin = None
    sample_match_info.win_margin_type = None
    sample_match_info.toss_winner = None
    sample_match_info.toss_decision = None
    
    transformer = CricketDataTransformer()
    record = transformer.transform_record(sample_match_info, sample_delivery_info)
    
    # Check that optional fields are handled correctly
    assert record["winner"] is None
    assert record["win_margin"] is None
    assert record["win_margin_type"] is None
    assert record["toss_winner"] is None
    assert record["toss_decision"] is None
    assert record["extras_type"] is None
    assert record["wicket_type"] is None
    assert record["wicket_player_out"] is None
    assert record["wicket_fielders"] == [] 