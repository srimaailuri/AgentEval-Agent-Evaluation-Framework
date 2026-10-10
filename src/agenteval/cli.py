from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agenteval.datasets.loader import load_dataset
from agenteval.evaluation.reports import write_json_report
from agenteval.evaluation.runner import run_evaluation


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="agenteval", description="AgentEval CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run evaluation from dataset + trace JSON files")
    run_p.add_argument("--dataset", required=True, type=Path)
    run_p.add_argument(
        "--traces",
        required=True,
        type=Path,
        help="JSON map of case_id -> raw trace, or list of {case_id, raw_trace}",
    )
    run_p.add_argument("--output", type=Path, default=Path(".agenteval/last_run.json"))

    sub.add_parser("version", help="Print version")

    args = parser.parse_args(argv)
    if args.command == "version":
        from agenteval import __version__

        print(__version__)
        return

    if args.command == "run":
        dataset = load_dataset(args.dataset)
        traces_raw = json.loads(args.traces.read_text(encoding="utf-8"))
        traces_by_case: dict = {}
        if isinstance(traces_raw, dict):
            traces_by_case = traces_raw
        elif isinstance(traces_raw, list):
            for item in traces_raw:
                if isinstance(item, dict) and item.get("case_id"):
                    traces_by_case[str(item["case_id"])] = item.get("raw_trace") or item.get("trace")
        else:
            print("Invalid traces file format", file=sys.stderr)
            sys.exit(1)
        run = run_evaluation(dataset, traces_by_case)
        write_json_report(run, args.output)
        print(json.dumps({"evaluation_run_id": run.evaluation_run_id, "output": str(args.output)}))


if __name__ == "__main__":
    main()
