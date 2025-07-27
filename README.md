# Naver Blog Automation

This project automates the process of creating and publishing blog posts on Naver using Python and Selenium. It leverages a web interface built with Flask to manage the automation tasks.

## Features

- **Automated Login**: Securely logs into Naver using provided credentials.
- **Content Generation**: Generates blog post content using the Gemini API.
- **Automated Posting**: Publishes the generated content to a Naver blog.
- **Web Interface**: Provides a user-friendly interface to start and monitor the automation process.

## Project Structure

- `app.py`: The main Flask application that serves the web interface and handles automation requests.
- `automation_runner.py`: Contains the core automation logic, including web scraping and browser interaction using Selenium.
- `templates/`: Contains the HTML templates for the web interface.
  - `index.html`: The main page with a form to start the automation.
  - `result.html`: Displays the progress and logs of the automation process.
- `static/`: Contains static files like CSS and JavaScript.
- `requirements.txt`: A list of Python dependencies required for the project.

## Setup and Usage

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/naver-blog-automation.git
   cd naver-blog-automation
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file**:
   Create a `.env` file in the root directory and add your Naver credentials:
   ```
   NAVER_ID="your_naver_id"
   NAVER_PASSWORD="your_naver_password"
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the web interface**:
   Open your web browser and go to `http://127.0.0.1:5001`.

6. **Start the automation**:
   - Fill in the required information in the form (e.g., keywords for content generation).
   - Click the "Start Automation" button.

7. **Monitor the progress**:
   You will be redirected to a page where you can see the logs of the automation process in real-time.

## How it Works

1. **Web Interface (`app.py`)**:
   - A Flask web server provides a user interface to start the automation.
   - It uses `glob` to find available automation scripts.
   - It uses `subprocess` to run the automation script in the background.
   - It provides an endpoint (`/status`) to check the status of the automation process.

2. **Automation Runner (`automation_runner.py`)**:
   - This script is executed by the Flask application.
   - It uses `glob` to find the latest version of the automation script.
   - It uses `subprocess` to run the automation script.

3. **Web Scraper (`scrapers/`)**:
   - This directory contains the web scraping logic.
   - It uses Selenium to automate browser interactions.
   - It logs into Naver, navigates to the blog editor, and publishes the content.

## Key Libraries

- **Flask**: For the web interface.
- **Selenium**: For browser automation and web scraping.
- **glob**: For finding files.
- **subprocess**: For running external commands.
- **dotenv**: For managing environment variables.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.