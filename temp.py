# import json
# import vosk
# import wave


# model = vosk.Model("vosk-model-en-us-0.22-lgraph")
# fl = wave.open("server_side_audio.wav", "rb")

# recognizer = vosk.KaldiRecognizer(model, fl.getframerate())
# question = ""

# try:
#     while True:
#         data = fl.readframes(4000)
#         if len(data) == 0:
#             break
#         if recognizer.AcceptWaveform(data):
#             result = recognizer.FinalResult()
#             print(result)
#             question += json.loads(result)["text"] + " "
# except Exception as e:
#     print(f"Error: {e}")
      
# print("Here's what I heard:")
# print(question)
