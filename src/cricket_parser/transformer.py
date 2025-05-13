from typing import Dict, Any, List
from datetime import datetime
from .models import MatchInfo, DeliveryInfo

class CricketDataTransformer:
    """
    Transforms cricket match data into a format suitable for Druid ingestion.
    Provides validation and field mapping for each delivery record.
    """

    @staticmethod
    def transform_record(match_info: MatchInfo, delivery_info: DeliveryInfo) -> Dict[str, Any]:
        """
        Transform a single delivery record.
        Args:
            match_info: MatchInfo object containing match information
            delivery_info: DeliveryInfo object containing delivery information
        Returns:
            Dictionary containing transformed record
        Raises:
            ValueError: If required fields are missing
            AssertionError: If data types or constraints are violated
        """
        # Convert match info to dictionary
        record = match_info.model_dump()
        
        # Add delivery info
        record.update(delivery_info.model_dump())
        
        # Ensure all required fields are present
        required_fields = {
            "match_date", "match_type", "venue", "city", "teams",
            "innings_number", "batting_team", "bowling_team",
            "over_number", "ball_number", "batter", "non_striker",
            "bowler", "runs_batter", "runs_extras", "runs_total"
        }
        
        # Validate required fields
        missing_fields = required_fields - set(record.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Validate data types
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
        
        # Validate numeric constraints
        assert record["runs_total"] == record["runs_batter"] + record["runs_extras"]
        assert record["over_number"] >= 0
        balls_per_over = record.get("balls_per_over", 6)
        assert 1 <= record["ball_number"] <= balls_per_over
        assert record["innings_number"] >= 1
        
        # Handle optional fields
        if record["runs_extras"] == 0:
            record["extras_type"] = None
        
        if record["wicket_type"] is None:
            record["wicket_player_out"] = None
            record["wicket_fielders"] = []
        
        return record 

    def test_json_output_format(self, output_data: List[Dict[str, Any]]) -> None:
        """
        Test the JSON output format to ensure it meets the expected structure.
        Args:
            output_data: List of dictionaries representing the transformed records
        Raises:
            AssertionError: If the output format does not meet the expected structure
        """
        # Check first record structure
        first_record = output_data[0]
        assert isinstance(first_record, dict)
        # Allow None values in the output record
        assert all((v is None) or isinstance(v, (str, int, list)) for v in first_record.values()) 