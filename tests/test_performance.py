import pytest
import time
import json
from pathlib import Path
from cricket_parser.parser import CricketParser
import tracemalloc

@pytest.fixture
def sample_data():
    data_path = Path(__file__).parent.parent / "src" / "conf" / "sample_data.json"
    with open(data_path) as f:
        return json.load(f)

@pytest.fixture
def parser():
    return CricketParser()

def test_parsing_speed(parser, sample_data):
    """Test that parsing is reasonably fast for a typical match file."""
    start = time.time()
    result = parser._parse_data(sample_data)
    end = time.time()
    assert len(result) > 0
    # Should parse in under 1 second for a single match file
    assert (end - start) < 1.0

def test_memory_usage(parser, sample_data):
    """Test that memory usage is reasonable for a typical match file."""
    tracemalloc.start()
    result = parser._parse_data(sample_data)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert len(result) > 0
    # Should not use more than 10MB for a single match file
    assert peak < 10 * 1024 * 1024

def test_large_file_handling(tmp_path, parser, sample_data):
    """Test that parser can handle a large file (simulated by duplicating data)."""
    # Simulate a large file by duplicating innings
    large_data = sample_data.copy()
    large_data["innings"] = sample_data["innings"] * 50  # 100 innings
    start = time.time()
    result = parser._parse_data(large_data)
    end = time.time()
    assert len(result) > 0
    # Should parse in under 10 seconds for a large file
    assert (end - start) < 10.0
    # Should not use more than 100MB for a large file
    tracemalloc.start()
    parser._parse_data(large_data)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert peak < 100 * 1024 * 1024 