import json
import uuid
from datetime import datetime
class UserBase:
    """
    Base interface implementation for API's to manage users.
    """

    # create a user
    def create_user(self, request: str) -> str:
        
        """
        :param request: A json string with the user details
        {
          "name" : "<user_name>",
          "display_name" : "<display name>"
        }
        :return: A json string with the response {"id" : "<user_id>"}

        Constraint:
            * user name must be unique
            * name can be max 64 characters
            * display name can be max 64 characters
        """
        data = json.loads(request)
        if len(data["name"]) > 64 or len(data["display_name"]) > 64:
            return json.dumps({"error" : "Name or Display_name exceeds 64 charchters"})
        
        try:
            with open("db/user_base.json","r")as f:
                content = f.read().strip()
                if content:
                  users = json.loads(content)
                else:
                    users = []
        except FileNotFoundError:
            users = []

        for user in users:
            if user["name"] == data["name"]:
                return json.dumps({"errors":"Username already exists"})
            
        user_id = str(uuid.uuid4())

        new_user ={
            "id" : user_id,
            "name" : data["name"],
            "display_name" : data["display_name"],
            "creation_time" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description" : data["description"]
        }

        users.append(new_user)

        with open("db/user_base.json","w") as f:
            json.dump(users,f,indent=4)

        return json.dumps({"id":user_id})
        
    

    # list all users
    def list_users(self) -> str:
        """
        :return: A json list with the response
        [
          {
            "name" : "<user_name>",
            "display_name" : "<display name>",
            "creation_time" : "<some date:time format>"
          }
        ]
        """
        try:
            with open("db/user_base.json","r") as f:
                content = f.read().strip()
                users = json.loads(content) if content else []
        except FileNotFoundError:
            users = []

        user_list =[
            {
                "name" : user.get("name",""),
                "display_name" : user.get("display_name",""),
                "creation_time" : user.get("creation_time","")
            }
            for user in users
        ]

        return json.dumps(user_list,indent=4)
        

    # describe user
    def describe_user(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "id" : "<user_id>"
        }

        :return: A json string with the response

        {
          "name" : "<user_name>",
          "description" : "<some description>",
          "creation_time" : "<some date:time format>"
        }

        """
        try:
            request_data = json.loads(request)
            user_id = request_data.get("id")

            if not user_id:
                return json.dumps({"error": "Missing user id"})
            
            with open("db/user_base.json" ,"r") as f:
                content = f.read().strip()
                users = json.loads(content) if content else []
            
            for user in users:
                if user["id"] == user_id:
                    return json.dumps(
                        {
                        "name" : user.get("name",""),
                        "description" : user.get("description",""),
                        "creation_time": user.get("creation_time", "No creation time found")

                    }
                    ,indent=4)
            return json.dumps({"error":"User not found"})
        
        except FileNotFoundError:
            return json.dumps({"error":"User base file not found"})
            

    # update user
    def update_user(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "id" : "<user_id>",
          "user" : {
            "name" : "<user_name>",
            "display_name" : "<display name>"
          }
        }

        :return:

        Constraint:
            * user name cannot be updated
            * name can be max 64 characters
            * display name can be max 128 characters
        """
        try:
            request_data = json.loads(request)
            user_id = request_data.get("id")
            updated_user = request_data.get("user",{})

            if not user_id:
                return json.dumps({"error": "Missing user id"})
            
            with open("db/user_base.json" ,"r") as f:
                content = f.read().strip()
                users = json.loads(content) if content else []
            
            user_found = False
            for user in users:
                if user["id"] == user_id:
                    user_found = True

                    if "name" in updated_user and updated_user["name"] != user["name"]:
                        return json.dumps({"error": "User cannot be updated"})
                    
                    if len(user["name"]) > 64:
                        return json.dumps({"error": "User name exceed 64 characters"})
                    if "display_name" in updated_user and len(updated_user["display_name"]) > 128:
                        return json.dumps({"error": "Display name exceed 128 characters"})
                    
                    #Upadte User name
                    if "display_name" in updated_user:
                        user["display_name"] = updated_user["display_name"]
                    break
                
            if not user_found:
              return json.dumps({"error": "User not found"})
            
            with open("db/user_base.json","w") as f:
                json.dump(users,f,indent=4)

            return json.dumps({"message": "User updated successfully"})
        
        except FileNotFoundError:
            return json.dumps({"error": "User base file not found"})




                

    def get_user_teams(self, request: str) -> str:
        """
        :param request:
        {
          "id" : "<user_id>"
        }

        :return: A json list with the response.
        [
          {
            "name" : "<team_name>",
            "description" : "<some description>",
            "creation_time" : "<some date:time format>"
          }
        ]
        """
        try:
            request_data = json.loads(request)
            user_id = request_data.get("id")

            if not user_id:
                return json.dumps({"error": "Missing user id"})
            
            with open("db/team_base.json" ,"r") as f:
                content = f.read().strip()
                teams = json.loads(content) if content else []

            user_team =[]
            for team in teams:
                if team.get("admin") == user_id:
                    user_team.append(
                        {
                        "team_name" : team.get("team_name",""),
                        "description" : team.get("description",""),
                        "creation_time": team.get("creation_time", "")   
                        }
                    )
            return json.dumps(user_team,indent=4)
        
        except FileNotFoundError:
            return json.dumps({"error": "Team base file not found"})
