import contextlib
import curses
import itertools
import math
from pomodoro import notification


class Time:
  def __init__(self, seconds, elapsed_seconds):
    self._seconds = seconds
    self._elapsed_seconds = elapsed_seconds

  def __str__(self):
    seconds_left = self._seconds - self._elapsed_seconds
    bar_count = math.ceil(seconds_left / 60)

    return '  timer: [' + '▉' * bar_count \
      + ' ' * math.floor(self._elapsed_seconds / 60) \
      + f'] {int(seconds_left / 60):0>2}:{seconds_left % 60:0>2}'


class Session:
  def __init__(self, window, minutes, color_pair, tomato_count):
    self._window = window
    self._seconds = minutes * 60
    self._color_pair = color_pair
    self._tomato_count = tomato_count

  def start(self):
    for elapsed_seconds in range(0, self._seconds + 1):
      time = Time(self._seconds, elapsed_seconds)
      with self._rendering():
        self._window.addstr(str(time), self._color_pair)
        self._window.addstr('\n')
        self._add_tomatos()

      for _ in range(10):
        self._window.nodelay(True)
        if self._window.getch() > 0:
          with self._rendering():
            self._window.addstr(str(time), self._color_pair)
            self._window.addstr(' (pause)')
            self._window.addstr('\n')
            self._add_tomatos()

          self._window.nodelay(False)
          self._window.getch()
        curses.napms(100)  # 0.1 second

  def finish(self, message):
    with self._rendering(clear=False):
      self._window.addstr('\n\n')
      self._window.addstr('         ' + message)
      self._window.refresh()

    self._window.nodelay(False)
    self._window.getch()

  @contextlib.contextmanager
  def _rendering(self, clear=True):
    try:
      if clear:
        self._window.clear()
      yield
      self._window.refresh()
    finally:
      pass

  def _add_tomatos(self):
    self._window.addstr('tomatos: ' + '🍅 ' * self._tomato_count,
                  curses.color_pair(2))


class Pomodoro:
  def __init__(self, cycle):
    self._tomato_count = 0
    self._cycle = cycle

  def start(self):
    curses.wrapper(self._main)

  def _main(self, window):
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)
    self._init_color_pairs()

    for i, minutes in enumerate(itertools.cycle(self._cycle)):
      try:
        if i % 2 == 0:
          session = Session(window, minutes, curses.color_pair(3),
                            self._tomato_count)
          session.start()
          notification.notify('Session finished.')
          session.finish('Press any key to take a break.')

          self._tomato_count += 1
        else:
          break_time = Session(window, minutes, curses.color_pair(5),
                               self._tomato_count)
          break_time.start()
          notification.notify('Break time finished.')
          break_time.finish('Press any key to start a new session.')
      except KeyboardInterrupt:
        break

  def _init_color_pairs(self):
    for i in range(0, curses.COLORS):
      curses.init_pair(i + 1, i, -1)


if __name__ == '__main__':
  Pomodoro().start()
