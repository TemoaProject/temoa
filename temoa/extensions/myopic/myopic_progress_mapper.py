"""
Simple visualizer to track the progress of myopic solve
"""

from datetime import datetime, timedelta

from temoa.extensions.myopic.myopic_index import MyopicIndex


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
