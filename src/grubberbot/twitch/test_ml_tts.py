
dependencies = [
    'torch', 'gdown', 'pysbd', 'gruut', 'anyascii', 'pypinyin', 'coqpit', 'mecab-python3', 'unidic-lite',
]
import sounddevice
import torch
import TTS
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer

message = (
    "Are you kidding? "
    "What the **** are you talking about man? "
    "You are the biggest loser i've ever seen in my life! "
    "You were doing pee pee in your pampers when i was beating players much "
        "stronger then you! "
    "You are not professional, because professionals know how to lose and "
        "congratulate opponents. you are like a girl crying after i beat you! "

)

manager = ModelManager('models.json')

    model_path, config_path, model_item = manager.download_model(model_name)
    vocoder_name = model_item[
        'default_vocoder'] if vocoder_name is None else vocoder_name
    vocoder_path, vocoder_config_path, _ = manager.download_model(vocoder_name)

synthesizer = Synthesizer(
    tts_checkpoint='tts_models/en/ljspeech/tacotron2-DDC',
    tts_config_path=None,
    #speakers_file_path,
    #language_ids_file_path,
    #vocoder_path,
    #vocoder_config_path,
    #encoder_path,
    #encoder_config_path,
    #args.use_cuda,
)
#wav = synthesizer.tts(args.text, args.speaker_idx, args.language_idx, args.speaker_wav)
#synthesizer.save_wav(wav, args.out_path)

raise Exception

def gen_synthesizer(
        model_name='tts_models/en/ljspeech/tacotron2-DCA',
        vocoder_name='vocoder_models/en/ljspeech/hifigan_v2',
        use_cuda=False):
    """TTS entry point for PyTorch Hub that provides a Synthesizer object to synthesize speech from a give text.

    Example:
        >>> synthesizer = torch.hub.load('coqui-ai/TTS', 'tts', source='github')
        >>> wavs = synthesizer.tts("This is a test! This is also a test!!")
            wavs - is a list of values of the synthesized speech.

    Args:
        model_name (str, optional): One of the model names from .model.json. Defaults to 'tts_models/en/ljspeech/tacotron2-DCA'.
        vocoder_name (str, optional): One of the model names from .model.json. Defaults to 'vocoder_models/en/ljspeech/multiband-melgan'.
        pretrained (bool, optional): [description]. Defaults to True.

    Returns:
        TTS.utils.synthesizer.Synthesizer: Synthesizer object wrapping both vocoder and tts models.
    """
    manager = ModelManager()

    model_path, config_path, model_item = manager.download_model(model_name)
    vocoder_name = model_item[
        'default_vocoder'] if vocoder_name is None else vocoder_name
    vocoder_path, vocoder_config_path, _ = manager.download_model(vocoder_name)

    # create synthesizer
    synt = Synthesizer(tts_checkpoint=model_path,
                       tts_config_path=config_path,
                       vocoder_checkpoint=vocoder_path,
                       vocoder_config=vocoder_config_path,
                       use_cuda=use_cuda)
    return synt


def tts(message):
    synthesizer = gen_synthesizer()
    output = synthesizer.tts(message)
    sounddevice.play(output, 44100/2)
    sounddevice.wait()


if __name__ == '__main__':
    message = (
        "Are you kidding? "
        "What the **** are you talking about man? "
        "You are the biggest loser i've ever seen in my life! "
        "You were doing pee pee in your pampers when i was beating players much "
            "stronger then you! "
        "You are not professional, because professionals know how to lose and "
            "congratulate opponents, you are like a girl crying after i beat you! "

    )
    print(message)
    #tts(message)
    #synthesizer = torch.hub.load('coqui-ai/TTS:dev', 'tts', source='github')
