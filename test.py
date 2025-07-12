# Import the orchestration functions
from setup.checks import run_all_checks, check_component

# Option 1: Check everything at once
results = run_all_checks()
print(results)
# Output: {'Node.js & npm': True, 'MySQL Server': False}

# Use the results
ready_components = sum(results.values())  # Count True values
total_components = len(results)
print(f"Ready: {ready_components}/{total_components}")

# Option 2: Check specific component
mysql_status = check_component('MySQL Server')
if mysql_status:
    print("MySQL is ready!")
else:
    print("MySQL needs setup")

# Option 3: Check component that doesn't exist
unknown_status = check_component('Redis')  # Returns False (default)