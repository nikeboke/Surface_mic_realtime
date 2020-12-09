
import numpy as np
import abc
import threading
import redis

class Shared:
    '''
    This class modifies the get_data and update_con methods,
    these methods will now use a redis server. This slowsdown the process

    reqirements:
    - Super class must have update_con and get_data methods.
    - a redis server must be running.
    '''
    def __init__(self, *args, **kwargs):
        self.r = redis.Redis('localhost')
        self.key = self.__class__.__name__
        super().__init__(*args, **kwargs)

    def update_con(self, data:'iterable'):
        '''
        We actually dont need to use super().get_data and super().update_con
        in this example, since they dont change the data
        and it seems that they dont decrase execution speed.
        '''

        super().update_con(data)
        data = super().get_data()

        if data:
            pipe = self.r.pipeline()
            pipe.delete(self.key)
            pipe.lpush(self.key, *data)
            pipe.execute()

    def get_data(self):
        return [float(_) for _ in self.r.lrange(self.key, 0, -1)[::-1]]

    def close(self):
        self.r.delete(self.key)
        super().close()

def limit_by_time(t : 'int(seconds)'):
    start_time = 0
    def _(func):
        import time
        from functools import wraps
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal t, start_time
            if start_time == 0:
                start_time = time.time()
            elif time.time() - start_time >= t:
                t1, start_time = start_time, 0
                raise TimeoutError(f'{func.__name__} ran for {time.time() - t1 : 10.8f}(s)')
            rv = func(*args, **kwargs)
            return rv
        return wrapper
    return _

class Data(abc.ABC):
    ''' ABC'''

    def __init__(self):
        self.container = []
        self._running = True
        self.daemon = threading.Thread(target=self.loop, daemon=True)
        self._con_lock = threading.Lock()
        self.daemon.start()
        import atexit
        atexit.register(self.close)

    def get_data(self):
        ''' return copy of data'''
        self._con_lock.acquire()
        rv = list(self.container)
        self._con_lock.release()
        return rv

    def update_con(self, data):
        self._con_lock.acquire()
        if not data:
            self.container = []
        else:
            self.container.extend(data)
        self._con_lock.release()


    @abc.abstractmethod
    def loop(self):
        pass

    def close(self):
        self._running = False
        if self.daemon.is_alive():
            self.daemon.join()

class Sound(Shared, Data):

    def __init__(self):
        import pyaudio as pa

        audio = pa.PyAudio()
        info = audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(numdevices):
            devinfo = audio.get_device_info_by_host_api_device_index(0, i)
            if devinfo.get('maxInputChannels') > 0 and devinfo.get('name') != 'Hue Sync Audio':
                     break
        devinfo = audio.get_device_info_by_host_api_device_index(0, i)
        kw = dict(
         rate = 44100,
         format = pa.paInt16,
         channels = devinfo.get('maxInputChannels'),
         input = True,
         output = False,
         frames_per_buffer = int(1024*4),
         input_device_index = i)

        self.audio = audio
        self.stream = audio.open(**kw)
        self.stream.start_stream()

        self.chunk_size = 1024 * 1

        super().__init__()

    def stream_read(self):
            data = self.stream.read(self.chunk_size, exception_on_overflow = False)
            data = np.frombuffer(data, dtype=np.int16).tolist()
            return data

    @limit_by_time(3)
    def listen(self):
        data = self.stream_read()
        if data:
            self.update_con(data)

    def loop(self):
        from collections import deque
        _prev = deque(maxlen=5*1024)
        while self._running:
            data = self.stream_read()
            _data = [abs(i) for i in data]
            if sum(_data) / len(_data) > 300:
                if _prev:
                    self.update_con(_prev)
                while True:
                    try:
                        self.listen()
                    except TimeoutError as e:
                        self.update_con(None)
                        break
            else:
                _prev.extend(data)

    def close(self):
        try:
            super().close()
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()



