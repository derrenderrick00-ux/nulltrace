"""Entry point; --strict retains Phase 0 diagnostic compatibility."""
from __future__ import annotations
import argparse

def main() -> int:
    parser=argparse.ArgumentParser(description='NULLTRACE v1.5 educational thriller and offline investigation candidate')
    parser.add_argument('--doctor','--strict',dest='doctor',action='store_true',help='Run environment diagnostic (Phase 0 compatible)')
    parser.add_argument('--qa',action='store_true',help='Launch developer QA mode with all 100 missions accessible; does not save mission progress')
    parser.add_argument('--list-missions',action='store_true',help='Print 100 mission identifiers and phase status')
    parser.add_argument('--lab',choices=['packet','nmap','john','web','incident'],help='Explicitly run a controlled lab and print its report')
    parser.add_argument('--headless-smoke',action='store_true',help='Run bounded Pygame smoke test (needs SDL_VIDEODRIVER=dummy on servers)')
    parser.add_argument('--export-dossier',metavar='PATH',help='Export current player synthetic case report as Markdown')
    parser.add_argument('--web-lab',action='store_true',help='Start the deliberate localhost HTTP training server for Burp Repeater (Ctrl+C stops)')
    args=parser.parse_args()
    if args.web_lab:
        from nulltrace.labs.web_training import serve_cli
        return serve_cli()
    if args.export_dossier:
        from nulltrace.persistence.store import Store
        from nulltrace.investigations.report import export_dossier
        from pathlib import Path
        store=Store()
        try:
            players=store.players()
            if not players:
                print('Create an operator profile before exporting a dossier.')
                return 2
            output=export_dossier(store,players[0]['id'],Path(args.export_dossier))
            print('Synthetic training dossier exported to:',output)
            return 0
        finally:store.close()
    if args.doctor:
        from nulltrace.doctor import main as doctor
        return doctor(["--strict"])
    if args.list_missions:
        from nulltrace.core.content import Curriculum
        for m in Curriculum().missions.values():
            print(m.id, 'PLAYABLE' if m.assessment else 'NOT IMPLEMENTED',m.title)
        return 0
    if args.lab:
        from nulltrace.labs.practical import run_lab
        result=run_lab(args.lab)
        print(f'{result.title}: {result.mode} ({"pass" if result.success else "failed"})')
        for line in result.details:print(' -',line)
        return 0 if result.success else 1
    if args.headless_smoke:
        from nulltrace.ui.app import smoke_test
        return smoke_test()
    from nulltrace.ui.app import run_game
    return run_game(qa=args.qa)
