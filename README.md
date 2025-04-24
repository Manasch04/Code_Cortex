**CODECORTEX**: Code Analysis Web Application


Project Overview:---


CODECORTEX is a Flask-based web application that enables users to submit code for automated analysis. It allows direct code submission or uploading ZIP files containing multiple code files. The application sends the submitted code to an external API for analysis and returns results in JSON and Markdown formats. With a futuristic UI and dark mode support, CODECORTEX provides a seamless and modern user experience for developers.


Features:----


1)Code Submission
Text Area Input: Submit code directly by pasting it into a text area.

ZIP File Upload: Upload ZIP files containing multiple code files for analysis.

2)Code Analysis
Submits the code (either direct input or from ZIP files) to an external API for processing.

3)Displays the results in both JSON and Markdown formats for ease of understanding.

4)Dark Mode
Toggle between Light and Dark modes for accessibility and user preferences.

5)Futuristic UI
The application features a modern design that includes gradients, glassmorphism, and neon effects for a futuristic user interface.

6)Download Results
Download the analysis results as a JSON file for further use or storage.



Folder Structure:-----


├── app/
│   ├── frontend/
│   │   ├── index.html
│   │   ├── input.html
│   │   ├── result.html
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
│   ├── uploads/
│   ├── history/
├── cortex.py
├── requirements.txt
└── README.md



Prerequisites:-----

Before running the application, make sure you have the following:

Python 3.7+ installed.


The following Python libraries installed:----
pip install -r requirements.txt


Setup Instructions:----

1. Clone the Repository
Clone the repository to your local machine:
git clone https://github.com/yourusername/codecortex.git
cd codecortex

2. Set Up the API Key
Open cortex.py.
Replace the placeholder YOUR_API_KEY with your actual API key obtained from the external API you are using for code analysis.
Update the ENDPOINT_URL variable in cortex.py to match the correct API endpoint URL.

3. Run the Application
To start the Flask application, run:
python cortex.py

4. Access the Application
Open your browser and navigate to http://127.0.0.1:5000/ to access the web application.



Usage:----

1. Home Page
Click Get Started to navigate to the input page where you can provide details about your code submission.

2. Input Page
Enter your name and select the type of code (e.g., library, API, etc.).
Click Next to proceed to the submission page.

3. Submission Page
Paste your code in the text area or upload a ZIP file containing your code files.
Click Analyze to submit the code for analysis.

4. Result Page
View the analysis results displayed in both JSON and Markdown formats.
Download the results as a JSON file by clicking the Download button.

Dark Mode
A Dark Mode toggle is available on all pages.
Click the Dark Mode button to switch between light and dark themes.

API Integration
The application integrates with an external API endpoint for code analysis:
Ensure the API is active and accessible.
The code will be submitted to the external endpoint for analysis, and the results will be displayed on the result page.


Customization:----

Frontend
Modify the HTML, CSS, and JS files in the frontend folder to customize the user interface.
You can adjust the themes, layout, or UI elements to suit your needs.

Storage Paths
The uploads folder stores uploaded ZIP files.
The history folder saves previous submissions and results.

You can update these paths in cortex.py if needed.


Known Issues:----

1. Large ZIP Files
Ensure that uploaded ZIP files do not exceed the server's upload limit. You may need to adjust the Flask configuration if you encounter this issue.

2. API Errors
If the API key or endpoint is incorrect, the application will display an error on the result page.




Future Enhancements:----

User Authentication: Implement user authentication for saving submission history and personalizing the experience.
Support for Additional File Formats: Extend support for other compressed formats like .tar.gz.
Real-time Progress Updates: Add real-time feedback during code analysis to keep the user informed.




License:---

This project is licensed under the MIT License. Feel free to use and modify it as needed.



Author:---

Developed by Manas Chauhan. For any queries, contact rajputmanas48@gmail.com.




