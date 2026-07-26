# colors
BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
PURPLE = 5
CYAN = 6
WHITE = 7

# color effect
STANDARD_FOREGROUND = '3'
BRIGHT_FOREGROUND = '9'
STANDARD_BACKGROUND = '4'
BRIGHT_BACKGROUND = '10'

def color(text, foreground_color: int, background_color: int = None, foreground_bright: bool = True, background_bright: bool = True) -> str:
    """Surrounds a string with ANSI escape color code.
    Parameters:
        text: Text to be surrounded by ANSI escape codes.
        foreground_color (int): Color number of foreground to be used in ANSI escape code.
        background_color (int): Optional. Color number of background to be used in ANSI escape code. Omitting means background color will be unaffected.
        foreground_bright (bool): Optional (defaults to True). True prints brighter foreground color.
        background_bright (bool): Optional (defaults to True). True prints brighter background color. Only applicable if background_color is provided.
    Returns:
        str: Text surrounded by ANSI color escape codes.
    """
    # if text is not a str, convert it to one
    if not isinstance(text, str):
        text = str(text)

    # construct the ANSI escape code; start with foreground
    ansi_code = f"\033[{BRIGHT_FOREGROUND if foreground_bright else STANDARD_FOREGROUND}{foreground_color}" # foreground

    # if background_color was provided, add that to the code
    if background_color is not None:
        ansi_code += f";{BRIGHT_BACKGROUND if background_bright else STANDARD_BACKGROUND}{background_color}"

    # add the final 'm' to the code
    ansi_code += 'm'

    # surround text with ANSI color codes and return
    return ansi_code + text + '\033[0m'

def red(text) -> str:
    """Surrounds a string with ANSI escape color code.
    Parameters:
        text: Text to be surrounded by ANSI escape codes.
    Returns:
        str: Text surrounded by ANSI color escape codes.
    """
    # if text is not a str, convert it to one
    if not isinstance(text, str):
        text = str(text)

    # surround text with ANSI color codes and return
    return '\033[91m' + text + '\033[0m'

def green(text) -> str:
    """Surrounds a string with ANSI escape color code.
    Parameters:
        text: Text to be surrounded by ANSI escape codes.
    Returns:
        str: Text surrounded by ANSI color escape codes.
    """
    # if text is not a str, convert it to one
    if not isinstance(text, str):
        text = str(text)

    # surround text with ANSI color codes and return
    return '\033[92m' + text + '\033[0m'

def yellow(text) -> str:
    """Surrounds a string with ANSI escape color code.
    Parameters:
        text: Text to be surrounded by ANSI escape codes.
    Returns:
        str: Text surrounded by ANSI color escape codes.
    """
    # if text is not a str, convert it to one
    if not isinstance(text, str):
        text = str(text)

    # surround text with ANSI color codes and return
    return '\033[93m' + text + '\033[0m'

def blue(text) -> str:
    """Surrounds a string with ANSI escape color code.
    Parameters:
        text: Text to be surrounded by ANSI escape codes.
    Returns:
        str: Text surrounded by ANSI color escape codes.
    """
    # if text is not a str, convert it to one
    if not isinstance(text, str):
        text = str(text)

    # surround text with ANSI color codes and return
    return '\033[94m' + text + '\033[0m'

def rainbow(text) -> str:
    """Surrounds a string with ANSI escape color code.
    Parameters:
        text: Text to be surrounded by ANSI escape codes.
    Returns:
        str: Text surrounded by ANSI color escape codes.
    """
    roygbiv = ('1', '3', '2', '6', '4', '5')
    color_index = 0 # start at first index
    result = "" # begin with empty string

    # if text is not a str, convert it to one
    if not isinstance(text, str):
        text = str(text)

    # iterate through letters
    for letter in text:
        result += f"\033[9{roygbiv[color_index]}m{letter}"
        color_index = (color_index + 1) % len(roygbiv)

    # return final result
    result += '\033[0m'
    return result

def color_test() -> None:
    """Print basic ANSI color code examples."""
    print(rainbow("\nPrinting color test..."))
    prefixes = ('3', '4', '9', '10')
    for prefix in prefixes:
        for suffix in range(8):
            color_code = prefix + str(suffix)
            print(f"\033[{color_code}m{color_code}", end='\t')
        print('\033[0m')
    print()

def color_test_2() -> None:
    """Tests out the more versatile 'color' function in this module."""
    for i in range(8):
        print(f"{color("XO", i)}\t{color("XO", i, 7 - i)}\t{color("XO", 7 - i, i)}")

if __name__ == "__main__":
    color_test()
    color_test_2()