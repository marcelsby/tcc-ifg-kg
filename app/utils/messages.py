from colorama import Fore


def print_error(msg: str):
    print(Fore.RED + msg + Fore.RESET)


def print_success(msg: str):
    print(Fore.GREEN + msg + Fore.RESET)
