import sounddevice as sd
import soundfile as sf
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# === 1. Record from USB Microphone ===
def record_audio(filename="output.wav", duration=5, samplerate=44100, mic_index=1):
    sd.default.device = (mic_index, None)  # Force input device (USB mic)

    print("[INFO] Recording from USB mic...")
    recording = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype='int16'
    )
    sd.wait()  # Wait for recording to finish

    sf.write(filename, recording, samplerate)
    print(f"[INFO] Saved recording to {filename}")

# === 2. Transcribe with IBM Watson ===
def transcribe_ibm(filename):
    api_key = 'LQ9GZIfQd2pVXX3M9Lz2ng40_OvkuV-o1zecTs5bL9Bo'
    url = 'https://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/2bb974d7-be23-4067-855f-0c8265933ac8'

    authenticator = IAMAuthenticator(api_key)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(url)

    print("[INFO] Transcribing with IBM Watson...")
    with open(filename, 'rb') as audio_file:
        result = speech_to_text.recognize(
            audio=audio_file,
            content_type='audio/wav',
            model='en-US_BroadbandModel'
        ).get_result()

    for res in result['results']:
        return res['alternatives'][0]['transcript']

    return ""
