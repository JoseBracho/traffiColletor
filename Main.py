import asyncio
import os
from dotenv import load_dotenv
from SnmpTraffic import SnmpTraffic 
from DbTraffic import PostgreSQLBatchInserter
from DbOlts import MongoDeviceManager

load_dotenv()

class Main:

    def __init__(self):
        self._DBTABLEPG = os.getenv("DBTABLEPG")
        self._COMMUNITY = os.getenv("COMMUNITY")
        self._OID = os.getenv("OID")
        self._DBHOSTMG = os.getenv("DBHOSTMG")
        self._DBPORTMG = int(os.getenv("DBPORTMG"))
        self._DBNAMEMG = os.getenv("DBNAMEMG")
        self._DBCOLLMG = os.getenv("DBCOLLMG")
        self._DBUSERMG = os.getenv("DBUSERMG")
        self._DBPASSMG = os.getenv("DBPASSMG")
        self._DBPG = {
            "host": os.getenv("DBHOSTPG"),
            "port": int(os.getenv("DBPORTPG")),
            "user": os.getenv("DBUSERPG"),
            "password": os.getenv("DBPASSWORD"),
            "database": os.getenv("DBNAMEPG")
        }
    def getIPS(self):
        mongo = MongoDeviceManager(self._DBHOSTMG, self._DBPORTMG, self._DBNAMEMG, self._DBCOLLMG, self._DBUSERMG, self._DBPASSMG)
        ips = []
        for data in mongo.get_devices():
            if int(data["ip_admin"].split(".")[-1]) > 29:
                ips.append(data["ip_admin"]) 
        return ips

    def run(self):
        devices = self.getIPS()
        interval = 300 
        snmp_traffic = SnmpTraffic(devices, self._COMMUNITY, self._OID, interval=interval)
        db_inserter = PostgreSQLBatchInserter(self._DBPG, self._DBTABLEPG)
        try:
            asyncio.run(db_inserter.run(snmp_traffic))
        except KeyboardInterrupt:
            print("\nEjecución interrumpida por el usuario.")

if __name__ == '__main__':
    main = Main()
    main.run()
