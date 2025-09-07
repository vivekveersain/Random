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
        self.last_read = 0
        self.last_written = 0
        self.last_time = time.time()
        
    def auth(self):
        self.cont = Controller.from_port()
        self.cont.authenticate(self.passkey)
    
    def printer(self, info):
        print(" "*self.printed, end="\r")
        print(info, end="\r")
        self.printed = len(info)
    
    def get_bandwidth(self):
        try:
            read_bytes = int(self.cont.get_info("traffic/read"))
            written_bytes = int(self.cont.get_info("traffic/written"))
            now = time.time()
            
            if self.last_time:  # calculate difference since last call
                elapsed = now - self.last_time
                down_speed = (read_bytes - self.last_read) / elapsed
                up_speed = (written_bytes - self.last_written) / elapsed
            else:
                down_speed, up_speed = 0, 0

            self.last_read = read_bytes
            self.last_written = written_bytes
            self.last_time = now

            return down_speed, up_speed
        except Exception:
            return 0, 0
    
    def check(self):
        try: 
            self.auth()
        except: 
            pass

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
                        used_circuit += (
                            str(circ["id"]) + ">>" +
                            "> ".join(set(circ["targets"])) + "@" +
                            "> ".join(circ["path"]) + " || "
                        )

                # bandwidth info
                down_speed, up_speed = self.get_bandwidth()
                info = (
                    f"Total circuits: {len(all_circs)} | {used_circuit}"
                    f"D: {down_speed/1024:.2f} KB/s | "
                    f"U: {up_speed/1024:.2f} KB/s"
                )

                if info != last_info: 
                    self.printer(info)
                last_info = info

            except KeyboardInterrupt:
                self.printer("Exiting...")
                return
            except:
                info = "waiting for circuit to come online..."
                self.printer(info)
                last_info = info
                time.sleep(4)
                try: 
                    self.auth()
                except: 
                    pass

            try: 
                time.sleep(1)
            except KeyboardInterrupt:
                self.printer("Exiting...")
                return

deep = Deep()
deep.check()
