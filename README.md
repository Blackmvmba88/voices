# VOICES — BlackMamba Voice Color

> **La voz escribe el color.**

VOICES es un experimento de transcripción acústica: una persona habla, el sistema convierte el audio en texto y conserva parte de la identidad sonora de la voz mediante color, variaciones cromáticas y textura tipográfica.

La idea no es pintar palabras por su significado. El color sale de **cómo suena la voz**.

## Idea central

Una voz tiene dos niveles distintos:

1. **Perfil global de voz** — relativamente estable durante una intervención.
2. **Entonación instantánea** — cambia palabra por palabra, sílaba por sílaba o frame por frame.

```text
VOZ
 │
 ├── timbre / profundidad / brillo / formantes
 │            ↓
 │       COLOR BASE
 │
 └── pitch / notas / entonación
              ↓
       VARIACIÓN DEL COLOR
```

Por ejemplo, una voz acústicamente profunda puede recibir una familia verde; una voz más brillante y ligera, una familia magenta o rosa. La asignación debe basarse en características acústicas medibles, no en sexo, género o identidad de la persona.

## Modelo

Definimos un vector acústico:

```text
V = [
  F0,
  pitch_range,
  spectral_centroid,
  spectral_flatness,
  HNR,
  RMS,
  formants,
  MFCC,
  low_frequency_energy
]
```

Y lo dividimos en dos salidas.

### 1. Color base

```text
C_voice = f(
  register,
  timbre,
  formants,
  spectral_balance,
  harmonicity
)
```

Este color cambia lentamente y representa el carácter acústico general de la voz.

### 2. Modulación de entonación

```text
ΔC(t) = g(
  F0(t),
  pitch_delta(t),
  melodic_contour(t),
  energy(t)
)
```

Resultado:

```text
C(t) = C_voice + ΔC(t)
```

La misma persona mantiene una familia cromática reconocible, pero el tono se mueve dentro de ella conforme cambia su entonación.

## Ejemplo conceptual

Si el perfil acústico base de una voz cae en verde:

```text
grave   → verde profundo
medio   → verde medio
agudo   → verde brillante
subida  → aumenta luminosidad / hue shift
bajada  → disminuye luminosidad / hue shift
```

Otra voz puede tener como base magenta:

```text
grave   → morado-magenta
medio   → magenta
agudo   → rosa brillante
```

Así evitamos que cada pequeña variación de pitch salte arbitrariamente entre rojo, azul, amarillo y verde.

## Tercera capa: textura

El color no tiene que cargar con toda la información.

La textura tipográfica puede representar otras propiedades:

```text
voz limpia      → texto sólido
voz aireada     → menor opacidad / borde suave
voz rasposa     → textura granulada
muchos armónicos→ glow
voz profunda    → mayor peso o sombra
alta energía    → mayor intensidad visual
```

Esto convierte el texto en una representación acústica, no solamente cromática.

## Pitch musical

La frecuencia fundamental también puede convertirse a MIDI continuo:

```text
MIDI = 69 + 12 × log2(F0 / 440)
```

Y obtener pitch class:

```text
PC = MIDI mod 12
```

Esto permite estudiar qué notas y escalas utiliza una persona naturalmente al hablar, sin usar esas notas como único color principal.

## Pipeline

```text
MICRÓFONO
   │
   ├───────────────┐
   │               │
   ▼               ▼
Speech-to-Text   Acoustic Analyzer
   │               │
   │         F0 / HNR / MFCC
   │         formantes / RMS
   │         espectro / pitch
   │               │
   │               ▼
   │          Voice Profile
   │               │
   │               ▼
   │           Color Engine
   │               │
   └───────┬───────┘
           ▼
      Time Alignment
           │
           ▼
   Colored Transcript
```

## Resolución

El sistema puede evolucionar por etapas:

- **MVP:** color por palabra.
- **v0.2:** color por sílaba.
- **v0.3:** modulación continua por fonema/frame.
- **v0.4:** perfil cromático persistente por hablante.
- **v0.5:** visualización de escala, rango y contorno melódico del habla.

## Stack propuesto

- Python
- NumPy / SciPy
- librosa
- sounddevice o PyAudio
- Whisper
- pYIN o CREPE para F0
- Praat / Parselmouth para formantes
- FastAPI + WebSocket
- Web Audio API para visualización en tiempo real

## Regla crítica

```text
COLOR ≠ significado
COLOR ≠ emoción
COLOR ≠ identidad
COLOR = perfil acústico + modulación de entonación
```

## Objetivo

Conservar algo que la transcripción tradicional elimina:

> **cómo sonaba la voz que pronunció las palabras.**

La voz deja de ser solamente texto y se convierte en una firma visual dinámica.

---

**BlackMamba Records**  
**Iyari Gomez**

`VOICE → PROFILE → PITCH → COLOR → TEXTURE → TEXT`


## Estado actual — MVP ejecutable

El repositorio ya incluye un motor funcional, no solamente el concepto:

- análisis acústico por frames con F0, RMS, centroide espectral, flatness, harmonicidad aproximada y energía grave;
- perfil de voz relativamente estable separado de la entonación instantánea;
- color base por perfil acústico y modulación limitada por pitch;
- textura tipográfica mediante opacidad, peso, glow y roughness;
- nota musical y cents por palabra;
- alineación de timestamps de palabras con frames acústicos;
- transcripción opcional con faster-whisper;
- render HTML de transcript cromático;
- modo en vivo por navegador: micrófono → PCM16 → WebSocket → VAD → Whisper → texto coloreado;
- medidor en tiempo real de F0, nota y color;
- pruebas automáticas y CI.

### Instalar

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e '.[all,dev]'

### Procesar un WAV

    voices transcribe voz.wav --language es --html salida.html

### Modo en vivo

    voices-server --language es --model small

Luego abre:

    http://127.0.0.1:8765

Pulsa **Iniciar micrófono**. El navegador envía audio mono a 16 kHz al servidor. Mientras hablas, el medidor muestra la frecuencia fundamental y la familia cromática; al detectar el final de una frase, Whisper entrega palabras con timestamps y VOICES las vuelve texto acústicamente coloreado.

### Separación de responsabilidades

    perfil acústico estable -> familia de color
    pitch / entonación       -> variación dentro de la familia
    harmonicidad / aire     -> saturación, opacidad, glow y textura
    energía / profundidad   -> luminosidad y peso
    palabra + timestamp     -> alineación con el audio

La paleta es una decisión visual explícita. VOICES no necesita inferir sexo, género, identidad ni emoción para elegir el color.
