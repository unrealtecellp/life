import torch
# from phonemizer.backend import EspeakBackend
# from phonemizer.separator import Separator
from app.lifemodels.controller.espeakIPA import to_ipa

from app.controller import life_logging

torch.set_num_threads(8)

logger = life_logging.get_logger()

def get_boundaries(model_name, model_params):
    # effective_func = getattr()
    timestamps, cleaned_audio = globals(
    )['get_boundaries_'+model_name](model_params)
    # timestamps, cleaned_audio = effective_func()
    return timestamps, cleaned_audio


def get_transcription(model_name, **kwargs):
    transcription = globals()['get_transcription_'+model_name](**kwargs)
    return transcription


def get_transliteration(data, source_script, target_script, **kwargs):
    if target_script == 'IPA':
        transcription_words = to_ipa(data.split(' '), lang_code = source_script)
        logger.info('Data %s, IPA Transcription %s', data, transcription_words)
        transcription = ' '.join(transcription_words)
    else:
        all_functs = globals()
        current_funct_name = 'get_transliteration_'+source_script + '_to_'+target_script
        if current_funct_name in all_functs:
            transcription = globals()[current_funct_name](data, **kwargs)
        else:
            transcription = ''
    return transcription

# This gets the timestamps of the parts of the audio with voice activity; also
# returns an audio after removing the pauses, if asked to


def get_boundaries_vadsilero(model_params):
    audio_file = model_params["audio_file"]
    SAMPLING_RATE = model_params["SAMPLING_RATE"]
    remove_pauses = model_params["remove_pauses"]
    USE_ONNX = model_params["USE_ONNX"]
    model_path = model_params['model_path']
    min_speech_duration = model_params['minimum_speech_duration']
    min_silence_duration = model_params['minimum_silence_duration']

    model, utils = torch.hub.load(repo_or_dir=model_path,
                                  model='silero_vad',
                                  force_reload=False,
                                  onnx=USE_ONNX)

    (get_speech_timestamps,
     save_audio,
     read_audio,
     VADIterator,
     collect_chunks) = utils

    wav = read_audio(audio_file, sampling_rate=SAMPLING_RATE)

    # get speech timestamps from full audio file
    speech_timestamps = get_speech_timestamps(
        wav, model, return_seconds=True, sampling_rate=SAMPLING_RATE, min_speech_duration_ms=min_speech_duration, min_silence_duration_ms=min_silence_duration)

    # TODO: implement this to save audio without pauses in MongoDB
    if remove_pauses:
        # wav = save_audio('only_speech.wav',
        #  collect_chunks(speech_timestamps, wav), sampling_rate=SAMPLING_RATE)
        wav = collect_chunks(speech_timestamps, wav)

    return speech_timestamps, wav


# Must return a list of transcriptions depending on the number of boundaries
def get_transcription_wav2vec2(model_params):
    transcriptions = {}
    audio_file = model_params["audio_file"]
    boundaries = model_params["boundaries"]
    model_path = model_params['model_path']
    # boundaries are a list of dictionaries with "start" and "end" as keys and their
    # values are the start and end position of boundary. The audio may be cropped using
    # this and individual boundaries may be autotranscribed
    return transcriptions


# def get_transliteration_Devanagari_to_IPA(data, **kwargs):
