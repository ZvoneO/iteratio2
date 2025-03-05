

#Role Hierarchy:
Admin → has all permissions of Manager, Project Manager, and Consultant
Manager → has all permissions of Project Manager and Consultant
Project Manager → has all permissions of Consultant
Consultant → has the most limited access


#User Stories Implemented in Admin Dashboard
#User Creation
As an admin, I want to create a new user by providing their username, email, first name, last name, password, and role so that I can onboard new team members efficiently.
##Acceptance Criteria:
The form must require a username, email, password, and role.
The username must be between 3 and 20 characters.
The email must be valid and unique.
The password must be at least 6 characters long.
Upon successful submission, the user should be created and a confirmation message displayed.
#User Editing
As an admin, I want to edit an existing user's details, including their username, email, first name, last name, and role so that I can keep user information up to date.
##Acceptance Criteria:
The form must pre-fill the existing user's information.
The username, email, and role must be required fields.
The username must be between 3 and 20 characters.
The email must be valid.
Upon successful submission, the user's details should be updated and a confirmation message displayed.
#Role Assignment
As an admin, I want to assign a role to a user (User, Manager, Project Manager, Administrator) so that I can control their access level within the application.
##Acceptance Criteria:
The role selection must be a dropdown with predefined choices.
The selected role must be saved when creating or editing a user.
#Validation Feedback
As an admin, I want to receive validation feedback when I submit the user creation or editing forms with invalid data so that I can correct any mistakes.
##Acceptance Criteria:
The form must display error messages for invalid fields (e.g., missing required fields, invalid email format).
The form must not submit until all validation criteria are met.
#User List Management (Implied)
As an admin, I want to view a list of all users in the system so that I can manage their accounts effectively.
##Acceptance Criteria:
The admin dashboard should display a table of users with their details (username, email, role).
Each user should have options to edit or delete their account.

#Admin User Stories
As an Admin, I want to upload csv lists of Clients to database.
As an Admin, I want to upload JSON files to populate database with initial set of data.
As an Admin, I want to view an overview dashboard so that I can see all active projects, clients, and resources.
As an Admin, I want to create new users and assign them to roles.
As an Admin, I want to invite new users to the system so that they can collaborate on projects.
As an Admin, I want to delete projects so that I can remove outdated or incorrect records.
As an Admin, I want to generate reports on resource allocation so that I can make data-driven decisions.
As an Admin, I want to remove discontinued products so that outdated items are not used.

#Manager User Stories
As a Manager, I want to view an overview dashboard so that I can see all active projects, clients, and resources.
As a Manager, I want to see detailed overview of Projects, Clients and Consultants.
As a Manager, I want to create a new project template so that I can use it in multiple projects. 
#Project Template Creation
As a manager, I want to create a new project template using all project relevant fields and phases, so that I can standardize project setups for future use.
#Acceptance Criteria:
The form must require a template name and at least one project phase.
The description is optional.
Upon successful submission, the project template should be created and a confirmation message displayed.
#Project Template Management
As a manager, I want to view a list of all project templates so that I can manage them effectively.
#Acceptance Criteria:
The project templates should be displayed in a table format with their details (name, description).
Each template should have options to edit or delete. 
#Project Template Editing
As a manager, I want to edit an existing project template's details so that I can keep the information up to date.
#Acceptance Criteria:
The form must pre-fill the existing project template's information.
Upon successful submission, the project template should be updated and a confirmation message displayed.
#Project Template Deletion
As a manager, I want to delete a project template that is no longer needed so that I can keep the project list clean and relevant.
#Acceptance Criteria:
The system should prompt for confirmation before deletion.
Upon confirmation, the project template should be removed from the database, and a success message should be displayed.
#Project Template Relationships
As a manager, I want to associate project templates with specific clients and managers so that I can track which templates are used for which projects.
#Acceptance Criteria:
The project template should have a dropdown to select a client and a manager.
The relationships should be reflected in the database, allowing for easy retrieval of templates by client or manager.
#Project Phases and Products Management in Project templates 
As a manager, I want to define phases and products/services associated with each project template so that I can outline the project workflow and deliverables.
#Acceptance Criteria:
The project template should allow adding, editing, and removing phases and products/services.
The relationships should be maintained in the database, ensuring that phases and products are linked to their respective templates.

As a Manager, I want to create a new project based on project template or from scratch.
As a Manager, I want to manage the product catalog so that I can update available products for projects.
As a Manager, I want to add, edit, and remove clients so that I can manage customer information efficiently.
As a Manager, I want to assign projects to specific clients so that they can track their resources.
As a Manager, I want to assign one or more Consultants to project using following criteria:
- Expertise level (1-5) for phases based on Project phases 
- Utilization data in planned period 
- Availability based on planned data (planned activities)
- Priority or importance of a project
- Geographic location (Client and Consultant located in same country, same town, or different) giving a rate of 1 to 3 stars

As a Manager, I want to create a project template so that I can standardize project structures for new projects.
As a Manager, I want to update product details so that the catalog remains accurate.
As a Manager, I want to see a history of past projects so that I can reference completed work.

#Project Management User Stories
As a Project Manager, I want to add, edit, and remove Consultants to a project so that I can allocate work efficiently.
As a Project Manager, I want to set deadlines for a project so that the team has a clear timeline.
As a Project Manager, I want to see clear overview of Consultants and their engagement so I can plan projects and engagement.
As a Project Manager, I want to update a project’s status so that stakeholders know the current progress.
As a Project Manager, I want to manage tasks on project level with clear assignment to other roles and planned date. 
As a Project Manager, I want to manage tasks on a project level with clear assignment to other users and a planned date, so that I can track progress efficiently. 
- Each task should be assigned to a specific user. 
- Tasks should have a planned completion date. 
- Completed tasks should have a checkbox to mark them as "done."

#Consultant User Stories
As a Consultant, I want to view my assigned projects so that I can track progress.
As a Consultant, I want to see calendar overview with planned activities and tasks. 
As a Consultant, I want to browse the product catalog so that I can see available products for my projects.
As a Consultant, I want to filter and search products so that I can find relevant items quickly.

#Authentication & Security User Stories
As a User, I want to log in securely so that I can access my data.
As a User, I want to reset my password so that I can recover my account.
As an Admin, I want to disable user accounts so that I can prevent unauthorized access.

#User Stories for later implementation (only comments/placeholders to be implement in code)
As a Project Manager, I want to attach documents to a project so that all relevant files are in one place.
As a User, I want to receive email notifications for important updates so that I stay informed.
As an Admin, I want to configure system settings so that I can customize the application.
