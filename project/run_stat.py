from optparse import OptionParser
from statistics.main import Statistics


def main():
    parser = OptionParser()
    parser.add_option("-p", "--db_path", type="string", help="Path to sqlite database with logs")
    parser.add_option("-l", "--limit", type="int")
    parser.add_option("-o", "--offset", type="int")
    opts, _ = parser.parse_args()

    Statistics(opts.db_path, opts.limit, opts.offset).calculate_statistics()


if __name__ == "__main__":
    main()
