from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class MatchInfo(BaseModel):
    """
    Model for match-level information.
    Fields:
        match_date: Date of the match (YYYY-MM-DD)
        match_type: Type of match (T20, ODI, Test)
        venue: Venue of the match
        city: City where the match was played
        teams: List of team names
        winner: Winning team name
        win_margin: Margin of victory
        win_margin_type: Type of margin (runs/wickets)
        toss_winner: Team that won the toss
        toss_decision: Toss decision (bat/field)
        balls_per_over: Number of balls per over (default 6)
        gender: Gender category of the match (men/women)
        event: Event information (tournament, series, etc.)
    """
    match_date: str
    match_type: str
    venue: str
    city: str
    teams: List[str]
    winner: Optional[str] = None
    win_margin: Optional[int] = None
    win_margin_type: Optional[str] = None
    toss_winner: Optional[str] = None
    toss_decision: Optional[str] = None
    balls_per_over: int = 6
    gender: str
    event: Dict[str, Any] = Field(default_factory=dict)

class DeliveryInfo(BaseModel):
    """
    Model for delivery-level (ball-by-ball) information.
    Fields:
        innings_number: Innings number (1 or 2)
        batting_team: Team batting
        bowling_team: Team bowling
        over_number: Over number (0-indexed)
        ball_number: Ball number within the over (1-indexed)
        batter: Name of batter
        non_striker: Name of non-striker
        bowler: Name of bowler
        runs_batter: Runs scored by batter
        runs_extras: Extra runs
        runs_total: Total runs from the delivery
        extras_type: Type of extra (wide, no-ball, etc.)
        wicket_type: Type of dismissal if wicket fell
        wicket_player_out: Name of dismissed player
        wicket_fielders: List of fielders involved in dismissal
    """
    innings_number: int
    batting_team: str
    bowling_team: str
    over_number: int
    ball_number: int
    batter: str
    non_striker: str
    bowler: str
    runs_batter: int
    runs_extras: int
    runs_total: int
    extras_type: Optional[str] = None
    wicket_type: Optional[str] = None
    wicket_player_out: Optional[str] = None
    wicket_fielders: List[str] = Field(default_factory=list) 