# odas_python_wrapper
A Python 3 wrapper for IntroLab's ODAS. The wrapper receives from odaslive:
1. audio source location and energy (unfiltered), JSON messages
2. location of audio sources being tracked, as JSON messages
3. a data stream containing "separated" audio (i.e. beamforming aimed at the tracked source)
4. a data stream containing "post-filtered" audio (i.e. separated as well as post-filtered)

odas_wrapper.py can write save data streams as a WAV file.

Usage:
```bash
# must launch odas_wrapper.py before launching odaslive
python3 odas_python_wrapper.py

# in a separate terminal window
/home/pi/odas/bin/odaslive -c /home/pi/odas/config/odaslive/respeaker_4_mic_array.cfg
```
