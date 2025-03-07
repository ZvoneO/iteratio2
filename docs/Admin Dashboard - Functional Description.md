# Functional Description for Admin Dashboard

## Overview
The Admin Dashboard provides a centralized interface for managing users, projects, clients, and settings within the Resource Planning Application. It is designed for users with administrative privileges, such as Admins and Managers.

## Key Components

### 1. Dashboard Overview
- **Purpose**: Display key metrics and statistics related to projects, clients, users, and consultants.
- **Features**:
  - Visual representation of project counts, client counts, user counts, and consultant counts.
  - Role-based content display, where different roles see different metrics.

### 2. User Management
- **Purpose**: Manage user accounts and roles within the application.
- **Features**:
  - **View Users**: List all users with options to search, filter, and paginate.
  - **Create User**: Form to add new users, including fields for username, email, password, first name, last name, and roles.
  - **Edit User**: Modify existing user details and roles.
  - **Delete User**: Remove users from the system with confirmation prompts.

### 3. Project Management
- **Purpose**: Manage projects within the application.
- **Features**:
  - **View Projects**: List all projects with details and statuses.
  - **Create Project**: Form to add new projects, including fields for project name, description, and assigned users.
  - **Edit Project**: Modify existing project details.
  - **Delete Project**: Remove projects from the system with confirmation prompts.

### 4. Client Management
- **Purpose**: Manage client accounts associated with projects.
- **Features**:
  - **View Clients**: List all clients with details and associated projects.
  - **Create Client**: Form to add new clients, including fields for client name and contact information.
  - **Edit Client**: Modify existing client details.
  - **Delete Client**: Remove clients from the system with confirmation prompts.

### 5. Settings Management
- **Purpose**: Manage application settings and dropdown values.
- **Features**:
  - **JSON Settings**: View and edit application settings stored in a JSON file.
  - **Database Lists**: Manage lists used throughout the application, including creating, viewing, and deleting lists.

## User Roles and Permissions
- **Admin**: Full access to all functionalities, including user management, project management, client management, and settings.
- **Manager**: Access to project management and client management, with limited user management capabilities.
- **Consultant**: Limited access, primarily to view their assigned projects and clients.

## Conclusion
The Admin Dashboard is a critical component of the Resource Planning Application, providing administrators with the tools needed to manage users, projects, clients, and application settings effectively. The design emphasizes usability and efficiency, ensuring that administrators can perform their tasks with minimal friction.
