class ItemStack(object):
    base64: str = None
    base64_type: str = None
    md5: str = None
    md5_type: str = None
    amount: int = 1
    name: str = None
    lore: list[str] = None

    def get_json(self):
        return {
            "name": self.name,
            "base64": self.base64,
            "amount": self.amount,
            "lore": self.lore
        }
