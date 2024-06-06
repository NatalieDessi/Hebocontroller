import asyncio
import math
import struct
from asyncio import AbstractEventLoop
from sys import argv

from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic
from pydualsense import *

x = 0
r2 = 0
l2 = 0


def r2_changed(state):
    global r2
    # r2 = state / 2
    # print(f'r2 {state}')


def l2_changed(state):
    global l2
    # l2 = state / 2
    # print(f'l2 {state}')


def joystick(_x, _y):
    global x
    # x = _x


def get_result():
    global x
    global r2
    global l2
    y = math.floor(r2 - l2)
    result = x
    result += y << 8
    return result


def _device_filter(_device, advertisement):
    return argv[1].lower() in advertisement.service_uuids


async def handle_input(_client, characteristic: BleakGATTCharacteristic):
    await asyncio.sleep(1 / 100)
    await _client.write_gatt_char(characteristic, struct.pack('<i', get_result()), response=True)


async def init_controller():
    dualsense = pydualsense()
    dualsense.init()
    dualsense.r2_changed.subscribe(r2_changed)
    dualsense.l2_changed.subscribe(l2_changed)
    dualsense.left_joystick_changed.subscribe(joystick)


async def loop(controller_loop: AbstractEventLoop):
    device = await BleakScanner.find_device_by_filter(_device_filter)
    async with BleakClient(device) as _client:
        service = _client.services.get_service(argv[1])
        characteristic = service.get_characteristic(argv[2])
        print(f"Connected to client {_client.address}")
        while True:
            await handle_input(_client, characteristic)


def main():
    if len(argv) != 3:
        print("Please specify service and characteristic uuid as cli parameters")
        return

    _loop = asyncio.new_event_loop()
    controller_loop = asyncio.new_event_loop()

    _loop.run_until_complete(loop(controller_loop))
    controller_loop.run_until_complete(init_controller())

    _loop.close()
    controller_loop.close()


if __name__ == '__main__':
    main()
