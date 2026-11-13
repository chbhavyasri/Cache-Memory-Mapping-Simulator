"""
cache_engine.py - Core Architecture Simulation Engine
Author: COA Project Team
Description: Simulates Direct-Mapped, Set-Associative, and Fully-Associative caches
             with bitwise address dissection, LRU/FIFO replacement, and 3C's miss classification.
"""

import math
from enum import Enum
from collections import deque


class ReplacementPolicy(Enum):
    LRU = "LRU (Least Recently Used)"
    FIFO = "FIFO (First In First Out)"


class MissType(Enum):
    NONE = "Hit"
    COMPULSORY = "Compulsory (Cold)"
    CONFLICT = "Conflict"
    CAPACITY = "Capacity"


class CacheBlock:
    """Represents a single cache line/block."""
    def __init__(self):
        self.valid = False
        self.tag = 0
        self.insertion_time = 0    # Used for FIFO
        self.last_access_time = 0  # Used for LRU


class CacheSet:
    """Represents a set containing one or more cache blocks (ways)."""
    def __init__(self, ways: int):
        self.blocks = [CacheBlock() for _ in range(ways)]


class AccessResult:
    """Encapsulates the complete result of a single memory access."""
    def __init__(self, address: int, tag: int, set_index: int, offset: int,
                 is_hit: bool, miss_type: MissType, evicted_tag=None, way_index: int = 0):
        self.address = address
        self.tag = tag
        self.set_index = set_index
        self.offset = offset
        self.is_hit = is_hit
        self.miss_type = miss_type
        self.evicted_tag = evicted_tag
        self.way_index = way_index


class CacheSimulator:
    """The central hardware cache controller simulation."""
    def __init__(self, cache_size_bytes: int, block_size_bytes: int, associativity: int,
                 policy: ReplacementPolicy = ReplacementPolicy.LRU, addr_bits: int = 32):
        self.cache_size = cache_size_bytes
        self.block_size = block_size_bytes
        self.policy = policy
        self.addr_bits = addr_bits
        self.cycle = 0

        # Hardware sanity checks
        if not self._is_power_of_two(cache_size_bytes):
            raise ValueError("Cache Size must be a power of 2.")
        if not self._is_power_of_two(block_size_bytes):
            raise ValueError("Block Size must be a power of 2.")
        if block_size_bytes > cache_size_bytes:
            raise ValueError("Block Size cannot exceed Cache Size.")

        self.total_blocks = self.cache_size // self.block_size

        # Associativity configuration
        # associativity == 0 or >= total_blocks indicates Fully Associative
        if associativity == 0 or associativity >= self.total_blocks:
            self.ways = self.total_blocks
            self.num_sets = 1
            self.mapping_type = "Fully Associative"
        elif associativity == 1:
            self.ways = 1
            self.num_sets = self.total_blocks
            self.mapping_type = "Direct Mapped"
        else:
            self.ways = associativity
            self.num_sets = self.total_blocks // self.ways
            self.mapping_type = f"{self.ways}-Way Set Associative"

        # Bit allocations
        self.offset_bits = int(math.log2(self.block_size))
        self.index_bits = int(math.log2(self.num_sets)) if self.num_sets > 1 else 0
        self.tag_bits = self.addr_bits - self.index_bits - self.offset_bits

        if self.tag_bits < 0:
            raise ValueError("Address width is too small for this cache configuration.")

        # Main cache memory array
        self.sets = [CacheSet(self.ways) for _ in range(self.num_sets)]

        # Tracking state for 3-C's miss categorization
        self.seen_blocks = set()
        self.shadow_fa_cache = deque(maxlen=self.total_blocks)

        # Performance counters
        self.hits = 0
        self.misses = 0
        self.compulsory_misses = 0
        self.conflict_misses = 0
        self.capacity_misses = 0

    @staticmethod
    def _is_power_of_two(n: int) -> bool:
        return (n > 0) and (n & (n - 1)) == 0

    def parse_address(self, address: int):
        """Splits an address into (Tag, Set Index, Block Offset) using bitwise operations."""
        offset_mask = (1 << self.offset_bits) - 1
        offset = address & offset_mask

        shifted = address >> self.offset_bits
        if self.index_bits > 0:
            index_mask = (1 << self.index_bits) - 1
            set_index = shifted & index_mask
            tag = shifted >> self.index_bits
        else:
            set_index = 0
            tag = shifted

        return tag, set_index, offset

    def get_binary_decomposition(self, address: int):
        """Returns the binary representation split into Tag, Index, and Offset strings."""
        bin_str = bin(address)[2:].zfill(self.addr_bits)
        tag_str = bin_str[:self.tag_bits]
        idx_str = bin_str[self.tag_bits: self.tag_bits + self.index_bits] if self.index_bits > 0 else ""
        off_str = bin_str[self.tag_bits + self.index_bits:]
        return tag_str, idx_str, off_str

    def access(self, address: int) -> AccessResult:
        """Simulates a memory read/write access."""
        self.cycle += 1
        tag, set_index, offset = self.parse_address(address)
        block_id = address >> self.offset_bits
        target_set = self.sets[set_index]

        # 1. Search for a Cache Hit
        for way_idx, block in enumerate(target_set.blocks):
            if block.valid and block.tag == tag:
                self.hits += 1
                block.last_access_time = self.cycle
                
                # Keep shadow cache updated
                if block_id in self.shadow_fa_cache:
                    self.shadow_fa_cache.remove(block_id)
                self.shadow_fa_cache.append(block_id)
                
                return AccessResult(address, tag, set_index, offset, True, MissType.NONE, None, way_idx)

        # 2. Handle a Cache Miss -> Classify Miss Type
        self.misses += 1
        if block_id not in self.seen_blocks:
            miss_type = MissType.COMPULSORY
            self.compulsory_misses += 1
            self.seen_blocks.add(block_id)
        elif block_id in self.shadow_fa_cache:
            # If it would have hit in an ideal fully-associative cache of the same size,
            # this miss was solely caused by set mapping restrictions.
            miss_type = MissType.CONFLICT
            self.conflict_misses += 1
        else:
            # Even a fully associative cache would have evicted it.
            miss_type = MissType.CAPACITY
            self.capacity_misses += 1

        # Update shadow cache
        if block_id in self.shadow_fa_cache:
            self.shadow_fa_cache.remove(block_id)
        self.shadow_fa_cache.append(block_id)

        # 3. Check for an empty slot in the target set
        for way_idx, block in enumerate(target_set.blocks):
            if not block.valid:
                block.valid = True
                block.tag = tag
                block.insertion_time = self.cycle
                block.last_access_time = self.cycle
                return AccessResult(address, tag, set_index, offset, False, miss_type, None, way_idx)

        # 4. Set is full -> Evict victim according to chosen policy
        if self.policy == ReplacementPolicy.FIFO:
            victim_idx = min(range(self.ways), key=lambda i: target_set.blocks[i].insertion_time)
        else:  # LRU
            victim_idx = min(range(self.ways), key=lambda i: target_set.blocks[i].last_access_time)

        victim_block = target_set.blocks[victim_idx]
        evicted_tag = victim_block.tag

        victim_block.tag = tag
        victim_block.insertion_time = self.cycle
        victim_block.last_access_time = self.cycle

        return AccessResult(address, tag, set_index, offset, False, miss_type, evicted_tag, victim_idx)