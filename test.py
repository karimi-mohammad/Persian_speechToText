#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import wave

wf = wave.open("test.wav", "rb")
model = Model("I:\computer\My projs\other\persian_stt/vosk-model-small-fa-0.42")
rec = KaldiRecognizer(model, wf.getframerate())


while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    rec.AcceptWaveform(data)


print(rec.FinalResult())
