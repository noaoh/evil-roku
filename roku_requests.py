import aiohttp
import xmltodict

async def get_device_info(ip):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{ip}/query/device-info") as resp:
            text = await resp.text()
            d = xmltodict.parse(text)
            return {
                "is_tv": d["device-info"]["is-tv"],
                "is_stick": d["device-info"]["is-stick"],
                "supports_find_remote": d["device-info"]["supports-find-remote"],
            }

async def make_roku_command(ip, command):
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{ip}/keypress/{command}") as resp:
            pass
