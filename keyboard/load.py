import asyncio
import sys
from asyncio import AbstractEventLoop
from sys import argv

import keyboard
from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic
from keyboard import KeyboardEvent


class Keyboard:
    def __init__(self, loop: AbstractEventLoop, service_uuid: str, characteristic_uuid: str, polling_rate: int = 100):
        self._client = None
        self._loop = loop
        self._service_uuid = service_uuid
        self._characteristic_uuid = characteristic_uuid
        self._poling_rate = polling_rate
        self._keys = []
        self._current_key = ' '

        keyboard.hook_key('w', self._key_hook)
        keyboard.hook_key('a', self._key_hook)
        keyboard.hook_key('s', self._key_hook)
        keyboard.hook_key('d', self._key_hook)
        keyboard.hook_key('esc', lambda _: sys.exit(0))

    def _key_hook(self, event: KeyboardEvent):
        if event.event_type == keyboard.KEY_DOWN and event.name not in self._keys:
            self._keys.append(event.name)
            self._current_key = event.name
        if event.event_type == keyboard.KEY_UP and event.name in self._keys:
            self._keys.remove(event.name)

            if len(self._keys) == 0:
                self._current_key = ' '
            elif event.name == self._current_key:
                self._current_key = self._keys[-1]

    def _device_filter(self, _device, advertisement):
        return self._service_uuid.lower() in advertisement.service_uuids

    def close(self, _event: KeyboardEvent = None):
        self._loop.call_soon(self._client.disconnect)

    @staticmethod
    def disconnect(client: BleakClient):
        print(f"Disconnected from {client.address}")

    async def handle_keys(self, client: BleakClient, characteristic: BleakGATTCharacteristic):
        await asyncio.sleep(1 / self._poling_rate)
        await client.write_gatt_char(characteristic, bytearray(self._current_key.encode('utf-8')), response=True)

    async def start(self):
        device = await BleakScanner.find_device_by_filter(self._device_filter)
        async with BleakClient(device, disconnected_callback=self.disconnect) as self._client:
            service = self._client.services.get_service(self._service_uuid)
            characteristic = service.get_characteristic(self._characteristic_uuid)
            print(f"Connected to client {self._client.address}")
            while True:
                await self.handle_keys(self._client, characteristic)


def main():
    if len(argv) != 3:
        print("Please specify service and characteristic uuid as cli parameters")
        return
    loop = asyncio.new_event_loop()
    _keyboard = Keyboard(loop, argv[1], argv[2])
    try:
        loop.run_until_complete(_keyboard.start())
    except KeyboardInterrupt:
        print("Programm was closed")
    finally:
        loop.close()


if __name__ == '__main__':
    main()
