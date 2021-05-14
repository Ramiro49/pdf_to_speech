import slate3k
import requests
import base64
import numpy
import pydub
import os

google_cloud_api_key = "YOUR API KEY"


def read_from_pdf(name_pdf_file, name_of_out_file="text"):

    with open(f"PDF/{name_pdf_file}.pdf", mode="rb") as pdf_file:
        list_text_pages = slate3k.PDF(pdf_file)

    text = ""
    for page in list_text_pages:
        text += page
    text = text.replace("\x0c", "")

    with open(f"PLAIN TEXT/{name_of_out_file}.txt", mode="w", encoding="utf-8") as text_file:
        text_file.write(text)

    return text


def text_to_speech(text_to_convert, audio_name):
    headers = {
        "x-goog-api-key": google_cloud_api_key
    }

    request_body = {
        "input": {
            "text": text_to_convert
        },
        "voice": {
            "languageCode": "es-us",
            "name": "es-US-Wavenet-A",
            "ssmlGender": "Female"
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": 0.85,
            "pitch": -5
        }
    }

    response = requests.post("https://texttospeech.googleapis.com/v1/text:synthesize",
                             json=request_body,
                             headers=headers)

    response.raise_for_status()

    audio_str = base64.b64decode(response.json()["audioContent"])

    with open(f"MP3/{audio_name}.mp3", mode="wb") as audio_file:
        audio_file.write(audio_str)


name_file = input("Write the name of your PDF file (Without extension):\n -> ")

plain_text = read_from_pdf(name_file)

# Google Cloud TTS support maximum 5000 characters per request
if len(plain_text) > 5000:
    # Create a list with all the sentences
    list_sentences = plain_text.split(".")
    divider = (len(list_sentences) // 5000) + 2

    # Divide the list of sentences into equal parts less than 5000 characters
    list_txt_chunks = numpy.array_split(numpy.array(list_sentences), divider)

    complete_audio = pydub.AudioSegment.empty()

    # Make a TTS request to Google
    for txt_chunk in list_txt_chunks:
        text_to_speech(txt_chunk, "audio_chunk")
        part_audio = pydub.AudioSegment.from_mp3("MP3/audio_chunk.mp3")
        complete_audio += part_audio

    # Export the complete audio
    complete_audio.export(f"MP3/{name_file}.mp3", format="mp3")
    # Delete the audio_chunk.mp3 file
    os.remove("MP3/audio_chunk.mp3")

else:
    text_to_speech(plain_text, name_file)


print("\nSuccess!")
