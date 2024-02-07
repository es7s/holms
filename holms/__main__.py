# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

from .cli import entrypoint_fn


# bind in pyproject
def main():
    entrypoint_fn()


if __name__ == "__main__":
    main()
