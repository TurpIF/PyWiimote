import bluetooth

def Discover():
  devices = bluetooth.discover_devices(lookup_names=True)
  return [addr for (addr, name) in devices
      if name == 'Nintendo RVL-CNT-01' or name == 'Nintendo RVL-CNT-01-TR']

# vim: et sw=2 sts=2
