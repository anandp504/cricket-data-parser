from pathlib import Path
import json
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from .models import MatchInfo, DeliveryInfo
from .transformer import CricketDataTransformer
from .output import OutputGenerator

class CricketParser:
    """
    Parser for cricket match data from cricsheet.org JSON format.
    Provides methods to parse, transform, and output ball-by-ball cricket data for Druid ingestion.
    """

    def __init__(self):
        """
        Initialize the parser and supporting transformer/output classes.
        """
        self.transformer = CricketDataTransformer()
        self.output_generator = OutputGenerator()

    def parse_file(self, file_path: str | Path) -> List[Dict[str, Any]]:
        """
        Parse a single cricket match file.
        Args:
            file_path: Path to the JSON file containing match data
        Returns:
            List of dictionaries containing parsed delivery data
        """
        with open(file_path) as f:
            data = json.load(f)
        return self._parse_data(data)

    def parse_directory(self, directory_path: str | Path) -> List[Dict[str, Any]]:
        """
        Parse all cricket match files in a directory.
        Args:
            directory_path: Path to directory containing match files
        Returns:
            List of dictionaries containing parsed delivery data from all matches
        """
        results = []
        for file_path in Path(directory_path).glob("*.json"):
            results.extend(self.parse_file(file_path))
        return results

    def _parse_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the cricket match data.
        Args:
            data: Dictionary containing match data
        Returns:
            List of dictionaries containing parsed delivery data
        """
        # Extract match information
        match_info = self._extract_match_info(data["info"])
        # Process innings
        results = []
        for innings_number, innings in enumerate(data["innings"], 1):
            results.extend(self._process_innings(innings, innings_number, match_info))
        return results

    def _extract_match_info(self, info: Dict[str, Any]) -> MatchInfo:
        """
        Extract match information from the info section.
        Args:
            info: Dictionary containing match information
        Returns:
            MatchInfo object containing extracted information
        """
        # Extract winner information
        winner = None
        win_margin = None
        win_margin_type = None
        if "outcome" in info:
            outcome = info["outcome"]
            if "winner" in outcome:
                winner = outcome["winner"]
                if "by" in outcome:
                    by_info = outcome["by"]
                    if "runs" in by_info:
                        win_margin = by_info["runs"]
                        win_margin_type = "runs"
                    elif "wickets" in by_info:
                        win_margin = by_info["wickets"]
                        win_margin_type = "wickets"
        # Extract toss information
        toss_winner = None
        toss_decision = None
        if "toss" in info:
            toss = info["toss"]
            toss_winner = toss.get("winner")
            toss_decision = toss.get("decision")
        balls_per_over = info.get("balls_per_over", 6)
        
        # Extract gender from event name if it contains "Women's"
        gender = "women" if "Women's" in info.get("event", {}).get("name", "") else "men"
        
        # Extract event information
        event = info.get("event", {})
        
        return MatchInfo(
            match_date=info["dates"][0],
            match_type=info["match_type"],
            venue=info["venue"],
            city=info["city"],
            teams=info["teams"],
            winner=winner,
            win_margin=win_margin,
            win_margin_type=win_margin_type,
            toss_winner=toss_winner,
            toss_decision=toss_decision,
            balls_per_over=balls_per_over,
            gender=gender,
            event=event
        )

    def _process_innings(self, innings: Dict[str, Any], innings_number: int, match_info: MatchInfo) -> List[Dict[str, Any]]:
        """
        Process a single innings.
        Args:
            innings: Dictionary containing innings data
            innings_number: Number of the innings (1 or 2)
            match_info: MatchInfo object containing match information
        Returns:
            List of dictionaries containing parsed delivery data
        """
        results = []
        batting_team = innings["team"]
        bowling_team = next(team for team in match_info.teams if team != batting_team)
        for over in innings["overs"]:
            results.extend(self._process_over(over, innings_number, batting_team, bowling_team, match_info))
        return results

    def _process_over(self, over: Dict[str, Any], innings_number: int, batting_team: str, 
                     bowling_team: str, match_info: MatchInfo) -> List[Dict[str, Any]]:
        """
        Process a single over.
        Args:
            over: Dictionary containing over data
            innings_number: Number of the innings
            batting_team: Team batting in this innings
            bowling_team: Team bowling in this innings
            match_info: MatchInfo object containing match information
        Returns:
            List of dictionaries containing parsed delivery data
        """
        results = []
        over_number = over["over"]
        balls_per_over = match_info.balls_per_over
        ball_number = 1
        legal_deliveries_count = 0
        for delivery in over["deliveries"]:
            # Check if this delivery is a legal ball (not a wide or no-ball)
            is_legal = True
            if "extras" in delivery:
                extras = delivery["extras"]
                if "wides" in extras or "noball" in extras:
                    is_legal = False
            delivery_info = self._process_delivery(
                delivery, over_number, ball_number, innings_number,
                batting_team, bowling_team
            )
            results.append(self.transformer.transform_record(match_info, delivery_info))
            if is_legal:
                legal_deliveries_count += 1
                ball_number += 1
        # No error raised for more than balls_per_over total deliveries, only for legal deliveries
        if legal_deliveries_count > balls_per_over:
            raise ValueError(f"Over {over_number} has more than {balls_per_over} legal deliveries.")
        return results

    def _process_delivery(self, delivery: Dict[str, Any], over_number: int, ball_number: int,
                         innings_number: int, batting_team: str, bowling_team: str) -> DeliveryInfo:
        """
        Process a single delivery.
        Args:
            delivery: Dictionary containing delivery data
            over_number: Number of the over
            ball_number: Number of the ball within the over
            innings_number: Number of the innings
            batting_team: Team batting in this innings
            bowling_team: Team bowling in this innings
        Returns:
            DeliveryInfo object containing delivery information
        """
        # Extract basic delivery information
        runs = delivery["runs"]
        runs_batter = runs["batter"]
        runs_extras = runs["extras"]
        runs_total = runs["total"]
        # Extract extras information
        extras_type = None
        if "extras" in delivery:
            extras_type = next(iter(delivery["extras"].keys()))
        # Extract wicket information
        wicket_type = None
        wicket_player_out = None
        wicket_fielders = []
        if "wickets" in delivery:
            wicket = delivery["wickets"][0]  # Assuming one wicket per delivery
            wicket_type = wicket["kind"]
            wicket_player_out = wicket["player_out"]
            if "fielders" in wicket:
                wicket_fielders = [fielder["name"] for fielder in wicket["fielders"]]
        return DeliveryInfo(
            innings_number=innings_number,
            batting_team=batting_team,
            bowling_team=bowling_team,
            over_number=over_number,
            ball_number=ball_number,
            batter=delivery["batter"],
            non_striker=delivery["non_striker"],
            bowler=delivery["bowler"],
            runs_batter=runs_batter,
            runs_extras=runs_extras,
            runs_total=runs_total,
            extras_type=extras_type,
            wicket_type=wicket_type,
            wicket_player_out=wicket_player_out,
            wicket_fielders=wicket_fielders
        )

    def write_output(self, data: Dict[str, Any], output_path: Union[str, Path]) -> None:
        """
        Write parsed data to a JSON file using OutputGenerator.
        Args:
            data: Dictionary containing match data
            output_path: Path to write the output file
        """
        records = self._parse_data(data)
        self.output_generator.write_output(records, output_path)

    def process_batch(self, input_files: List[Union[str, Path]], output_path: Union[str, Path]) -> None:
        """
        Process multiple input files and write combined output using OutputGenerator.
        Args:
            input_files: List of input file paths
            output_path: Path to write the combined output file
        """
        all_records = []
        for input_file in input_files:
            with open(input_file) as f:
                data = json.load(f)
            all_records.extend(self._parse_data(data))
        self.output_generator.write_output(all_records, output_path) 