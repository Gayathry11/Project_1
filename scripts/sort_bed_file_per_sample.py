import argparse
import gzip
from pathlib import Path


def open_bed(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt")
    return open(path, "r")


def get_selection_name(selection_file):
    name = Path(selection_file).name

    for suffix in [".gz", ".tsv", ".txt"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]

    if name.endswith("_selection"):
        name = name[: -len("_selection")]

    return name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", required=True)
    parser.add_argument("--selection", required=True)
    parser.add_argument("bed_files", nargs="+")
    args = parser.parse_args()

    chromosome_order = {}
    with open(args.selection, "r") as selection:
        for index, line in enumerate(selection):
            chromosome = line.strip()
            if chromosome:
                chromosome_order[chromosome] = index

    records = []
    for bed_file in args.bed_files:
        with open_bed(bed_file) as bed:
            for line in bed:
                columns = line.split()
                if len(columns) < 3:
                    continue

                chromosome = columns[0]
                if chromosome not in chromosome_order:
                    continue

                start = int(columns[1])
                end = int(columns[2])
                records.append((chromosome_order[chromosome], start, end, line))

    records.sort()

    output_dir = Path("sorted_bed_file_per_sample")
    output_dir.mkdir(exist_ok=True)

    selection_name = get_selection_name(args.selection)
    output_file = output_dir / f"{args.sample}.{selection_name}.sorted.bed"

    with open(output_file, "w") as output:
        for record in records:
            output.write(record[3])

    print(f"Wrote {len(records)} lines to {output_file}")


if __name__ == "__main__":
    main()
