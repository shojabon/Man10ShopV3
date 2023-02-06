import json

from pymongo import MongoClient
import MySQLdb

file = open("config.json", "r")
config = json.loads(file.read())
file.close()

mongo = MongoClient(config["mongo"])

result = {}

for shop in mongo["man10shop_v3"]["shops"].find({"delete.deleted": False}):
    money = shop["money"]["money"]
    owner = None
    for user in shop["permission"]["users"].values():
        if user["permission"] == "OWNER":
            owner = user
            break
    if owner is None:
        continue
    if owner["uuid"] not in result:
        owner["money"] = 0
        result[owner["uuid"]] = owner
    result[owner["uuid"]]["money"] += money

connection = MySQLdb.connect(
    host=config["mysql"]["host"],
    port=config["mysql"]["port"],
    user=config["mysql"]["user"],
    passwd=config["mysql"]["password"],
    db=config["mysql"]["db"])
cursor = connection.cursor()

create_table = """
CREATE TABLE IF NOT EXISTS `money_status` (
	`id` INT(10) NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`uuid` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`balance` INT(10) NULL DEFAULT NULL,
	PRIMARY KEY (`id`) USING BTREE,
	UNIQUE INDEX `インデックス 2` (`uuid`) USING BTREE
)
COLLATE='utf8mb4_0900_ai_ci'
ENGINE=InnoDB
;
"""
cursor.execute(create_table)

for user in result.values():
    query = "INSERT INTO money_status (`name`, `uuid`, `balance`) VALUES "
    query += "(\"{0}\", \"{1}\", {2})".format(user["name"], user["uuid"], user["money"])
    query += "ON DUPLICATE KEY UPDATE `balance` = " + str(user["money"])
    cursor.execute(query)
    connection.commit()

cursor.close()
connection.close()
