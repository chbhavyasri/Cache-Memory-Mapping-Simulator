# Cache Memory Mapping Simulator

An interactive, parameterized hardware cache simulator developed for Computer Organization & Architecture (COA). Simulates address decoding, set mapping, block replacement, and provides real-time telemetry with 3-C's miss classification.

---

## 1. Mathematical Formulation

Every memory address requested by the CPU is decoded using bit-level masking:

$$\text{Address} = [\; \text{Tag Bits } (t) \;|\; \text{Set Index Bits } (s) \;|\; \text{Block Offset Bits } (b) \;]$$

* **Block Offset Bits ($b$):**
  $$b = \log_2(\text{Block Size})$$
* **Total Lines / Blocks ($L$):**
  $$L = \frac{\text{Cache Size}}{\text{Block Size}}$$
* **Number of Sets ($S$):**
  $$S = \frac{L}{\text{Associativity } (k)}$$
* **Set Index Bits ($s$):**
  $$s = \log_2(S) \quad (\text{Note: } s = 0 \text{ for Fully Associative})$$
* **Tag Bits ($t$):**
  $$t = \text{Address Bus Width} - s - b$$

---

## 2. Quick Setup & Execution

### Prerequisites
Python 3.8 or higher installed on your system.

### Step 1: Install Dependencies
Open your terminal in the `CacheSimulator` folder and run:
```bash
pip install -r requirements.txt