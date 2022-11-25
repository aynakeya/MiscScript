import role


class GameController():
    pass

class Player():
    def __init__(self,index,id,name):
        self.index = index
        self.id = id
        self.name = name
        self.role = role.Role()

    def send_private_msg(self,msg):
        pass

    def is_self(self,player) -> bool:
        return self.id == player.id

class Game():
    def __init__(self):
        self.roles = []
        self.players = []

    def get_players_by_role(self,rolename):
        return list(filter(lambda player:player.role.role_name == rolename,
                           self.players))

    def parse_players_info(self):
        msg_list = ["闲置牌"]
        for role in self.roles:
            msg_list.append("#{}".format(role.))
        msg_list.append("玩家")

