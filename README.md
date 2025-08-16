# Task Management System
## Overview
This Task Management System allows Admins, Managers, and Employees to manage tasks efficiently with **role-based access control**, **task approval workflows**, and **status updates**.  

- **Backend:** Python, Flask, SQLAlchemy, MySQL  
- **Frontend:** React.js, Material-UI (MUI)  
- **Authentication:** Session-based login  
- **Database:** MySQL  

---

## Features
- **CRUD** tasks based on user role
- Assign tasks to users dynamically based on role
- Task status updates: `Pending`, `Done`, `Approved`, `Rejected`
- Remarks for task approvals/rejections
- Role-based dashboard filtering
- Modal forms for task editing
- Approval workflows for Manager and Admin





## User Roles
| Role    | Permissions |
|---------|-------------|
| **Admin** | Full control: Create/update/delete users, assign tasks, approve/reject tasks, view all tasks |
| **Manager** | Create/update/delete tasks for Employees, approve/reject Employee tasks, view tasks assigned by Admin |
| **Employee** | View assigned tasks, update status (`Pending` / `Done`) |

---


## Backend
**Structure:**


**Install dependencies and run backend:**
```bash
cd backend
python -m venv venv          # Create virtual environment
venv\Scripts\activate        # Activate (Windows)
pip install -r requirements.txt
flask run
```
## Frontend
```bash
cd frontend
npm install
npm start
```
