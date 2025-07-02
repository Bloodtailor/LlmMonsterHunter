# Test Enhanced Pagination API
# Comprehensive test of new server-side filtering, sorting, and pagination
# Tests the correct order of operations: filter -> sort -> paginate

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:5000/api"

def test_api_call(endpoint: str, expected_success: bool = True) -> Dict[str, Any]:
    """Make API call and return response with error handling"""
    try:
        print(f"\n🔍 Testing: {endpoint}")
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', 'Unknown')}")
            return data
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
                return error_data
            except:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return {"success": False, "error": str(e)}

def print_monster_summary(monsters, title="Monsters"):
    """Print a concise summary of monsters for verification"""
    print(f"\n📋 {title} ({len(monsters)} total):")
    
    if not monsters:
        print("   (No monsters returned)")
        return
    
    for i, monster in enumerate(monsters[:5]):  # Show first 5
        name = monster.get('name', 'Unknown')
        species = monster.get('species', 'Unknown')
        created = monster.get('created_at', '')[:10]  # Just date part
        has_art = monster.get('card_art', {}).get('has_card_art', False)
        art_status = "🎨" if has_art else "❌"
        
        print(f"   {i+1}. {name} ({species}) - {created} {art_status}")
    
    if len(monsters) > 5:
        print(f"   ... and {len(monsters) - 5} more")

def print_pagination_info(pagination, title="Pagination"):
    """Print pagination details"""
    print(f"\n📄 {title}:")
    print(f"   Limit: {pagination.get('limit', 'Unknown')}")
    print(f"   Offset: {pagination.get('offset', 'Unknown')}")
    print(f"   Has More: {pagination.get('has_more', 'Unknown')}")
    print(f"   Next Offset: {pagination.get('next_offset', 'None')}")
    print(f"   Prev Offset: {pagination.get('prev_offset', 'None')}")

def print_stats_summary(stats, filter_applied="all"):
    """Print statistics summary"""
    print(f"\n📊 Statistics (filter: {filter_applied}):")
    print(f"   Total Monsters: {stats.get('total_monsters', 0)}")
    print(f"   Total Abilities: {stats.get('total_abilities', 0)}")
    print(f"   With Card Art: {stats.get('with_card_art', 0)}")
    print(f"   Without Card Art: {stats.get('without_card_art', 0)}")
    print(f"   Card Art %: {stats.get('card_art_percentage', 0)}%")
    print(f"   Unique Species: {stats.get('unique_species', 0)}")
    
    species_breakdown = stats.get('species_breakdown', {})
    if species_breakdown:
        print(f"   Top Species: {list(species_breakdown.items())[:3]}")

def test_basic_functionality():
    """Test 1: Basic functionality without parameters"""
    print("=" * 60)
    print("🧪 TEST 1: Basic Functionality")
    print("=" * 60)
    
    # Test basic monsters endpoint
    response = test_api_call("/monsters")
    
    if response.get('success'):
        monsters = response.get('monsters', [])
        pagination = response.get('pagination', {})
        total = response.get('total', 0)
        
        print(f"\n✅ Basic monsters endpoint working")
        print(f"   Total in DB: {total}")
        print(f"   Returned: {len(monsters)}")
        
        print_monster_summary(monsters, "Default Response")
        print_pagination_info(pagination)
    else:
        print(f"❌ Basic endpoint failed: {response.get('error')}")
        return False
    
    # Test basic stats endpoint
    stats_response = test_api_call("/monsters/stats")
    
    if stats_response.get('success'):
        stats = stats_response.get('stats', {})
        print_stats_summary(stats)
    else:
        print(f"❌ Stats endpoint failed: {stats_response.get('error')}")
    
    return True

def test_pagination_order():
    """Test 2: Verify correct order of operations (filter -> sort -> paginate)"""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Order of Operations (Filter -> Sort -> Paginate)")
    print("=" * 60)
    
    # Get monsters with card art, sorted by name, limited to 3
    response = test_api_call("/monsters?limit=3&filter=with_art&sort=name")
    
    if not response.get('success'):
        print(f"❌ Order test failed: {response.get('error')}")
        return False
    
    monsters = response.get('monsters', [])
    total = response.get('total', 0)
    pagination = response.get('pagination', {})
    filters = response.get('filters_applied', {})
    
    print(f"\n✅ Filter -> Sort -> Paginate test")
    print(f"   Filter Applied: {filters.get('filter_type')}")
    print(f"   Sort Applied: {filters.get('sort_by')}")
    print(f"   Total Matching Filter: {total}")
    print(f"   Returned (limit 3): {len(monsters)}")
    
    print_monster_summary(monsters, "Filtered, Sorted, Paginated")
    
    # Verify they all have card art (filter worked)
    all_have_art = all(monster.get('card_art', {}).get('has_card_art', False) for monster in monsters)
    print(f"\n🔍 Verification:")
    print(f"   All have card art: {all_have_art} {'✅' if all_have_art else '❌'}")
    
    # Verify they're sorted by name (sort worked)
    names = [monster.get('name', '') for monster in monsters]
    sorted_names = sorted(names)
    names_sorted = names == sorted_names
    print(f"   Names sorted alphabetically: {names_sorted} {'✅' if names_sorted else '❌'}")
    print(f"   Names: {names}")
    
    return all_have_art and names_sorted

def test_filtering_options():
    """Test 3: All filtering options"""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Filtering Options")
    print("=" * 60)
    
    filters = ['all', 'with_art', 'without_art']
    results = {}
    
    for filter_type in filters:
        response = test_api_call(f"/monsters?filter={filter_type}&limit=5")
        
        if response.get('success'):
            total = response.get('total', 0)
            monsters = response.get('monsters', [])
            results[filter_type] = {'total': total, 'monsters': monsters}
            
            print(f"\n✅ Filter '{filter_type}': {total} total monsters")
            
            # Verify filter correctness
            if filter_type == 'with_art':
                all_have_art = all(monster.get('card_art', {}).get('has_card_art', False) for monster in monsters)
                print(f"   All have art: {all_have_art} {'✅' if all_have_art else '❌'}")
            elif filter_type == 'without_art':
                none_have_art = all(not monster.get('card_art', {}).get('has_card_art', False) for monster in monsters)
                print(f"   None have art: {none_have_art} {'✅' if none_have_art else '❌'}")
        else:
            print(f"❌ Filter '{filter_type}' failed: {response.get('error')}")
            return False
    
    # Verify math: all = with_art + without_art
    total_all = results['all']['total']
    total_with = results['with_art']['total']
    total_without = results['without_art']['total']
    
    math_correct = total_all == (total_with + total_without)
    print(f"\n🔍 Math Check:")
    print(f"   All: {total_all} = With Art: {total_with} + Without Art: {total_without}")
    print(f"   Math correct: {math_correct} {'✅' if math_correct else '❌'}")
    
    return math_correct

def test_sorting_options():
    """Test 4: All sorting options"""
    print("\n" + "=" * 60)
    print("🧪 TEST 4: Sorting Options")
    print("=" * 60)
    
    sorts = ['newest', 'oldest', 'name', 'species']
    
    for sort_type in sorts:
        response = test_api_call(f"/monsters?sort={sort_type}&limit=5")
        
        if response.get('success'):
            monsters = response.get('monsters', [])
            print(f"\n✅ Sort '{sort_type}': {len(monsters)} monsters")
            
            # Show first few to verify sort order
            if sort_type in ['newest', 'oldest']:
                dates = [monster.get('created_at', '')[:10] for monster in monsters]
                print(f"   Dates: {dates}")
            elif sort_type == 'name':
                names = [monster.get('name', '') for monster in monsters]
                print(f"   Names: {names}")
            elif sort_type == 'species':
                species = [monster.get('species', '') for monster in monsters]
                print(f"   Species: {species}")
            
        else:
            print(f"❌ Sort '{sort_type}' failed: {response.get('error')}")
            return False
    
    return True

def test_statistics_filtering():
    """Test 5: Statistics with filtering"""
    print("\n" + "=" * 60)
    print("🧪 TEST 5: Statistics with Filtering")
    print("=" * 60)
    
    filters = ['all', 'with_art', 'without_art']
    
    for filter_type in filters:
        response = test_api_call(f"/monsters/stats?filter={filter_type}")
        
        if response.get('success'):
            stats = response.get('stats', {})
            filter_applied = response.get('filter_applied', 'unknown')
            context = response.get('context')
            
            print(f"\n✅ Stats with filter '{filter_type}':")
            print_stats_summary(stats, filter_applied)
            
            if context:
                print(f"   Context - All Monsters: {context.get('all_monsters_count', 0)}")
                print(f"   Context - Overall Art %: {context.get('overall_card_art_percentage', 0)}%")
                
        else:
            print(f"❌ Stats filter '{filter_type}' failed: {response.get('error')}")
            return False
    
    return True

def test_pagination_flow():
    """Test 6: Multi-page pagination flow"""
    print("\n" + "=" * 60)
    print("🧪 TEST 6: Multi-Page Pagination Flow")
    print("=" * 60)
    
    page_size = 3
    current_offset = 0
    page_num = 1
    all_monster_ids = []
    
    while True:
        response = test_api_call(f"/monsters?limit={page_size}&offset={current_offset}&sort=name")
        
        if not response.get('success'):
            print(f"❌ Pagination failed: {response.get('error')}")
            return False
        
        monsters = response.get('monsters', [])
        pagination = response.get('pagination', {})
        total = response.get('total', 0)
        
        print(f"\n📄 Page {page_num} (offset {current_offset}):")
        print(f"   Got {len(monsters)} monsters")
        
        # Collect monster IDs to check for duplicates
        page_ids = [monster.get('id') for monster in monsters]
        all_monster_ids.extend(page_ids)
        
        # Show monster names (should be in alphabetical order)
        names = [monster.get('name', '') for monster in monsters]
        print(f"   Names: {names}")
        
        # Check if we have more pages
        has_more = pagination.get('has_more', False)
        next_offset = pagination.get('next_offset')
        
        print(f"   Has more: {has_more}")
        print(f"   Next offset: {next_offset}")
        
        if not has_more or next_offset is None:
            break
        
        current_offset = next_offset
        page_num += 1
        
        # Safety break to avoid infinite loops
        if page_num > 50:
            print("⚠️ Safety break: Too many pages")
            break
    
    # Check for duplicate IDs (should be none)
    unique_ids = set(all_monster_ids)
    has_duplicates = len(unique_ids) != len(all_monster_ids)
    
    print(f"\n🔍 Pagination Verification:")
    print(f"   Total pages: {page_num}")
    print(f"   Total monsters seen: {len(all_monster_ids)}")
    print(f"   Unique monsters: {len(unique_ids)}")
    print(f"   Has duplicates: {has_duplicates} {'❌' if has_duplicates else '✅'}")
    
    return not has_duplicates

def test_error_handling():
    """Test 7: Error handling for invalid parameters"""
    print("\n" + "=" * 60)
    print("🧪 TEST 7: Error Handling")
    print("=" * 60)
    
    error_tests = [
        ("/monsters?filter=invalid", "Invalid filter"),
        ("/monsters?sort=invalid", "Invalid sort"),
        ("/monsters?limit=-1", "Invalid limit"),
        ("/monsters?offset=-5", "Invalid offset"),
        ("/monsters?limit=abc", "Invalid limit type"),
        ("/monsters?offset=xyz", "Invalid offset type"),
        ("/monsters/stats?filter=bad", "Invalid stats filter")
    ]
    
    all_errors_handled = True
    
    for endpoint, expected_error in error_tests:
        response = test_api_call(endpoint, expected_success=False)
        
        if response.get('success') == False:
            error_msg = response.get('error', '')
            print(f"   ✅ Correctly rejected: {endpoint}")
            print(f"      Error: {error_msg}")
        else:
            print(f"   ❌ Should have failed: {endpoint}")
            all_errors_handled = False
    
    return all_errors_handled

def main():
    """Run all tests"""
    print("🧪 Enhanced Pagination API Test Suite")
    print("Testing server-side filtering, sorting, and pagination")
    print("Verifying correct order: Filter -> Sort -> Paginate")
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Order of Operations", test_pagination_order),
        ("Filtering Options", test_filtering_options),
        ("Sorting Options", test_sorting_options),
        ("Statistics Filtering", test_statistics_filtering),
        ("Pagination Flow", test_pagination_flow),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            print(f"\n💥 {test_name}: CRASHED - {e}")
    
    print("\n" + "=" * 60)
    print("🏁 TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Enhanced pagination is working correctly.")
        print("✅ Filter -> Sort -> Paginate order verified")
        print("✅ Server-side operations confirmed")
        print("✅ Frontend can now implement efficient pagination")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print(f"\n💡 Frontend can now use these endpoints:")
    print(f"   GET /api/monsters?limit=12&filter=with_art&sort=name")
    print(f"   GET /api/monsters/stats?filter=without_art")

if __name__ == "__main__":
    main()