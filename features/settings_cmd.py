# features/settings_cmd.py
from typing import Tuple


def _parse_on_off(val: str) -> Tuple[bool, bool]:
    v = val.strip().lower()
    if v in ("on", "true", "1", "yes"):
        return True, True
    if v in ("off", "false", "0", "no"):
        return True, False
    return False, False


def make_handlers(brain):
    def set_handle(state, console, args):
        """
        /set <key> <value>
        Keys:
          - model <id>              (örn: llama3.2:3b)
          - temp <float>            (örn: 0.6)
          - memory on|off
          - web on|off
          - stream on|off
        """
        if len(args) < 2:
            console.print_sys("Kullanım: /set <model|temp|memory|web|stream> <değer>")
            return

        key, val = args[0].lower(), " ".join(args[1:]).strip()
        updated = False

        if key == "model":
            state.config["model"] = val
            updated = True

        elif key in ("temp", "temperature"):
            try:
                state.config["temperature"] = float(val)
                updated = True
            except ValueError:
                console.print_sys("Hata: temp sayısal olmalı, örn: 0.6")
                return

        elif key == "memory":
            ok, b = _parse_on_off(val)
            if ok:
                state.config["use_memory"] = b
                updated = True
            else:
                console.print_sys("Hata: memory on|off")
                return

        elif key == "web":
            ok, b = _parse_on_off(val)
            if ok:
                state.config["use_web"] = b
                updated = True
            else:
                console.print_sys("Hata: web on|off")
                return

        elif key == "stream":
            ok, b = _parse_on_off(val)
            if ok:
                state.config["stream"] = b
                updated = True
            else:
                console.print_sys("Hata: stream on|off")
                return
        else:
            console.print_sys(f"Bilinmeyen ayar: {key}")
            return

        if updated:
            brain.rebuild(state)
            console.print_sys(f"Güncellendi: {key} = {state.config.get(key, val)}")

    def show_config_handle(state, console, args):
        cfg = state.config
        console.print_sys("Ayarlar:")
        console.print_sys(f"  model       : {cfg['model']}")
        console.print_sys(f"  temperature : {cfg['temperature']}")
        console.print_sys(f"  use_memory  : {cfg['use_memory']}")
        console.print_sys(f"  use_web     : {cfg['use_web']}")
        console.print_sys(f"  stream      : {cfg['stream']}")

    return set_handle, show_config_handle
