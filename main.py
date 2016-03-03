import HTTPServer


ROOT = "/home/guy/Work/PyProjects/root"


def main():
    server = HTTPServer.HTTPServer(ROOT)
    server.start_server()


if __name__ == "__main__":
    main()
