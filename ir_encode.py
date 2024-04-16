import tuya
import consts
import argparse
import sys
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--on", action="store_const", const=True, default=True)
    parser.add_argument("--off", action="store_const", const=False, dest="on")
    parser.add_argument("--temp", type=int, default=16)
    parser.add_argument(
        "--celsius", action="store_const", const="C", dest="unit", default="C"
    )
    parser.add_argument("--fahrenheit", action="store_const", const="F", dest="unit")
    parser.add_argument(
        "--mode", type=str.lower, choices=["auto", "cool", "dry", "fan"], default="auto"
    )
    parser.add_argument(
        "--fan", type=str.lower, choices=["auto", "high", "mid", "low"], default="auto"
    )
    parser.add_argument("--swing", action="store_true")
    parser.add_argument("--sleep", action="store_true")
    parser.add_argument(
        "--button",
        type=str.lower,
        choices=[
            "plus",
            "minus",
            "swing",
            "speed",
            "onoff",
            "mode",
            "sleep",
            "unit",
            "timer",
        ],
        default="plus",  # plus corresponds to all zeros for the button
    )

    parser.add_argument("--json", type=str.lower)

    args = parser.parse_args()
    if args.verbose:
        print(args, file=sys.stderr)

    if args.json is None:
        message = encode_message(
            args.on,
            args.temp,
            args.mode,
            args.fan,
            args.swing,
            args.sleep,
            args.button,
            args.unit,
        )
    else:
        params = json.loads(args.json)
        message = encode_message(
            params.get("on", True),
            params.get("temp", 16),
            params.get("mode", "auto"),
            params.get("fan", "auto"),
            params.get("swing", False),
            params.get("sleep", False),
            params.get("button", "plus"),
            params.get("unit", "C"),
        )

    if args.verbose:
        print(
            "    100   96   92   88   84   80   76   72   68   64   60   56   52   48   44   40   36   32   28   24   20   16   12    8    4    0",
            file=sys.stderr,
        )
        print(f"   {message:0>129_b}", file=sys.stderr)

    ir_message = encode_ir_message(message)
    assert len(ir_message) == (consts.MESSAGE_LENGTH_BITS * 2) + 3

    if args.verbose:
        print(ir_message)

    tuya_message = tuya.encode_ir(ir_message)
    print(tuya_message)


def encode_message(on, temp, mode, fan, swing, sleep, button, unit="C"):
    message = consts.PREAMBLE
    message |= (0 if swing else 7) << 8

    # the temp seems to be 0 in "fan" mode
    if mode in ["auto", "cool", "dry"]:
        if unit == "C":
            message |= (temp - 8) << 11
        elif unit == "F":
            message |= (temp + 8) << 81

    if mode == "auto":
        # "auto" allows only fan speed auto as well
        message |= encode_fan("auto") << 37
    elif mode == "cool":
        message |= encode_fan(fan) << 37
    elif mode == "dry":
        # "dry" is always fan speed low
        message |= encode_fan("low") << 37
    elif mode == "fan":
        # "fan" allows only high, mid or low fan speeds, force high if set to auto
        message |= encode_fan("high" if fan == "auto" else fan) << 37

    message |= (0 if unit == "C" else 1) << 49
    message |= (1 if sleep else 0) << 50
    message |= encode_mode(mode) << 53
    message |= (1 if on else 0) << 77
    message |= encode_button(button) << 88
    message |= calc_checksum(message) << 96

    return message


def encode_mode(mode):
    if mode == "auto":
        return 0
    elif mode == "cool":
        return 1
    elif mode == "dry":
        return 2
    elif mode == "dry":
        return 6

    print(f"WARN: Unknown mode: {mode}")
    return 0


def encode_fan(speed):
    if speed == "auto":
        return 5
    elif speed == "high":
        return 1
    elif speed == "mid":
        return 2
    elif speed == "low":
        return 3

    print(f"WARN: Unknown fan speed: {speed}")
    return 5


def encode_button(button):
    if button == "plus":
        return 0
    elif button == "minus":
        return 1
    elif button == "swing":
        return 2
    elif button == "speed":
        return 4
    elif button == "onoff":
        return 5
    elif button == "mode":
        return 6
    elif button == "unit":
        return 7
    elif button == "sleep":
        return 11
    elif button == "timer":
        return 13

    print(f"WARN: Unknown button: {button}")
    return 0


def calc_checksum(message):
    sum = 0
    for _ in range(0, consts.MESSAGE_LENGTH_BITS // 8):
        sum += message & 0xFF
        message >>= 8

    return sum & 0xFF


def encode_ir_message(message):
    ir_message = [consts.INTRO1, consts.INTRO2]

    for _ in range(0, consts.MESSAGE_LENGTH_BITS):
        ir_message.append(consts.SHORT)
        ir_message.append(consts.LONG if message & 1 else consts.SHORT)
        message >>= 1

    # footer
    ir_message.append(consts.SHORT)
    return ir_message


if __name__ == "__main__":
    main()
