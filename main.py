from user_base import UserBase
from team_base import TeamBase
from project_board_base import ProjectBoardBase
import json
from datetime import datetime

# Initialize APIs
user_api = UserBase()
team_api = TeamBase()
project_board_api = ProjectBoardBase()


# ------------------- Create a User -------------------
request_data = json.dumps({
    "name": "renuka123",
    "display_name": "Renuka Pawar",
    "description": "Backend Developer"
})
response = user_api.create_user(request_data)
print("Create User Response")
print(response)

request_data1 = json.dumps({
    "name": "abc123",
    "display_name": "Alphabet",
    "description": "Backend Developer SDE"
})
response1 = user_api.create_user(request_data1)
print("Create 2nd User Response")
print(response1)

# DEBUG: Check if response contains 'id'
try:
    user_id1 = json.loads(response).get("id")
    user_id2 = json.loads(response1).get("id")

    print(f"User ID 1: {user_id1} {type(user_id1)}")
    print(f"User ID 2: {user_id2} {type(user_id2)}")
except json.JSONDecodeError as e:
    print("Failed to decode JSON from response:", e)
    print("Response 1:", response)
    print("Response 2:", response1)



# ------------------- List Users -------------------
print("\nList of Users")
print(user_api.list_users())

# ------------------- Describe User -------------------
print("\nDescription of User")
with open("db/user_base.json", "r") as f:
    users = json.load(f)
    user_id = users[0]["id"]  # Fetch the first user's ID dynamically

request = json.dumps({
    "id": user_id
})
print(user_api.describe_user(request))

# ------------------- Update User -------------------
print("\nUpdated User")
update_request = json.dumps({
    "id": user_id,
    "user": {
        "name": "renuka123",  # name must remain the same
        "display_name": "Renuka Pawar Updated"
    }
})
print(user_api.update_user(update_request))

# ------------------- Get User Team -------------------
print("\nGet User Team")
get_user_team_request = json.dumps({
    "id": user_id
})
print(user_api.get_user_teams(get_user_team_request))


# ------------------- Create Team -------------------
print("\nCreating Team")
team_request = json.dumps({
    "team_name": "Backend Team",
    "team_description": "Handles API's",
    "admin": user_id  # Using the same user as admin
})
team_response = team_api.create_team(team_request)
print("Team Created:", team_response)



# ------------------- List Team -------------------
print("\nList of Team")
print(team_api.list_teams())

# ------------------- Describe Team -------------------
print("\nDescription of Team")
with open("db/team_base.json", "r") as f:
    teams = json.load(f)
    team_id = teams[0]["id"]  # Fetch the first team's ID dynamically

request = json.dumps({
    "id": team_id
})
print(team_api.describe_team(request))

# ------------------- Update Team -------------------
print("\nUpdated Team")
update_request = json.dumps({
    "id": team_id,
    "user": {
        "team_name": "Backend Team",  # name must remain the same
        "team_description": "Handles API's",
        "admin" : user_id
    }
})
print(team_api.update_team(update_request))

# ------------------- Add Users to team -------------------
print("\nAdd Users to team")
add_user_team_request = json.dumps({
    "id": team_id,
    "users" : [user_id,user_id2]
})
print(team_api.add_users_to_team(add_user_team_request))

# ------------------- Remove Users from team -------------------
print("\nRemove Users from team")
remove_user_team_request = json.dumps({
    "id": team_id,
    "users": [user_id2]  # Remove 2nd user from team
})
print(team_api.remove_users_from_team(remove_user_team_request))

# ------------------- List Users in Team -------------------

list_user_team_request = json.dumps({"id": team_id})
print("List Users in Team")
print(team_api.list_team_users(list_user_team_request))

# ------------------- Create Board -------------------
print("Create Board")
request_data = json.dumps({
    "board_name": "Backend Board",
    "board_description": "Tasks related to product API's",
    "team_id": team_id,
})
print(project_board_api.create_board(request_data))



# ------------------- Closed(status) Board -------------------
with open("db/project_board_base.json", "r") as f:
    boards = json.load(f)
    board_id = boards[0]["id"]

print("Closed(status) Board")
request_data = json.dumps({
    "id": board_id
})
print(project_board_api.close_board(request_data))

# ------------------- Add task -------------------
with open("db/project_board_base.json", "r") as f:
    tasks = json.load(f)
    task_id = tasks[0]["id"]

print("Add task")
request_data = json.dumps({
    "id": task_id,
    "title": "Fix User Login API",
    "description": "Ensure proper token validation",
    "user_id": team_id,
    "creation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
})
print(project_board_api.add_task(request_data))
# ------------------- Update task -------------------
print("Update task")
request_data = json.dumps({
    "id": task_id,
    "status": "COMPLETE"
})
print(project_board_api.update_task_status(request_data))

# ------------------- List Board -------------------
print("List Board")
request = json.dumps({
    "id": team_id
})
print(project_board_api.list_boards(request))

# Step 1: Read board_id from the existing board database
with open("db/project_board_base.json", "r") as f:
    boards = json.load(f)
    if not boards:
        print("No boards found.")
        exit()
    board_id = boards[0]["id"]  # Or select dynamically

# Step 2: Prepare request JSON
request_data = json.dumps({
    "id": board_id
})

# Step 3: Call export_board method
response = project_board_api.export_board(request_data)

# Step 4: Print output
print("Export Board Response:")
print(response)

