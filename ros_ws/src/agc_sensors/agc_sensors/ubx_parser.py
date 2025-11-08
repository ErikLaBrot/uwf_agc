import struct

class UbxParser:
    SYNC1 = 0xB5
    SYNC2 = 0x62

    def __init__(self):
        self.buffer = bytearray()

    def parse(self, data):
        self.buffer.extend(data)
        messages = []

        while len(self.buffer) > 8:
            if self.buffer[0] != self.SYNC1 or self.buffer[1] != self.SYNC2:
                self.buffer.pop(0)
                continue

            msg_class = self.buffer[2]
            msg_id = self.buffer[3]
            length = struct.unpack('<H', self.buffer[4:6])[0]

            if len(self.buffer) < 6 + length + 2:
                break  # incomplete frame

            payload = self.buffer[6:6+length]
            ck_a, ck_b = self.buffer[6+length:6+length+2]
            if self._checksum(self.buffer[2:6+length]) == (ck_a, ck_b):
                if msg_class == 0x01 and msg_id == 0x07:  # NAV-PVT
                    messages.append(self._parse_nav_pvt(payload))
            del self.buffer[:6+length+2]

        return messages

    def _checksum(self, data):
        ck_a, ck_b = 0, 0
        for b in data:
            ck_a = (ck_a + b) & 0xFF
            ck_b = (ck_b + ck_a) & 0xFF
        return ck_a, ck_b

    def _parse_nav_pvt(self, payload):
        fields = struct.unpack('<LHBBBBBBLlBBBBllllLLlllllLLHHH', payload[:92])
        lat = fields[20] * 1e-7
        lon = fields[19] * 1e-7
        alt = fields[21] * 1e-3
        return {'lat': lat, 'lon': lon, 'alt': alt}
