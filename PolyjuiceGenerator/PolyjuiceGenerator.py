"""
Created 3 November 2023
@author: Dimitris Lymperopoulos
Description: A script containing a counterfactual generator class that uses Polyjuice to generate edits
"""

import os
import torch
import argparse
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from polyjuice import Polyjuice


class PolyjuiceGenerator:
    def __init__(self, source_csv=None, source_col=None, dest_csv=None, cuda=None):
        """

        :param source_csv: a path to the csv file containing the original sentences
        :param source_col: the name of the column containing the original sentences
        :param dest_csv: a path to the csv file where the generated counterfactuals will be stored
        :param cuda: a boolean value indicating whether to use gpu for model inference
        """

        if source_csv is None:
            print("[ERROR]: source_csv must be specified")
            exit(1)
        if not os.path.exists(source_csv):
            print("[ERROR]: file {} does not exist".format(source_csv))
            exit(1)
        if source_col is None:
            print("[ERROR]: source_col must be specified")
            exit(1)
        self.sentences = pd.read_csv(source_csv)[source_col].tolist()

        self.cuda = torch.cuda.is_available() if cuda is None else cuda
        self.model = Polyjuice(model_path='uw-hai/polyjuice', is_cuda=self.cuda)

        self.dest_csv = 'polyjuice_edits.csv' if dest_csv is None else dest_csv
        self.counter_sentences = None

    def generate_counterfactuals(self):
        """
        A function that returns a list of counterfactuals generated by Polyjuice

        :return: a list of the generated counterfactual sentences
        """

        print("[INFO]: Generating Counterfactuals...")

        for s in tqdm(self.sentences):
            perturbations = self.model.perturb(s, num_perturbations=1)
            self.counter_sentences.append(perturbations[0] if perturbations else s)

        return self

    def export_to_csv(self):
        """
        A function that exports the generated counterfactuals to a csv file

        :return: None
        """

        print("[INFO]: Exporting counterfactuals to {}...".format(self.dest_csv))

        counter_df = pd.DataFrame({
            'counter_sents': self.counter_sentences
        })
        counter_df.to_csv(self.dest_csv, index=False)

        return self

    def pipeline(self, debug=False):
        if debug:
            self.generate_counterfactuals()
            for s in zip(self.sentences, self.counter_sentences):
                print("Original: {}\n\nCounter: {}\n".format(s[0], s[1]))
                print('=' * 100)
        else:
            self.generate_counterfactuals().export_to_csv()


def parse_input(args=None):
    """
        param args: The command line arguments provided by the user
        :return:  The parsed input Namespace
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--source-csv", type=str, action="store", metavar="source_csv",
                        required=True, help="The csv file with the sentences to be edited")
    parser.add_argument("-c", "--source-col", type=str, action="store", metavar="source_col",
                        required=True, help="The column name of the sentences in the csv")
    parser.add_argument("-d", "--dest-csv", type=str, action="store", metavar="dest_csv",
                        required=False, help="The destination csv where the edits will be stored")
    parser.add_argument("--cuda", action='store_true', required=False,
                        help="Whether to use cuda or not")

    return parser.parse_args(args)


def main(args):
    start_time = datetime.now()

    poly_generator = PolyjuiceGenerator(source_csv=args.source_csv, source_col=args.source_col,
                                        dest_csv=args.dest_csv, cuda=args.cuda)

    poly_generator.pipeline()

    print("\n\nScript execution time: " + str(datetime.now() - start_time))


if __name__ == '__main__':
    ARG = parse_input()
    main(ARG)
