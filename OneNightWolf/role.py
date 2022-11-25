class Role():
    role_name = ""

    def __init__(self,game,player):
        self.game = game
        self.player = player
        self.current_role_name = self.role_name

    def send_hint(self):
        pass
    def process_command(self,command) -> bool:
        pass


class Wolf(Role):
    role_name = "wolf"
    def send_hint(self):
        for player in self.game.get_roles(self.role_name):
            if self.player.is_self(player):
                continue
            self.player.send_private_msg()
    def process_command(self,command):
        return False


class WolfHelper(Role):
    role_name = "wolf_helper"

    def send_hint(self):


    def process_command(self, command) -> bool:
        return False
