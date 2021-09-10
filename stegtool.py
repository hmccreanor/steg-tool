import argparse
import os
import sys

from PIL import Image


EIGHT_BIT_MASK = 0b11111111

parser = argparse.ArgumentParser()
parser.add_argument("payloadfile", help = "filename of payload")
parser.add_argument("transportfile", help = "filename of transport image")
parser.add_argument("-b", "--bits", help = "number of least significant bits to use", type = int, default = 1, choices = [1, 2, 4])
args = parser.parse_args()

img = Image.open(args.transportfile)
if img.mode != "RGB":
    sys.exit("Error: Transport image is not RGB")

lsb_bitmask = EIGHT_BIT_MASK << args.bits # Clears least significant bits before new ones can be written in with bitwise or

_, payload_extension = os.path.splitext(args.payloadfile)

if payload_extension == ".txt":
    with open(args.payloadfile) as f:
        data = []
        for c in bytearray(f.read(), "utf-8"):
            for i in range(8 - args.bits, -1 * args.bits , -1 * args.bits):
                data.append((c >> i) & 0b11) # Get data in lsb_chunks
    
    l = len(data)

    if len(data) / 2 > img.size[0] * img.size[1] * 3:
        sys.exit("Error: Payload too large for transport image")

    ix = 0 # Payload data index

    pixels = img.load()

    for i in range(img.size[0]):
        if ix < l:
            for j in range(img.size[1]):
                if ix < l:
                    t = pixels[i,j]
                    pixels[i, j] = (
                        (t[0] & lsb_bitmask) | data[ix    ],
                        (t[1] & lsb_bitmask) | data[ix + 1],
                        (t[2] & lsb_bitmask) | data[ix + 2],
                    )
                    
        
    img.save("modified_" + args.transportfile, format="png")

elif payload_extension in [".png", ".jpeg", ".jpg"]:
    print("Processing image file")
