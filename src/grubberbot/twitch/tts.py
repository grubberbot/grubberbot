#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from argparse import RawTextHelpFormatter

# pylint: disable=redefined-outer-name, unused-argument
from pathlib import Path

from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    if v.lower() in ("no", "false", "f", "n", "0"):
        return False
    raise argparse.ArgumentTypeError("Boolean value expected.")


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class TTS:
    def __init__(
        self,
        list_models=False,
        model_name="tts_models/en/ljspeech/tacotron2-DDC",
        out_path="tts_output.wav",
        use_cuda=False,
        text=None,
        vocoder_name=None,
        config_path=None,
        model_path=None,
        vocoder_path=None,
        vocoder_config_path=None,
        encoder_path=None,
        encoder_config_path=None,
        speakers_file_path=None,
        language_ids_file_path=None,
        speaker_idx=None,
        language_idx=None,
        speaker_wav=None,
        gst_style=None,
        list_speaker_idxs=False,
        list_language_idxs=False,
        save_spectogram=False,
    ):

        self.text = text

        self.list_models = list_models
        self.model_name = model_name
        self.vocoder_name = vocoder_name
        self.config_path = config_path
        self.model_path = model_path
        self.out_path = out_path
        self.use_cuda = use_cuda
        self.vocoder_path = vocoder_path
        self.vocoder_config_path = vocoder_config_path
        self.encoder_path = encoder_path
        self.encoder_config_path = encoder_config_path
        self.speakers_file_path = speakers_file_path
        self.language_ids_file_path = language_ids_file_path
        self.speaker_idx = speaker_idx
        self.anguage_idx = language_idx
        self.speaker_wav = speaker_wav
        self.gst_style = gst_style
        self.list_speaker_idxs = list_speaker_idxs
        self.list_language_idxs = list_language_idxs
        self.save_spectogram = save_spectogram

    def speak(self, text):

        # load model manager
        path = Path(__file__).parent / "models.json"
        manager = ModelManager(path)

        model_path = None
        config_path = None
        speakers_file_path = None
        language_ids_file_path = None
        vocoder_path = None
        vocoder_config_path = None
        encoder_path = None
        encoder_config_path = None

        # CASE1: list pre-trained TTS models
        if args.list_models:
            manager.list_models()
            sys.exit()

        # CASE2: load pre-trained model paths
        if args.model_name is not None and not args.model_path:
            model_path, config_path, model_item = manager.download_model(
                args.model_name
            )
            args.vocoder_name = (
                model_item["default_vocoder"]
                if args.vocoder_name is None
                else args.vocoder_name
            )

        if args.vocoder_name is not None and not args.vocoder_path:
            vocoder_path, vocoder_config_path, _ = manager.download_model(
                args.vocoder_name
            )

        # CASE3: set custom model paths
        if args.model_path is not None:
            model_path = args.model_path
            config_path = args.config_path
            speakers_file_path = args.speakers_file_path
            language_ids_file_path = args.language_ids_file_path

        if args.vocoder_path is not None:
            vocoder_path = args.vocoder_path
            vocoder_config_path = args.vocoder_config_path

        if args.encoder_path is not None:
            encoder_path = args.encoder_path
            encoder_config_path = args.encoder_config_path

        # load models
        synthesizer_arguments = [
            model_path,
            config_path,
            speakers_file_path,
            language_ids_file_path,
            vocoder_path,
            vocoder_config_path,
            encoder_path,
            encoder_config_path,
            args.use_cuda,
        ]
        print(synthesizer_arguments)
        synthesizer = Synthesizer(*synthesizer_arguments)

        # query speaker ids of a multi-speaker model.
        if args.list_speaker_idxs:
            print(
                " > Available speaker ids: (Set --speaker_idx flag to one of these values to use the multi-speaker model."
            )
            print(synthesizer.tts_model.speaker_manager.speaker_ids)
            return

        # query langauge ids of a multi-lingual model.
        if args.list_language_idxs:
            print(
                " > Available language ids: (Set --language_idx flag to one of these values to use the multi-lingual model."
            )
            print(synthesizer.tts_model.language_manager.language_id_mapping)
            return

        # check the arguments against a multi-speaker model.
        if synthesizer.tts_speakers_file and (
            not args.speaker_idx and not args.speaker_wav
        ):
            print(
                " [!] Looks like you use a multi-speaker model. Define `--speaker_idx` to "
                "select the target speaker. You can list the available speakers for this model by `--list_speaker_idxs`."
            )
            return

        # RUN THE SYNTHESIS
        print(" > Text: {}".format(args.text))

        # kick it
        wav = synthesizer.tts(
            args.text, args.speaker_idx, args.language_idx, args.speaker_wav
        )

        # save the results
        import sounddevice

        print("playing audio")
        sounddevice.play(wav, synthesizer.vocoder_config.audio["sample_rate"])
        sounddevice.wait()

        # print(" > Saving output to {}".format(args.out_path))
        # synthesizer.save_wav(wav, args.out_path)


if __name__ == "__main__":
    message = (
        "Are you kidding? "
        "What the **** are you talking about man? "
        "You are the biggest loser i've ever seen in my life! "
        "You were doing pee pee in your pampers when i was beating players much "
        "stronger then you! "
        "You are not professional, because professionals know how to lose and "
        "congratulate opponents. you are like a girl crying after i beat you! "
    )
    main(text=message)
