import os
from Source.Application import Application

def main():

    # config path
    config_path = os.path.join(os.getcwd(),'Config','config.yaml')

    # Run app
    app = Application(config_path=config_path)
    app.work()

if __name__ == '__main__':

    main()