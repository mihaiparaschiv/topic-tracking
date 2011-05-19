class ThriftClientWrapper(object):

    def __init__(self, client):
        self._client = client

    def connect(self):
        input = self._client._iprot.trans
        output = self._client._oprot.trans
        input.open()
        if input is not output:
            output.open()

    def disconnect(self):
        input = self._client._iprot.trans
        output = self._client._oprot.trans
        input.close()
        if input is not output:
            output.close()

    def is_connected(self):
        # TODO: output should be tested too
        return self._client._iprot.trans.isOpen()

    def __getattr__(self, name):
        return getattr(self._client, name)
