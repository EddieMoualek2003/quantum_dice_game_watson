import wave
import pyaudio
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# 1. Record audio from microphone
def record_audio(filename="output.wav", duration=5):
    chunk = 1024  # Record in chunks
    format = pyaudio.paInt16
    channels = 1
    rate = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=format, channels=channels,
                    rate=rate, input=True,
                    frames_per_buffer=chunk)

    frames = []

    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

# 2. Transcribe with IBM Watson
def transcribe_ibm(filename):
    api_key = 'LQ9GZIfQd2pVXX3M9Lz2ng40_OvkuV-o1zecTs5bL9Bo'
    url = 'https://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/2bb974d7-be23-4067-855f-0c8265933ac8'

    authenticator = IAMAuthenticator(api_key)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(url)

    with open(filename, 'rb') as audio_file:
        result = speech_to_text.recognize(
            audio=audio_file,
            content_type='audio/wav',
            model='en-US_BroadbandModel'
        ).get_result()

    for res in result['results']:
        return res['alternatives'][0]['transcript']