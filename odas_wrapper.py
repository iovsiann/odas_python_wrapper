#!/usr/bin/env python3
from socket import socket
from threading import Thread
import signal
import sys
import time
import wave


# /home/pi/odas/bin/odaslive -c /home/pi/odas/config/odaslive/respeaker_4_mic_array.cfg
class ODASWrapper(object):
    def __init__(self, host='localhost', on_tracked_source=None, on_raw_source=None,
                 on_post_filtered_audio=None, on_separated_audio=None):
        self.tracking_thread = Thread(target=self.run_server, args=(host, 9000, on_tracked_source))
        self.raw_source_thread = Thread(target=self.run_server, args=(host, 9001, on_raw_source))
        self.separated_audio_thread = Thread(target=self.run_raw_server, args=(host, 9002, on_separated_audio))
        self.post_filtered_audio_thread = Thread(target=self.run_raw_server, args=(host, 9003, on_post_filtered_audio))
        self._shutdown = False

    def start(self):
        self.tracking_thread.start()
        self.raw_source_thread.start()
        self.separated_audio_thread.start()
        self.post_filtered_audio_thread.start()
        return self

    def shutdown(self):
        self._shutdown = True
        self.tracking_thread.join()
        self.raw_source_thread.join()
        self.separated_audio_thread.join()
        self.post_filtered_audio_thread.join()

    def run_server(self, host, port, on_json_):
        sock = socket()
        sock.bind((host, port))
        sock.listen(1)

        print("Connecting ...")
        client, _ = sock.accept()
        print("Connected")
        buf = ''

        while not self._shutdown:
            buf += client.recv(256).decode('ascii')
            jsons = buf.split('}\n{')

            for json in jsons[:-1]:
                json = '{{{}}}'.format(json)
                callable(on_json_) and on_json_(json)
            buf = jsons[-1]

        client.close()
        sock.close()

    def run_raw_server(self, host, port, on_data_):
        sock = socket()
        sock.bind((host, port))
        sock.listen(1)

        print("Connecting ...")
        client, _ = sock.accept()
        print("Connected")

        while not self._shutdown:
            _data = client.recv(4096*10)
            callable(on_data_) and on_data_(_data)

        client.close()
        sock.close()


def on_tracked(json):
    # print("******************* filtered/tracked sources ***************")
    # print(json)
    pass


def on_raw(json):
    # print("******************* raw audio event *************************")
    # print(json)
    pass


def write_wav(data_, path, channels=1, sample_width=2, sample_rate=16000):
    wf = wave.open(path, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(sample_rate)
    wf.writeframes(data_)
    wf.close()


filtered_audio_frames = []
separated_audio_frames = []
odas = ODASWrapper(on_post_filtered_audio=lambda d: filtered_audio_frames.append(d),
                   on_separated_audio=lambda d: separated_audio_frames.append(d)).start()
try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    # write_wav(b''.join(separated_audio_frames), 'separated.wav', channels=4)
    write_wav(b''.join(filtered_audio_frames), 'post_filtered.wav', channels=4)

odas.shutdown()
