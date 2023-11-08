# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import random
import time

while True:
    try:
        n = random.randint(0, 0x100000)
        r = [1, random.randint(1,5)][random.randint(0, 100) > 90]
        print(chr(n)*r, end='', flush=True)
        # if n < 0x80:
        #     break
    except:
        print(random.randbytes(6), end='', flush=True)
    time.sleep(0.3)
