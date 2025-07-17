#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Member Cache Service untuk optimasi performance member card lookup
Compatible with Python 2.7 and 3.x
"""

from __future__ import absolute_import, print_function, unicode_literals

import time
import logging
import threading
from collections import OrderedDict

logger = logging.getLogger(__name__)

class MemberCache(object):
    """High-performance cache untuk member cards dengan LRU eviction dan TTL"""
    
    def __init__(self, max_size=1000, ttl=300):  # 5 minutes TTL
        """
        Initialize member cache
        
        Args:
            max_size (int): Maximum cache size (default: 1000)
            ttl (int): Time to live in seconds (default: 300 = 5 minutes)
        """
        self.cache = OrderedDict()
        self.access_times = {}
        self.max_size = max_size
        self.ttl = ttl
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_requests': 0
        }
        
        logger.info("Member cache initialized (max_size: {}, ttl: {}s)".format(max_size, ttl))
    
    def get(self, card_number):
        """
        Get member from cache
        
        Args:
            card_number (str): Card number to lookup
            
        Returns:
            dict or None: Member data if found and valid, None otherwise
        """
        with self.lock:
            current_time = time.time()
            self.stats['total_requests'] += 1
            
            # Check if exists and not expired
            if card_number in self.cache:
                access_time = self.access_times.get(card_number, 0)
                if current_time - access_time < self.ttl:
                    # Move to end (LRU)
                    self.cache.move_to_end(card_number)
                    self.access_times[card_number] = current_time
                    self.stats['hits'] += 1
                    
                    logger.debug("Cache HIT for card: {}".format(card_number))
                    return self.cache[card_number]
                else:
                    # Expired
                    del self.cache[card_number]
                    del self.access_times[card_number]
                    logger.debug("Cache EXPIRED for card: {}".format(card_number))
            
            self.stats['misses'] += 1
            logger.debug("Cache MISS for card: {}".format(card_number))
            return None
    
    def put(self, card_number, member_data):
        """
        Put member in cache
        
        Args:
            card_number (str): Card number
            member_data (dict): Member data to cache
        """
        with self.lock:
            current_time = time.time()
            
            # Remove oldest if at capacity
            if len(self.cache) >= self.max_size and card_number not in self.cache:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
                self.stats['evictions'] += 1
                logger.debug("Evicted cache entry: {}".format(oldest_key))
            
            # Store in cache
            self.cache[card_number] = member_data.copy() if isinstance(member_data, dict) else member_data
            self.access_times[card_number] = current_time
            self.cache.move_to_end(card_number)
            
            logger.debug("Cached member: {}".format(card_number))
    
    def invalidate(self, card_number=None):
        """
        Invalidate cache entry or all
        
        Args:
            card_number (str, optional): Specific card to invalidate, None for all
        """
        with self.lock:
            if card_number:
                self.cache.pop(card_number, None)
                self.access_times.pop(card_number, None)
                logger.debug("Invalidated cache for card: {}".format(card_number))
            else:
                self.cache.clear()
                self.access_times.clear()
                logger.info("Invalidated entire member cache")
    
    def get_stats(self):
        """
        Get cache statistics
        
        Returns:
            dict: Cache performance statistics
        """
        with self.lock:
            total_requests = self.stats['total_requests']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'evictions': self.stats['evictions'],
                'total_requests': total_requests,
                'hit_rate': round(hit_rate, 2),
                'cache_size': len(self.cache),
                'max_size': self.max_size,
                'ttl_seconds': self.ttl
            }
    
    def cleanup_expired(self):
        """
        Clean up expired entries manually
        
        Returns:
            int: Number of expired entries removed
        """
        with self.lock:
            current_time = time.time()
            expired_keys = []
            
            for card_number, access_time in self.access_times.items():
                if current_time - access_time >= self.ttl:
                    expired_keys.append(card_number)
            
            for key in expired_keys:
                del self.cache[key]
                del self.access_times[key]
            
            if expired_keys:
                logger.info("Cleaned up {} expired cache entries".format(len(expired_keys)))
            
            return len(expired_keys)
    
    def preload_members(self, members_list):
        """
        Preload multiple members into cache
        
        Args:
            members_list (list): List of member dictionaries with card_number field
            
        Returns:
            int: Number of members preloaded
        """
        with self.lock:
            count = 0
            
            for member in members_list:
                if isinstance(member, dict) and member.get('card_number'):
                    card_number = member['card_number']
                    self.put(card_number, member)
                    count += 1
            
            logger.info("Preloaded {} members into cache".format(count))
            return count


# Global member cache instance
member_cache = MemberCache()
