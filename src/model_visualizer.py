import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
import random
from datetime import datetime
from matplotlib import animation
import time
from threading import Thread, Lock


plt.style.use('dark_background')

x_values = []
y_values = []
values_lock = Lock()

fmt_maj = mdates.MonthLocator(interval=3)
fmt_min = mdates.MonthLocator(interval=1)

dirty = False

fig, ax = plt.subplots(1, 1, figsize=(16, 8))


def set_style(title):
    ax.xaxis.set_major_locator(fmt_maj)
    ax.xaxis.set_minor_locator(fmt_min)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.format_xdata = mdates.DateFormatter('%Y-%m')
    ax.format_ydata = lambda x: f'${x:.2f}'
    ax.grid(True)
    fig.autofmt_xdate()
    ax.set_xlabel('Date')
    ax.set_ylabel('Adj. Close')
    ax.set_title(title)


def add_point(x, y):
    global dirty, x_values, y_values, values_lock
    values_lock.acquire()
    x_values.append(x)
    y_values.append(y)
    dirty = True
    values_lock.release()


tmp = None


def redraw(i):
    global dirty, ax, x_values, y_values, values_lock, tmp
    values_lock.acquire()
    if dirty:
        if tmp is not None:
            l = tmp.pop(0)
            l.remove()
            del l
        if len(x_values) > 0:
            tmp = ax.plot(x_values, y_values, 'C2')
        dirty = False
    values_lock.release()


def reset():
    global dirty, x_values, y_values, values_lock
    values_lock.acquire()
    x_values.clear()
    y_values.clear()
    dirty = True
    values_lock.release()


def start(title):
    global fig, ax

    set_style(title)
    anim = animation.FuncAnimation(fig, redraw, interval=1)

    plt.show()


def test_loop():
    while True:
        add_point(datetime.now(), random.random() * 1000)
        time.sleep(1)


if __name__ == "__main__":
    x = Thread(target=test_loop, daemon=True)
    x.start()
    start('Testing')
