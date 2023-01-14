from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class PermissionFunction(ShopFunction):
    allowed_shop_type = []

    def on_function_init(self):
        self.set_variable("users", {})

    def set_permission(self, player: Player, permission: str):
        default = {
            "name": player.name,
            "uuid": player.uuid,
            "permission": permission,
            "notify": True
        }
        users = self.get("users")
        if player.get_uuid_formatted() in users:
            default = users[player.get_uuid_formatted()]

        self.set("users." + player.get_uuid_formatted(), default)

    def remove_user(self, player: Player):
        permission_list = self.get("users")
        if player.get_uuid_formatted() in permission_list:
            del permission_list[player.get_uuid_formatted()]
        else:
            return True
        return self.set("users", permission_list)

    def get_permission(self, player: Player):
        permission_list = self.get("users")
        result = permission_list.get(player.get_uuid_formatted())
        if result is None:
            return "NONE"
        return result["permission"]
    def get_permission_level(self, permission):
        permission_level = 0
        if permission == "OWNER": permission_level = 10
        if permission == "MODERATOR": permission_level = 9
        if permission == "ACCOUNTANT": permission_level = 7
        if permission == "STORAGE_ACCESS": permission_level = 6
        return permission_level

    def has_permission_at_least(self, target_permission: str, owning_permission: str):
        return self.get_permission_level(owning_permission) >= self.get_permission_level(target_permission)

    def has_permission(self, player: Player, permission: str):
        return self.has_permission_at_least(permission, self.get_permission(player))
