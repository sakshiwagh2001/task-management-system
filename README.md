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


User Roles

Admin

Full access to all modules.

Can create/update/delete users.

Can create/update/delete/assign tasks.

Can view all tasks and approve/reject tasks submitted by Managers.

Manager

Can create/update/delete tasks assigned to Employees.

Can view tasks created by Admin.

Can approve/reject tasks submitted by Employees.

Employee

Can view tasks assigned to them by Admin or Manager.

Can update task status (Pending, Done).
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
cd frontend
npm install
npm start
