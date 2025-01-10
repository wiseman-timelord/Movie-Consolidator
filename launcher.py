# .\launcher.py

import os, sys, json
from data.temporary import SEARCH_CRITERIA, VIDEO_CONFIG, HARDWARE_CONFIG
from typing import Dict, Any
from utility import (
    load_hardware_config,
    load_settings,
    log_event,
    cleanup_work_directory
)
from scripts.generate import process_videos, process_video
from scripts.interface import launch_gradio_interface

class MovieConsolidator:
    def __init__(self):
        self.settings = load_settings()
        self.hardware_config = load_hardware_config()
        self.search_criteria = self.settings.get('search', {})
        self.video_config = self.settings.get('video', {})
        self.validate_environment()

    def validate_environment(self) -> None:
        """Validate the program environment."""
        try:
            required_dirs = ['data', 'input', 'output', 'work']
            for dir_name in required_dirs:
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
                    log_event(f"Created missing directory: {dir_name}")

            required_files = [
                os.path.join('data', 'temporary.py'),
                os.path.join('data', 'persistent.json'),
                os.path.join('data', 'hardware.txt')
            ]
            
            for file_path in required_files:
                if not os.path.exists(file_path):
                    log_event(f"Error: Required file missing: {file_path}")
                    raise FileNotFoundError(f"Required file missing: {file_path}")
                    
        except Exception as e:
            log_event(f"Environment validation failed: {e}")
            sys.exit(1)

    def print_hardware_info(self) -> None:
        """Display hardware configuration."""
        print("\nHardware Configuration:")
        for key, value in self.hardware_config.items():
            print(f"{key}: {value}")
        
        if self.hardware_config["OpenCL"]:
            print("Using OpenCL for GPU acceleration")
        elif self.hardware_config["Avx2"]:
            print("Using AVX2 for CPU acceleration")
        else:
            print("Using standard CPU processing")

    def process_directory(self, input_dir: str, output_dir: str) -> None:
        """Process all videos in a directory."""
        try:
            if not os.path.exists(input_dir):
                raise FileNotFoundError(f"Input directory not found: {input_dir}")
                
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            log_event(f"Starting batch processing: {input_dir} -> {output_dir}")
            process_videos(input_dir, output_dir)
            
        except Exception as e:
            log_event(f"Directory processing failed: {e}")
            cleanup_work_directory()

    def process_single_file(self, input_path: str, output_path: str) -> None:
        """Process a single video file."""
        try:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")
                
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            log_event(f"Processing single file: {input_path} -> {output_path}")
            process_video(input_path, output_path)
            
        except Exception as e:
            log_event(f"Single file processing failed: {e}")
            cleanup_work_directory()

def main():
    """Main entry point for the program."""
    try:
        # Initialize the consolidator
        consolidator = MovieConsolidator()
        consolidator.print_hardware_info()
        
        # Load settings
        settings = load_settings()
        
        # Determine if we're using GUI or command line
        if len(sys.argv) > 1:
            # Command line mode
            if sys.argv[1] == "--gui":
                launch_gradio_interface()
            elif len(sys.argv) == 3:
                # Process single directory
                input_dir = sys.argv[1]
                output_dir = sys.argv[2]
                consolidator.process_directory(input_dir, output_dir)
            elif len(sys.argv) == 4 and sys.argv[1] == "--file":
                # Process single file
                input_path = sys.argv[2]
                output_path = sys.argv[3]
                consolidator.process_single_file(input_path, output_path)
            else:
                print("\nUsage:")
                print("  Launch GUI:")
                print("    python launcher.py --gui")
                print("  Process directory:")
                print("    python launcher.py input_dir output_dir")
                print("  Process single file:")
                print("    python launcher.py --file input_path output_path")
        else:
            # Default to GUI mode
            launch_gradio_interface()
            
    except Exception as e:
        log_event(f"Program execution failed: {e}")
        print(f"Error: {e}")
        cleanup_work_directory()
        sys.exit(1)
        
    finally:
        cleanup_work_directory()

if __name__ == "__main__":
    main()