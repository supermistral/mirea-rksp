import multiprocessing
import random
import time
from dataclasses import dataclass
from abc import abstractmethod, ABCMeta
from typing import NamedTuple
from typing import Iterable

import reactivex
from reactivex import operators as ops
from reactivex.scheduler import ThreadPoolScheduler

class SensorData(NamedTuple):
    name: str
    value: int


class BaseSensor(metaclass=ABCMeta):
    TIMEOUT_SECONDS = 1

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def _publish_value(self) -> int:
        ...

    def _wait(self):
        time.sleep(self.TIMEOUT_SECONDS)

    def __call__(self, observer, scheduler):
        while True:
            self._wait()

            observer.on_next(
                SensorData(
                    name=self.name,
                    value=self._publish_value(),
                )
            )


class TemperatureSensor(BaseSensor):
    @property
    def name(self) -> str:
        return "Temperature"

    def _publish_value(self) -> int:
        return random.randint(15, 30)


class CO2Sensor(BaseSensor):
    @property
    def name(self) -> str:
        return "CO2"

    def _publish_value(self) -> int:
        return random.randint(30, 100)


@dataclass(frozen=True)
class SensorCreationData:
    sensor: BaseSensor
    normal_value: int


class Signaling:
    def __init__(self):
        self.sensors_creation_data = [
            SensorCreationData(sensor=TemperatureSensor(), normal_value=25),
            SensorCreationData(sensor=CO2Sensor(), normal_value=70),
        ]
        self.sensor_name_to_normal_value = {
            data.sensor.name: data.normal_value
            for data in self.sensors_creation_data
        }

    def schedule(self):
        threadpool = self._create_threadpool()
        sources = []

        for sensor_data in self.sensors_creation_data:
            source = reactivex.create(sensor_data.sensor).pipe(
                ops.subscribe_on(threadpool),
            )
            sources.append(source)

        join_source = reactivex.zip(*sources)
        join_source.subscribe(
            on_next=self._handle_sensors_data,
        )

    def _is_sensor_value_higher(self, sensor_data: SensorData) -> bool:
        print(f"received: {sensor_data.name} {sensor_data.value}")

        normal_value = self.sensor_name_to_normal_value[sensor_data.name]

        if sensor_data.value > normal_value:
            print(f"WARNING: {sensor_data.value} > {normal_value}")

        return sensor_data.value > normal_value

    def _handle_sensors_data(self, sensors_data: Iterable[SensorData]):
        is_all_higher = True

        for sensor_data in sensors_data:
            is_all_higher &= self._is_sensor_value_higher(sensor_data=sensor_data)

        if is_all_higher:
            print("ALARM!!!")

    def _create_threadpool(self) -> ThreadPoolScheduler:
        optimal_thread_count = multiprocessing.cpu_count()
        return ThreadPoolScheduler(optimal_thread_count)


def main():
    signaling = Signaling()
    signaling.schedule()


if __name__ == "__main__":
    main()
