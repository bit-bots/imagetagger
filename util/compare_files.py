import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_path", type=str, default="", help="path to the image dataset")
    parser.add_argument("label_path", type=str, default="", help="path to the label file (txt)")
    args = parser.parse_args()

    # get the contents of the directory
    contents = os.listdir(args.dataset_path)

    # get all png files
    contents = list(filter(lambda x: x.lower().endswith(".png"), contents))

    labels = dict()

    with open(args.label_path, mode="r") as f:
        found_format_line = False

        # search for the format line 'imagename|x1|y1|x2|y2' line by line
        # labels are saved directly after this line
        for line in f:
            if "imagename|x1|y1|x2|y2" in line:
                found_format_line = True
                break

        # if format line was found, extract labels line by line
        if found_format_line:
            # starting at the first label-line
            for line in f:
                filename, x1, y1, x2, y2 = line.split("|")
                labels[filename] = {"x1": x1.strip(),
                                    "y1": y1.strip(),
                                    "x2": x2.strip(),
                                    "y2": y2.strip()}

    # image and label information
    print()
    print("comparing dataset '{}' with label txt '{}'".format(args.dataset_path.split("/")[-1],
                                                          args.label_path.split("/")[-1]))
    print()
    print("dataset '{1}'\n-> contains {0} png files".format(len(contents), args.dataset_path))
    print()
    print("label txt '{1}'\n-> contains {0} labels".format(len(labels.keys()), args.label_path))
    print()

    # compute difference
    set_pngs = set(contents)
    set_labels = set(labels.keys())

    diff = sorted(set_pngs.symmetric_difference(set_labels))

    print("symmetric difference of dataset and labels contains {} entries".format(len(diff)))

    print()
    print("files that are missing in labels txt:")
    for i, file in enumerate(set_pngs.difference(set_labels)):
        print("#{}  ->  {}".format(i, file))

    print()
    print("files that are missing in dataset:")
    for i, file in enumerate(set_labels.difference(set_pngs)):
        print("#{}  ->  {}".format(i, file))


