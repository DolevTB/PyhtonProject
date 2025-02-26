# PythonProject

This project provides a CLI tool to manage AWS services, including EC2, S3, and Route 53. It offers an interactive menu for users to perform various AWS operations easily.

## Prerequisites

Before using this tool, make sure you have the following:

- AWS CLI installed [installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- AWS credentials configured using `aws configure`
- Python 3 installed
- Required dependencies installed
- Make sure that every input you make is in English (other languages might crash the CLI)

## Installation

Clone this repository:

```bash
git clone https://github.com/DolevTB/PyhtonProject.git
cd PyhtonProject
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the CLI tool with:

```bash
python main.py
```

## Menu Options

- **EC2 Service**: Manage EC2 instances.
- **S3 Service**: Manage S3 buckets.
- **Route 53 Service**: Manage DNS settings.
- **Exit**: Quit the program.
  
## Flow Chart
![My image](images/Flow%20Chart%20AWS-Python-Project.jpg)

## Project Structure

```
.
├── main.py              # Entry point for the CLI
├── modules/
│   ├── ec2.py               # EC2 management functions
│   ├── S3.py                # S3 management functions
│   ├── Route53.py           # Route 53 management functions
│   └── General_func.py      # Utility functions (e.g., clearing terminal)
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```
