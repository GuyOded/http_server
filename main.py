import HTTPServer


ROOT = "/home/guy/Work/PyProjects/root"
RESTRICTED = []


def main():
    server = HTTPServer.HTTPServer(ROOT, RESTRICTED)
    server.start_server()


if __name__ == "__main__":
    main()
