import gizmo
from subsync import assets
from subsync import error
import json
import os

import logging
logger = logging.getLogger(__name__)


_speechModels = {}

def loadSpeechModel(lang):
    if lang in _speechModels:
        return _speechModels[lang]

    logger.info('loading speech recognition model for language %s', lang)

    path = assets.getLocalAsset('speech', [lang], raiseIfMissing=True)
    with open(path, encoding='utf8') as fp:
        model = json.load(fp)

    # fix paths
    if 'sphinx' in model:
        dirname = os.path.abspath(os.path.dirname(path))
        sphinx = model['sphinx']
        for key, val in sphinx.items():
            if val.startswith('./'):
                sphinx[key] = os.path.join(dirname, *val.split('/')[1:])

    logger.debug('model ready: %s', model)
    _speechModels[lang] = model
    return model


def createSpeechRec(model):
    speechRec = gizmo.SpeechRecognition()
    if 'sphinx' in model:
        for key, val in model['sphinx'].items():
            speechRec.setParam(key, val)
    return speechRec


def getSpeechAudioFormat(speechModel):
    try:
        sampleFormat = getattr(gizmo.AVSampleFormat,
                speechModel.get('sampleformat', 'S16'))

        sampleRate = speechModel.get('samplerate', 16000)
        if type(sampleRate) == str:
            sampleRate = int(sampleRate)

        return gizmo.AudioFormat(sampleFormat, sampleRate, 1)
    except:
        raise error.Error(_('Invalid speech audio format'))
