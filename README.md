# Python Console - README

## Description
This Python console is a simple command-line application that allows you to interact with various system utilities and web services. It includes features such as pinging a host, starting a temporary web server, scanning websites, and storing variables. The application is built using Python libraries like `Flask`, `requests`, and `BeautifulSoup`.

### Features:
- **Ping a host**: Check the latency to a given host.
- **Start a temporary web server**: Create a temporary website accessible for 5 minutes.
- **Scan a website**: Download and save resources from a website.
- **Save and display variables**: Store user-defined variables and display them when needed.
- **Browser operations**: Simulate simple browser interactions (such as clicking buttons or filling out forms).

## Installation
To run this Python console, you will need to install Python 3.9+ and the required libraries.

### Prerequisites:
Make sure you have **Python 3.9 or higher** installed. You can check your version using the following command:
```bash
python --version
or

python3 --version
Install Dependencies:
The following Python libraries are required:

ping3
pyfiglet
colorama
flask
requests
beautifulsoup4
You can install them using pip with the following command:

pip install ping3 pyfiglet colorama flask requests beautifulsoup4
Run the Console:
After installing the necessary libraries, you can run the console by executing the Python script:

python console.py

Commands
Here is a list of available commands that you can use in the console:

-help: Displays the available commands and their descriptions.
-ping [host]: Pings the specified host (e.g., -ping google.com).
-browser connect: Starts a temporary web server.
-browser connect off: Stops the running temporary web server.
-browser create scan: Creates a 1:1 replica of a scanned website.
-scan [url]: Scans a website and saves its resources locally (e.g., -scan https://example.com).
-exit: Exits the console.
-vars: Displays all the saved variables.

Example Usage

<< -ping google.com
Ping to google.com: 23.45 ms

<< -browser connect
Starting temporary web server...

<< -scan https://example.com
Scanning website https://example.com...

<< -vars
username = john_doe
password = secret_password

<< -exit
Exiting the console...
