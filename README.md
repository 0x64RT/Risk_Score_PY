# Risk_Score_PY

Fair-Play Analyzer User Guide 
1. Application Startup
Install requierements.
Make sure to have some recent python version compatible with pygame.

2. Terms and Conditions
Display of Terms:
Before accessing the main features, the terms and conditions will be displayed.
Terms wont appear if accept_terms.txt is on the same directory has main.py.

Confirmation:
Type “accept” in the designated field and press Enter to continue. This action creates a confirmation file to prevent the terms from being shown again in future sessions.

3. Main Interface
After completing the login and accepting the terms, the main interface opens, organized into different modules accessible via the top menu:

a) Top Menu
Available Options:
The top menu displays the following sections:

1: Risk Score
2: Comparison
3: Trend
4: Elo Change
5: Range
6: Evolution
Navigation:
You can switch between modules by using the number keys. (Always make sure to do this whe you are not writing on the user boxes).
Important: Pressing the Escape key anywhere in the application will automatically redirect you to tab 1 (Risk Score).

b) Module 1: Risk Score
Objective:
Provides an evaluation of the user's performance in chess games across different time controls (rapid, bullet, blitz).

Usage:

By default, the Risk Score is calculated for the most recent month.
Enter the username in the text field at the bottom by clicking on the corresponding rectangle.
Press the button to start the analysis.
The user's profile (if available) will be displayed along with visual indicators representing the score for each game type.
c) Module 2: Comparison
Objective:
Visually compares certain accuracy indicators between the user and their opponents.

Usage:
When this module is selected, a bar chart is generated to show the comparison.

d) Module 3: Trend
Objective:
Displays the monthly evolution of specific performance indicators, highlighting significant changes.

Usage:
A graph showing trends over time is displayed, allowing you to visually identify important variations.

e) Module 4: Elo Change
Objective:
Visualizes the month-by-month evolution of the user's Elo rating.

Usage:
A graph is generated that clearly shows how the rating has changed, without disclosing internal calculation details.

f) Module 5: Range
Objective:
Provides an evaluation (Risk Score) for a specific date range. (A calendar will show, where you will need to select the personalized dates, and the click enter).

Usage:

Although the default calculation uses the most recent month, this option allows you to define a date range using an interactive calendar.
Once the range is confirmed, the corresponding Risk Score is calculated and displayed.
g) Module 6: Evolution
Objective:
Analyzes the weekly evolution of the performance evaluation over a defined period.

Usage:

Enter the username and the number of weeks to analyze in the corresponding fields.
Press the button (arrow icon) to initiate the analysis, and a graph showing the weekly evolution will be displayed.
4. Security Considerations and Requirements
Security:
For security reasons, we are not comfortable publicly sharing the internal methods and algorithms used in the analyses at this time.

Minimum Requirements:
A monitor with at least Full HD resolution is recommended to ensure proper display of graphs and animations.

Manual Game Type Selection:
In some menus, you can manually choose which type of game to analyze (e.g., rapid, bullet, or blitz) using the horizontal arrow keys.
Note: To change the game type using the arrow keys, ensure that you are not typing in the user input field.

5. Upcoming Updates
Move Time Analysis Mode:
A new mode for analyzing move times using PGN files will be added soon. This feature will analyze the time taken per move, identify consistent patterns, and generate detailed graphs with statistics such as average time, deviation, and coefficient of variation.

Bulk Risk Score Analysis:
Another upcoming update is the introduction of a bulk Risk Score analysis mode, ideal for analyzing many users in a very short time. This mode, will process multiple analyses simultaneously, optimizing processing time when evaluating a large number of users.

6. General Interface and Navigation
Animations and Visuals:
During processing, animations (such as moving chessboards or particle effects) are shown to indicate that analysis is in progress. Once complete, the corresponding graphs are displayed.

Input Fields:
Text fields are highlighted with a border , facilitating data entry.

Interaction:
Navigation is intuitive via mouse and keyboard, allowing you to switch between modules and access various features easily.
Remember, pressing the Escape key anywhere in the application will return you to tab 1 (Risk Score).

7. Final Considerations
Compatibility and Data:
The application is designed to run on almost any windows, mac and linux distros. Public data from the Chess.com API is used for the analyses, and only minimal data is stored locally.

Responsible Use:
This tool is intended solely to provide informational insights. Under no circumstances should the results be considered sufficient evidence of cheating. The developer is not responsible for any misuse of this information.
Note: These analyses are intended for 95% of regular players; it is normal that when analyzing many grandmasters, or other excellent players extreme percentages appear that do not reflect typical performance.
Note: Please keep forum discussions limited to suggestions and improvement ideas. For any technical issues or potential bugs, contact me at agostjordi@gmail.com .
Final Note: This program has been tested by over 5 users for several weeks. Although no major bugs have been detected, there might still be minor issues present.

Enjoy!
With love from Spain!
