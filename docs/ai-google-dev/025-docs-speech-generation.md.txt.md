---
title: Speech generation
url: https://ai.google.dev/gemini-api/docs/speech-generation.md.txt
source: llms
fetched_at: 2026-04-29T11:17:00.325341151-03:00
rendered_js: false
word_count: 1323
summary: This guide demonstrates how to use the Gemini API to generate single and multi-speaker audio from text, providing instructions on configuration and implementation across various programming languages.
tags:
    - gemini-api
    - text-to-speech
    - audio-generation
    - multi-speaker
    - speech-synthesis
    - developer-guide
category: guide
optimized: true
optimized_at: 2026-04-29T12:00:00Z
---
The Gemini API transforms text input into single-speaker or multi-speaker audio. TTS is *controllable*—use natural language to structure interactions and guide *style*, *accent*, *pace*, and *tone*. [Try in AI Studio](https://aistudio.google.com/apps/bundled/voice-library?showPreview=truew)

TTS differs from [[003-docs-live-api-get-started-sdk|Live API]] speech generation. Live API excels in dynamic conversational contexts; TTS is tailored for exact text recitation with fine-grained control, such as podcast or audiobook generation.

> [!WARNING]
> **Preview:** Gemini text-to-speech (TTS) is in [Preview](https://ai.google.dev/gemini-api/docs/models#preview).

## Before you begin

- Use a Gemini model variant with TTS capabilities (see [Supported models](#supported-models))
- [Test TTS models in AI Studio](https://aistudio.google.com/generate-speech) before building

> [!NOTE]
> TTS models accept text-only inputs and produce audio-only outputs. Review [Limitations](#limitations) for restrictions.

## Single-speaker TTS

Set `response_modalities` to `"AUDIO"` and pass a `SpeechConfig` with `VoiceConfig`. Choose a voice from prebuilt [output voices](#voice-options).

### Python

```python
from google import genai
from google.genai import types
import wave

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

client = genai.Client()

response = client.models.generate_content(
   model="gemini-3.1-flash-tts-preview",
   contents="Say cheerfully: Have a wonderful day!",
   config=types.GenerateContentConfig(
      response_modalities=["AUDIO"],
      speech_config=types.SpeechConfig(
         voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
               voice_name='Kore',
            )
         )
      ),
   )
)

data = response.candidates[0].content.parts[0].inline_data.data
file_name='out.wav'
wave_file(file_name, data)
```

> [!NOTE]
> More code samples in the [TTS Get Started cookbook](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_TTS.ipynb).

### JavaScript

```javascript
import {GoogleGenAI} from '@google/genai';
import wav from 'wav';

async function saveWaveFile(
   filename,
   pcmData,
   channels = 1,
   rate = 24000,
   sampleWidth = 2,
) {
   return new Promise((resolve, reject) => {
      const writer = new wav.FileWriter(filename, {
            channels,
            sampleRate: rate,
            bitDepth: sampleWidth * 8,
      });

      writer.on('finish', resolve);
      writer.on('error', reject);

      writer.write(pcmData);
      writer.end();
   });
}

async function main() {
   const ai = new GoogleGenAI({});

   const response = await ai.models.generateContent({
      model: "gemini-3.1-flash-tts-preview",
      contents: [{ parts: [{ text: 'Say cheerfully: Have a wonderful day!' }] }],
      config: {
            responseModalities: ['AUDIO'],
            speechConfig: {
               voiceConfig: {
                  prebuiltVoiceConfig: { voiceName: 'Kore' },
               },
            },
      },
   });

   const data = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
   const audioBuffer = Buffer.from(data, 'base64');

   const fileName = 'out.wav';
   await saveWaveFile(fileName, audioBuffer);
}
await main();
```

### REST

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-tts-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
        "contents": [{
          "parts":[{
            "text": "Say cheerfully: Have a wonderful day!"
          }]
        }],
        "generationConfig": {
          "responseModalities": ["AUDIO"],
          "speechConfig": {
            "voiceConfig": {
              "prebuiltVoiceConfig": {
                "voiceName": "Kore"
              }
            }
          }
        },
        "model": "gemini-3.1-flash-tts-preview",
    }' | jq -r '.candidates[0].content.parts[0].inlineData.data' | \
              base64 --decode >out.pcm
ffmpeg -f s16le -ar 24000 -ac 1 -i out.pcm out.wav
```

## Multi-speaker TTS

Use `MultiSpeakerVoiceConfig` with up to 2 speakers as `SpeakerVoiceConfig`. Define each `speaker` with names matching the [prompt](#controlling-speech-style-with-prompts):

### Python

```python
from google import genai
from google.genai import types
import wave

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

client = genai.Client()

prompt = """TTS the following conversation between Joe and Jane:
         Joe: How's it going today Jane?
         Jane: Not too bad, how about you?"""

response = client.models.generate_content(
   model="gemini-3.1-flash-tts-preview",
   contents=prompt,
   config=types.GenerateContentConfig(
      response_modalities=["AUDIO"],
      speech_config=types.SpeechConfig(
         multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
            speaker_voice_configs=[
               types.SpeakerVoiceConfig(
                  speaker='Joe',
                  voice_config=types.VoiceConfig(
                     prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Kore',
                     )
                  )
               ),
               types.SpeakerVoiceConfig(
                  speaker='Jane',
                  voice_config=types.VoiceConfig(
                     prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Puck',
                     )
                  )
               ),
            ]
         )
      )
   )
)

data = response.candidates[0].content.parts[0].inline_data.data
file_name='out.wav'
wave_file(file_name, data)
```

### JavaScript

```javascript
import {GoogleGenAI} from '@google/genai';
import wav from 'wav';

async function saveWaveFile(filename, pcmData, channels = 1, rate = 24000, sampleWidth = 2) {
   return new Promise((resolve, reject) => {
      const writer = new wav.FileWriter(filename, {
            channels, sampleRate: rate, bitDepth: sampleWidth * 8,
      });
      writer.on('finish', resolve);
      writer.on('error', reject);
      writer.write(pcmData);
      writer.end();
   });
}

async function main() {
   const ai = new GoogleGenAI({});

   const prompt = `TTS the following conversation between Joe and Jane:
         Joe: How's it going today Jane?
         Jane: Not too bad, how about you?`;

   const response = await ai.models.generateContent({
      model: "gemini-3.1-flash-tts-preview",
      contents: [{ parts: [{ text: prompt }] }],
      config: {
            responseModalities: ['AUDIO'],
            speechConfig: {
               multiSpeakerVoiceConfig: {
                  speakerVoiceConfigs: [
                        { speaker: 'Joe', voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Kore' } } },
                        { speaker: 'Jane', voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Puck' } } }
                  ]
               }
            }
      }
   });

   const data = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
   await saveWaveFile('out.wav', Buffer.from(data, 'base64'));
}
await main();
```

### REST

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-tts-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts":[{"text": "TTS: Joe: Hows it going today Jane? Jane: Not too bad..."}]}],
    "generationConfig": {
      "responseModalities": ["AUDIO"],
      "speechConfig": {
        "multiSpeakerVoiceConfig": {
          "speakerVoiceConfigs": [
            {"speaker": "Joe", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}},
            {"speaker": "Jane", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Puck"}}}
          ]
        }
      }
    },
    "model": "gemini-3.1-flash-tts-preview"
  }' | jq -r '.candidates[0].content.parts[0].inlineData.data' | base64 --decode > out.pcm
ffmpeg -f s16le -ar 24000 -ac 1 -i out.pcm out.wav
```

## Controlling speech style with prompts

Control style, tone, accent, and pace using natural language prompts or [audio tags](#audio-tags).

**Single-speaker:**
```
Say in an spooky voice:
"By the pricking of my thumbs... [short pause]
[whisper] Something wicked this way comes"
```

**Multi-speaker:**
```
Make Speaker1 sound tired and bored, and Speaker2 sound excited and happy:
Speaker1: So... [yawn] what's on the agenda today?
Speaker2: You're never going to guess!
```

Use a [voice option](#voice-options) that corresponds to the style. *Enceladus*'s breathiness emphasizes "tired/bored"; *Puck*'s upbeat tone complements "excited/happy".

> [!TIP]
> [Voice Library](https://aistudio.google.com/apps/bundled/voice-library?showPreview=true) in AI Studio is great for trying out styles and voices.

## Generating a prompt for audio

Use other models to generate a transcript first, then pass to TTS:

### Python

```python
from google import genai
from google.genai import types

client = genai.Client()

transcript = client.models.generate_content(
   model="gemini-3-flash-preview",
   contents="""Generate a short transcript around 100 words that reads
            like it was clipped from a podcast by excited herpetologists.
            The hosts names are Dr. Anya and Liam.""").text

response = client.models.generate_content(
   model="gemini-3.1-flash-tts-preview",
   contents=transcript,
   config=types.GenerateContentConfig(
      response_modalities=["AUDIO"],
      speech_config=types.SpeechConfig(
         multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
            speaker_voice_configs=[
               types.SpeakerVoiceConfig(
                  speaker='Dr. Anya',
                  voice_config=types.VoiceConfig(
                     prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name='Kore')
                  )
               ),
               types.SpeakerVoiceConfig(
                  speaker='Liam',
                  voice_config=types.VoiceConfig(
                     prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name='Puck')
                  )
               ),
            ]
         )
      )
   )
)
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

async function main() {
  const transcript = await ai.models.generateContent({
     model: "gemini-3-flash-preview",
     contents: "Generate a short transcript around 100 words that reads like a podcast by excited herpetologists. Hosts: Dr. Anya and Liam.",
  });

  const response = await ai.models.generateContent({
     model: "gemini-3.1-flash-tts-preview",
     contents: transcript,
     config: {
        responseModalities: ['AUDIO'],
        speechConfig: {
           multiSpeakerVoiceConfig: {
              speakerVoiceConfigs: [
                 { speaker: "Dr. Anya", voiceConfig: { prebuiltVoiceConfig: {voiceName: "Kore"}} },
                 { speaker: "Liam", voiceConfig: { prebuiltVoiceConfig: {voiceName: "Puck"}} }
              ]
            }
        }
    }
  });
}
await main();
```

## Voice options

30 voices available via `voice_name`:

|---|---|---|
| **Zephyr** -- *Bright* | **Puck** -- *Upbeat* | **Charon** -- *Informative* |
| **Kore** -- *Firm* | **Fenrir** -- *Excitable* | **Leda** -- *Youthful* |
| **Orus** -- *Firm* | **Aoede** -- *Breezy* | **Callirrhoe** -- *Easy-going* |
| **Autonoe** -- *Bright* | **Enceladus** -- *Breathy* | **Iapetus** -- *Clear* |
| **Umbriel** -- *Easy-going* | **Algieba** -- *Smooth* | **Despina** -- *Smooth* |
| **Erinome** -- *Clear* | **Algenib** -- *Gravelly* | **Rasalgethi** -- *Informative* |
| **Laomedeia** -- *Upbeat* | **Achernar** -- *Soft* | **Alnilam** -- *Firm* |
| **Schedar** -- *Even* | **Gacrux** -- *Mature* | **Pulcherrima** -- *Forward* |
| **Achird** -- *Friendly* | **Zubenelgenubi** -- *Casual* | **Vindemiatrix** -- *Gentle* |
| **Sadachbia** -- *Lively* | **Sadaltager** -- *Knowledgeable* | **Sulafat** -- *Warm* |

[Hear all voices in AI Studio](https://aistudio.google.com/generate-speech).

## Supported languages

TTS models detect input language automatically:

| Language | BCP-47 | Language | BCP-47 |
|---|---|---|---|
| Arabic | ar | Filipino | fil |
| Bangla | bn | Finnish | fi |
| Dutch | nl | Galician | gl |
| English | en | Georgian | ka |
| French | fr | Greek | el |
| German | de | Gujarati | gu |
| Hindi | hi | Haitian Creole | ht |
| Indonesian | id | Hebrew | he |
| Italian | it | Hungarian | hu |
| Japanese | ja | Icelandic | is |
| Korean | ko | Javanese | jv |
| Marathi | mr | Kannada | kn |
| Polish | pl | Konkani | kok |
| Portuguese | pt | Lao | lo |
| Romanian | ro | Latin | la |
| Russian | ru | Latvian | lv |
| Spanish | es | Lithuanian | lt |
| Tamil | ta | Luxembourgish | lb |
| Telugu | te | Macedonian | mk |
| Thai | th | Maithili | mai |
| Turkish | tr | Malagasy | mg |
| Ukrainian | uk | Malay | ms |
| Vietnamese | vi | Malayalam | ml |
| Afrikaans | af | Mongolian | mn |
| Albanian | sq | Nepali | ne |
| Amharic | am | Norwegian, Bokmål | nb |
| Armenian | hy | Norwegian, Nynorsk | nn |
| Azerbaijani | az | Odia | or |
| Basque | eu | Pashto | ps |
| Belarusian | be | Persian | fa |
| Bulgarian | bg | Punjabi | pa |
| Burmese | my | Serbian | sr |
| Catalan | ca | Sindhi | sd |
| Cebuano | ceb | Sinhala | si |
| Chinese, Mandarin | cmn | Slovak | sk |
| Croatian | hr | Slovenian | sl |
| Czech | cs | Swahili | sw |
| Danish | da | Swedish | sv |
| Estonian | et | Urdu | ur |

## Supported models

| Model | Single speaker | Multispeaker |
|---|---|---|
| [Gemini 3.1 Flash TTS Preview](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-tts-preview) | ✔️ | ✔️ |
| [Gemini 2.5 Flash Preview TTS](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash-preview-tts) | ✔️ | ✔️ |
| [Gemini 2.5 Pro Preview TTS](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-pro-preview-tts) | ✔️ | ✔️ |

## Prompting guide

Gemini TTS uses a large language model that knows *what to say and how to say it*. Out of the box, it natively interprets transcripts for natural delivery.

### Audio tags

Inline modifiers for granular control over tone, pace, and delivery. Also add non-verbal sounds: `[cough]`, `[sighs]`, `[gasp]`.

> [!NOTE]
> For non-English transcripts, use English audio tags for best results.

**Change emphasis:**
- `[excitedly]` Hey there, I'm a new text to speech model...
- `[bored]` Hey there, I'm a new text to speech model...
- `[reluctantly]` Hey there, I'm a new text to speech model...

**Change pace:**
- `[very fast]` Hey there, I'm a new text to speech model...
- `[very slow]` Hey there, I'm a new text to speech model...
- `[sarcastically, one painfully slow word at a time]` Hey there...

**Combine pace with emphasis:**
- `[whispers]` Hey there... `[shouting]` and I can say things... `[whispers]` How can I help

**Creative styles:**
- `[like a cartoon dog]` Hey there...
- `[like dracula]` Hey there...

**Common tags:**

|---|---|---|---|
| `[amazed]` | `[crying]` | `[curious]` | `[excited]` |
| `[sighs]` | `[gasp]` | `[giggles]` | `[laughs]` |
| `[mischievously]` | `[panicked]` | `[sarcastic]` | `[serious]` |
| `[shouting]` | `[tired]` | `[trembling]` | `[whispers]` |

### Advanced prompting

System instruction for the model. Includes:

- **Audio Profile** — Persona, character identity, archetype, age, background
- **Scene** — Physical environment and "vibe"
- **Director's Notes** — Style, breathing, pacing, articulation, accent
- **Sample context** — Starting point for natural entry
- **Transcript** — Text to speak (topic/writing style should correlate to directions)
- **Audio tags** — Inline modifiers

> [!NOTE]
> Ask Gemini to help build a prompt—just give it a blank outline and ask it to sketch out a character.

**Full prompt example:**
```markdown
# AUDIO PROFILE: Jaz R.
## "The Morning Hype"

## THE SCENE: The London Studio
It is 10:00 PM in a glass-walled studio overlooking the moonlit London skyline,
but inside, it is blindingly bright. The red "ON AIR" tally light is blazing.
Jaz is standing up, bouncing on the balls of their heels to the rhythm of a
thumping backing track. Their hands fly across the faders on a massive mixing
desk.

### DIRECTOR'S NOTES
Style:
* The "Vocal Smile": You must hear the grin in the audio. The soft palate is
always raised to keep the tone bright, sunny, and explicitly inviting.
* Dynamics: High projection without shouting. Punchy consonants and elongated
vowels on excitement words (e.g., "Beauuutiful morning").

Pacing: Speaks at an energetic pace, keeping up with the fast music. High-speed
delivery with fluid transitions—no dead air.

Accent: Jaz is from Brixton, London.

### SAMPLE CONTEXT
Jaz is the industry standard for Top 40 radio, high-octane event promos, or any
script requiring charismatic Estuary accent and 11/10 infectious energy.

#### TRANSCRIPT
[excitedly] Yes, massive vibes in the studio! You are locked in and it is
absolutely popping off in London right now. If you're stuck on the tube, or
just sat there pretending to work... stop it. [shouting] Turn this up! We've got
the project roadmap landing in three, two... let's go!
```

**Element breakdown:**

| Element | Description |
|---|---|
| **Audio Profile** | Name and role/archetype (e.g., Radio DJ, Podcaster) |
| **Scene** | Location, mood, environmental details establishing tone |
| **Director's Notes** | Performance guidance: Style, Pacing, Accent—don't overspecify |
| **Style** | Tone: upbeat, energetic, relaxed, bored, "vocal smile", dynamics |
| **Accent** | Be specific: "British English as heard in Croydon" vs "British Accent" |
| **Pacing** | Overall tempo and variation: fast, slow, "Drift" (slow and liquid) |
| **Transcript** | Exact words + audio tags in square brackets |

## Limitations

- TTS accepts text-only input, generates audio-only output
- Context window: 32k tokens
- No streaming
- Language support per table above

**Gemini 3.1 Flash TTS Preview specific:**

- **Voice inconsistency:** Output may not match selected speaker if prompt tone doesn't align with voice profile
- **Longer outputs:** Quality may drift with outputs longer than a few minutes—split transcripts
- **Text token returns:** Occasional `500` error—implement retry logic
- **Prompt classifier false rejections:** Vague prompts may be rejected or read aloud—add preamble: "Synthesize the following as speech" and label transcript clearly

## What's next

- [Audio generation cookbook](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_TTS.ipynb)
- [[003-docs-live-api-get-started-sdk|Live API]] for interactive audio generation
- [[006-docs-audio|Audio understanding]] for audio inputs

#gemini-api #text-to-speech #audio-generation #speech-synthesis