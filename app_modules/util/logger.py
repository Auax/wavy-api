from typing import Any
import colorama

colorama.init(autoreset=True)


def log(identifier: Any, v: Any, mode: int = 1) -> None:
    """
    Simple function to improve text printing
    :param v: text to print
    :param mode: (1=Success)(2=Warning)(3=Error)
    :return: None
    """
    if mode == 1:
        print(f"[{colorama.Fore.GREEN}{identifier}{colorama.Fore.RESET}] {v}")

    elif mode == 2:
        print(f"[{colorama.Fore.YELLOW}{identifier}{colorama.Fore.RESET}] {v}")

    elif mode == 3:
        print(f"[{colorama.Fore.RED}{identifier}{colorama.Fore.RESET}] {v}")
