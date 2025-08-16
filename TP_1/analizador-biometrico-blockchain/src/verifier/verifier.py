import time


def run(freq_q, oxy_q, pres_q):
    """
    Verificador: consume resultados de las tres queues
    e imprime por pantalla. Termina cuando recibe los tres sentinels END.
    """
    print("Iniciando verifier...", flush=True)
    ends_needed = 3
    ends_received = 0

    buffer = {}

    try:
        while ends_received < ends_needed:
            # leer de las tres colas de forma intercalada no bloqueante estricta:
            # usare get() bloqueante con timeout pequeño para poder chequear las 3
            got = False
            try:
                res = freq_q.get(timeout=0.5)
                got = True
                if isinstance(res, dict) and res.get("tipo") == "END":
                    ends_received += 1
                else:
                    print(f"[Verifier] freq: {res}", flush=True)
            except Exception:
                pass

            try:
                res = oxy_q.get(timeout=0.5)
                got = True
                if isinstance(res, dict) and res.get("tipo") == "END":
                    ends_received += 1
                else:
                    print(f"[Verifier] oxy: {res}", flush=True)
            except Exception:
                pass

            try:
                res = pres_q.get(timeout=0.5)
                got = True
                if isinstance(res, dict) and res.get("tipo") == "END":
                    ends_received += 1
                else:
                    print(f"[Verifier] pres: {res}", flush=True)
            except Exception:
                pass

            if not got:
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("Verifier interrumpido por usuario", flush=True)
    except Exception as e:
        print(f"Verifier error: {e}", flush=True)

    print("Verifier terminó.", flush=True)