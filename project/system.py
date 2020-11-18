from system_testing.generate_documentation import DocGen
from system_testing.generate_tests import TestsGen


def main():
    DocGen.generate_documentation()
    TestsGen.generate_documentation()


if __name__ == "__main__":
    main()
