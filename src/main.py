import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cricket_parser.parser import CricketParser
from cricket_parser.output import OutputGenerator

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output.json"

    try:
        # Initialize parser and output generator
        parser = CricketParser()
        output_gen = OutputGenerator()

        # Parse the input file
        parsed_data = parser.parse_file(input_file)
        
        # Write the output
        output_gen.write_output(parsed_data, output_file)
        
        print(f"Successfully parsed {input_file} and wrote output to {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 