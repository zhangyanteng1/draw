import time
import random


class UUIDUtils:
    def __init__(self, machine_id=1):
        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = -1

    def _generate_id(self):
        timestamp = int(time.time() * 1000)

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 4095
            if self.sequence == 0:
                timestamp = self._wait_next_millis(self.last_timestamp)
        else:
            self.sequence = random.randint(0, 4095)

        self.last_timestamp = timestamp

        return ((timestamp - 1288834974657) << 22) | (self.machine_id << 12) | self.sequence

    def _wait_next_millis(self, last_timestamp):
        timestamp = int(time.time() * 1000)
        while timestamp <= last_timestamp:
            timestamp = int(time.time() * 1000)
        return timestamp

    @classmethod
    def get_uuid(cls):
        while True:
            uuid = UUIDUtils()._generate_id() % 10 ** 10
            if len(str(uuid)) >= 7:  # 至少7位数
                return uuid


# if __name__ == '__main__':
#     for i in range(0, 20):
#         print(UUID.get_uuid())

