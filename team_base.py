import json
import uuid
from datetime import datetime
class TeamBase:
    """
    Base interface implementation for API's to manage teams.
    For simplicity a single team manages a single project. And there is a separate team per project.
    Users can be
    """

    # create a team
    def create_team(self, request: str) -> str:
        """
        :param request: A json string with the team details
        {
          "name" : "<team_name>",
          "description" : "<some description>",
          "admin": "<id of a user>"
        }
        :return: A json string with the response {"id" : "<team_id>"}

        Constraint:
            * Team name must be unique
            * Name can be max 64 characters
            * Description can be max 128 characters
        """
        
        data = json.loads(request)
        if len(data["team_name"]) > 64:
            return json.dumps({"error":"Team name exceed 64 character"})
        
        if len(data["team_description"]) > 128:
            return json.dumps({"error":"Team description exceed 64 character"})
        
        # Load user to validate admin id

        try:
            with open("db/user_base.json","r") as f:
                user_data = f.read().strip()
                users = json.loads(user_data) if user_data else []
        except FileNotFoundError:
            return json.dumps({"error":"UserBase not found"})
        
        #checks if admin id exists

        admin_id = data.get("admin")
        if not any(user.get("id") == admin_id for user in users):
            return json.dumps({"error":"Admin user id does not exist"})

        try:
            with open("db/team_base.json","r")as f:
                content = f.read().strip()
                if content:
                    teams = json.loads(content)
                else:
                    teams = []
        except FileNotFoundError:
            teams = []

        for team in teams:
            if team["team_name"] == data["team_name"]:
                return json.dumps({"error":"Team Name already exists"})
            
        team_id = str(uuid.uuid4())

        new_team={
            "id" : team_id,
            "team_name" : data["team_name"],
            "team_description" : data["team_description"],
            "admin" : admin_id,
            "creation_time" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        teams.append(new_team)

        with open("db/team_base.json","w") as f:
            json.dump(teams,f,indent=4)

        return json.dumps({"id":team_id})

    # list all teams
    def list_teams(self) -> str:
        """
        :return: A json list with the response.
        [
          {
            "name" : "<team_name>",
            "description" : "<some description>",
            "creation_time" : "<some date:time format>",
            "admin": "<id of a user>"
          }
        ]
        """
        
        try:
            with open("db/team_base.json","r") as f:
                content = f.read().strip()
                teams = json.loads(content) if content else []
        except FileNotFoundError:
            teams = []

        team_list =[
            {
                "team_name" : team.get("team_name",""),
                "team_description" : team.get("team_description",""),
                "creation_time" : team.get("creation_time",""),
                "admin" : team.get("admin","")
            }
            for team in teams
        ]

        return json.dumps(team_list,indent=4)

    # describe team
    def describe_team(self, request: str) -> str:
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>"
        }

        :return: A json string with the response

        {
          "name" : "<team_name>",
          "description" : "<some description>",
          "creation_time" : "<some date:time format>",
          "admin": "<id of a user>"
        }

        """
        try:
            request_data = json.loads(request)
            team_id = request_data.get("id")

            if not team_id:
                return json.dumps({"error": "Missing team id"})
            
            with open("db/team_base.json" ,"r") as f:
                content = f.read().strip()
                teams = json.loads(content) if content else []
            
            for team in teams:
                if team["id"] == team_id:
                    return json.dumps(
                        {
                         "team_name" : team.get("team_name",""),
                        "team_description" : team.get("team_description",""),
                        "creation_time": team.get("creation_time", "No creation time found"),
                        "admin" : team.get("admin","")

                    }
                    ,indent=4)
            return json.dumps({"error":"Team not found"})
        
        except FileNotFoundError:
            return json.dumps({"error":"Team base file not found"})

    # update team
    def update_team(self, request: str) -> str:
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "team" : {
            "name" : "<team_name>",
            "description" : "<team_description>",
            "admin": "<id of a user>"
          }
        }

        :return:

        Constraint:
            * Team name must be unique
            * Name can be max 64 characters
            * Description can be max 128 characters
        """
        try:
            request_data = json.loads(request)
            team_id = request_data.get("id")
            updated_team = request_data.get("team",{})

            if not team_id:
                return json.dumps({"error": "Missing team id"})
            
            with open("db/team_base.json" ,"r") as f:
                content = f.read().strip()
                teams = json.loads(content) if content else []
            
            team_found = False
            for team in teams:
                if team["id"] == team_id:
                    team_found = True

                    if "team_name" in updated_team and updated_team["team_name"] != team["team_name"]:
                        return json.dumps({"error": "Team cannot be updated"})
                    
                    if len(team["team_name"]) > 64:
                        return json.dumps({"error": "Team name exceed 64 characters"})
                    if "description_name" in updated_team and len(updated_team["description_name"]) > 128:
                        return json.dumps({"error": "Description name exceed 128 characters"})
                    
                    
                    if "description_name" in updated_team:
                        team["description_name"] = updated_team["description_name"]
                    break
                
            if not team_found:
              return json.dumps({"error": "Team not found"})
            
            with open("db/team_base.json","w") as f:
                json.dump(teams,f,indent=4)

            return json.dumps({"message": "Team, updated successfully"})
        
        except FileNotFoundError:
            return json.dumps({"error": "Team base file not found"})



    # add users to team
    def add_users_to_team(self, request: str):
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "users" : ["user_id 1", "user_id2"]
        }

        :return:

        Constraint:
        * Cap the max users that can be added to 50
        """
        try:
            request_data = json.loads(request)
            team_id = request_data.get("id")
            new_user_ids = request_data.get("users",[])

            if not team_id:
                return json.dumps({"error":"Missing team ID"})
            
            if not isinstance(new_user_ids,list) or not all(isinstance(u,str) for u in new_user_ids):
                return json.dumps({"error":"Invalid user format.Expected a list of user IDs"})
            
            with open("db/team_base.json","r") as f:
                content = f.read().strip()
                teams = json.loads(content) if content else []

            team_found  = False
            for team in teams:
                if team["id"] == team_id:
                    team_found = True

                    existing_member = team.get("members",[])
                    total_users = len(set(existing_member + new_user_ids))

                    if total_users > 50:
                        return json.dumps({"error":"Cannot exceed 50 user in team"})
                    
                    #Remove duplicated
                    team["members"] =list(set(existing_member + new_user_ids))
                    break
              
            if not team_found:
                return json.dumps({"error": "Team not found"})
            
            with open("db/team_base.json","w") as f:
                json.dump(teams,f,indent=4)

            return json.dumps({"message":"Users successfully added to team"})
        
        except FileNotFoundError:
            return json.dumps({"message":"Team base file not found"})

    # remove users to team
    def remove_users_from_team(self, request: str):
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "users" : ["user_id 1", "user_id2"]
        }

        :return:

        Constraint:
        * Cap the max users that can be added to 50
        """
        try:
            request_data = json.loads(request)
            team_id = request_data.get("id")
            remove_user_ids = request_data.get("users",[])

            if not team_id:
                return json.dumps({"error":"Missing team ID"})
            
            if not isinstance(remove_user_ids,list) or not all(isinstance(u,str) for u in remove_user_ids):
                return json.dumps({"error":"Invalid user format.Expected a list of user IDs"})
            
            with open("db/team_base.json","r") as f:
                content = f.read().strip()
                teams = json.loads(content) if content else []

            team_found  = False
            for team in teams:
                if team["id"] == team_id:
                    team_found = True

                    current_member = team.get("members",[])
                    updated_members = len(set(current_member + remove_user_ids))

                    
                    
                    
                    team["members"] = updated_members
                    break
              
            if not team_found:
                return json.dumps({"error": "Team not found"})
            
            with open("db/team_base.json","w") as f:
                json.dump(teams,f,indent=4)

            return json.dumps({"message":"Users successfully removed from team"})
        
        except FileNotFoundError:
            return json.dumps({"message":"Team base file not found"})

    

    # list users of a team
    def list_team_users(self, request: str):
        """
        :param request: A json string with the team identifier
        {
          "id" : "<team_id>"
        }

        :return:
        [
          {
            "id" : "<user_id>",
            "name" : "<user_name>",
            "display_name" : "<display name>"
          }
        ]
        """

        try:
            request_data = json.loads(request)
            team_id = request_data.get("id")
            

            if not team_id:
                return json.dumps({"error":"Missing team ID"})
            
            #Load Team
            with open("db/team_base.json","r") as f:
                content = f.read().strip()
                teams = json.loads(content) if content else []

            # Load User
            with open("db/user_base.json","r") as f:
                content = f.read().strip()
                users = json.loads(content) if content else []
    
            for team in teams:
                if team["id"] == team_id:
                    member_ids = team.get("members",[])
                    if not isinstance(member_ids,list):
                        member_ids = [member_ids]
                    results = []

                    for user in users:
                        if user["id"] in member_ids:
                            results.append({
                                "id" : user["id"],
                                "name" : user["name"],
                                "display_name" : user.get("display_name","")
                            })
                    return json.dumps(results,indent=2)
                
            return json.dumps({"error":"Team not found"})
        
        except FileNotFoundError:
            return json.dumps({"error":"User or Team base file not found"})

