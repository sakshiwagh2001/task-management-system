from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from model import db, User, Task, Position
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@localhost/taskmanagement'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",  
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False    
)


db.init_app(app)


ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

with app.app_context():
    db.create_all()

    if not Position.query.first():
        db.session.add_all([
            Position(role="Admin"),
            Position(role="Manager"),
            Position(role="Employee")
        ])
        db.session.commit()

    admin_position = Position.query.filter_by(role="Admin").first()
    if not User.query.filter_by(email=ADMIN_EMAIL).first():
        admin_user = User(
            name="Admin",
            email=ADMIN_EMAIL,
            password=generate_password_hash(ADMIN_PASSWORD),
            role_id=admin_position.id
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created in DB")




@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')  
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    if not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401


    if user.position.role != role:
        return jsonify({"message": f"Role mismatch. Please login as {user.position.role}"}), 403

    session['user'] = {
        'id': user.id,
        'email': user.email,
        'role': user.position.role
    }

    return jsonify({
        "message": f"{user.position.role} login successful",
        "role": user.position.role,
        "name": user.name,       
        "email": user.email 
    }), 200



@app.route('/logout')
def logout():
    session.pop('user', None)
    return jsonify({"message": "Logged out"}), 200


# ======= User CRUD (Admin Only) =======
@app.route('/users', methods=['POST'])
def create_user():
    if 'user' not in session or session['user']['role'] != 'Admin':
        return jsonify({"message": "Forbidden"}), 403

    data = request.json
    hashed_password = generate_password_hash(data['password'])
    role = Position.query.filter_by(role=data['role']).first()
    if not role:
        return jsonify({"message": "Invalid role"}), 400

    user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password,
        role_id=role.id
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": f"{data['role']} created successfully"}), 201


@app.route('/users', methods=['GET'])
def get_users():
    role = request.args.get('role')  
    if not role:
        return jsonify({"message": "Role is required"}), 400

    users = User.query.join(Position).filter(Position.role == role).all()
    result = [{"id": u.id, "name": u.name} for u in users]
    return jsonify(result), 200


# ======= Task CRUD =======

@app.route('/tasks', methods=['POST'])
def create_task():
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json
    user_id = session['user'].get('id')
    task = Task(
        title=data['title'],
        description=data['description'],
        deadline=datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M:%S'),
        created_by=user_id,
        assigned_to=data['assigned_to']
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Task created successfully"}), 201


@app.route('/my-tasks', methods=['GET'])
def my_tasks():
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user_role = session['user']['role']
    user_id = session['user']['id']

    if user_role == "Manager":
        tasks = (
            Task.query 
            .filter(
                Task.assigned_to == user_id
            )
            .join(User, Task.created_by == User.id)
            .join(Position)
            .filter(Position.role == "Admin")
            .all()
        )

    elif user_role == "Employee":
        tasks = (
            Task.query
            .filter(
                Task.assigned_to == user_id
            )
            .join(User, Task.created_by == User.id)
            .join(Position)
            .filter(Position.role.in_(["Admin", "Manager"]))
            .all()
        )

    else:
        return jsonify({"message": "Forbidden"}), 403

    result = [{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status,
        "remark": t.remark,
        "assigned_to": t.assignee.name if t.assignee else None,
        "assigned_role": t.assignee.position.role if t.assignee else None,
        "created_by": t.creator.name if t.creator else None,
        "creator_role": t.creator.position.role if t.creator else None
    } for t in tasks]

    return jsonify(result), 200




@app.route('/tasks', methods=['GET'])
def get_tasks():
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user_role = session['user']['role']
    user_id = session['user']['id']
    view = request.args.get('view')  


    if view == "my":
        tasks = Task.query.filter_by(assigned_to=user_id).all()

    elif view == "approve":
        if user_role == "Admin":
            tasks = Task.query.filter_by(status="Done").all()
        elif user_role == "Manager":
            tasks = (
                Task.query
                .join(User, Task.assigned_to == User.id)
                .join(Position)
                .filter(Task.status == "Done", Position.role == "Employee")
                .all()
            )
        else:
            tasks = []

 
    else:
        if user_role == "Admin":
            tasks = Task.query.all()
        elif user_role == "Manager":
            tasks = (
                Task.query
                .join(User, Task.assigned_to == User.id)
                .join(Position)
                .filter(Position.role == "Employee")
                .all()
            )
        else:  
            tasks = Task.query.filter_by(assigned_to=user_id).all()

    result = [{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status,
        "remark": t.remark,
        "deadline": t.deadline.strftime('%Y-%m-%d %H:%M:%S') if t.deadline else None,  
        "assigned_to": t.assignee.name if t.assignee else None,
        "assigned_role": t.assignee.position.role if t.assignee else None,
        "created_by": t.creator.name if t.creator else None
    } for t in tasks]

    return jsonify(result), 200



@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = session['user']
    role = user['role']
    user_id = user['id']
    data = request.json

    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    if role == 'Manager' and task.created_by != user_id:
        return jsonify({"message": "Not authorized to edit this task"}), 403

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M:%S') if data.get('deadline') else task.deadline
    task.assigned_to = data.get('assigned_to', task.assigned_to)

    task.status = 'Pending'
    db.session.commit()

    return jsonify({"message": "Task updated successfully"}), 200



@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = session['user']
    role = user['role']
    user_id = user['id']

    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    if role == 'Manager' and task.created_by != user_id:
        return jsonify({"message": "Not authorized to delete this task"}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully"}), 200


@app.route('/tasks/<int:task_id>/approval', methods=['PUT'])
def approve_or_reject_task(task_id):
    if 'user' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = session['user']['id']
    role = session['user']['role']
    data = request.json
    new_status = data.get('status')
    remark = data.get('remark', '')

    if role not in ['Admin', 'Manager']:
        return jsonify({'message': 'You are not allowed to approve/reject tasks'}), 403

    if new_status not in ['Approved', 'Rejected']:
        return jsonify({'message': f'{role} cannot set status to {new_status} here'}), 403

    task = Task.query.get(task_id)
    if not task:
        return jsonify({'message': 'Task not found'}), 404

    assigned_user_role = None
    if task.assignee and task.assignee.position:
        assigned_user_role = task.assignee.position.role

    if role == 'Manager' and assigned_user_role != 'Employee':
        return jsonify({'message': 'Managers can only approve/reject Employee tasks'}), 403

    task.status = new_status
    task.remark = remark
    db.session.commit()
    return jsonify({'message': f'Task {new_status} successfully'})



@app.route('/tasks/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    if 'user' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = session['user']['id']
    role = session['user']['role']
    data = request.json
    new_status = data.get('status')

    allowed_statuses = {
        'Employee': ['Pending', 'Done'],
        'Manager': ['Pending', 'Done']
    }

    if role not in allowed_statuses or new_status not in allowed_statuses[role]:
        return jsonify({'message': f'{role} cannot set status to {new_status}'}), 403

    task = Task.query.get(task_id)
    if not task:
        return jsonify({'message': 'Task not found'}), 404

    if task.assigned_to != user_id:
        return jsonify({'message': 'Not authorized to update this task'}), 403

    task.status = new_status
    db.session.commit()
    return jsonify({'message': 'Status updated successfully'}), 200




if __name__ == '__main__':
    app.run(debug=True)
