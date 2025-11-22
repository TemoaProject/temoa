"""
Simple visualizer to track the progress of myopic solve
"""

from datetime import datetime, timedelta

from temoa.extensions.myopic.myopic_index import MyopicIndex

"""
Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

Copyright (C) 2015,  NC State University

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A complete copy of the GNU General Public License v2 (GPLv2) is available
in LICENSE.txt.  Users uncompressing this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.


Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  1/22/24

"""


class MyopicProgressMapper:
    def __init__(self, sorted_future_years: list):
        self.leader = '--'
        self.trailer = ''.join(reversed(self.leader))
        self.years = sorted_future_years
        self.tag_width = max(len(str(t)) for t in sorted_future_years) + 2 * len(self.leader)
        self.pos = {
            yr: idx * (self.tag_width + 2) + 2 for idx, yr in enumerate(sorted_future_years)
        }
        self.hack: datetime = datetime.now()

    def draw_header(self):
        time_buffer = ' ' * 10
        tot_length = len(self.years) * self.tag_width + 2 * len(self.years)
        print(time_buffer, end='')
        print('*' * tot_length)

        label = 'Myopic  Progress'
        half_slack = (tot_length + 1 - len(label)) // 2 - 1
        print(time_buffer, end='')
        print('*', end='')
        print(' ' * half_slack, end='')
        print(label, end='')
        print(' ' * half_slack, end='')
        print('*')

        print(time_buffer, end='')
        print('*' * tot_length)
        print()
        print(f"{'HH:MM:SS':10s}", end='')
        print(' ', end='')
        for year in self.years:
            print(f'{self.leader}{year}{self.trailer}  ', end='')
        print()

    def timestamp(self) -> str:
        delta = datetime.now() - self.hack
        return (
            f'Elapsed: {int(delta.total_seconds()//3600):02d}:'
            f'{int(delta.total_seconds()%3600//60):02d}:{int(delta.total_seconds())%60:02d}   '
        )

    def report(self, mi: MyopicIndex, status):
        if status not in {'load', 'solve', 'report', 'check'}:
            raise ValueError(f'bad status: {status} received in MyopicProgressMapper')

        if status == 'load':
            repeats = self.years.index(mi.last_demand_year) - self.years.index(mi.base_year) + 1
            print(self.timestamp(), end='')
            print(' ' * self.pos[mi.base_year], end='')
            for _ in range(repeats):
                print('LOAD', end=' ' * (self.tag_width + 2 - 4))  # 4=length('LOAD')

        if status == 'check':
            repeats = self.years.index(mi.last_demand_year) - self.years.index(mi.base_year) + 1
            print(self.timestamp(), end='')
            print(' ' * self.pos[mi.base_year], end='')
            for _ in range(repeats):
                print('CHEK', end=' ' * (self.tag_width + 2 - 4))  # 4=length('CHEK')

        if status == 'solve':
            repeats = self.years.index(mi.last_demand_year) - self.years.index(mi.base_year) + 1
            print(self.timestamp(), end='')
            print(' ' * self.pos[mi.base_year], end='')
            for _ in range(repeats):
                print('SOLV', end=' ' * (self.tag_width + 2 - 4))  # 4=length('SOLV')

        if status == 'report':
            repeats = self.years.index(mi.step_year) - self.years.index(mi.base_year)
            print(self.timestamp(), end='')
            print(' ' * self.pos[mi.base_year], end='')
            for _ in range(repeats):
                print('RECD', end=' ' * (self.tag_width + 2 - 4))  # 4=length('RECD')
        print()


if __name__ == '__main__':
    mapper = MyopicProgressMapper([1, 2, 3])
    mapper.hack = datetime.now() - timedelta(hours=20, minutes=5, seconds=9)
    print(mapper.timestamp())
