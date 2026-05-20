---
title: Process audio...
url: https://ai.google.dev/gemini-api/docs/realtime-music-generation.md.txt
source: llms
fetched_at: 2026-04-29T11:16:58.312583207-03:00
rendered_js: false
word_count: 978
summary: This document explains how to use the Lyria RealTime API to stream, generate, and dynamically steer instrumental music using WebSockets.
tags:
    - gemini-api
    - lyria-realtime
    - music-generation
    - streaming-audio
    - websockets
    - ai-development
category: api
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
> [!WARNING]
> **Experimental:** Lyria RealTime is an [experimental model](https://ai.google.dev/gemini-api/docs/models/experimental-models).

# Realtime Music Generation

The Gemini API with [Lyria RealTime](https://deepmind.google/technologies/lyria/realtime/) provides real-time, streaming music generation via [WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API). Build apps where users interactively create, steer, and perform instrumental music.

Try it in AI Studio with [Prompt DJ](https://aistudio.google.com/apps/bundled/promptdj) or [MIDI DJ](https://aistudio.google.com/apps/bundled/promptdj-midi).

> [!NOTE]
> Looking for non-streaming music generation? See [Generate music with Lyria 3](https://ai.google.dev/gemini-api/docs/music-generation).

## Generate and Control Music

Lyria RealTime uses WebSockets for real-time communication, similar to the [Live API](https://ai.google.dev/gemini-api/docs/live).

### Python

```python
import asyncio
from google import genai
from google.genai import types

client = genai.Client(http_options={'api_version': 'v1alpha'})

async def main():
    async def receive_audio(session):
        """Example background task to process incoming audio."""
        while True:
            async for message in session.receive():
                audio_data = message.server_content.audio_chunks[0].data
                # Process audio...
                await asyncio.sleep(10**-12)

    async with (
        client.aio.live.music.connect(model='models/lyria-realtime-exp') as session,
        asyncio.TaskGroup() as tg,
    ):
        # Set up task to receive server messages.
        tg.create_task(receive_audio(session))

        # Send initial prompts and config
        await session.set_weighted_prompts(
            prompts=[
                types.WeightedPrompt(text='minimal techno', weight=1.0),
            ]
        )
        await session.set_music_generation_config(
            config=types.LiveMusicGenerationConfig(bpm=90, temperature=1.0)
        )

        # Start streaming music
        await session.play()

if __name__ == "__main__":
    asyncio.run(main())
```

> [!NOTE]
> For a complete code sample, see the [Lyria RealTime - Get Started](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_LyriaRealTime.py) notebook.

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";
import Speaker from "speaker";
import { Buffer } from "buffer";

const client = new GoogleGenAI({
    apiKey: GEMINI_API_KEY,
    apiVersion: "v1alpha" ,
});

async function main() {
    const speaker = new Speaker({
        channels: 2,       // stereo
        bitDepth: 16,      // 16-bit PCM
        sampleRate: 44100, // 44.1 kHz
    });

    const session = await client.live.music.connect({
        model: "models/lyria-realtime-exp",
        callbacks: {
            onmessage: (message) => {
                if (message.serverContent?.audioChunks) {
                    for (const chunk of message.serverContent.audioChunks) {
                        const audioBuffer = Buffer.from(chunk.data, "base64");
                        speaker.write(audioBuffer);
                    }
                }
            },
            onerror: (error) => console.error("music session error:", error),
            onclose: () => console.log("Lyria RealTime stream closed."),
        },
    });

    await session.setWeightedPrompts({
        weightedPrompts: [
            { text: "Minimal techno with deep bass, sparse percussion, and atmospheric synths", weight: 1.0 },
        ],
    });

    await session.setMusicGenerationConfig({
        musicGenerationConfig: {
            bpm: 90,
            temperature: 1.0,
            audioFormat: "pcm16",
            sampleRateHz: 44100,
        },
    });

    await session.play();
}

main().catch(console.error);
```

Use `session.play()`, `session.pause()`, `session.stop()`, and `session.reset_context()` to control playback.

## Steer Music in Real-Time

Send prompts and update generation parameters while streaming to alter the generated music.

### Prompt Lyria RealTime

Send new `WeightedPrompt` messages to smoothly transition based on new input. Prompts require `text` and `weight` (any value except `0`; `1.0` is a good starting point).

### Python

```python
await session.set_weighted_prompts(
    prompts=[
        {"text": "Piano", "weight": 2.0},
        types.WeightedPrompt(text="Meditation", weight=0.5),
        types.WeightedPrompt(text="Live Performance", weight=1.0),
    ]
)
```

### JavaScript

```javascript
await session.setMusicGenerationConfig({
    weightedPrompts: [
        { text: 'Harmonica', weight: 0.3 },
        { text: 'Afrobeat', weight: 0.7 }
    ],
});
```

> [!TIP]
> Drastic prompt changes can cause abrupt transitions. Implement cross-fading by sending intermediate weight values.

### Update Configuration

Update `MusicGenerationConfig` to steer music in real time. You must set the entire configuration; unset fields reset to defaults. For drastic changes (bpm, scale), call `reset_context()` for a hard transition.

### Python

```python
await session.set_music_generation_config(
    config=types.LiveMusicGenerationConfig(
        bpm=128,
        scale=types.Scale.D_MAJOR_B_MINOR,
        music_generation_mode=types.MusicGenerationMode.QUALITY
    )
)
await session.reset_context();
```

### JavaScript

```javascript
await session.setMusicGenerationConfig({
    musicGenerationConfig: { 
        bpm: 120,
        density: 0.75,
        musicGenerationMode: MusicGenerationMode.QUALITY
    },
});
await session.reset_context();
```

## Prompt Guide

### Instruments

303 Acid Bass, 808 Hip Hop Beat, Accordion, Alto Saxophone, Bagpipes, Balalaika Ensemble, Banjo, Bass Clarinet, Bongos, Boomy Bass, Bouzouki, Buchla Synths, Cello, Charango, Clavichord, Conga Drums, Didgeridoo, Dirty Synths, Djembe, Drumline, Dulcimer, Fiddle, Flamenco Guitar, Funk Drums, Glockenspiel, Guitar, Hang Drum, Harmonica, Harp, Harpsichord, Hurdy-gurdy, Kalimba, Koto, Lyre, Mandolin, Maracas, Marimba, Mbira, Mellotron, Metallic Twang, Moog Oscillations, Ocarina, Persian Tar, Pipa, Precision Bass, Ragtime Piano, Rhodes Piano, Shamisen, Shredding Guitar, Sitar, Slide Guitar, Smooth Pianos, Spacey Synths, Steel Drum, Synth Pads, Tabla, TR-909 Drum Machine, Trumpet, Tuba, Vibraphone, Viola Ensemble, Warm Acoustic Guitar, Woodwinds

### Music Genre

Acid Jazz, Afrobeat, Alternative Country, Baroque, Bengal Baul, Bhangra, Bluegrass, Blues Rock, Bossa Nova, Breakbeat, Celtic Folk, Chillout, Chiptune, Classic Rock, Contemporary R&B, Cumbia, Deep House, Disco Funk, Drum & Bass, Dubstep, EDM, Electro Swing, Funk Metal, G-funk, Garage Rock, Glitch Hop, Grime, Hyperpop, Indian Classical, Indie Electronic, Indie Folk, Indie Pop, Irish Folk, Jam Band, Jamaican Dub, Jazz Fusion, Latin Jazz, Lo-Fi Hip Hop, Marching Band, Merengue, New Jack Swing, Minimal Techno, Moombahton, Neo-Soul, Orchestral Score, Piano Ballad, Polka, Post-Punk, 60s Psychedelic Rock, Psytrance, R&B, Reggae, Reggaeton, Renaissance Music, Salsa, Shoegaze, Ska, Surf Rock, Synthpop, Techno, Trance, Trap Beat, Trip Hop, Vaporwave, Witch house

### Mood/Description

Acoustic Instruments, Ambient, Bright Tones, Chill, Crunchy Distortion, Danceable, Dreamy, Echo, Emotional, Ethereal Ambience, Experimental, Fat Beats, Funky, Glitchy Effects, Huge Drop, Live Performance, Lo-fi, Ominous Drone, Psychedelic, Rich Orchestration, Saturated Tones, Subdued Melody, Sustained Chords, Swirling Phasers, Tight Groove, Unsettling, Upbeat, Virtuoso, Weird Noises

## Best Practices

- Implement robust audio buffering to ensure smooth playback despite network jitter and latency variations.
- Be descriptive with prompts (mood, genre, instrumentation).
- Iterate and steer gradually—modify elements rather than completely changing prompts.
- Experiment with `weight` values to influence how strongly new prompts affect generation.

## Technical Details

### Specifications

- **Output format:** Raw 16-bit PCM Audio
- **Sample rate:** 48kHz
- **Channels:** 2 (stereo)

### Controls

| Parameter | Type | Range | Default | Description |
|---|---|---|---|---|
| `guidance` | float | [0.0, 6.0] | 4.0 | Strictness of prompt adherence. Higher = stricter but more abrupt transitions. |
| `bpm` | int | [60, 200] | — | Beats per minute. Requires reset_context() for changes to take effect. |
| `density` | float | [0.0, 1.0] | — | Density of notes/sounds. Higher = busier music. |
| `brightness` | float | [0.0, 1.0] | — | Tonal quality. Higher = brighter, emphasizing higher frequencies. |
| `scale` | enum | — | — | Musical scale (key and mode). Requires reset_context() for changes. |
| `mute_bass` | bool | — | False | Reduce bass output. |
| `mute_drums` | bool | — | False | Reduce drum output. |
| `only_bass_and_drums` | bool | — | False | Output only bass and drums. |
| `music_generation_mode` | enum | — | QUALITY | Focus on QUALITY, DIVERSITY, or VOCALIZATION. |
| `temperature` | float | [0.0, 3.0] | 1.1 | — |
| `top_k` | int | [1, 1000] | 40 | — |
| `seed` | int | [0, 2147483647] | random | — |

If no value is provided for `bpm`, `density`, `brightness`, or `scale`, the model decides based on initial prompts.

### Scale Enum Values

| Enum Value | Scale |
|---|---|
| `C_MAJOR_A_MINOR` | C major / A minor |
| `D_FLAT_MAJOR_B_FLAT_MINOR` | D♭ major / B♭ minor |
| `D_MAJOR_B_MINOR` | D major / B minor |
| `E_FLAT_MAJOR_C_MINOR` | E♭ major / C minor |
| `E_MAJOR_D_FLAT_MINOR` | E major / C♯/D♭ minor |
| `F_MAJOR_D_MINOR` | F major / D minor |
| `G_FLAT_MAJOR_E_FLAT_MINOR` | G♭ major / E♭ minor |
| `G_MAJOR_E_MINOR` | G major / E minor |
| `A_FLAT_MAJOR_F_MINOR` | A♭ major / F minor |
| `A_MAJOR_G_FLAT_MINOR` | A major / F♯/G♭ minor |
| `B_FLAT_MAJOR_G_MINOR` | B♭ major / G minor |
| `B_MAJOR_A_FLAT_MINOR` | B major / G♯/A♭ minor |
| `SCALE_UNSPECIFIED` | Default / model decides |

The model does not distinguish between relative keys. Each enum corresponds to both relative major and minor.

### Limitations

- **Instrumental only:** No vocal output.
- **Safety:** Prompts are filtered; filtered prompts appear in the output's `filtered_prompt` field.
- **Watermarking:** Output audio is watermarked per [Responsible AI](https://ai.google/responsibility/principles/) principles.

## What's Next

- Generate full songs with [Lyria 3](https://ai.google.dev/gemini-api/docs/music-generation)
- Generate multi-speaker conversation using [TTS models](https://ai.google.dev/gemini-api/docs/audio-generation)
- Generate [images](https://ai.google.dev/gemini-api/docs/image-generation) or [videos](https://ai.google.dev/gemini-api/docs/video)
- Understand [audio files](https://ai.google.dev/gemini-api/docs/audio)
- Real-time conversation with [Live API](https://ai.google.dev/gemini-api/docs/live)

Explore the [Cookbook](https://github.com/google-gemini/cookbook) for more code examples.
