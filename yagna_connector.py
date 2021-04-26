from time import sleep
from tempfile import NamedTemporaryFile
from serializable_request import Request, Response


class YagnaConnector():
    def __init__(self):
        self._init_provider()

    def process_request(self, req: Request):
        with NamedTemporaryFile() as in_file, NamedTemporaryFile() as out_file:
            req.to_file(in_file.name)
            self.run_request(in_file.name, out_file.name)
            res = Response.from_file(out_file.name)
        return res

    def run_request(self, fname):
        raise NotImplementedError

    def _init_provider(self):
        print("PROVIDER INITIALIZATION")
        sleep(0.5)
