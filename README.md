# Overview

As a software developer, I am focused on building applications that combine structured data management with meaningful user interaction. This project was designed to strengthen my understanding of full-stack development concepts, particularly how backend logic, relational data, and dynamic interfaces work together in a web application.

LoreForge is a web-based world-building tool that allows users to create and manage factions and characters, including hierarchical mentorship relationships. The application supports creating, viewing, and deleting entities, while maintaining data integrity through validation rules and relational logic.

The purpose of this software is to explore how complex relationships (such as mentorship hierarchies) can be modeled, validated, and visualized in a web environment using Django.

# Web Pages

## Home Page

- Serves as the main navigation hub.
- Provides quick access to all main features (viewing and creating factions and characters).

## Factions Page

- Displays all factions dynamically from the database.
- Shows each faction’s leader.
- Includes navigation to delete a faction.

## Characters Page

- Displays all characters dynamically.
- Shows role, faction, and mentor relationships.
- Includes options to view mentorship trees and delete characters.

## Add Faction Page

- Form that allows users to create a faction and its leader at the same time.
- Automatically creates a leader character and assigns it to the faction.

## Add Character Page

- Form to create a new character.
- Dynamically filters mentor options based on selected faction.
- Applies validation rules (same faction, no self-mentoring, no loops).

## Delete Character Page

- Confirmation page before deletion.
- Reassigns students to the deleted character’s mentor.
- Handles leader reassignment or faction deletion if necessary.

## Delete Faction Page

- Confirmation page showing all members of the faction.
- Deletes all associated characters before removing the faction.

## Mentorship Tree Page

- Displays a recursive hierarchy of characters.
- Dynamically generated using a tree structure built in Python and rendered with a recursive template.

# Development Environment

**Tools Used**:

- **Visual Studio Code**: Used as the primary IDE for its strong support for web development and extensions that improve productivity.
- **Git and GitHub**: Used for version control, tracking changes, and managing the project repository.

**Programming Language & Libraries:**

- **Python**: Used as the core backend language to handle application logic, data processing, and server-side operations.
- **Django**: Used as the web framework to manage routing, models, forms, and dynamic page rendering.
- **HTML**: Used to structure the web pages and display dynamic content from the backend.
- **CSS**: Used to style the application and improve the visual layout and user experience.

**Execution Instructions:**

To run the application locally:

1. **Navigate to the project folder**:
   ```bash
   cd loreforge-django
   ```
2. **Start the development server**: `python manage.py runserver`
3. **Open your browser and go to**: `http://127.0.0.1:8000/`

This will load the main page of the application.

# Useful Websites

- [Django Documentation](https://docs.djangoproject.com/en/6.0/) - Used for understanding models, views, forms, and overall framework structure.
- [MDN Web Docs](https://developer.mozilla.org/) - Used for HTML and CSS reference and best practices.
- [W3Schools Django Tutorial](https://www.w3schools.com/django/) - Used as a beginner-friendly reference for Django concepts and syntax.
- [Stack Overflow](https://stackoverflow.com) - Used for troubleshooting errors and finding solutions to specific implementation issues.

# Future Work

- Add editing functionality for characters and factions
- Improve mentorship tree visualization with more advanced styling
- Add user authentication and persistent user-specific worlds
