# Cache Memory Mapping & Hardware Architecture Simulator

A parameterized hardware cache simulator developed for **Computer Organization and Architecture (COA)**. This project models CPU memory address decoding, cache mapping schemes, block eviction policies, quantitative latency modeling via AMAT, and the textbook Hennessy-Patterson 3-C's miss classification.

The project features a **dual-tier implementation**:
1. **High-Level Visual Platform (Python + Streamlit):** An interactive 5-section dashboard supporting dynamic cache sizing, trace file uploading, single-step execution, and CSV export.
2. **Low-Level Microprocessor Emulator (8086 Assembly):** A bare-metal routine executed in **emu8086** that models silicon bitwise address multiplexing (`AND`, `SHR`) at the register level.

---

## 1. Architectural Features

* **Hardware Bit Partitioning:** Decodes CPU addresses into `[ Tag | Set Index | Block Offset ]` using bitwise shift (`>>`) and mask (`&`) operations rather than arithmetic division.
* **Mapping Schemes Supported:**
  * **Direct-Mapped ($k = 1$):** 1 line per set.
  * **$N$-Way Set Associative ($k = 2, 4$):** $N$ parallel lines per set with parallel tag comparison.
  * **Fully Associative ($k = \text{Total Blocks}$):** Single set ($S=1$, $0$ index bits).
* **Replacement Policies:**
  * **LRU (Least Recently Used):** Cycle-accurate recency timestamp tracking.
  * **FIFO (First-In, First-Out):** Arrival timestamp queueing.
* **Hennessy-Patterson 3-C's Miss Model:** Employs an auxiliary shadow cache to classify misses into:
  * **Compulsory (Cold):** First-time memory references.
  * **Conflict:** Misses caused by set mapping collisions that would have hit in an ideal fully-associative cache of equal size.
  * **Capacity:** Misses caused by the active working set exceeding total cache capacity.
* **AMAT Latency Calculator:** Computes Average Memory Access Time using configurable hit latency and miss penalty cycles.
* **Lab Utilities:** Benchmarking trace upload (`.txt` / `.trace`), single-step execution, state Undo/Reset, and cycle-by-cycle CSV export.

---

## 2. Mathematical Formulation

Every CPU memory address is sliced into three physical fields:

$$\text{Address} = [\; \text{Tag Bits } (t) \;|\; \text{Set Index Bits } (s) \;|\; \text{Block Offset Bits } (b) \;]$$

Given:
* Address Bus Width $= W\text{ bits}$ (16-bit or 32-bit)
* Cache Capacity $= C\text{ bytes}$
* Block / Line Size $= B\text{ bytes}$
* Associativity $= k\text{ ways}$

$$\text{Block Offset Bits: } b = \log_2(B)$$

$$\text{Total Cache Lines: } L = \frac{C}{B}$$

$$\text{Number of Sets: } S = \frac{L}{k} = \frac{C}{B \times k}$$

$$\text{Set Index Bits: } s = \log_2(S) \quad (s = 0 \text{ for Fully Associative})$$

$$\text{Tag Bits: } t = W - (s + b)$$

### Average Memory Access Time (AMAT)

$$\text{AMAT} = \text{Hit Latency} + (\text{Miss Rate} \times \text{Miss Penalty})$$

---

## 3. Project Structure

```text
CacheSimulator/
│
├── app.py                  # Streamlit graphical dashboard (5 tabs, AMAT, CSV export)
├── cache_engine.py         # Hardware logic, bit-slicing, LRU/FIFO, 3-C shadow cache
├── cache_emu8086.asm       # Bare-metal 8086 assembly program for emu8086
├── benchmark_trace.txt     # 25-cycle memory workload trace (Spatial, Temporal, Conflicts)
├── requirements.txt        # Python package dependencies
├── .gitignore              # Ignores virtual environments (.venv) and bytecode
└── README.md               # Project documentation and theoretical specification

---

## 5. Benchmark Workload & Demonstration

The included `benchmark_trace.txt` file evaluates three critical cache access patterns:

* **Spatial Locality (`0x0000, 0x0004`):**
  * `0x0000` triggers a **Compulsory Miss**, fetching the entire 8-byte block (`0x0000`–`0x0007`) into cache.
  * `0x0004` results in an immediate **HIT** because byte offset 4 already resides in the fetched block.

* **Temporal Locality (`0x0010, 0x0020, 0x0010`):**
  * Repeatedly referencing recently accessed addresses retains them in cache lines, producing consecutive **HITS**.

* **Conflict Thrashing Resolution:**
  * **Direct-Mapped ($k = 1$):** `0x0000`, `0x0040`, and `0x0080` all map to **Set 0**, causing continuous eviction (thrashing) and a low **20% Hit Rate**.
  * **2-Way Set Associative ($k = 2$):** Both conflicting memory blocks fit into Set 0 simultaneously across **Way 0** and **Way 1**, eliminating the collisions and substantially reducing AMAT.

---

## 6. Sample Performance Output

text
=======================================================
        8086 HARDWARE CACHE ARCHITECTURE SIMULATOR      
=======================================================

Address: 0x0000 | Tag: 0x0000 | Set: 0 | Offset: 0 -> [ MISS ]
Address: 0x0004 | Tag: 0x0000 | Set: 0 | Offset: 4 -> [ HIT  ]
Address: 0x0040 | Tag: 0x0001 | Set: 0 | Offset: 0 -> [ MISS ]
Address: 0x0000 | Tag: 0x0000 | Set: 0 | Offset: 0 -> [ MISS ]
Address: 0x0080 | Tag: 0x0002 | Set: 0 | Offset: 0 -> [ MISS ]

--- PERFORMANCE METRICS ---
  Total Accesses : 5
  Total Hits     : 1
  Total Misses   : 4
  Hit Ratio      : 20%

  ```