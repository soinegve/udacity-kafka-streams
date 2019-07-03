"""Defines functionality relating to train lines"""
import collections
from enum import IntEnum
import logging

from models import Station, Train


logger = logging.getLogger(__name__)


class Line:
    """Contains Chicago Transit Authority (CTA) Elevated Loop Train ("L") Station Data"""

    colors = IntEnum("colors", "blue", start=0)
    num_directions = 2

    def __init__(self, color, station_data, num_trains=10):
        self.color = color
        self.num_trains = num_trains
        self.stations = self._build_line_data(station_data)
        self.trains = self._build_trains()

    def _build_line_data(self, station_df):
        """Constructs all stations on the line"""
        stations = station_df["STATION_NAME"].unique()
        line = [Station(stations[0])]
        prev_station = line[0]
        for station in stations[1:]:
            new_station = Station(station, prev_station)
            prev_station.dir_b = new_station
            prev_station = new_station
            line.append(new_station)
        return line

    def _build_trains(self):
        """Constructs and assigns train objects to stations"""
        trains = []
        curr_loc = 0
        b_dir = True
        print(f"len: {len(self.stations)}")
        for train_id in range(self.num_trains):
            train = Train(f"{self.color.name[0].upper()}L{train_id}", Train.status.in_service)
            trains.append(train)

            if b_dir:
                self.stations[curr_loc].arrive_b(train)
            else:
                self.stations[curr_loc].arrive_a(train)
            curr_loc, b_dir = self._get_next_idx(curr_loc, b_dir)

        return trains

    def advance(self):
        """Advances trains between stations in the simulation"""
        # Find the first b train
        curr_train, curr_index, b_direction = self._next_train()
        self.stations[curr_index].b_train = None

        trains_advanced = 0
        while trains_advanced < self.num_trains - 1:
            print(f"curr index {curr_index}")
            print(f"curr train {curr_train}")
            print(f"curr direc {'b' if b_direction else 'a'}")
            next_train, curr_index, b_direction = self._get_next_idx(curr_index, b_direction)
            print(f"post index {curr_index}")
            print(f"post direc {'b' if b_direction else 'a'}")
            if b_direction is True:
                next_train = self.stations[curr_index].b_train
                self.stations[curr_index].arrive_b(curr_train)
            else:
                next_train = self.stations[curr_index].a_train
                self.stations[curr_index].arrive_a(curr_train)

            #if next_train is not None:
            curr_train = next_train
            #else:
            #    curr_train, curr_index, b_direction = self._next_train(
            #            b_direction=b_direction,
            #            start_index=curr_index,
            #            step_size=1,
            #    )
            #    print(f"next index {curr_index}")
            #    print(f"next direc {'b' if b_direction else 'a'}")
            #    #if b_direction is True:
            #    #    self.stations[curr_index].b_train = None
            #    #else:
            #    #    self.stations[curr_index].a_train = None
            print("-----------------------")
            trains_advanced += 1

        curr_index, b_direction = self._get_next_idx(curr_index, b_direction)
        if b_direction is True:
            next_train = self.stations[curr_index].b_train
            self.stations[curr_index].arrive_b(curr_train)
        else:
            next_train = self.stations[curr_index].a_train
            self.stations[curr_index].arrive_a(curr_train)

    def _next_train(self, b_direction=True, start_index=0, step_size=1):
        """Given a starting index, finds the next train in either direction"""
        if b_direction is True:
            curr_index = self._next_train_b(start_index, step_size)

            if curr_index == -1:
                curr_index = self._next_train_a(len(self.stations) - 1, step_size)
                b_direction = False
        else:
            curr_index = self._next_train_a(start_index, step_size)

            if curr_index == -1:
                curr_index = self._next_train_b(0, step_size)
                b_direction = True

        if b_direction is True:
            return self.stations[curr_index].b_train, curr_index, True
        return self.stations[curr_index].a_train, curr_index, False

    def _next_train_b(self, start_index, step_size):
        """Finds the next train in the b direction, if any"""
        for i in range(start_index, len(self.stations), step_size):
            if self.stations[i].b_train is not None:
                return i
        return -1

    def _next_train_a(self, start_index, step_size):
        """Finds the next train in the a direction, if any"""
        for i in range(len(self.stations)-1, start_index, -step_size):
            if self.stations[i].a_train is not None:
                return i
        return -1

    def _get_next_idx(self, curr_index, b_direction, step_size=None):
        """Calculates the next station index. Returns next index and if it is b direction"""
        if step_size is None:
            step_size = int((len(self.stations) * Line.num_directions)/self.num_trains)
        if b_direction is True:
            next_index = curr_index + step_size
            if next_index < len(self.stations):
                return next_index, True
            else:
                return len(self.stations) - (next_index % len(self.stations)) - 1, False
        else:
            next_index = curr_index - step_size
            if next_index >= 0:
                return next_index, False
            else:
                return abs(next_index), True

    def __str__(self):
        return "\n".join(str(station) for station in self.stations)

    def __repr__(self):
        return str(self)
