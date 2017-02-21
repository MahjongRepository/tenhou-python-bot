# -*- coding: utf-8 -*-
from analytics.logs_compressor import TenhouLogCompressor


def main():
    compressor = TenhouLogCompressor()
    compressor.compress('samples/test.log')

if __name__ == '__main__':
    main()
