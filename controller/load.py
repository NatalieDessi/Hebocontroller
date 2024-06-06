import asyncio
import math
from asyncio import AbstractEventLoop
from sys import argv

from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic
from pydualsense import *


class Controller:
    l2 = 0
    r2 = 0
    x = 0

    def __init__(self, loop: AbstractEventLoop, service_uuid: str, characteristic_uuid: str, polling_rate: int = 100):
        self._client = None
        self._loop = loop
        self._service_uuid = service_uuid
        self._characteristic_uuid = characteristic_uuid
        self._poling_rate = polling_rate

        self.dualsense = pydualsense()
        self.dualsense.init()
        self.dualsense.r2_changed.subscribe(self.r2_changed)
        self.dualsense.l2_changed.subscribe(self.l2_changed)
        self.dualsense.left_joystick_changed.subscribe(self.joystick)

    def _device_filter(self, _device, advertisement):
        return self._service_uuid.lower() in advertisement.service_uuids

    def close(self):
        self._loop.call_soon(self._client.disconnect)

    @staticmethod
    def disconnect(client: BleakClient):
        print(f"Disconnected from {client.address}")

    def r2_changed(self, state):
        self.r2 = state / 2
        # print(f'r2 {state}')

    def l2_changed(self, state):
        self.l2 = state / 2
        # print(f'l2 {state}')

    def joystick(self, x, _y):
        self.x = x

    async def handle_input(self, characteristic: BleakGATTCharacteristic):
        y = math.floor(self.r2 - self.l2)
        result = self.x
        result += y << 8
        await asyncio.sleep(1 / self._poling_rate)
        await self._client.write_gatt_char(characteristic, result.to_bytes(2, 'big', signed=True), response=True)

    async def loop(self):
        device = await BleakScanner.find_device_by_filter(self._device_filter)
        async with BleakClient(device, disconnected_callback=self.disconnect) as self._client:
            service = self._client.services.get_service(self._service_uuid)
            characteristic = service.get_characteristic(self._characteristic_uuid)
            print(f"Connected to client {self._client.address}")
            while True:
                await self.handle_input(characteristic)


def main():
    if len(argv) != 3:
        print("Please specify service and characteristic uuid as cli parameters")
        return
    loop = asyncio.new_event_loop()
    _controller = Controller(loop, argv[1], argv[2])
    try:
        loop.run_until_complete(_controller.loop())
    except KeyboardInterrupt:
        print("Programm was closed")
    finally:
        loop.close()
        _controller.dualsense.close()


if __name__ == '__main__':
    main()
