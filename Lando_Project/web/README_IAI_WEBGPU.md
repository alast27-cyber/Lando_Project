# IAI WebGPU Local-First Blueprint

This blueprint describes a browser-native implementation of the Instinctive Artificial Intelligence (IAI) stack with zero API dependency after first model download.

## Architecture Diagram (Mermaid)

```mermaid
flowchart TD
  U[User Input] --> EMD[Energy Minimization Driver]

  EMD --> L1[Layer 1: IRL Heuristic Reflex]
  L1 -->|confidence >= tau1| R1[Reflex Response]
  L1 -->|confidence < tau1| L2[Layer 2: ILL Retrieval]

  L2 --> VDB[(IndexedDB Vector Store\nOrama/Voy)]
  L2 -->|confidence >= tau2| R2[Instinct Circuit Response]
  L2 -->|confidence < tau2| L3[Layer 3: CLL Heavy LLM]

  L3 --> WGPU[WebLLM / Transformers.js on WebGPU]
  WGPU --> R3[Generative Response]

  R1 --> O[Output]
  R2 --> O
  R3 --> O

  subgraph Persistence
    SW[Service Worker]
    OPFS[(OPFS Model Cache + Instinct Tensors)]
    BG[Background Training / Sync]
  end

  O --> SW
  SW --> OPFS
  SW --> BG
  BG --> VDB

  subgraph Data Injection
    DIW[Data Ingestion Worker]
    EXT[CORS-enabled External Sources]
  end

  EXT --> DIW
  DIW --> VDB
```

## Layer Semantics

- **Layer 1 (IRL):** fast regex/heuristic checks + lightweight confidence score.
- **Layer 2 (ILL):** local vector retrieval against instinct circuits in IndexedDB.
- **Layer 3 (CLL):** heavy model inference (WebGPU) only when earlier layers fail confidence thresholds.

## Runtime Components

- `iai-kernel.js`: orchestrates the energy-aware handoff between IRL/ILL/CLL.
- `service-worker.js`: keeps model/runtime state persistent and manages background jobs.
- `opfs-store.js`: handles OPFS initialization + high-speed file access.
- `data-ingestion-worker.js`: fetches external data and injects embeddings/documents into Layer 2.
- `main.js`: UI thread integration and 60fps-safe messaging with workers.

## 60fps Responsiveness Guidelines

- Keep all heavy work off main thread (Service Worker + Web Workers).
- Batch ingestion and embedding jobs in small chunks (`requestIdleCallback` or timed slices).
- Stream partial tokens from CLL to UI rather than blocking full response.
- Prefer IRL/ILL first; CLL only under threshold (`tau`).

## Offline-Ready Strategy

1. First run downloads model weights once.
2. Persist weights and updated instinct tensors to OPFS.
3. Cache app shell + scripts in Service Worker cache.
4. Resume from local OPFS + IndexedDB on subsequent loads.

