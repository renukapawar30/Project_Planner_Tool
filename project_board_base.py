import json
import uuid
from datetime import datetime
import os
class ProjectBoardBase:
    """
    A project board is a unit of delivery for a project. Each board will have a set of tasks assigned to a user.
    """

    def create_board(self, request: str):
        """
        :param request: A json string with the board details.
        {
            "name" : "<board_name>",
            "description" : "<description>",
            "team_id" : "<team id>",
            "creation_time" : "<date:time when board was created>"
        }
        :return: A json string with the response {"id" : "<board_id>"}

        Constraint:
         * board name must be unique for a team
         * board name can be max 64 characters
         * description can be max 128 characters
        """
        data = json.loads(request)
        
        if len(data["board_name"]) > 64:
            return json.dumps({"error":"Board name exceed 64 character"})
        
        if len(data["board_description"]) > 128:
            return json.dumps({"error":"Board description exceed 64 character"})

        
        team_id = data.get("team_id")
        if not team_id:
            return json.dumps({"error":"Missing team id"})
        
        # Load and  valiadte team id

        try:
            with open("db/team_base.json","r") as f:
                team_data = f.read().strip()
                teams = json.loads(team_data) if team_data else []

        except FileNotFoundError:
            return json.dumps({"error":"Team Base not found"})
        

        
        if not any(team.get("id") == team_id for team in teams):
            return json.dumps({"error":"Team id does not exist"})
        
        try:
            with open("db/project_board_base.json","r")as f:
                content = f.read().strip()
                if content:
                    boards = json.loads(content)
                else:
                    boards = []
        except FileNotFoundError:
            boards = []

        for board in boards:
            if board["board_name"] == data["board_name"]:
                return json.dumps({"error":"Board Name already exists"})
            
        board_id = str(uuid.uuid4())

        new_board={
            "id" : board_id,
            "board_name" : data["board_name"],
            "board_description" : data["board_description"],
            "team_id" : team_id,
            "creation_time" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            
        }
        boards.append(new_board)

        with open("db/project_board_base.json","w") as f:
            json.dump(boards,f,indent=4)

        return json.dumps({"id":board_id})

  
    # close a board
    def close_board(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "id" : "<board_id>"
        }

        :return:

        Constraint:
          * Set the board status to CLOSED and record the end_time date:time
          * You can only close boards with all tasks marked as COMPLETE
        """
        data = json.loads(request)
        board_id = data.get("id")

        if not board_id:
          return json.dumps({"error": "Board ID is required"})

        try:
          with open("db/project_board_base.json", "r") as f:
            boards = json.load(f)
        except FileNotFoundError:
          return json.dumps({"error": "Board database not found"})

        board_found = False
        for board in boards:
          if board["id"] == board_id:
            board_found = True

            tasks = board.get("tasks", [])

            # Check if all tasks are COMPLETE
            incomplete_tasks = [t for t in tasks if t.get("status") != "COMPLETE"]
            if incomplete_tasks:
                return json.dumps({"error": "All tasks must be COMPLETE to close the board"})

            board["status"] = "CLOSED"
            board["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            break

          if not board_found:
            return json.dumps({"error": "Board not found"})

    # Save back to file
          with open("db/project_board_base.json", "w") as f:
            json.dump(boards, f, indent=4)

          return json.dumps({"message": "Board closed successfully"})

    

    # add task to board
    def add_task(self, request: str) -> str:
        """
        :param request: A json string with the task details. Task is assigned to a user_id who works on the task
        {
            "title" : "<board_name>",
            "description" : "<description>",
            "user_id" : "<team id>"
            "creation_time" : "<date:time when task was created>"
        }
        :return: A json string with the response {"id" : "<task_id>"}

        Constraint:
         * task title must be unique for a board
         * title name can be max 64 characters
         * description can be max 128 characters

        Constraints:
        * Can only add task to an OPEN board
        """
       
        data = json.loads(request)
    
        try:
          with open("db/team_base.json", "r") as f:
              team_data = f.read().strip()
              teams = json.loads(team_data) if team_data else []
        except FileNotFoundError:
          return json.dumps({"error": "TeamBase not found"})

        team_id = data.get("user_id")
        if not any(team.get("id") == team_id for team in teams):
          return json.dumps({"error": "Team id does not exist"})

        if len(data["title"]) > 64:
          return json.dumps({"error": "Title exceeds 64 characters"})

        if len(data["description"]) > 128:
          return json.dumps({"error": "Description exceeds 128 characters"})

        board_id = data.get("id")
        if not board_id:
          return json.dumps({"error": "Missing board id"})

        try:
          with open("db/project_board_base.json", "r") as f:
            content = f.read().strip()
            boards = json.loads(content) if content else []
        except FileNotFoundError:
          return json.dumps({"error": "Board database not found"})

        board = next((b for b in boards if b["id"] == board_id), None)
        if not board:
          return json.dumps({"error": "Board not found"})

        if board.get("status") == "CLOSED":
          return json.dumps({"error": "Board already closed"})

        tasks = board.get("tasks", [])

        if any(t["title"].lower() == data["title"].lower() for t in tasks):
          return json.dumps({"error": "Task title already exists in board"})

        task_id = str(uuid.uuid4())
        new_task = {
                "id": task_id,
                "title": data["title"],
                "description": data["description"],
                "user_id": team_id,
                "status": "IN PROGRESS",
                "creation_time": data.get("creation_time") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              }

        tasks.append(new_task)
        board["tasks"] = tasks

        with open("db/project_board_base.json", "w") as f:
          json.dump(boards, f, indent=4)

        return json.dumps({"id": task_id})


    # update the status of a task
    def update_task_status(self, request: str):
        """
        :param request: A json string with the user details
        {
            "id" : "<task_id>",
            "status" : "OPEN | IN_PROGRESS | COMPLETE"
        }
        """
        
    
        data = json.loads(request)
    
        task_id = data.get("id")
        new_status = data.get("status")

        if not task_id or not new_status:
          return json.dumps({"error": "Missing task id or status"})

        if new_status not in ["OPEN", "IN_PROGRESS", "COMPLETE"]:
          return json.dumps({"error": "Invalid status value"})

        try:
          with open("db/project_board_base.json", "r") as f:
            boards_data = f.read().strip()
            boards = json.loads(boards_data) if boards_data else []
        except FileNotFoundError:
          return json.dumps({"error": "Board database not found"})

    # Look for the task in all boards
        task_found = False
        for board in boards:
          tasks = board.get("tasks", [])
          for task in tasks:
            if task["id"] == task_id:
                task["status"] = new_status
                task["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                task_found = True
                break
          if task_found:
            break

        if not task_found:
          return json.dumps({"error": "Task not found"})

    # Save the updated data back
        with open("db/project_board_base.json", "w") as f:
          json.dump(boards, f, indent=4)

        return json.dumps({"message": "Task status updated successfully"})



    # list all open boards for a team
    def list_boards(self, request: str) -> str:
        """
        :param request: A json string with the team identifier
        {
          "id" : "<team_id>"
        }

        :return:
        [
          {
            "id" : "<board_id>",
            "name" : "<board_name>"
          }
        ]
        """
        
        data = json.loads(request)

        team_id = data.get("id")
        if not team_id:
          return json.dumps({"error": "Missing team id"})

    # Validate team exists
        try:

          with open("db/team_base.json", "r") as f:
            content = f.read().strip()
            teams = json.loads(content) if content else []
        except FileNotFoundError:
          return json.dumps({"error": "TeamBase not found"})

        if not any(team.get("id") == team_id for team in teams):
          return json.dumps({"error": "Team ID does not exist"})
        # Read boards
        try:
          with open("db/project_board_base.json", "r") as f:
            content = f.read().strip()
            boards = json.loads(content) if content else []
        except FileNotFoundError:
          return json.dumps({"error": "Board database not found"})

    # Find boards with at least one task assigned to the team
        result = []
        for board in boards:
          for task in board.get("tasks", []):

            if task.get("user_id") == team_id:
                result.append({
                    "id": board["id"],
                    "board_name": board["board_name"]
                })
                break  # No need to check other tasks in this board

        return json.dumps(result)

    def export_board(self, request: str) -> str:
        """
        Export a board in the out folder. The output will be a txt file.
        We want you to be creative. Output a presentable view of the board and its tasks with the available data.
        :param request:
        {
          "id" : "<board_id>"
        }
        :return:
        {
          "out_file" : "<name of the file created>"
        }
        """
        data = json.loads(request)
        board_id = data.get("id")
        if not board_id:
          return json.dumps({"error": "Missing board id"})

    # Load boards
        try:
          with open("db/project_board_base.json", "r") as f:
            content = f.read().strip()
            boards = json.loads(content) if content else []
        except FileNotFoundError:
          return json.dumps({"error": "Board database not found"})

    # Find the board
        board = next((b for b in boards if b["id"] == board_id), None)
        if not board:
          return json.dumps({"error": "Board not found"})

        board_name = board.get("name", "Unnamed Board")
        board_status = board.get("status", "UNKNOWN")
        tasks = board.get("tasks", [])

        # Prepare content
        output_lines = [
          f"BOARD NAME     : {board_name}",
          f"BOARD ID       : {board_id}",
          f"STATUS         : {board_status}",
          f"TASK COUNT     : {len(tasks)}",
          f"EXPORT TIME    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
          "-" * 60
        ]

        if tasks:
          for idx, task in enumerate(tasks, start=1):
            output_lines.append(f"TASK {idx}")
            output_lines.append(f"  ID          : {task.get('id')}")
            output_lines.append(f"  Title       : {task.get('title')}")
            output_lines.append(f"  Description : {task.get('description', '')}")
            output_lines.append(f"  Assigned To : {task.get('user_id')}")
            output_lines.append(f"  Status      : {task.get('status')}")
            output_lines.append(f"  Created At  : {task.get('creation_time')}")
            output_lines.append("-" * 60)
        else:
          output_lines.append("No tasks available in this board.")

    # Ensure output folder exists
        os.makedirs("out", exist_ok=True)

    # Create file name
        safe_board_name = "".join(c if c.isalnum() else "_" for c in board_name)
        filename = f"{safe_board_name}_{board_id}.txt"
        filepath = os.path.join("out", filename)

    # Write to file
        with open(filepath, "w") as f:
          f.write("\n".join(output_lines))

        return json.dumps({"out_file": filename})
