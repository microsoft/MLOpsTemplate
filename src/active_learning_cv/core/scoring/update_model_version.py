import argparse
from strictyaml import load
from azureml.core import Workspace, Model

def main(args):
    # read in data
    ws = Workspace.get(name="ws01ent")  
    current_version= Model(ws,args.model_name).version
    with open(args.job_file, 'r') as yml_file:
        yml_content = yml_file.read()
        yml_obj =load(yml_content)
    with open(args.job_file, 'w') as yml_file:
        yml_obj["model"] =f"azureml:{args.model_name}:{current_version}"
        yml_file.write(yml_obj.as_yaml())


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--job_file", type=str)
    parser.add_argument("--model_name", type=str)
    # parse args
    args = parser.parse_args()

    # return args
    return args


# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)