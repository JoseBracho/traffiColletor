from concurrent.futures import ThreadPoolExecutor
from pysnmp.hlapi import *
from datetime import datetime
import asyncio


class SnmpTraffic:
    def __init__(self, devices, community, oid, port=161, interval=300):
        self._devices = devices  
        self._community = community
        self._oid = oid
        self._port = port
        self._interval = interval 

    def _blocking_snmp_walk(self, ip):
        result = []
        iterator = nextCmd(
            SnmpEngine(),
            CommunityData(self._community),
            UdpTransportTarget((ip, self._port)),
            ContextData(),
            ObjectType(ObjectIdentity(self._oid)),
            lexicographicMode=False
        )
        for errorIndication, errorStatus, errorIndex, varBinds in iterator:
            if errorIndication:
                print(f"Error en {ip}: {errorIndication}")
                break
            elif errorStatus:
                print(
                    f"Error en {ip}: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
                break
            else:
                for varBind in varBinds:
                    current_time = datetime.now()
                    oid, value = varBind
                    ifindex = str(oid).split('.')[-2]
                    ontindex = str(oid).split('.')[-1]
                    result.append((ip, ifindex, ontindex, str(value), current_time))
        return result

    async def snmp_walk(self, ip):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self._blocking_snmp_walk, ip)

    async def device_task(self, ip, db_inserter):
        while True:
            results = await self.snmp_walk(ip)
            await db_inserter.insert_data(results)
            await asyncio.sleep(self._interval)

    async def main(self, db_inserter):
        tasks = [self.device_task(ip, db_inserter) for ip in self._devices]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    ...
