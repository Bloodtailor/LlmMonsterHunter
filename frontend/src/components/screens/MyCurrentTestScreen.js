import React, { useState, useEffect, useCallback } from "react";
import { useApi } from "../../refactored/shared/hooks/useApi";
import { usePagination, useSimplePagination } from "../../refactored/shared/hooks/usePagination";
import { loadMonsters } from "../../refactored/api/services/monsters";

// Import all pagination components
import FullPagination, { PAGINATION_LAYOUTS } from "../../refactored/shared/components/Pagination";
import { 
  Pagination as PaginationPrimitive, 
  PaginationInfo, 
  PageJumper, 
  ItemsPerPageSelector 
} from "../../refactored/shared/ui/Pagination";

function MyCurrentTestScreen() {
    const [limit, setLimit] = useState(5);
    const [filter, setFilter] = useState('all');

    // API hook
    const { 
        data: rawApiData, 
        execute: executeLoadMonsters, 
        isLoading,
        isError,
        error
    } = useApi(loadMonsters);

    // Full-featured pagination hook
    const fullPagination = usePagination({ 
        limit, 
        total: rawApiData?.total || null
    });

    // Simple pagination hook (no total)
    const simplePagination = useSimplePagination(1);

    // Load monsters function
    const loadMonstersWithPagination = useCallback(async () => {
        console.log('Loading monsters:', {
            limit,
            offset: fullPagination.currentOffset,
            page: fullPagination.currentPage,
            filter
        });

        await executeLoadMonsters({
            limit,
            offset: fullPagination.currentOffset,
            filter: filter !== 'all' ? filter : undefined
        });
    }, [limit, fullPagination.currentOffset, executeLoadMonsters, filter]);

    // Auto-load when pagination or filter changes
    useEffect(() => {
        loadMonstersWithPagination();
    }, [loadMonstersWithPagination]);

    // Handle limit change
    const handleLimitChange = useCallback((newLimit) => {
        console.log('Limit changed to:', newLimit);
        setLimit(newLimit);
    }, []);

    return (
        <div>
            <h1>Complete Pagination System Test</h1>
            
            {/* Current Status */}
            <div>
                <h2>Current Status</h2>
                <p>
                    API: {isLoading ? 'Loading' : isError ? 'Error' : 'Success'} | 
                    Monsters: {rawApiData?.monsters?.length || 0} | 
                    Total: {rawApiData?.total || 'unknown'} | 
                    Page: {fullPagination.currentPage} | 
                    Limit: {limit}
                </p>
                
                <p>
                    Filter: 
                    <select value={filter} onChange={(e) => setFilter(e.target.value)}>
                        <option value="all">All</option>
                        <option value="with_art">With Art</option>
                        <option value="without_art">Without Art</option>
                    </select>
                </p>
                
                {error && <p>Error: {error.message}</p>}
            </div>

            {/* Monster List */}
            <div>
                <h2>Monster List</h2>
                {isLoading ? (
                    <p>Loading monsters...</p>
                ) : rawApiData?.monsters?.length > 0 ? (
                    <div>
                        {rawApiData.monsters.map((monster, index) => (
                            <div key={monster.id || index}>
                                {monster.name} - {monster.species}
                                {monster.card_art && ' 🎨'}
                            </div>
                        ))}
                    </div>
                ) : (
                    <p>No monsters found</p>
                )}
            </div>

            <hr/>

            {/* Test 1: Full-Featured Component - Default Layout */}
            <div>
                <h2>Test 1: Full-Featured Component (Default Layout)</h2>
                <p>Everything in one component with default vertical layout</p>
                
                <FullPagination
                    pagination={fullPagination}
                    itemName="monsters"
                    showInfo={true}
                    showJumper={true}
                    showItemsPerPage={true}
                    itemsPerPageOptions={[3, 5, 10, 20]}
                    currentLimit={limit}
                    onLimitChange={handleLimitChange}
                    layout={PAGINATION_LAYOUTS.DEFAULT}
                />
            </div>

            <hr/>

            {/* Test 2: Full-Featured Component - Compact Layout */}
            <div>
                <h2>Test 2: Full-Featured Component (Compact Layout)</h2>
                <p>Everything in one horizontal row</p>
                
                <FullPagination
                    pagination={fullPagination}
                    itemName="monsters"
                    showInfo={true}
                    showJumper={true}
                    showItemsPerPage={false}
                    layout={PAGINATION_LAYOUTS.COMPACT}
                />
            </div>

            <hr/>

            {/* Test 3: Full-Featured Component - Spread Layout */}
            <div>
                <h2>Test 3: Full-Featured Component (Spread Layout)</h2>
                <p>Info left, pagination center, jumper right</p>
                
                <FullPagination
                    pagination={fullPagination}
                    itemName="monsters"
                    showInfo={true}
                    showJumper={true}
                    showItemsPerPage={false}
                    layout={PAGINATION_LAYOUTS.SPREAD}
                />
            </div>

            <hr/>

            {/* Test 4: Individual Primitives */}
            <div>
                <h2>Test 4: Individual UI Primitives</h2>
                <p>Using each primitive component separately</p>
                
                <h3>Pagination Info Only:</h3>
                <PaginationInfo pagination={fullPagination} itemName="monsters" />
                
                <h3>Main Pagination Only:</h3>
                <PaginationPrimitive 
                    pagination={fullPagination} 
                    showFirstLast={true} 
                    showPrevNext={true} 
                />
                
                <h3>Page Jumper Only:</h3>
                <PageJumper pagination={fullPagination} />
                
                <h3>Items Per Page Selector Only:</h3>
                <ItemsPerPageSelector
                    value={limit}
                    onChange={handleLimitChange}
                    options={[3, 5, 10, 20]}
                    itemName="monsters"
                />
            </div>

            <hr/>

            {/* Test 5: Minimal Configurations */}
            <div>
                <h2>Test 5: Minimal Configurations</h2>
                
                <h3>Just Page Numbers (No First/Last):</h3>
                <PaginationPrimitive 
                    pagination={fullPagination} 
                    showFirstLast={false} 
                    showPrevNext={true} 
                />
                
                <h3>Just Prev/Next (No Page Numbers):</h3>
                <div>
                    <button 
                        onClick={fullPagination.prevPage} 
                        disabled={!fullPagination.hasPrev}
                    >
                        Previous
                    </button>
                    <span> Page {fullPagination.currentPage} </span>
                    <button 
                        onClick={fullPagination.nextPage} 
                        disabled={!fullPagination.hasNext}
                    >
                        Next
                    </button>
                </div>
                
                <h3>Info Only (No Navigation):</h3>
                <PaginationInfo pagination={fullPagination} itemName="monsters" />
            </div>

            <hr/>

            {/* Test 6: Simple Pagination Hook */}
            <div>
                <h2>Test 6: Simple Pagination Hook (No Total)</h2>
                <p>For infinite scroll or when total is unknown</p>
                
                <p>Simple Page: {simplePagination.currentPage}</p>
                
                <button onClick={simplePagination.prevPage}>Prev</button>
                <span> Page {simplePagination.currentPage} </span>
                <button onClick={simplePagination.nextPage}>Next</button>
                <button onClick={simplePagination.reset}>Reset</button>
                
                <p>Note: Simple pagination has no total, so no "last page" concept</p>
            </div>

            <hr/>

            {/* Test 7: Custom Manual Controls */}
            <div>
                <h2>Test 7: Manual Pagination Controls</h2>
                <p>Direct access to pagination actions</p>
                
                <div>
                    <button onClick={fullPagination.firstPage}>First</button>
                    <button onClick={fullPagination.prevPage}>Prev</button>
                    <button onClick={() => fullPagination.goToPage(5)}>Go to 5</button>
                    <button onClick={() => fullPagination.goToPage(10)}>Go to 10</button>
                    <button onClick={fullPagination.nextPage}>Next</button>
                    <button onClick={fullPagination.lastPage}>Last</button>
                    <button onClick={fullPagination.reset}>Reset</button>
                </div>
            </div>

            <hr/>

            {/* Debug Information */}
            <div>
                <h2>Debug Information</h2>
                
                <details>
                    <summary>Full Pagination State</summary>
                    <pre>{JSON.stringify({
                        currentPage: fullPagination.currentPage,
                        currentOffset: fullPagination.currentOffset,
                        totalPages: fullPagination.totalPages,
                        total: fullPagination.total,
                        limit: fullPagination.limit,
                        hasNext: fullPagination.hasNext,
                        hasPrev: fullPagination.hasPrev,
                        isFirstPage: fullPagination.isFirstPage,
                        isLastPage: fullPagination.isLastPage
                    }, null, 2)}</pre>
                </details>
                
                <details>
                    <summary>Page Range Array</summary>
                    <pre>{JSON.stringify(fullPagination.paginationInfo?.pageRange, null, 2)}</pre>
                </details>
                
                <details>
                    <summary>Complete Pagination Info</summary>
                    <pre>{JSON.stringify(fullPagination.paginationInfo, null, 2)}</pre>
                </details>
                
                <details>
                    <summary>Raw API Response</summary>
                    <pre>{JSON.stringify(rawApiData, null, 2)}</pre>
                </details>
            </div>

            <hr/>

            {/* Usage Examples */}
            <div>
                <h2>What You Can Do With This System</h2>
                <ul>
                    <li>✅ <strong>Full-featured pagination</strong> - One component does everything</li>
                    <li>✅ <strong>Custom layouts</strong> - Default, compact, spread arrangements</li>
                    <li>✅ <strong>Individual primitives</strong> - Use just what you need</li>
                    <li>✅ <strong>Manual controls</strong> - Direct access to all pagination actions</li>
                    <li>✅ <strong>Items per page</strong> - Dynamic limit changing</li>
                    <li>✅ <strong>Page jumping</strong> - Type page number to navigate</li>
                    <li>✅ <strong>Smart page ranges</strong> - Ellipsis for large page counts</li>
                    <li>✅ <strong>Simple pagination</strong> - For unknown totals</li>
                    <li>✅ <strong>Pure utilities</strong> - Use pagination math anywhere</li>
                    <li>✅ <strong>Clean separation</strong> - UI, state, and logic separated</li>
                </ul>
            </div>
        </div>
    );
}

export default MyCurrentTestScreen;