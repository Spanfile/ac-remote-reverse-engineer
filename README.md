# Reverse engineering the YK-H/531E AC remote control IR protocol

This repository contains Python scripts that I used to reverse engineer the YK-H/531E air conditioner remote control IR protocol, and to encode my own messages for the protocol that can be sent out from an IR blaster.

[More information in my blog post.](https://blog.spans.fi/2024/04/16/reverse-engineering-the-yk-h531e-ac-remote-control-ir-protocol.html)

## Examples

Capture a stream of IR messages from a Zigbee2MQTT-connected IR blaster:

```sh
python ir_receive.py --broker your.mqtt.broker --topic "zigbee2mqtt/IR blaster" --username username --password password > captured_messages.txt
```

Decode captured messages:

```sh
python ir_decode.py captured_messages.txt
```

Encode a control message:

```sh
python ir_encode.py --on --temp 20 --mode cool --fan mid --swing --button onoff
```
