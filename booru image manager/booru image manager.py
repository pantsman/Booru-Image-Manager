import yaml, helper, argparse, logging
from pathlib import Path, PurePath

def startup(configLoc):
    if args.verbose == True:
        logging.basicConfig(level=logging.INFO)
        logging.info('Loading App')
        if Path(configLoc).exists() == True:
            logging.info('Config file found')
            with open(configLoc) as configFile:
                try:
                    logging.info('Loading Config')
                    config = yaml.load(configFile)
                except yaml.YAMLError as exc:
                    logging.error(exc)
                    exit()
            return config
        else:
            logging.error('Configuration File Missing Exiting')
            exit()
            
    else:
        if Path(configLoc).exists() == True:
            with open(configLoc) as configFile:
                try:
                    config = yaml.load(configFile)
                except yaml.YAMLError as exc:
                    exit()
            return config
        else:
            exit()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Booru Image Manager')

    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Increases Verbosity')
    parser.add_argument('-c', '--config', dest='configLoc', default=Path('{0}/{1}'.format(Path(__file__).parent,'config.yml')), help='Specifies the Location of the Configuration File')
    
    subParsers = parser.add_subparsers(help='Available Commands', title='subcommands')
    
    parserDownload = subParsers.add_parser('download', help='Download Images')
    parserDownload.add_argument('-t', '--tags', dest='tags', help='Tags to Search for', nargs='+', required=True)
    parserDownload.add_argument('-f', '--folder', dest='downloadFolder', help='Folder to Download Images to', required=True)
    parserDownload.add_argument('-b', '--booru', dest='booru', help='Booru Site to Search', required=True)
    parserDownload.add_argument('-p', '--page', dest='page', help='Page to start downloading images from', nargs='?', default=1)
    
    #parserLoad = subParsers.add_parser('load', help='Load New Folders/Images')
    #parserLoad.add_argument('-f', '--folder', dest='imageFolder', help='Location of Folder to Load', required=True)

    args = parser.parse_args()
    
    config = startup(args.configLoc)

    if args.downloadFolder:
        helper.download(config['banned_tags'],config['ratings'],args.tags, args.downloadFolder, args.booru, args.page)