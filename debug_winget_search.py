import subprocess
import importlib
import core.search

def run_shell_search(q):
    proc = subprocess.run(["winget","search",q,"--accept-source-agreements"], capture_output=True, text=True)
    print("=== subprocess.run returncode ===")
    print(proc.returncode)
    print("=== repr(stdout) ===")
    print(repr(proc.stdout))
    print("=== repr(stderr) ===")
    print(repr(proc.stderr))
    print("=== raw stdout below ===")
    print(proc.stdout)
    print("=== raw stderr below ===")
    print(proc.stderr)

if __name__ == "__main__":
    query = "steam"
    print(">>> Running raw winget search for:", query)
    run_shell_search(query)
    print("\n>>> Calling core.search.search_first_package_id")
    try:
        ok, res = core.search.search_first_package_id(query)
        print("RESULT from core.search.search_first_package_id ->", ok, res)
    except Exception as e:
        print("EXCEPTION from core.search:", repr(e))