
# Mail-Parser

## Overview
Mail-Parser is a rule-based email processor that allows users to fetch and manipulate emails based on predefined rules. It uses the Gmail API to interact with emails, providing functionalities such as marking emails as read/unread, moving emails to specific folders, and applying custom actions based on conditions like sender, subject, received date, etc.

## Setup

To get started with the project, follow these steps:

### 1. Set Up a Virtual Environment
To isolate your project dependencies, it is recommended to create a virtual environment.

- **Windows**:
  ```bash
  python -m venv venv
  ```

- **macOS/Linux**:
  ```bash
  python3 -m venv venv
  ```

### 2. Activate the Virtual Environment

- **Windows**:
  ```bash
  .\venv\Scripts\activate
  ```

- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies
Once the virtual environment is activated, install all the required dependencies by running:

```bash
pip install -r requirements.txt
```
NOTE: IF YOU ARE ON MAC YOU MAY HAVE TO INSTALL Tkinter and sqlite3 (use : pip install tkinter sqlite3)
This will install the necessary libraries to run the project.


### 4. OAuth Authentication
Before using the tool, make sure to set up OAuth authentication with your Gmail account by following these steps:

- Create OAuth credentials in the Google Cloud Console and download the `credentials.json` file.
- Place the `credentials.json` file in the project directory.
- You will need to authenticate your Gmail account to interact with the Gmail API.(FOR NOW THIS IS NOT POSSIBLE DUE TO MY PROJECT NOT BEING VERIFIED FOR EXTERNAL ACCESS BY THE CLOUD PLATFORM)

### 5. Run the Main.py
Running the following command in the terminal where the virtual environment is active will open the app.
```bash
python main.py
```


---

## How to Use

### Step 1: Add Rules
Once the project is set up and running, the first step is to define the rules that will govern how the emails are processed. To add rules:

- Open the `rules.json` file or use the GUI(Just run main.py) to create rules.
- Each rule can have conditions (such as "Sender equals" or "Received Date within last X days") and actions (such as "Mark as Read" or "Move to Folder").
- Ensure the rules are in the correct format as specified in the configuration.

### Step 2: Select Your Requirements
Use the provided GUI to select the conditions and actions you want to apply to your emails:

- Choose conditions from options like "Sender," "Subject," and "Received Date."
- Set the type of action, such as marking as read or moving emails to a folder.

### Step 3: Save and Apply Rules
Once you’ve selected your conditions and actions, save the rules and apply them to your emails:

- Click the **Save Rules** button to store your selections.
- Click **Apply Rules** to execute the rules and process the emails according to your specifications.

---
### NOTE: There are few test cases i have placed in the tests folder that can be accessed/ run via the following command in the terminal. It will run all the tests simultaneously, the tests are not all encompassing, ive only done those which I could.
```bash
     python -m unittest discover -s Tests
```

## Drawbacks of the Current Implementation

While the Mail-Parser project is functional, there are several limitations in the current version that need attention, For this project was built under time constraints and is initial version:

1. **Authentication Requirement**:
   - The tool requires OAuth authentication for Gmail, which may be cumbersome for users who don't want to authenticate each time they use the tool. This also introduces security risks related to managing OAuth tokens.
   
2. **Handling of Edge Cases**:
   - The current implementation does not handle certain edge cases. For example:
     - If the `received` condition is based on a `datetime`, the user interface should dynamically update to show days or other units based on the user's selection. This isn't currently implemented.
  

3. **Performance Issues**:
   - The current method of checking email labels and processing actions is slow and inefficient. The iteration over labels, fetching information repeatedly from Gmail, adds significant time to the processing.
   - Using **multithreading** or other optimization methods would drastically reduce the time taken to perform actions on emails and improve the overall user experience.

4. **Lack of Dynamic UI Updates**:
   - The UI does not provide real-time updates based on user selections. For example, when selecting the `received` condition based on a number of days, the interface should dynamically adjust the available options based on the user's choice, but this is not yet handled in the current version.

5. **Limited Error Handling**:
   - The current system does not adequately handle errors such as network failures, API rate limits, or edge cases like empty label fields or malformed input, which can result in crashes or unexpected behavior.

6. **Scalability**:
   - As the number of emails grows, the current implementation may not scale well due to repeated API calls and database queries. Future versions should consider optimizing performance and allowing for more efficient batch processing.

---

## Conclusion

While the Mail-Parser project is a useful tool for processing Gmail emails based on user-defined rules, there are several areas that need improvement, including handling edge cases, improving performance with multithreading, and enhancing the user interface for better interaction. However, the current implementation offers a good starting point for rule-based email management and can be expanded in the future with additional features and optimizations.
