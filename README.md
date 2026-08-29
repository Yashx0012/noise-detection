# Smart Urban Environmental & Noise Classification System
## Complete Project Documentation (v2.0 — Hybrid High-Performance Architecture)

**Version**: 2.0
**Type**: Production-oriented Machine Learning + Systems Web Application
**Domain**: Smart City / Environmental Monitoring / Industrial Noise Compliance
**Change from v1.0**: Backend networking layer migrated to Go; DSP/feature-extraction engine migrated to C; Python retained for ML inference and dashboard.

---

## 1. Executive Summary

The Smart Urban Environmental & Noise Classification System is an end-to-end platform that captures environmental audio (via microphone or file upload), processes it using digital signal processing (DSP) techniques, extracts acoustic features, and classifies the sound source (traffic, sirens, construction, dog barking, crowds) using classical Machine Learning models. It combines **loudness monitoring**, **sound-source classification**, and **historical trend tracking** — suitable for smart-city infrastructure, industrial safety compliance, and environmental noise-pollution monitoring.

Version 2.0 restructures the system into a **polyglot, performance-oriented architecture**:
- **Go** handles networking, concurrency, and API orchestration (replacing FastAPI)
- **C** handles the DSP/feature-extraction engine (replacing NumPy/Librosa in the hot path)
- **Python** is retained for classical ML inference/training and the dashboard, where its ecosystem is unmatched

### 1.1 Core Capabilities
- Live microphone capture and continuous (streaming) classification
- File upload classification for pre-recorded audio
- Real-time decibel (dB) / loudness monitoring
- Sound-source classification with confidence scores
- Waveform, Spectrogram, and Mel Spectrogram visualization
- Historical prediction storage and trend analysis dashboard

### 1.2 What Makes It Different
- Combines **classification + loudness**, not one or the other
- **Persists** predictions over time instead of showing a number and forgetting it
- Uses **interpretable classical ML** (Random Forest/SVM/XGBoost on engineered features) instead of a black-box deep model — faster inference, explainable, works with smaller datasets
- Full **visual transparency** (waveform/spectrogram shown alongside predictions)
- Built as a real **modular, deployable system** (backend + engine + ML + DB + frontend), not a notebook
- **v2.0:** Low-latency concurrent networking (Go) + near-native DSP throughput (C) — designed for real continuous live-monitoring loads, not just demo requests

### 1.3 Why the Hybrid Rewrite
| Layer | Bottleneck in v1.0 (Python-only) | Fix in v2.0 |
|---|---|---|
| Networking / API | GIL limits true concurrency under many simultaneous streams | Go goroutines — cheap, native concurrency |
| DSP / Feature Extraction | NumPy/Librosa overhead adds up on continuous live-streaming frames | C engine — direct memory control, no interpreter overhead |
| ML Inference | Already near-optimal (sklearn/XGBoost are C/C++ under the hood) | Kept in Python — rewriting here has poor ROI |
| Dashboard | Not performance-critical | Kept in Python (Streamlit) |

---

## 2. System Architecture (v2.0)

### 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          HARDWARE LAYER                              │
│   Built-in Laptop Mic  /  USB External Mic  →  ADC  →  OS Driver     │
└───────────────────────────────┬──────────────────────────────────---┘
                                 │  (raw digital audio samples)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                AUDIO CAPTURE + NETWORKING LAYER (Go)                 │
│   Handles: mic stream ingestion, file uploads, WebSocket/HTTP API,   │
│   concurrent client connections, request routing, backpressure       │
│              (net/http, gorilla/websocket, goroutines, channels)     │
└───────────────────────────────┬──────────────────────────────────---┘
                                 │  (raw PCM frames via cgo / IPC)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DSP / FEATURE ENGINE LAYER (C)                    │
│  Normalize → Trim Silence → Framing/Windowing → FFT/STFT → Mel Spec  │
│  → RMS/dB → MFCC/Chroma/ZCR/Centroid/Bandwidth/Rolloff extraction    │
│         Compiled as shared library (.so/.dll), called via cgo        │
└───────────────────────────────┬──────────────────────────────────---┘
                                 │  (fixed-length feature vector)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ML INFERENCE LAYER (Python)                        │
│   Feature Vector → Trained Model (RF / SVM / XGBoost) → Prediction    │
│    Served as microservice (FastAPI, internal-only) OR exported to     │
│              ONNX and called directly via cgo/onnxruntime             │
│                   Class Label + Confidence Score                      │
└───────────────────────────────┬──────────────────────────────────---┘
                                 ▼
                    ┌────────────┴────────────┐
                    ▼                         ▼
┌───────────────────────────────┐  ┌───────────────────────────────┐
│      DATABASE LAYER            │  │       FRONTEND LAYER          │
│  SQLite (dev) / PostgreSQL     │  │        Streamlit Dashboard    │
│  (prod) — predictions,          │  │  Record/Upload, Live dB Meter,│
│  timestamps, dB, confidence     │  │  Waveform/Spectrogram Display,│
│  Accessed by Go via pgx/sqlx    │  │  History Charts, Confidence UI│
└───────────────────────────────┘  └───────────────────────────────┘
```

### 2.2 Layered Design Philosophy

Strict separation of concerns so each layer can be developed, tested, and swapped independently — same principle as v1.0, now extended across language boundaries:

| Layer | Responsibility | Language | Independent of |
|---|---|---|---|
| Hardware | Physical sound capture | — | Everything above it |
| Audio Capture + Networking | Ingest audio, serve API, manage concurrency | **Go** | DSP internals, ML model choice, DB engine |
| DSP/Feature Engine | Turn raw samples into feature vectors | **C** | Networking layer, ML model, DB, frontend |
| ML Inference | Turn features into a prediction | **Python** | Networking, DSP internals, frontend |
| Database | Persistence | SQLite/PostgreSQL | Frontend, ML internals |
| Frontend | User interaction/visualization | **Python (Streamlit)** | Backend/engine implementation details |

### 2.3 Inter-Language Communication Strategy

Three layers, two integration boundaries — this is the part that needs the most care:

**Go ↔ C (audio → features):**
- Preferred: **cgo** — compile the C DSP engine as a static/shared library, call directly from Go. Lowest latency, no serialization overhead, but couples build toolchains.
- Alternative: C engine exposed as a small **Unix socket / gRPC service**; Go talks to it over IPC. Cleaner separation, easier to test each side independently, slightly higher latency (usually negligible for frame-sized payloads).
- **Recommendation for this project:** start with cgo for the live-streaming hot path (latency matters most here); keep the option to swap to IPC if the C engine grows complex or needs independent scaling.

**Go/C ↔ Python (features → prediction):**
- Preferred for simplicity: Python ML model served as an **internal-only microservice** (FastAPI or plain HTTP), Go calls it over localhost HTTP/gRPC per prediction request.
- Preferred for performance: **export the trained sklearn/XGBoost model to ONNX**, load it directly in Go (via `onnxruntime-go`) or C — removes Python from the runtime hot path entirely, keeping Python only for **training/experimentation**, not inference.
- **Recommendation for this project:** start with the microservice approach (simpler, keeps sklearn's native format), migrate to ONNX only if inference latency becomes a bottleneck under live-streaming load.

---

## 3. Hardware Layer

### 3.1 Audio Input Devices
- **Built-in laptop/device microphone**: MEMS or condenser capsule wired to the motherboard's audio codec chip (e.g. Realtek ALC-series), which contains the ADC.
- **USB external microphone**: contains its own ADC; sends already-digital audio over USB using the USB Audio Class (UAC) protocol — plug-and-play, generally cleaner signal (shorter analog path = less electrical noise).

### 3.2 Capture Chain
```
Sound wave (air pressure)
   → Diaphragm vibrates
   → Analog voltage generated
   → ADC samples + quantizes (sampling rate + bit depth)
   → OS Audio Driver (WASAPI / CoreAudio / ALSA)
   → PortAudio (cross-platform abstraction, via Go binding or cgo)
   → Go audio-capture goroutine → raw PCM buffer
   → passed to C engine (cgo call) as []float32 / float32*
```

### 3.3 Key Hardware/OS Parameters Used in the System
| Parameter | Value Used | Reason |
|---|---|---|
| Sample rate | 22050 Hz | Covers all relevant environmental-sound frequency content (Nyquist = 11025 Hz), keeps data volume manageable |
| Channels | Mono (1) | Classification only needs overall pressure signal, not spatial/stereo information |
| Bit depth | 16-bit (storage) / 32-bit float (processing) | 16-bit for WAV storage compatibility; float32 in-memory for numerically stable DSP math |
| Buffer size | 1024–2048 samples | Balances low latency (~46–93ms) against CPU overhead and glitch risk, for live streaming mode |

### 3.4 Minimum Hardware Requirements
- Any device with a working microphone (built-in or USB)
- CPU sufficient for real-time feature extraction + classical ML inference (no GPU required)
- Optional: dedicated USB mic for higher-quality/lower-noise field deployment (e.g. outdoor smart-city sensor unit)
- **v2.0 note:** the C engine + Go networking layer significantly lower the CPU/memory footprint needed for live continuous monitoring versus the pure-Python v1.0 stack — makes edge deployment (Raspberry Pi class devices) considerably more realistic.

---

## 4. Audio Capture + Networking Layer (Go)

### 4.1 Responsibilities
- Accept live mic stream input (via PortAudio binding or OS-level capture bridge)
- Accept file uploads (multipart HTTP)
- Serve REST/WebSocket API endpoints
- Manage concurrent client connections (multiple simultaneous live-monitoring sessions)
- Apply backpressure/buffering so slow consumers don't stall audio capture
- Hand raw PCM frames to the C engine (cgo) and receive back feature vectors
- Call the ML inference service/model and receive predictions
- Write results to the database
- Return JSON/WebSocket responses to the frontend

### 4.2 Suggested Package Structure
```
/cmd
  /server           # main.go — entrypoint, server bootstrap
/internal
  /capture           # mic stream handling, PortAudio bindings
  /api               # HTTP handlers: /upload /record /predict /history /stream /health
  /engine            # cgo bindings to the C DSP library
  /inference         # client for ML microservice (or ONNX runtime calls)
  /db                # DB access layer (sqlx/pgx), migrations
  /models            # shared structs: PredictionResult, Session, etc.
  /config            # environment-based config (dev/prod DB, sample rate, ports)
/pkg
  /dsp_engine        # compiled C shared library + cgo header bindings
```

### 4.3 Concurrency Model
- One goroutine per live-monitoring client session (mic stream or WebSocket connection)
- Channels used to pass raw audio frames from capture goroutine → processing goroutine
- Worker pool (bounded goroutine pool) for feature-extraction + inference calls, to avoid unbounded concurrency under load
- Context-based cancellation so stopping a session cleanly tears down its goroutines

### 4.4 API Endpoints (unchanged surface from v1.0, reimplemented in Go)
| Endpoint | Method | Purpose |
|---|---|---|
| `/upload` | POST | Upload a pre-recorded audio file for classification |
| `/record` | POST | Start/stop a live recording session |
| `/predict` | POST | Run prediction on a given audio buffer/session |
| `/stream` | WebSocket | Continuous live classification stream |
| `/history` | GET | Query past predictions (filterable by class/time/dB) |
| `/health` | GET | Liveness/readiness check |

---

## 5. DSP / Feature Engine Layer (C)

### 5.1 Responsibilities
This layer converts a raw waveform into a machine-learning-ready feature vector — now implemented as a compiled C library for maximum throughput on the live-streaming hot path.

### 5.2 Preprocessing Pipeline (applied to every clip, training and inference alike)
1. **Load & standardize** — force mono, force target sample rate (22050 Hz)
2. **Normalize** — peak or RMS normalization
3. **Trim silence** — remove near-silent leading/trailing sections (upload/clip mode only)
4. **Framing** — slice into short overlapping frames (`n_fft=2048`, `hop_length=512`)
5. **Windowing** — apply a Hann window per frame to prevent spectral leakage
6. **FFT/STFT** — implemented via a lightweight C FFT library (e.g. **KissFFT** or **FFTW**) applied per frame
7. **Spectrogram / Mel Spectrogram generation** — for visualization and future CNN-style extensions

### 5.3 Core Signal Metrics Computed
| Metric | Purpose |
|---|---|
| RMS (Root Mean Square) | Frame-level energy/loudness |
| Decibel (dB) | Log-scaled, perceptually meaningful loudness (`20·log10(RMS/ref)`) |
| Zero Crossing Rate (ZCR) | Signal "noisiness" |
| Spectral Centroid | "Brightness" — where spectral energy is concentrated |
| Spectral Bandwidth | Spread of frequencies around the centroid |
| Spectral Rolloff | Frequency below which 85% of spectral energy lies |

### 5.4 Feature Extraction (ML input)
| Feature | Dimensionality | What it captures |
|---|---|---|
| MFCC | 13 coefficients × (mean+std) | Timbre / spectral envelope shape |
| Chroma | 12 bins × (mean+std) | Pitch-class energy distribution |
| ZCR | 1 × (mean+std) | Noisiness/percussiveness |
| Spectral Centroid | 1 × (mean+std) | Brightness |
| Spectral Bandwidth | 1 × (mean+std) | Frequency spread |
| Spectral Rolloff | 1 × (mean+std) | Energy concentration cutoff |

### 5.5 Suggested File Structure
```
/dsp_engine
  ├── include/
  │   └── dsp_engine.h        # public API exposed to Go via cgo
  ├── src/
  │   ├── preprocess.c        # normalize, trim, resample
  │   ├── fft.c                # FFT/STFT wrapper (KissFFT/FFTW)
  │   ├── features.c          # MFCC/Chroma/ZCR/Centroid/Bandwidth/Rolloff
  │   ├── mel.c                 # Mel filterbank + Mel spectrogram
  │   └── engine.c              # top-level orchestration, exported entrypoints
  ├── tests/
  │   └── test_features.c     # unit tests against known reference values
  └── Makefile                  # builds static (.a) and shared (.so/.dll) lib
```

### 5.6 Memory & Correctness Practices
Given this is the performance-critical layer, apply the same discipline used elsewhere in systems work:
- All buffers pre-allocated where possible (avoid malloc/free churn in the live streaming loop)
- Run under **Valgrind/Helgrind** regularly — memory leaks or races here directly degrade a long-running live-monitoring session
- Validate feature outputs against a reference (e.g. compare against Librosa output on the same clips) as part of the test suite, so numerical correctness isn't silently lost in the port from Python

---

## 6. ML Inference & Training Layer (Python)

### 6.1 Responsibilities
- **Training** (offline, not on the runtime hot path): dataset preparation, model training (Random Forest / SVM / XGBoost), evaluation, hyperparameter tuning
- **Inference** (runtime): served either as an internal microservice called by Go, or exported to ONNX and executed without Python in the loop

### 6.2 Two Serving Modes

**Mode A — Python Microservice (simpler, recommended to start)**
```
/ml_service
  ├── train.py            # offline training script
  ├── serve.py            # lightweight FastAPI/Flask service, /infer endpoint
  ├── model_loader.py     # loads trained model once at startup
  └── models/
      └── noise_classifier.pkl   # joblib/pickle persisted model
```
Go calls `POST /infer` with the feature vector, receives `{class, confidence}` back over localhost.

**Mode B — ONNX Export (higher performance, adopt once bottlenecked)**
```
/ml_service
  ├── train.py
  ├── export_onnx.py      # convert sklearn/XGBoost model → ONNX format
  └── models/
      └── noise_classifier.onnx
```
Go loads the ONNX model directly via `onnxruntime-go` — no Python process, no network hop, at runtime. Python is only ever invoked for retraining.

### 6.3 Model Persistence
- Mode A: `joblib` / `pickle`
- Mode B: ONNX (`skl2onnx` / `onnxmltools` for conversion)

---

## 7. Database Layer

### 7.1 Engine Strategy
- **Development**: SQLite — zero-config, file-based, fast to iterate on
- **Production**: PostgreSQL — concurrent access, scalability, robust for multi-user smart-city deployment
- **Access from Go**: `sqlx` (SQLite/Postgres, lightweight) or `pgx` (Postgres-specific, higher performance) — replaces SQLAlchemy from v1.0
- Migrations handled via `golang-migrate` or a similar Go-native migration tool

### 7.2 Suggested Schema

**`predictions` table**
| Column | Type | Notes |
|---|---|---|
| id | Integer, PK | Auto-increment |
| timestamp | DateTime | When the prediction was made |
| source_type | String | `"upload"` / `"live_mic"` |
| predicted_class | String | e.g. `"siren"`, `"traffic"`, `"dog_bark"` |
| confidence_score | Float | 0.0–1.0 |
| rms | Float | Average RMS for the clip/window |
| decibel | Float | Average dB for the clip/window |
| duration_seconds | Float | Length of the analyzed audio |
| audio_reference | String (nullable) | Path/ID to stored audio or spectrogram image, if retained |

**`sessions` table** (for live monitoring runs, optional)
| Column | Type | Notes |
|---|---|---|
| id | Integer, PK | |
| started_at | DateTime | |
| ended_at | DateTime (nullable) | |
| device_info | String | Which mic/device was used |

### 7.3 Why Persistence Matters (project differentiator)
Storing every prediction with a timestamp enables **historical trend analysis** — peak traffic-noise hours, recurring construction windows, siren frequency patterns by time of day. Plain decibel-meter apps fundamentally lack this since they never store anything.

---

## 8. Frontend Layer (Streamlit)

### 8.1 Responsibilities
- Provide the user-facing dashboard
- Trigger audio recording or file upload (calls the Go API, not Python backend directly)
- Render results returned from the Go API
- Visualize waveform, spectrogram, Mel spectrogram
- Display live dB meter and classification results with confidence
- Show historical trend charts

### 8.2 Suggested Pages/Sections
| Section | Contents |
|---|---|
| **Live Monitor** | Start/stop mic capture (via Go `/record` + `/stream`), real-time dB meter, rolling classification result |
| **Upload & Classify** | File upload widget, waveform + spectrogram display, predicted class + confidence |
| **History Dashboard** | Filterable table + charts of past predictions (by class, by time, by dB level) via `/history` |
| **Insights** | Aggregated stats — most common noise source by hour, average dB trend over the week |

### 8.3 Visualization Components
- Waveform plot (amplitude vs. time)
- Spectrogram (STFT-based, dB-scaled)
- Mel Spectrogram (perceptually-scaled)
- Confidence score bar/gauge per prediction
- Time-series charts for historical dB and class-frequency trends

**Note:** the frontend remains decoupled from *how* predictions are computed — it only talks to the Go API's JSON/WebSocket contract, so the v1.0→v2.0 backend rewrite required **zero frontend changes** beyond pointing at the new server. This is the payoff of the layered design.

---

## 9. End-to-End Data Flow

### 9.1 Application Workflow — Single Prediction Request (Upload Mode)
```
1. User uploads audio via Streamlit frontend
2. Frontend sends audio (bytes/file) to Go backend: POST /upload
3. Go handler receives file, passes raw PCM buffer to C engine via cgo call
4. C engine runs DSP preprocessing:
      normalize → trim silence → resample/mono-check
5. C engine extracts features:
      MFCC, Chroma, ZCR, Centroid, Bandwidth, Rolloff, RMS
      (mean + std pooled into one fixed-length vector)
      returns feature vector + RMS/dB back to Go
6. Go calls ML inference (Python microservice or ONNX runtime)
7. Prediction {class, confidence} returned to Go
8. Go writes result to database (predictions table) via sqlx/pgx
9. Go returns JSON response: {class, confidence, dB, timestamp}
10. Frontend renders: predicted class, confidence bar, dB reading,
    waveform + spectrogram images
11. History dashboard later queries GET /history to show trends
```

### 9.2 Application Workflow — Live Streaming Mode
```
1. User clicks "Start Monitoring" in Streamlit → Go POST /record
2. Go spins up a dedicated goroutine + WebSocket connection: /stream
3. Go's capture goroutine pulls audio frames continuously from mic (PortAudio)
4. Each frame batch (buffer size 1024–2048 samples) is:
      passed to C engine (cgo) → feature vector + dB
      passed to ML inference → class + confidence
      written to DB (async, non-blocking)
      pushed to frontend over WebSocket
5. Streamlit renders rolling dB meter + latest classification in near real-time
6. User clicks "Stop" → Go cancels the session context, goroutines clean up,
   session record finalized in `sessions` table
```

### 9.3 Development Workflow

**Phase 1 — Foundation & Contracts**
1. Define the API contract (endpoints, request/response JSON schemas) — this is the interface every layer builds against, so nail it first
2. Define the cgo boundary: C function signatures in `dsp_engine.h` (what Go passes in, what it gets back)
3. Define the feature-vector format precisely (order, dimensionality) — this is the contract between C and Python/ONNX

**Phase 2 — Independent Layer Development (parallelizable)**
4. Build and unit-test the C DSP engine standalone (feed known WAV files, validate output against Librosa reference values)
5. Build the Go networking/API layer standalone (mock the C engine and ML service initially with stub responses)
6. Train the ML model in Python using existing/sample datasets, independent of the rest of the system
7. Build the Streamlit frontend against a mocked/stubbed API

**Phase 3 — Integration**
8. Wire Go → C via cgo; validate feature vectors match the standalone C engine's test output
9. Wire Go → Python ML service (or export + load ONNX model); validate predictions match Python-side evaluation
10. Wire Go → DB; validate persistence and `/history` queries
11. Point Streamlit frontend at the real Go API

**Phase 4 — Live Streaming & Hardening**
12. Implement and stress-test the live-streaming path (concurrent sessions, backpressure, goroutine cleanup)
13. Run Valgrind/Helgrind against the C engine under sustained load
14. Load-test the Go API (many concurrent clients) to validate the concurrency model actually delivers the intended performance gain

**Phase 5 — Deployment Readiness**
15. Containerize each service (Go binary, C engine as linked library or sidecar, Python ML service) — Docker Compose for local, k8s/Compose for prod
16. Switch DB from SQLite → PostgreSQL for production config
17. Add monitoring/logging across all three languages (structured logs, correlated by request ID)

---

## 10. Technology Stack Summary (v2.0)

| Layer | Technology | Change from v1.0 |
|---|---|---|
| Hardware | Built-in / USB microphone | — |
| Audio Capture | Go (PortAudio binding) | Was: Python `sounddevice` |
| Networking / Backend API | **Go** (`net/http`, `gorilla/websocket`) | Was: FastAPI (Python) |
| DSP / Signal Processing | **C** (custom engine, KissFFT/FFTW) | Was: NumPy, SciPy, Librosa |
| ML Training | Python (scikit-learn, XGBoost) | Unchanged |
| ML Inference | Python microservice **or** ONNX (loaded from Go/C) | Was: in-process Python call |
| Database Access | Go (`sqlx` / `pgx`) | Was: SQLAlchemy (Python) |
| Database | SQLite (dev), PostgreSQL (prod) | Unchanged |
| Frontend | Streamlit (Python) | Unchanged |
| Visualization | Matplotlib/Librosa.display + Streamlit charts | Unchanged |
| Model Persistence | joblib/pickle (Mode A) or ONNX (Mode B) | Extended |
| Inter-layer Integration | cgo (Go↔C), HTTP/gRPC or ONNX runtime (Go↔Python) | New |

---

## 11. Key Differentiators (vs. Consumer Apps and vs. v1.0)

| Capability | Consumer dB apps | v1.0 (Python-only) | v2.0 (Go+C+Python) |
|---|---|---|---|
| Loudness (dB) measurement | ✅ | ✅ | ✅ |
| Sound-source classification | ❌ | ✅ | ✅ |
| Waveform/spectrogram visualization | ❌ | ✅ | ✅ |
| Historical data persistence | ❌ | ✅ | ✅ |
| Trend analysis over time | ❌ | ✅ | ✅ |
| Concurrent live sessions at scale | ❌ | Limited (GIL) | ✅ (goroutines) |
| Real-time DSP throughput | ❌ | Moderate (NumPy/Librosa overhead) | ✅ High (native C) |
| Edge-device feasibility (e.g. Raspberry Pi) | Partial | Limited | ✅ Improved (lower resource footprint) |
| Target use case | Personal curiosity | Smart city / demo-scale | Smart city / industrial, load-ready |

---

## 12. Limitations & Future Scope

### 12.1 Current Limitations
- dB readings are relative (dBFS-style), not calibrated absolute SPL — would need microphone-specific calibration for legally-binding noise measurements
- Classification accuracy depends on training dataset quality/diversity; real-world acoustic conditions can differ from training data
- Single-microphone setup — no sound-source localization/direction
- **v2.0 specific:** the Go↔C↔Python boundary adds real engineering overhead (build complexity, cross-language debugging, FFI edge cases) — worth it for scale/latency goals, but a heavier lift than the v1.0 pure-Python stack

### 12.2 Potential Extensions
- CNN-based classification on raw Mel spectrograms once a larger labeled dataset is available (would likely run via ONNX too, for the same reason as the classical models)
- Multi-microphone arrays for spatial localization of noise sources
- Edge deployment (Raspberry Pi + USB mic) — meaningfully more viable now given the lighter Go+C runtime footprint
- Real SPL calibration against a reference sound level meter
- Alerting/notification system when noise thresholds are exceeded (natural fit for Go's concurrency — e.g. threshold watchers per session)
- Mobile app frontend as an alternative/complement to the Streamlit dashboard
- Full ONNX migration (Mode B) to remove Python from the runtime path entirely, keeping it strictly as a training/offline tool

---

## 13. Development Methodology

1. **Architecture design first** — full system architecture (this document) designed before implementation, including explicit cross-language contracts (API schema, cgo header, feature-vector format)
2. **Independent pipeline validation** — each piece (C DSP engine, Go networking layer, Python ML training) built and tested standalone before integration
3. **Modular workflow construction** — engine, backend, ML, database, and frontend developed as independently testable modules across language boundaries
4. **Integration only after each layer is individually validated** — C engine output checked against reference values, Go API tested with mocked dependencies, before wiring the real cross-language calls
5. **Performance validation as an explicit phase** — the entire point of the v2.0 rewrite is throughput/concurrency, so load-testing and profiling are not optional cleanup steps but a required milestone before calling the system "production-ready"
6. **Iterative refinement** — each phase includes testing, refactoring, and optimization for maintainability, scalability, and production readiness

---

## 14. Suggested Contribution Areas by Skillset

Given the polyglot nature of v2.0, contributions map naturally to background:

| Contributor Background | Best-fit Areas |
|---|---|
| Systems / C / networking (e.g. sockets, concurrency, OS-level work) | Go networking layer, C DSP engine, cgo integration, performance profiling, edge deployment |
| Python / ML | Model training/tuning, ONNX export pipeline, feature engineering |
| Frontend / data viz | Streamlit dashboard, chart/insight design |
| DevOps | Docker Compose / k8s setup, CI across three language toolchains, monitoring/logging |
| QA / testing | Cross-layer integration tests, reference-value validation for the C engine, load testing the Go API |
