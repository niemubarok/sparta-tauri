#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Performance Test Script untuk Member Card vs Barcode
Test dan bandingkan performance member card lookup setelah optimasi
"""

from __future__ import absolute_import, print_function, unicode_literals

import sys
import os
import time
import logging

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_service import db_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_member_optimization():
    """Test member card optimization"""
    print("=" * 70)
    print("MEMBER CARD OPTIMIZATION TEST")
    print("=" * 70)
    
    try:
        # Check database connection
        if not db_service.local_db:
            print("❌ Database not connected")
            return False
        
        print("✅ Database connected")
        
        # Check if views are initialized
        print("\n1. Checking member optimization views...")
        if db_service.views_initialized:
            print("✅ Member views initialized")
        else:
            print("⚠️  Member views not initialized, initializing now...")
            success = db_service._initialize_member_views()
            if success:
                print("✅ Member views initialized successfully")
            else:
                print("❌ Failed to initialize member views")
        
        # Check member cache
        print("\n2. Checking member cache...")
        cache_stats = db_service.get_member_cache_stats()
        if cache_stats.get('enabled', True):
            print("✅ Member cache enabled")
            print("   Cache size: {}/{}".format(
                cache_stats.get('cache_size', 0), 
                cache_stats.get('max_size', 0)
            ))
            print("   Hit rate: {:.1f}%".format(cache_stats.get('hit_rate', 0)))
        else:
            print("❌ Member cache disabled")
        
        # Create test data
        print("\n3. Creating test data...")
        test_cards = ["TESTCARD001", "TESTCARD002", "TESTCARD003"]
        test_barcodes = ["TESTBAR001", "TESTBAR002", "TESTBAR003"]
        
        # Create test member entries
        member_count = 0
        for card in test_cards:
            success = db_service.create_test_member_entry(card, "PLATE{}".format(card[-3:]))
            if success:
                member_count += 1
        
        # Create test parking transactions
        barcode_count = 0
        for barcode in test_barcodes:
            success = db_service.create_test_transaction(barcode, "PLATE{}".format(barcode[-3:]))
            if success:
                barcode_count += 1
        
        print("✅ Created {} test members and {} test parking transactions".format(
            member_count, barcode_count))
        
        # Test member lookup performance
        print("\n4. Testing member lookup performance...")
        
        # Test uncached
        db_service.invalidate_member_cache()
        start_time = time.time()
        result1 = db_service.find_member_transaction_optimized("TESTCARD001")
        uncached_time = (time.time() - start_time) * 1000
        
        # Test cached
        start_time = time.time()
        result2 = db_service.find_member_transaction_optimized("TESTCARD001")
        cached_time = (time.time() - start_time) * 1000
        
        # Test barcode lookup for comparison
        start_time = time.time()
        result3 = db_service.find_transaction_by_barcode("TESTBAR001")
        barcode_time = (time.time() - start_time) * 1000
        
        print("   Member lookup (uncached): {:.2f}ms".format(uncached_time))
        print("   Member lookup (cached):   {:.2f}ms".format(cached_time))
        print("   Barcode lookup:           {:.2f}ms".format(barcode_time))
        
        # Performance comparison
        cache_improvement = ((uncached_time - cached_time) / uncached_time) * 100
        vs_barcode_cached = cached_time / barcode_time
        vs_barcode_uncached = uncached_time / barcode_time
        
        print("\n5. Performance Analysis:")
        print("   Cache improvement: {:.1f}%".format(cache_improvement))
        print("   Cached vs barcode: {:.1f}x slower".format(vs_barcode_cached))
        print("   Uncached vs barcode: {:.1f}x slower".format(vs_barcode_uncached))
        
        # Success criteria
        success = True
        if cached_time > barcode_time * 3:  # Cached should be within 3x of barcode
            print("⚠️  WARNING: Cached member lookup is significantly slower than barcode")
            success = False
        
        if uncached_time > 50:  # Uncached should be under 50ms
            print("⚠️  WARNING: Uncached member lookup is too slow")
            success = False
        
        if cache_improvement < 50:  # Cache should provide at least 50% improvement
            print("⚠️  WARNING: Cache improvement is less than expected")
            success = False
        
        # Test process_vehicle_exit with members
        print("\n6. Testing integrated exit processing...")
        
        start_time = time.time()
        exit_result = db_service.process_vehicle_exit(
            "TESTCARD002", 
            "TEST_OPERATOR", 
            "TEST_GATE"
        )
        exit_time = (time.time() - start_time) * 1000
        
        if exit_result['success']:
            print("✅ Member exit processed successfully ({:.2f}ms)".format(exit_time))
            print("   Search method: {}".format(exit_result.get('search_method')))
            print("   Transaction type: {}".format(exit_result.get('transaction_type')))
            print("   Search time: {:.2f}ms".format(exit_result.get('search_time_ms', 0)))
        else:
            print("❌ Member exit processing failed: {}".format(exit_result.get('message')))
            success = False
        
        # Cleanup
        print("\n7. Cleaning up test data...")
        cleanup_success = db_service.cleanup_test_transactions()
        if cleanup_success:
            print("✅ Test data cleaned up")
        else:
            print("⚠️  Warning: Failed to clean up test data")
        
        # Final cache stats
        final_cache_stats = db_service.get_member_cache_stats()
        print("\n8. Final cache statistics:")
        print("   Total requests: {}".format(final_cache_stats.get('total_requests', 0)))
        print("   Cache hits: {}".format(final_cache_stats.get('hits', 0)))
        print("   Cache misses: {}".format(final_cache_stats.get('misses', 0)))
        print("   Hit rate: {:.1f}%".format(final_cache_stats.get('hit_rate', 0)))
        
        print("\n" + "=" * 70)
        if success:
            print("✅ MEMBER OPTIMIZATION TEST PASSED")
            print("🎯 Member card performance has been optimized successfully!")
        else:
            print("❌ MEMBER OPTIMIZATION TEST FAILED")
            print("⚠️  Some performance targets were not met")
        print("=" * 70)
        
        return success
        
    except Exception as e:
        print("❌ Error during test: {}".format(str(e)))
        logger.error("Test error: {}".format(str(e)))
        return False

def run_comprehensive_benchmark():
    """Run comprehensive benchmark test"""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE PERFORMANCE BENCHMARK")
    print("=" * 70)
    
    try:
        # Run benchmark
        results = db_service.benchmark_member_vs_barcode(test_iterations=20)
        
        if results:
            print("\n🎯 BENCHMARK COMPLETED SUCCESSFULLY!")
            print("\nKey Performance Metrics:")
            print("  Barcode average:        {:.2f}ms".format(results['barcode']['avg']))
            print("  Member cached average:  {:.2f}ms".format(results['member_cached']['avg']))
            print("  Member uncached average:{:.2f}ms".format(results['member_uncached']['avg']))
            print("  Cache improvement:      {:.1f}%".format(results['improvement_percent']))
            print("  Performance vs barcode:")
            print("    Cached:    {:.1f}x slower".format(results['vs_barcode_factor']['cached']))
            print("    Uncached:  {:.1f}x slower".format(results['vs_barcode_factor']['uncached']))
            
            # Success criteria
            success = True
            
            if results['vs_barcode_factor']['cached'] > 5:
                print("⚠️  WARNING: Cached member lookup is more than 5x slower than barcode")
                success = False
            
            if results['improvement_percent'] < 70:
                print("⚠️  WARNING: Cache improvement is less than 70%")
                success = False
            
            if results['member_cached']['avg'] > 10:
                print("⚠️  WARNING: Cached member lookup is slower than 10ms")
                success = False
            
            return success
        else:
            print("❌ Benchmark failed to run")
            return False
            
    except Exception as e:
        print("❌ Benchmark error: {}".format(str(e)))
        return False

if __name__ == "__main__":
    print("Starting Member Card Performance Tests...")
    
    # Run basic optimization test
    test_success = test_member_optimization()
    
    if test_success:
        # Run comprehensive benchmark
        benchmark_success = run_comprehensive_benchmark()
        
        if benchmark_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Member card performance optimization is working correctly")
            print("🚀 Member cards now have performance comparable to barcode scanning")
        else:
            print("\n⚠️  BENCHMARK WARNINGS")
            print("Member optimization is working but may need further tuning")
    else:
        print("\n❌ BASIC TESTS FAILED")
        print("Member optimization needs troubleshooting")
    
    print("\nTest completed.")
