"""
app.py - Graphical UI for Cache Memory Simulator
Computer Organization & Architecture (COA) Academic Project
Clean Tabular Hardware Table with Canva-Style Animated Cover Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from cache_engine import CacheSimulator, ReplacementPolicy, MissType

# --- Page Setup & Styling ---
st.set_page_config(page_title="Cache Memory Mapping Simulator", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 95%; }
    
    div[data-baseweb="select"] {
        min-height: 42px !important;
        font-size: 0.95rem !important;
        border-radius: 8px !important;
    }
    .stSelectbox, .stTextInput, .stNumberInput {
        max-width: 100% !important;
    }
    
    div.stButton > button, div.stDownloadButton > button {
        background-color: transparent !important;
        border: 1px solid #475569 !important;
        color: #f1f5f9 !important;
        border-radius: 8px !important;
        height: 42px !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        border-color: #94a3b8 !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    
    .bit-card {
        border-left: 4px solid #475569;
        background-color: #1e293b;
        color: #f8fafc;
        padding: 9px 15px;
        margin-bottom: 7px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 0.92rem;
    }
    .bit-tag { border-left-color: #ef4444; }
    .bit-idx { border-left-color: #3b82f6; }
    .bit-off { border-left-color: #10b981; }

    /* Compact Metric Values Size */
    div[data-testid="stMetricValue"] {
        font-size: 1.38rem !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #94a3b8 !important;
    }

    /* =========================================================================
       CANVA-STYLE STAGGERED ENTRANCE ANIMATIONS (COVER PAGE)
       ========================================================================= */
    @keyframes canvaPopUp {
        0% {
            opacity: 0;
            transform: translateY(32px) scale(0.95);
        }
        70% {
            transform: translateY(-4px) scale(1.01);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    @keyframes canvaFadeUp {
        0% {
            opacity: 0;
            transform: translateY(20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .cover-viewport {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        min-height: 68vh;
        padding: 40px 20px 20px 20px;
    }

    /* Stagger 1: Heading Pops Up */
    .cover-hero-title {
        font-size: 3.3rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.03em;
        margin-bottom: 18px;
        animation: canvaPopUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* Stagger 2: Single-Line Description Fades In */
    .cover-hero-caption {
        font-size: 1.25rem;
        font-weight: 400;
        color: #94a3b8;
        max-width: 820px;
        line-height: 1.6;
        margin: 0 auto 40px auto;
        opacity: 0;
        animation: canvaFadeUp 0.85s cubic-bezier(0.16, 1, 0.3, 1) 0.35s forwards;
    }

    /* Stagger 3: Action Button Fades In */
    .cover-btn-wrapper {
        opacity: 0;
        animation: canvaFadeUp 0.85s cubic-bezier(0.16, 1, 0.3, 1) 0.65s forwards;
    }
</style>
""", unsafe_allow_html=True)

# --- Safe Session State Initialization ---
if "entered" not in st.session_state:
    st.session_state.entered = False

if "sim" not in st.session_state:
    st.session_state.sim = CacheSimulator(
        cache_size_bytes=64,
        block_size_bytes=8,
        associativity=1,
        policy=ReplacementPolicy.LRU,
        addr_bits=16
    )

if "session_step_log" not in st.session_state:
    st.session_state.session_step_log = []

if "session_run_records" not in st.session_state:
    st.session_state.session_run_records = []

if "queue" not in st.session_state:
    st.session_state.queue = []

sim = st.session_state.sim

# ==============================================================================
# LANDING VIEW: CANVA-ANIMATED COVER PAGE
# ==============================================================================
if not st.session_state.entered:
    st.markdown("""
    <div class="cover-viewport">
        <div class="cover-hero-title">Cache Memory Mapping Simulator</div>
        <div class="cover-hero-caption">
            An interactive hardware simulator that emulates how a CPU breaks down memory addresses and maps them into cache memory to track hits, misses, and latency in real time.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_left, c_btn, c_right = st.columns([1.8, 1.1, 1.8])
    with c_btn:
        st.markdown('<div class="cover-btn-wrapper">', unsafe_allow_html=True)
        if st.button("Launch Simulator", use_container_width=True):
            st.session_state.entered = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# MAIN VIEW: THE 5 SIMULATOR SECTIONS
# ==============================================================================
else:
    st.title("Cache Memory Mapping Simulator")
    st.caption("Computer Organization & Architecture | Parameterized Hardware Simulation Platform")

    # --- The 5 Working Sections ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1. Architecture Setup",
        "2. Execution Controller",
        "3. Cache Memory Table",
        "4. Session Access Step Log",
        "5. Session Telemetry & History"
    ])

    # ==============================================================================
    # TAB 1: ARCHITECTURE SETUP & BIT PARTITIONING
    # ==============================================================================
    with tab1:
        st.markdown("#### Architecture Setup")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            addr_bits_val = st.selectbox("Address Bus Width (Bits)", [16, 32], index=0 if sim.addr_bits == 16 else 1)
        with c2:
            cache_sizes = [16, 32, 64, 128, 256, 512, 1024]
            cache_size_val = st.selectbox("Cache Size (Bytes)", cache_sizes, index=cache_sizes.index(sim.cache_size) if sim.cache_size in cache_sizes else 2)
        with c3:
            block_sizes = [4, 8, 16, 32]
            block_size_val = st.selectbox("Block / Line Size (Bytes)", block_sizes, index=block_sizes.index(sim.block_size) if sim.block_size in block_sizes else 1)

        c4, c5, c6 = st.columns(3)
        with c4:
            mapping_options = ["Direct Mapped (1-Way)", "2-Way Set Associative", "4-Way Set Associative", "Fully Associative"]
            default_map_idx = 0
            if sim.ways == 2:
                default_map_idx = 1
            elif sim.ways == 4:
                default_map_idx = 2
            elif sim.num_sets == 1 and sim.ways > 4:
                default_map_idx = 3
            mapping_val = st.selectbox("Mapping Scheme", mapping_options, index=default_map_idx)
        with c5:
            policy_options = [ReplacementPolicy.LRU.value, ReplacementPolicy.FIFO.value]
            default_pol_idx = 0 if sim.policy == ReplacementPolicy.LRU else 1
            policy_val = st.selectbox("Eviction Policy", policy_options, index=default_pol_idx)
        with c6:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Apply Configuration", use_container_width=True):
                if "Direct" in mapping_val:
                    assoc_val = 1
                elif "2-Way" in mapping_val:
                    assoc_val = 2
                elif "4-Way" in mapping_val:
                    assoc_val = 4
                else:
                    assoc_val = 0

                chosen_policy = ReplacementPolicy.LRU if "LRU" in policy_val else ReplacementPolicy.FIFO
                st.session_state.sim = CacheSimulator(cache_size_val, block_size_val, assoc_val, chosen_policy, addr_bits_val)
                st.session_state.queue = []
                st.rerun()

        st.markdown("---")
        st.markdown("#### Bit Partitioning Output")

        offset_low = 0
        offset_high = sim.offset_bits - 1

        if sim.index_bits > 0:
            index_low = sim.offset_bits
            index_high = sim.offset_bits + sim.index_bits - 1
        else:
            index_low = index_high = None

        tag_low = sim.offset_bits + sim.index_bits
        tag_high = sim.addr_bits - 1

        st.markdown(f"""
        <div class="bit-card bit-tag">
            <strong>TAG FIELD:</strong> {sim.tag_bits} Bits &nbsp;|&nbsp; Bit Range: <code>[{tag_high}:{tag_low}]</code>
        </div>
        """, unsafe_allow_html=True)

        index_range_str = f"[{index_high}:{index_low}]" if sim.index_bits > 0 else "None (Single Set)"
        st.markdown(f"""
        <div class="bit-card bit-idx">
            <strong>SET INDEX FIELD:</strong> {sim.index_bits} Bits &nbsp;|&nbsp; Bit Range: <code>{index_range_str}</code>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="bit-card bit-off">
            <strong>BLOCK OFFSET FIELD:</strong> {sim.offset_bits} Bits &nbsp;|&nbsp; Bit Range: <code>[{offset_high}:{offset_low}]</code>
        </div>
        """, unsafe_allow_html=True)

    # ==============================================================================
    # TAB 2: EXECUTION CONTROLLER
    # ==============================================================================
    with tab2:
        st.markdown("#### Memory Access Controller")

        col_in, col_pre = st.columns([2, 1])
        with col_pre:
            preset_choice = st.selectbox(
                "Benchmark Workload Preset",
                ["Custom", "Spatial Locality (Array Scan)", "Temporal Locality (Loop)", "Conflict Thrashing (Direct-Map Test)"]
            )

        preset_map = {
            "Custom": "0x0000, 0x0004, 0x0008, 0x0040, 0x0000",
            "Spatial Locality (Array Scan)": "0x0000, 0x0004, 0x0008, 0x000C, 0x0010, 0x0014",
            "Temporal Locality (Loop)": "0x0010, 0x0020, 0x0010, 0x0020, 0x0010",
            "Conflict Thrashing (Direct-Map Test)": "0x0000, 0x0040, 0x0080, 0x0000, 0x0040"
        }

        uploaded_file = st.file_uploader("Upload Benchmark Trace (.txt or .trace)", type=["txt", "trace"])
        if uploaded_file is not None:
            file_contents = uploaded_file.read().decode("utf-8")
            trace_str = ", ".join(file_contents.replace("\n", ",").replace(" ", ",").split(","))
            trace_str = ", ".join([x.strip() for x in trace_str.split(",") if x.strip()])
        else:
            trace_str = preset_map[preset_choice]

        with col_in:
            trace_input = st.text_input("Memory Addresses (Hexadecimal, comma-separated)", trace_str)

        btn_c1, btn_c2, btn_c3, _ = st.columns([1.3, 1.4, 1.4, 3.5])
        with btn_c1:
            execute_all = st.button("Run Full Trace", use_container_width=True)
        with btn_c2:
            step_one = st.button("Step Next Address", use_container_width=True)
        with btn_c3:
            clear_queue = st.button("Clear Input Queue", use_container_width=True)

        if clear_queue:
            st.session_state.queue = []
            st.info("Input stepping queue cleared.")

        if execute_all:
            raw_addrs = [int(x.strip(), 16) for x in trace_input.split(",") if x.strip()]
            start_cycle = sim.cycle + 1
            initial_hits = sim.hits
            initial_misses = sim.misses

            for addr in raw_addrs:
                res = sim.access(addr)
                st.session_state.session_step_log.append(res)

            st.session_state.queue = []
            batch_hits = sim.hits - initial_hits
            batch_misses = sim.misses - initial_misses
            batch_total = batch_hits + batch_misses
            batch_rate = (batch_hits / batch_total * 100) if batch_total > 0 else 0.0

            st.session_state.session_run_records.append({
                "Run ID": len(st.session_state.session_run_records) + 1,
                "Type": "Batch Trace",
                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                "Trace Input": trace_input,
                "Accesses": batch_total,
                "Hits": batch_hits,
                "Misses": batch_misses,
                "Hit Rate": f"{batch_rate:.1f}%",
                "Cycle Range": f"{start_cycle} - {sim.cycle}"
            })
            st.success(f"Executed batch of {len(raw_addrs)} accesses.")

        if step_one:
            if not st.session_state.queue:
                st.session_state.queue = [int(x.strip(), 16) for x in trace_input.split(",") if x.strip()]
            if st.session_state.queue:
                next_addr = st.session_state.queue.pop(0)
                res = sim.access(next_addr)
                st.session_state.session_step_log.append(res)

                st.session_state.session_run_records.append({
                    "Run ID": len(st.session_state.session_run_records) + 1,
                    "Type": "Single Step",
                    "Timestamp": datetime.now().strftime("%H:%M:%S"),
                    "Trace Input": f"0x{next_addr:04X}",
                    "Accesses": 1,
                    "Hits": 1 if res.is_hit else 0,
                    "Misses": 0 if res.is_hit else 1,
                    "Hit Rate": "100.0%" if res.is_hit else "0.0%",
                    "Cycle Range": f"{sim.cycle}"
                })
                st.info(f"Stepped address 0x{next_addr:04X}. Remaining in queue: {len(st.session_state.queue)}")

        st.markdown("---")
        st.markdown("#### Current Engine Telemetry")
        total_reqs = sim.hits + sim.misses
        hit_rate = (sim.hits / total_reqs * 100) if total_reqs > 0 else 0.0

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Hit Rate", f"{hit_rate:.1f}%")
        m2.metric("Total Hits", sim.hits)
        m3.metric("Cold Misses", sim.compulsory_misses)
        m4.metric("Conflict Misses", sim.conflict_misses)
        m5.metric("Capacity Misses", sim.capacity_misses)

        if st.session_state.session_step_log:
            last_res = st.session_state.session_step_log[-1]
            t_bin, i_bin, o_bin = sim.get_binary_decomposition(last_res.address)
            st.markdown("#### Most Recent Access Bit Parsing")
            st.code(
                f"Address: 0x{last_res.address:04X}  |  Binary: {t_bin} {i_bin} {o_bin}\n"
                f"Tag: {t_bin} (0x{last_res.tag:X})  |  Index: {i_bin if i_bin else 'None'} ({last_res.set_index})  |  Offset: {o_bin} ({last_res.offset} Bytes)",
                language="text"
            )

    # ==============================================================================
    # TAB 3: CACHE MEMORY TABLE (COMPACT METRICS + TABULAR VIEW ONLY)
    # ==============================================================================
    with tab3:
        st.markdown("#### Hardware Cache State Grid")
        
        total_slots = sim.total_blocks
        occupied_slots = sum(b.valid for s in sim.sets for b in s.blocks)
        occupancy_pct = (occupied_slots / total_slots * 100) if total_slots > 0 else 0.0

        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        stat_col1.metric("Total Capacity", f"{sim.cache_size} Bytes")
        stat_col2.metric("Total Hardware Sets", f"{sim.num_sets} Sets")
        stat_col3.metric("Associativity (Ways)", f"{sim.ways} Ways / Set")
        stat_col4.metric("Cache Occupancy", f"{occupied_slots}/{total_slots} ({occupancy_pct:.0f}% Full)")

        st.markdown("---")

        cache_rows = []
        for s_idx, c_set in enumerate(sim.sets):
            for w_idx, block in enumerate(c_set.blocks):
                cache_rows.append({
                    "Set Index": f"Set {s_idx}",
                    "Way (Line)": f"Way {w_idx}",
                    "Status": "VALID" if block.valid else "EMPTY",
                    "Tag (Hex)": f"0x{block.tag:X}" if block.valid else "—",
                    "Insertion Cycle": block.insertion_time if block.valid else "—",
                    "Last Access Cycle": block.last_access_time if block.valid else "—"
                })

        df_cache = pd.DataFrame(cache_rows)
        st.dataframe(df_cache, use_container_width=True, hide_index=True)

    # ==============================================================================
    # TAB 4: SESSION ACCESS STEP LOG (WITH CSV EXPORT)
    # ==============================================================================
    with tab4:
        col_t4_head, col_t4_dl, col_t4_btn = st.columns([3, 1.2, 1])
        with col_t4_head:
            st.markdown("#### Complete Session Access Step Log")
            st.caption("Chronological record of every memory cycle executed during this session.")
        with col_t4_btn:
            if st.button("Clear Step Log"):
                st.session_state.session_step_log = []
                st.session_state.session_run_records = []
                st.rerun()

        if st.session_state.session_step_log:
            log_records = []
            for cycle_idx, h in enumerate(reversed(st.session_state.session_step_log)):
                outcome_str = "HIT" if h.is_hit else f"MISS ({h.miss_type.value})"
                eviction_str = f"Evicted Tag 0x{h.evicted_tag:X}" if h.evicted_tag is not None else "None"
                log_records.append({
                    "Cycle": len(st.session_state.session_step_log) - cycle_idx,
                    "Address": f"0x{h.address:04X}",
                    "Tag": f"0x{h.tag:X}",
                    "Set": h.set_index,
                    "Offset": f"{h.offset} Bytes",
                    "Result": outcome_str,
                    "Target Line": f"Way {h.way_index}",
                    "Eviction Note": eviction_str
                })

            df_log = pd.DataFrame(log_records)

            with col_t4_dl:
                csv_data = df_log.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Log (CSV)",
                    data=csv_data,
                    file_name="cache_simulation_log.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            st.dataframe(df_log, use_container_width=True, hide_index=True)
        else:
            st.info("No accesses recorded in this session yet.")

    # ==============================================================================
    # TAB 5: SESSION TELEMETRY & AMAT CALCULATOR
    # ==============================================================================
    with tab5:
        col_t5_head, col_t5_btn = st.columns([3, 1])
        with col_t5_head:
            st.markdown("#### Cumulative Session Telemetry & AMAT Analysis")
            st.caption("Lifetime analytics and real-time hardware access latency modeling.")
        with col_t5_btn:
            if st.button("Reset Session History"):
                st.session_state.session_run_records = []
                st.session_state.session_step_log = []
                st.rerun()

        if st.session_state.session_step_log:
            total_session_accesses = len(st.session_state.session_step_log)
            total_session_hits = sum(1 for x in st.session_state.session_step_log if x.is_hit)
            total_session_misses = total_session_accesses - total_session_hits
            session_hit_rate = (total_session_hits / total_session_accesses * 100) if total_session_accesses > 0 else 0.0
            session_miss_rate = (total_session_misses / total_session_accesses) if total_session_accesses > 0 else 0.0

            total_cold = sum(1 for x in st.session_state.session_step_log if x.miss_type == MissType.COMPULSORY)
            total_conflict = sum(1 for x in st.session_state.session_step_log if x.miss_type == MissType.CONFLICT)
            total_capacity = sum(1 for x in st.session_state.session_step_log if x.miss_type == MissType.CAPACITY)

            st.markdown("##### Average Memory Access Time (AMAT) Parameters")
            amat_c1, amat_c2, amat_c3 = st.columns(3)
            with amat_c1:
                hit_latency = st.number_input("Cache Hit Latency (Cycles)", min_value=1, max_value=20, value=1)
            with amat_c2:
                miss_penalty = st.number_input("Main Memory Miss Penalty (Cycles)", min_value=10, max_value=500, value=100)
            with amat_c3:
                amat_value = hit_latency + (session_miss_rate * miss_penalty)
                st.metric("Computed AMAT", f"{amat_value:.2f} Cycles")

            st.caption("Formula: AMAT = Hit Latency + (Miss Rate x Miss Penalty)")

            st.markdown("---")
            p1, p2 = st.columns(2)
            with p1:
                st.markdown("##### Performance Summary")
                perf_df = pd.DataFrame([
                    {"Metric": "Total Session Accesses", "Value": str(total_session_accesses)},
                    {"Metric": "Overall Hit Rate", "Value": f"{session_hit_rate:.1f}%"},
                    {"Metric": "Total Hits", "Value": str(total_session_hits)},
                    {"Metric": "Total Misses", "Value": str(total_session_misses)}
                ])
                st.dataframe(perf_df, use_container_width=True, hide_index=True)

            with p2:
                st.markdown("##### Miss Classification Breakdown")
                miss_df = pd.DataFrame([
                    {"Category": "Cold (Compulsory) Misses", "Count": total_cold, "Percentage": f"{(total_cold/total_session_misses*100):.1f}%" if total_session_misses > 0 else "0.0%"},
                    {"Category": "Conflict Misses", "Count": total_conflict, "Percentage": f"{(total_conflict/total_session_misses*100):.1f}%" if total_session_misses > 0 else "0.0%"},
                    {"Category": "Capacity Misses", "Count": total_capacity, "Percentage": f"{(total_capacity/total_session_misses*100):.1f}%" if total_session_misses > 0 else "0.0%"}
                ])
                st.dataframe(miss_df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("##### Workload Execution Log")
            if st.session_state.session_run_records:
                df_runs = pd.DataFrame(st.session_state.session_run_records)
                st.dataframe(df_runs, use_container_width=True, hide_index=True)
        else:
            st.info("No memory accesses have been recorded in this session yet.")