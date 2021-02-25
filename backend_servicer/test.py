from holoViveCom_pb2 import LighthouseState

t = LighthouseState()
print(t.holoTracker)

if t.holoTracker.isEmpty():
    print("huh")
else:
    print("babab")
