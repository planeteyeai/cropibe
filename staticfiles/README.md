# Farm Management System - Test UI

This is a simple testing interface for the Farm Management System API. It provides a user-friendly way to interact with all the API endpoints.

## Features

- User authentication
- User management (create, view, edit, delete)
- Task management (create, view, edit, delete)
- Equipment management (create, view, edit, delete)
- Booking management (create, view, edit, delete)

## Setup

1. Make sure the Django backend server is running:
   ```bash
   python manage.py runserver
   ```

2. Open the `index.html` file in a web browser.

## Usage

1. **Login**
   - Enter your username and password
   - Click the "Login" button
   - Upon successful login, you'll be redirected to the Users section

2. **Navigation**
   - Use the navigation bar at the top to switch between different sections
   - Each section displays a table of items with options to create, edit, and delete

3. **Creating Items**
   - Click the "Create New" button in each section
   - Fill in the required information in the modal form
   - Click "Create" to save

4. **Editing Items**
   - Click the "Edit" button next to any item
   - Modify the information in the form
   - Click "Save" to update

5. **Deleting Items**
   - Click the "Delete" button next to any item
   - Confirm the deletion in the popup dialog

## API Endpoints

The UI interacts with the following API endpoints:

- Users: `/api/users/`
- Tasks: `/api/tasks/`
- Equipment: `/api/equipment/`
- Bookings: `/api/bookings/`

## Notes

- The UI requires a running Django backend server
- Make sure CORS is properly configured in the Django settings
- The authentication token is stored in localStorage
- All API requests include the authentication token in the Authorization header 