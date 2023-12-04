from os import environ
#from dotenv import load_dotenv
import ifaddr

# Only needed for developing, on production Docker .env file is used
#load_dotenv()


class Config:
    """Set configuration vars from .env file."""
    CONSUL_HOST = "192.168.17.91"
    CONSUL_PORT = 8500
    CONSUL_DNS_PORT = 8600
    PORT = int('443')
    SERVICE_NAME = "delivery"
    SERVICE_ID = "deliveryr0"
    IP = None

    __instance = None

    @staticmethod
    def get_instance():
        if Config.__instance is None:
            Config()
        return Config.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Config.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.get_ip()
            Config.__instance = self

    def get_ip(self):
        ip = Config.get_adapter_ip("eth0")  # this is the default interface in docker
        if ip is None:
            ip = "127.0.0.1"
        self.IP = ip

    @staticmethod
    def get_adapter_ip(nice_name):
        adapters = ifaddr.get_adapters()

        for adapter in adapters:
            if adapter.nice_name == nice_name and len(adapter.ips) > 0:
                return adapter.ips[0].ip

        return None