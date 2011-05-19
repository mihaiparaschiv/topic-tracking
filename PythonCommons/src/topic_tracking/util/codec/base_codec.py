class BaseCodec(object):

    def _get_data(self, model):
        specs = model.thrift_spec[1:]
        fields = [spec[2] for spec in specs]
        data = {}
        for name in fields:
            data[name] = getattr(model, name)
        return data
