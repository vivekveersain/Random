from stem.control import Controller
import time

class Deep:
    def __init__(self):
        prompt = "Enter the secret: "
        passkey = input(prompt)
        printed = len(prompt) + len(passkey)
        print("\033[A%s\033[A" % (" "*printed))
        self.passkey = passkey
        self.printed = 0
        self.cont = None
        
    def auth(self):
        self.cont = Controller.from_port()
        self.cont.authenticate(self.passkey)
    
    def printer(self, info):
        print(" "*self.printed, end = "\r")
        print(info, end = "\r")
        self.printed = len(info)
    
    def check(self):
        try: self.auth()
        except: pass
        last_info = ""
        while True:
            try:
                all_circs = []
                all_streams = self.cont.get_streams()
                for circ in self.cont.get_circuits():
                        path = [nick for fp, nick in circ.path]
                        streams = [s for s in all_streams if s.circ_id == circ.id]
                        all_circs.append({
                            'id': int(circ.id),
                            'path': path,
                            'used': True if len(streams) else False,
                            'targets': [s.target for s in streams],
                        })

                all_circs = sorted(all_circs, key=lambda c: c['id'])
                used_circuit = ""
                for circ in all_circs:
                    if circ["used"]:
                        used_circuit += str(circ["id"]) + " >> " + "> ".join(set(circ["targets"])) + " " + "> ".join(circ["path"]) + " || "
                info = "Total circuits: %d | %s" % (len(all_circs), used_circuit)
                if info!= last_info: self.printer(info)
                last_info = info
            except KeyboardInterrupt:
                self.printer("Exiting...")
                return
            except:
                info = "waiting for circuit to come online..."
                self.printer(info)
                last_info = info
                time.sleep(4)
                #if not self.cont.is_authenticated(): pass
                try: self.auth()
                except: pass
            try: time.sleep(1)
            except KeyboardInterrupt:
                self.printer("Exiting...")
                return

deep = Deep()
deep.check()