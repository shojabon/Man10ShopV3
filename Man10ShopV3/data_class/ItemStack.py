class ItemStack(object):
    type_base64: str = "rO0ABXcEAAAAAXNyABpvcmcuYnVra2l0LnV0aWwuaW8uV3JhcHBlcvJQR+zxEm8FAgABTAADbWFwdAAPTGphdmEvdXRpbC9NYXA7eHBzcgA1Y29tLmdvb2dsZS5jb21tb24uY29sbGVjdC5JbW11dGFibGVNYXAkU2VyaWFsaXplZEZvcm0AAAAAAAAAAAIAAlsABGtleXN0ABNbTGphdmEvbGFuZy9PYmplY3Q7WwAGdmFsdWVzcQB+AAR4cHVyABNbTGphdmEubGFuZy5PYmplY3Q7kM5YnxBzKWwCAAB4cAAAAAN0AAI9PXQAAXZ0AAR0eXBldXEAfgAGAAAAA3QAHm9yZy5idWtraXQuaW52ZW50b3J5Lkl0ZW1TdGFja3NyABFqYXZhLmxhbmcuSW50ZWdlchLioKT3gYc4AgABSQAFdmFsdWV4cgAQamF2YS5sYW5nLk51bWJlcoaslR0LlOCLAgAAeHAAAAqqdAAHRElBTU9ORA=="
    type_md5: str = "f955adf1e7104a74953d377f4b039b52"
    amount: int = 1
    display_name: str = None

    def from_json(self, data: dict):
        self.type_base64 = data.get("type_base64")
        self.type_md5 = data.get("type_md5")
        self.amount = data.get("amount")
        self.display_name = data.get("display_name")

        return self

    def get_json(self):
        return {
            "type_base64": self.type_base64,
            "type_md5": self.type_md5,
            "amount": self.amount,
            "display_name": self.display_name
        }
