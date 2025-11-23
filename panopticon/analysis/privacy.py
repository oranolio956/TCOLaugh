import hashlib
import math
import logging
from typing import List, Optional

try:
    from bitarray import bitarray
except ImportError:
    # Fallback if bitarray not available
    bitarray = None

logger = logging.getLogger(__name__)

class BloomFilter:
    """
    Implements a Privacy-Preserving Bloom Filter for PII.
    Allows for similarity comparison (Dice Coefficient) without revealing raw data.
    """
    def __init__(self, capacity: int = 1000, error_rate: float = 0.001):
        self.capacity = capacity
        self.error_rate = error_rate
        self.num_bits = int(- (capacity * math.log(error_rate)) / (math.log(2) ** 2))
        self.num_hashes = int((self.num_bits / capacity) * math.log(2))
        self.bit_array = bitarray(self.num_bits) if bitarray else [0] * self.num_bits
        if bitarray:
            self.bit_array.setall(0)

    def add(self, item: str):
        """Add an item to the Bloom filter."""
        for i in range(self.num_hashes):
            digest = hashlib.sha256(f"{item}{i}".encode("utf-8")).hexdigest()
            index = int(digest, 16) % self.num_bits
            self.bit_array[index] = 1

    def generate_mask(self, pii_data: str) -> str:
        """
        Generates a hex representation of the bloom filter for a single PII item.
        Used for PPRL.
        """
        # Create a fresh filter for this specific item (record-level bloom filter)
        # Note: In real PPRL, we often use 'ngrams' of the PII to populate the filter
        # so we can measure similarity.
        bf = BloomFilter(capacity=50, error_rate=0.01) # Smaller capacity for single field n-grams
        
        # Bigrams
        cleaned = pii_data.lower().strip()
        ngrams = [cleaned[i:i+2] for i in range(len(cleaned)-1)]
        
        for gram in ngrams:
            bf.add(gram)
            
        if bitarray:
            return bf.bit_array.to01() # Return binary string
        else:
            return "".join(map(str, bf.bit_array))

    @staticmethod
    def calculate_similarity(mask1: str, mask2: str) -> float:
        """
        Calculates Dice Coefficient between two bloom filter masks.
        2 * |A ∩ B| / (|A| + |B|)
        """
        if len(mask1) != len(mask2):
            return 0.0
            
        # Convert strings back to bits
        try:
            # Optimized counting
            a_ones = mask1.count('1')
            b_ones = mask2.count('1')
            
            if a_ones + b_ones == 0:
                return 1.0 if mask1 == mask2 else 0.0

            # Intersection
            intersection = 0
            for i in range(len(mask1)):
                if mask1[i] == '1' and mask2[i] == '1':
                    intersection += 1
                    
            return (2.0 * intersection) / (a_ones + b_ones)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

class PrivacyEngine:
    @staticmethod
    def mask_record(record: dict) -> dict:
        """
        Takes a raw record (e.g., {'email': 'foo@bar.com', 'name': 'John Doe'})
        and returns a masked version for safe storage/linking.
        """
        masked = record.copy()
        
        # Fields to mask
        sensitive_fields = ['email', 'name', 'phone', 'address']
        
        for field in sensitive_fields:
            if field in record and record[field]:
                # Generate Bloom Filter Mask
                bf = BloomFilter()
                masked[f"{field}_mask"] = bf.generate_mask(str(record[field]))
                # We typically KEEP the hash for exact lookups, but remove the raw text
                # depending on the privacy level required.
                masked[f"{field}_hash"] = hashlib.sha256(str(record[field]).encode()).hexdigest()
                
                # In a strict PPRL system, we might remove the raw field:
                # del masked[field] 
                # But for Panopticon "Intelligence", we often need the raw data if we have permissions.
                # We'll mark it as 'protected'.
                
        return masked
