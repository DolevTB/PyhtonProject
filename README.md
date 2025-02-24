# PyhtonProject
This project provides a CLI tool to manage AWS services, including EC2, S3, and Route 53. It offers an interactive menu for users to perform various AWS operations easily.

# Prerequisites
Before using this tool, make sure you have the following:
AWS CLI installed (installation guide)
AWS credentials configured using aws configure
Python 3 installed
Required dependencies installed

# Installation
1. Clone this repository:
git clone https://github.com/DolevTB/PyhtonProject.git
cd PyhtonProject

2. Install dependencies:
pip install -r requirements.txt

# Usage
Run the CLI tool with:
python main.py

# Menu Options
1. EC2 Service: Manage EC2 instances.
2. S3 Service: Manage S3 buckets.
3. Route 53 Service: Manage DNS settings.
4. Exit: Quit the program.

# Project Structure
.
├── main.py              # Entry point for the CLI
├── modules/
│   ├── ec2.py               # EC2 management functions
│   ├── S3.py                # S3 management functions
│   ├── Route53.py           # Route 53 management functions
│   └── General_func.py      # Utility functions (e.g., clearing terminal)
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation

