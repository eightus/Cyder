
try:
    from probe.fingerprint import OSFingerprint
except ModuleNotFoundError:
    from Cloaked.probe.fingerprint import OSFingerprint


class Configuration:
    def __init__(self):
        self.fgrpt = None
        self.debug = False
        self.service = dict()

    def set_fgrpt(self, fgrpt_):
        self.fgrpt = fgrpt_

    def set_debug(self, debug_):
        self.debug = debug_

    def set_service(self, service_):
        self.service = service_

    def save_cfg(self):
        self.fgrpt = OSFingerprint(self.fgrpt, self.debug)
