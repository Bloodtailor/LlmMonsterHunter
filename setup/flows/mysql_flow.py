#!/usr/bin/env python3
"""
MySQL Interactive Setup Flow
The one component a new player cannot skip and cannot fully automate:
MySQL ships as a third-party installer wizard. The flow's job is to fix
everything it can WITHOUT asking (a stopped service is the most common
failure and needs zero user effort), and when the wizard truly is
needed, to shrink it to the few answers that matter and then wait and
verify right here - no "re-run the launcher and hope".
"""

COMPONENT_NAME = "MySQL"

MYSQL_DOWNLOAD_URL = "https://dev.mysql.com/downloads/mysql/"

from setup.checks.mysql_checks import (
    check_mysql_server,
    get_mysql_installations_list,
    get_mysql_service_name,
)
from setup.installation.mysql_installation import start_mysql_service
from setup.utils.ux_utils import *


def run_mysql_interactive_setup(current=None, total=None, dry_run=False):
    """
    Interactive setup flow for the MySQL server.

    Returns:
        bool: True if MySQL is up and reachable when we're done.
    """

    show_component_header(
        component_name="MySQL Server",
        current=current,
        total=total,
        description="The game stores your monsters and progress in a MySQL database",
    )

    print("Checking whether MySQL is running...")
    server_ok, server_message = check_mysql_server()

    # Dry run mode - simulate the initial check instead of probing
    if dry_run:
        print_dry_run_header()

        from setup.utils.dry_run_utils import set_dry_run

        server_ok, server_message = set_dry_run('check_mysql_server')

    if server_ok:
        print_success(server_message)
        return True

    print(server_message)
    print()

    # Fix it ourselves when we can: MySQL installed but not running is
    # the most common failure, and starting the service needs nothing
    # from the user
    if not dry_run and get_mysql_service_name():
        print("MySQL is installed on this computer - it just isn't running.")
        print("Starting it for you...")
        print()

        success, message = start_mysql_service()
        if success:
            print_success(message)
            return verify_mysql_setup(dry_run)

        print(message)
        print()
        return handle_service_wont_start(dry_run)

    # Installed somewhere but no service registered: genuinely unusual,
    # hand over the troubleshooting guide rather than the install card
    if not dry_run and get_mysql_installations_list():
        print("MySQL files were found on this computer, but the server isn't")
        print("set up as a Windows service, so the game can't start it.")
        print()
        show_message_and_wait('mysql_troubleshooting', "Press Enter after fixing MySQL... ")
        return verify_mysql_setup(dry_run)

    # Nothing found: the guided fresh install
    return handle_fresh_install(dry_run)


def handle_fresh_install(dry_run=False):
    """Walk a first-timer through the MySQL installer, then wait and verify."""

    print("MySQL isn't installed yet. It's free, and this is the one step of")
    print("the whole setup that uses an installer wizard - here's exactly")
    print("what to do.")
    print()

    if dry_run:
        print_dry_run(f"(dry run: would open {MYSQL_DOWNLOAD_URL} in the browser)")
    else:
        import webbrowser

        webbrowser.open(MYSQL_DOWNLOAD_URL)

    show_message('mysql_installation')

    # Wait right here and verify, instead of ending the walkthrough and
    # hoping the player re-runs the launcher
    while True:
        input("Press Enter when the installer says it's finished... ")
        print()
        print("Checking...")

        if verify_mysql_setup(dry_run):
            return True

        print("MySQL doesn't seem to be running yet. That's usually one of:")
        print("  - the installer is still working (give it another minute)")
        print("  - the final 'Configurator' step hasn't been run yet - it's a")
        print("    separate wizard that appears near the end of the install")
        print()
        if not prompt_user_confirmation("Check again? (N shows more help) [Y/n]: "):
            show_message_and_wait('mysql_troubleshooting', "Press Enter after fixing MySQL... ")
            return verify_mysql_setup(dry_run)


def handle_service_wont_start(dry_run=False):
    """The service exists but refused to start automatically."""

    print("The MySQL service exists but didn't start automatically.")
    print("Starting it by hand usually works:")
    print()
    show_message_and_wait('mysql_service_start', "Press Enter after starting MySQL... ")
    return verify_mysql_setup(dry_run)


def verify_mysql_setup(dry_run=False):
    """Final verification that the MySQL server is reachable."""

    # The MSI's configurator usually starts the service itself; cover
    # the case where it didn't before declaring failure
    server_ok, _ = (False, None) if dry_run else check_mysql_server()
    if not dry_run and not server_ok and get_mysql_service_name():
        start_mysql_service()

    if dry_run:
        from setup.utils.dry_run_utils import set_dry_run

        server_ok, server_message = set_dry_run('check_mysql_server')
    else:
        server_ok, server_message = check_mysql_server()

    if server_ok:
        print_success(f"{server_message} - MySQL is ready!")
        print()
        return True

    print_warning(server_message)
    print_info("MySQL setup isn't finished - the walkthrough can be re-run anytime.")
    print()
    return False


if __name__ == "__main__":
    from setup.utils.dry_run_utils import run_as_standalone_component

    run_as_standalone_component(COMPONENT_NAME, run_mysql_interactive_setup)
